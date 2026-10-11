export type SplitType = 'equal' | 'exact' | 'percentage' | 'shares';
export type SettlementMethod = 'greedy' | 'dp';
export type TxnStatus = 'pending' | 'paid' | 'cancelled';

export interface Group {
  id: string;
  owner_id: string;
  name: string;
  currency: string;
  created_at: string;
}

export interface Member {
  id: string;
  group_id: string;
  name: string;
  email?: string;
  created_at: string;
}

export interface ExpenseSplit {
  expense_id: string;
  member_id: string;
  owed_paise: number;
  share_value?: number;
}

export interface Expense {
  id: string;
  group_id: string;
  description: string;
  category: string;
  amount_paise: number;
  paid_by: string;
  split_type: SplitType;
  expense_date: string;
  created_at: string;
  updated_at: string;
  splits?: ExpenseSplit[];
}

export interface ParticipantSplitInput {
  member_id: string;
  owed_paise?: number;
  percentage?: number;
  shares?: number;
}

export interface ExpenseCreatePayload {
  description: string;
  category: string;
  amount_paise: number;
  paid_by: string;
  split_type: SplitType;
  expense_date?: string;
  participants: ParticipantSplitInput[];
}

export interface SettlementTransaction {
  id?: string;
  run_id?: string;
  from_member: string;
  to_member: string;
  amount_paise: number;
  due_date?: string;
  priority: number;
  status: TxnStatus;
  paid_at?: string;
}

export interface SettlementRunPlan {
  id: string;
  method: SettlementMethod;
  member_count: number;
  nonzero_count: number;
  txn_count: number;
  total_moved_paise: number;
  runtime_ms: number;
  transactions: SettlementTransaction[];
}

export interface SettleCompareResponse {
  compare_id: string;
  greedy: SettlementRunPlan;
  dp?: SettlementRunPlan;
  transactions_saved_by_dp: number;
  dp_notice?: string;
}

export interface DebtEdge {
  from_member: string;
  to_member: string;
  amount_paise: number;
}

export interface CancelledCycle {
  nodes: string[];
  bottleneck_paise: number;
}

export interface DebtGraphResponse {
  raw: DebtEdge[];
  simplified: DebtEdge[];
  cancelled_cycles: CancelledCycle[];
}

export interface ItemAllocationInput {
  id?: string;
  description: string;
  amount_paise: number;
}

export interface AllocationResponse {
  group_1: ItemAllocationInput[];
  group_2: ItemAllocationInput[];
  group_1_total: number;
  group_2_total: number;
  difference: number;
}

export interface TopSpender {
  member_id: string;
  member_name: string;
  total_spent_paise: number;
}

export interface TopExpense {
  id: string;
  description: string;
  amount_paise: number;
  category: string;
  paid_by: string;
  paid_by_name: string;
  expense_date: string;
}

export interface InsightsResponse {
  top_spenders: TopSpender[];
  top_expenses: TopExpense[];
  spend_by_category: Record<string, number>;
}

export interface BenchmarkSeriesPoint {
  n: number;
  trials: number;
  greedy_ms: number;
  dp_ms: number;
  greedy_txns: number;
  dp_txns: number;
}

export interface BenchmarkResponse {
  series: BenchmarkSeriesPoint[];
}
