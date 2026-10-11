-- Seed data for Demo Group with 6 members and 15 realistic expenses

do $$
declare
  v_owner_id uuid;
  v_group_id uuid := '11111111-1111-1111-1111-111111111111';
  v_m1 uuid := '22222222-1111-1111-1111-111111111111'; -- Asha
  v_m2 uuid := '22222222-2222-2222-2222-222222222222'; -- Ravi
  v_m3 uuid := '22222222-3333-3333-3333-333333333333'; -- Karan
  v_m4 uuid := '22222222-4444-4444-4444-444444444444'; -- Sneha
  v_m5 uuid := '22222222-5555-5555-5555-555555555555'; -- Rohan
  v_m6 uuid := '22222222-6666-6666-6666-666666666666'; -- Priya

  v_e1 uuid := gen_random_uuid();
  v_e2 uuid := gen_random_uuid();
  v_e3 uuid := gen_random_uuid();
  v_e4 uuid := gen_random_uuid();
  v_e5 uuid := gen_random_uuid();
  v_e6 uuid := gen_random_uuid();
  v_e7 uuid := gen_random_uuid();
  v_e8 uuid := gen_random_uuid();
  v_e9 uuid := gen_random_uuid();
  v_e10 uuid := gen_random_uuid();
  v_e11 uuid := gen_random_uuid();
  v_e12 uuid := gen_random_uuid();
  v_e13 uuid := gen_random_uuid();
  v_e14 uuid := gen_random_uuid();
  v_e15 uuid := gen_random_uuid();
