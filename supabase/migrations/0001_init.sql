-- ============================================================
-- Extensions and enums
-- ============================================================
create extension if not exists pgcrypto;

create type public.split_type as enum ('equal', 'exact', 'percentage', 'shares');
create type public.settlement_method as enum ('greedy', 'dp');
create type public.txn_status as enum ('pending', 'paid', 'cancelled');

-- ============================================================
-- Core tables
-- ============================================================
create table public.groups (
 id uuid primary key default gen_random_uuid(),
 owner_id uuid not null references auth.users (id) on delete cascade,
 name text not null check (char_length(name) between 1 and 80),
 currency char(3) not null default 'INR',
 created_at timestamptz not null default now()
);
create index groups_owner_idx on public.groups (owner_id);

-- Members are people inside a group. They do not need their own login.
create table public.members (
 id uuid primary key default gen_random_uuid(),
 group_id uuid not null references public.groups (id) on delete cascade,
 name text not null check (char_length(name) between 1 and 60),
 email text,
 created_at timestamptz not null default now(),
 unique (id, group_id) -- target for composite FKs below
);
create unique index members_group_name_uq on public.members (group_id, lower(name));

create table public.expenses (
 id uuid primary key default gen_random_uuid(),
 group_id uuid not null references public.groups (id) on delete cascade,
 description text not null check (char_length(description) between 1 and 200),
 category text not null default 'general',
 amount_paise bigint not null check (amount_paise > 0),
 paid_by uuid not null,
 split_type public.split_type not null default 'equal',
 expense_date date not null default current_date,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 -- payer must belong to the same group
 foreign key (paid_by, group_id) references public.members (id, group_id) on delete restrict
);
create index expenses_group_date_idx on public.expenses (group_id, expense_date desc);
create index expenses_group_cat_idx on public.expenses (group_id, category);
create index expenses_paid_by_idx on public.expenses (paid_by);

-- One row per participant of an expense. owed_paise is the final resolved share.
create table public.expense_splits (
 expense_id uuid not null references public.expenses (id) on delete cascade,
 member_id uuid not null references public.members (id) on delete restrict,
 owed_paise bigint not null check (owed_paise >= 0),
 share_value numeric(12,4), -- the raw input: percentage, share count, or null
 primary key (expense_id, member_id)
);
create index expense_splits_member_idx on public.expense_splits (member_id);

-- Invariant: the splits of an expense must sum exactly to its amount.
create or replace function public.check_split_total() returns trigger
language plpgsql as $$
declare
 v_expense uuid := coalesce(new.expense_id, old.expense_id);
 v_amount bigint;
 v_total bigint;
begin
 select amount_paise into v_amount from public.expenses where id = v_expense;
 if v_amount is null then
 return null; -- expense was deleted (cascade); nothing to check
 end if;
 select coalesce(sum(owed_paise), 0) into v_total
 from public.expense_splits where expense_id = v_expense;
 if v_total <> v_amount then
 raise exception 'Splits (%) do not sum to expense amount (%) for expense %',
 v_total, v_amount, v_expense;
 end if;
 return null;
end $$;

create constraint trigger expense_splits_total_ck
 after insert or update or delete on public.expense_splits
 deferrable initially deferred
 for each row execute function public.check_split_total();

-- ============================================================
-- Settlement
-- ============================================================
-- One row per algorithm run. A greedy run and a dp run triggered by the same
-- "compare" action share a compare_id.
create table public.settlement_runs (
 id uuid primary key default gen_random_uuid(),
 group_id uuid not null references public.groups (id) on delete cascade,
 compare_id uuid not null,
 method public.settlement_method not null,
 is_active boolean not null default false, -- the plan the group adopted
 member_count int not null,
 nonzero_count int not null, -- members with non-zero net balance
 txn_count int not null,
 total_moved_paise bigint not null,
 runtime_ms numeric(10,3) not null,
 balances jsonb not null, -- snapshot: { member_id: net_paise }
 created_at timestamptz not null default now()
);
create index settlement_runs_group_idx on public.settlement_runs (group_id, created_at desc);
create index settlement_runs_compare_idx on public.settlement_runs (compare_id);
create unique index one_active_run_per_group on public.settlement_runs (group_id) where is_active = true;