begin
  -- Get first existing user ID or fallback
  select id into v_owner_id from auth.users limit 1;
  if v_owner_id is null then
    return;
  end if;

  -- Create group
  insert into public.groups (id, owner_id, name, currency)
  values (v_group_id, v_owner_id, 'Goa Beach House & Flatmates', 'INR')
  on conflict (id) do nothing;

  -- Insert 6 members
  insert into public.members (id, group_id, name, email) values
    (v_m1, v_group_id, 'Asha Sharma', 'asha@example.com'),
    (v_m2, v_group_id, 'Ravi Verma', 'ravi@example.com'),
    (v_m3, v_group_id, 'Karan Patel', 'karan@example.com'),
    (v_m4, v_group_id, 'Sneha Gupta', 'sneha@example.com'),
    (v_m5, v_group_id, 'Rohan Mehta', 'rohan@example.com'),
    (v_m6, v_group_id, 'Priya Singh', 'priya@example.com')
  on conflict (id, group_id) do nothing;

  -- 1. Villa Rent (Rent - ₹60,000 = 6,000,000 paise) split equally among 6 (1,000,000 paise each)
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e1, v_group_id, 'Goa Luxury Villa Rent', 'rent', 6000000, v_m1, 'equal', current_date - interval '14 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e1, v_m1, 1000000), (v_e1, v_m2, 1000000), (v_e1, v_m3, 1000000),
    (v_e1, v_m4, 1000000), (v_e1, v_m5, 1000000), (v_e1, v_m6, 1000000);

  -- 2. Beachside Seafood Dinner (Food - ₹12,000 = 1,200,000 paise) paid by Ravi
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e2, v_group_id, 'Beachside Shack Dinner', 'food', 1200000, v_m2, 'equal', current_date - interval '13 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e2, v_m1, 200000), (v_e2, v_m2, 200000), (v_e2, v_m3, 200000),
    (v_e2, v_m4, 200000), (v_e2, v_m5, 200000), (v_e2, v_m6, 200000);

  -- 3. Airport SUV Cab (Travel - ₹3,600 = 360,000 paise) paid by Karan
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e3, v_group_id, 'Airport Cab Transfer', 'travel', 360000, v_m3, 'equal', current_date - interval '14 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e3, v_m1, 60000), (v_e3, v_m2, 60000), (v_e3, v_m3, 60000),
    (v_e3, v_m4, 60000), (v_e3, v_m5, 60000), (v_e3, v_m6, 60000);

  -- 4. Water Sports Adventure (Entertainment - ₹18,000 = 1,800,000 paise) paid by Sneha
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e4, v_group_id, 'Parasailing & Jet Ski', 'entertainment', 1800000, v_m4, 'equal', current_date - interval '12 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e4, v_m1, 300000), (v_e4, v_m2, 300000), (v_e4, v_m3, 300000),
    (v_e4, v_m4, 300000), (v_e4, v_m5, 300000), (v_e4, v_m6, 300000);

  -- 5. Grocery Supermarket Run (Utilities - ₹4,500 = 450,000 paise) paid by Rohan
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e5, v_group_id, 'Supermarket Drinks & Snacks', 'utilities', 450000, v_m5, 'equal', current_date - interval '11 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e5, v_m1, 75000), (v_e5, v_m2, 75000), (v_e5, v_m3, 75000),
    (v_e5, v_m4, 75000), (v_e5, v_m5, 75000), (v_e5, v_m6, 75000);

  -- 6. Sunset Cruise Tickets (Entertainment - ₹9,000 = 900,000 paise) paid by Priya
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e6, v_group_id, 'Mandovi Sunset Cruise', 'entertainment', 900000, v_m6, 'equal', current_date - interval '10 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e6, v_m1, 150000), (v_e6, v_m2, 150000), (v_e6, v_m3, 150000),
    (v_e6, v_m4, 150000), (v_e6, v_m5, 150000), (v_e6, v_m6, 150000);

  -- 7. Scooters Fuel & Rental (Travel - ₹6,000 = 600,000 paise) paid by Asha
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e7, v_group_id, 'Scooter Rental & Petrol', 'travel', 600000, v_m1, 'equal', current_date - interval '9 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e7, v_m1, 100000), (v_e7, v_m2, 100000), (v_e7, v_m3, 100000),
    (v_e7, v_m4, 100000), (v_e7, v_m5, 100000), (v_e7, v_m6, 100000);

  -- 8. Gourmet Breakfast Cafe (Food - ₹3,600 = 360,000 paise) paid by Ravi
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e8, v_group_id, 'Artisan Cafe Breakfast', 'food', 360000, v_m2, 'equal', current_date - interval '8 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e8, v_m1, 60000), (v_e8, v_m2, 60000), (v_e8, v_m3, 60000),
    (v_e8, v_m4, 60000), (v_e8, v_m5, 60000), (v_e8, v_m6, 60000);

  -- 9. Scuba Diving Expedition (Entertainment - ₹24,000 = 2,400,000 paise) paid by Karan
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e9, v_group_id, 'Grande Island Scuba Diving', 'entertainment', 2400000, v_m3, 'equal', current_date - interval '7 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e9, v_m1, 400000), (v_e9, v_m2, 400000), (v_e9, v_m3, 400000),
    (v_e9, v_m4, 400000), (v_e9, v_m5, 400000), (v_e9, v_m6, 400000);

  -- 10. Villa Electricity & WiFi (Utilities - ₹3,000 = 300,000 paise) paid by Sneha
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e10, v_group_id, 'Villa WiFi & Utilities', 'utilities', 300000, v_m4, 'equal', current_date - interval '6 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e10, v_m1, 50000), (v_e10, v_m2, 50000), (v_e10, v_m3, 50000),
    (v_e10, v_m4, 50000), (v_e10, v_m5, 50000), (v_e10, v_m6, 50000);

  -- 11. Club Night Out (Entertainment - ₹15,000 = 1,500,000 paise) paid by Rohan
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e11, v_group_id, 'Tito’s Lane Club Party', 'entertainment', 1500000, v_m5, 'equal', current_date - interval '5 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e11, v_m1, 250000), (v_e11, v_m2, 250000), (v_e11, v_m3, 250000),
    (v_e11, v_m4, 250000), (v_e11, v_m5, 250000), (v_e11, v_m6, 250000);

  -- 12. Souvenir Shopping & Gifts (General - ₹6,600 = 660,000 paise) paid by Priya
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e12, v_group_id, 'Flea Market Spices & Souvenirs', 'general', 660000, v_m6, 'equal', current_date - interval '4 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e12, v_m1, 110000), (v_e12, v_m2, 110000), (v_e12, v_m3, 110000),
    (v_e12, v_m4, 110000), (v_e12, v_m5, 110000), (v_e12, v_m6, 110000);

  -- 13. Poolside Barbecue (Food - ₹7,200 = 720,000 paise) paid by Asha
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e13, v_group_id, 'Villa Barbecue Supplies', 'food', 720000, v_m1, 'equal', current_date - interval '3 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e13, v_m1, 120000), (v_e13, v_m2, 120000), (v_e13, v_m3, 120000),
    (v_e13, v_m4, 120000), (v_e13, v_m5, 120000), (v_e13, v_m6, 120000);

  -- 14. Return Train Tickets (Travel - ₹10,800 = 1,080,000 paise) paid by Ravi
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e14, v_group_id, 'Vande Bharat Express Tickets', 'travel', 1080000, v_m2, 'equal', current_date - interval '2 days');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e14, v_m1, 180000), (v_e14, v_m2, 180000), (v_e14, v_m3, 180000),
    (v_e14, v_m4, 180000), (v_e14, v_m5, 180000), (v_e14, v_m6, 180000);

  -- 15. Farewell Dinner & Drinks (Food - ₹14,400 = 1,440,000 paise) paid by Karan
  insert into public.expenses (id, group_id, description, category, amount_paise, paid_by, split_type, expense_date)
  values (v_e15, v_group_id, 'Farewell Dinner at Thalassa', 'food', 1440000, v_m3, 'equal', current_date - interval '1 day');
  insert into public.expense_splits (expense_id, member_id, owed_paise) values
    (v_e15, v_m1, 240000), (v_e15, v_m2, 240000), (v_e15, v_m3, 240000),
    (v_e15, v_m4, 240000), (v_e15, v_m5, 240000), (v_e15, v_m6, 240000);

end $$;