create table public.settlement_transactions (
 id uuid primary key default gen_random_uuid(),
 run_id uuid not null references public.settlement_runs (id) on delete cascade,
 from_member uuid not null references public.members (id) on delete restrict,
 to_member uuid not null references public.members (id) on delete restrict,
 amount_paise bigint not null check (amount_paise > 0),
 due_date date,
 priority int not null default 0, -- computed by the scheduler heap
 status public.txn_status not null default 'pending',
 paid_at timestamptz,
 check (from_member <> to_member)
);
create index settlement_txn_run_idx on public.settlement_transactions (run_id);
create index settlement_txn_due_idx on public.settlement_transactions (status, due_date);

-- Money actually paid. Feeds the balances view so settled debts drop out.
create table public.payments (
 id uuid primary key default gen_random_uuid(),
 group_id uuid not null references public.groups (id) on delete cascade,
 from_member uuid not null references public.members (id) on delete restrict,
 to_member uuid not null references public.members (id) on delete restrict,
 amount_paise bigint not null check (amount_paise > 0),
 txn_id uuid references public.settlement_transactions (id) on delete set null,
 created_at timestamptz not null default now(),
 check (from_member <> to_member)
);
create index payments_group_idx on public.payments (group_id);

-- Measured greedy-vs-DP runs for the comparison chart.
create table public.benchmark_runs (
 id uuid primary key default gen_random_uuid(),
 owner_id uuid not null references auth.users (id) on delete cascade,
 n int not null check (n between 2 and 22),
 trials int not null default 5,
 greedy_ms numeric(10,3) not null,
 dp_ms numeric(10,3) not null,
 greedy_txns numeric(6,2) not null, -- mean over trials
 dp_txns numeric(6,2) not null,
 created_at timestamptz not null default now()
);
create index benchmark_owner_idx on public.benchmark_runs (owner_id, n);

-- ============================================================
-- Balances view (net_paise > 0 => is owed money; < 0 => owes money)
-- net = paid - owed + payments_sent - payments_received
-- ============================================================
create view public.member_balances with (security_invoker = true) as
select
 m.group_id,
 m.id as member_id,
 m.name,
 coalesce((select sum(e.amount_paise) from public.expenses e where e.paid_by = m.id), 0)
 - coalesce((select sum(s.owed_paise) from public.expense_splits s where s.member_id = m.id), 0)
 + coalesce((select sum(p.amount_paise) from public.payments p where p.from_member = m.id), 0)
 - coalesce((select sum(p.amount_paise) from public.payments p where p.to_member = m.id), 0)
 as net_paise
from public.members m;

-- ============================================================
-- Row-level security (defense in depth; the API also checks ownership)
-- ============================================================
create or replace function public.owns_group(gid uuid) returns boolean
language sql stable security definer set search_path = public as $$
 select exists (select 1 from public.groups g where g.id = gid and g.owner_id = auth.uid());
$$;

alter table public.groups enable row level security;
alter table public.members enable row level security;
alter table public.expenses enable row level security;
alter table public.expense_splits enable row level security;
alter table public.settlement_runs enable row level security;
alter table public.settlement_transactions enable row level security;
alter table public.payments enable row level security;
alter table public.benchmark_runs enable row level security;

create policy groups_rw on public.groups for all
 using (owner_id = auth.uid()) with check (owner_id = auth.uid());

create policy benchmark_rw on public.benchmark_runs for all
 using (owner_id = auth.uid()) with check (owner_id = auth.uid());

do $$
declare t text;
begin
 foreach t in array array['members', 'expenses', 'settlement_runs', 'payments'] loop
 execute format(
 'create policy %I on public.%I for all using (public.owns_group(group_id)) with check (public.owns_group(group_id))',
 t || '_rw', t);
 end loop;
end $$;

create policy expense_splits_rw on public.expense_splits for all
 using (exists (select 1 from public.expenses e
 where e.id = expense_id and public.owns_group(e.group_id)))
 with check (exists (select 1 from public.expenses e
 where e.id = expense_id and public.owns_group(e.group_id)));

create policy settlement_txn_rw on public.settlement_transactions for all
 using (exists (select 1 from public.settlement_runs r
 where r.id = run_id and public.owns_group(r.group_id)))
 with check (exists (select 1 from public.settlement_runs r
 where r.id = run_id and public.owns_group(r.group_id)));
