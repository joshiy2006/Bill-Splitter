"""
Full end-to-end FastAPI integration test walking through:
Create Group -> Add Members -> Add Expenses in 4 Split Modes -> Compare (Greedy vs DP) -> Adopt Plan -> Pay Queue -> Verify All Balances Return to Zero.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.deps import get_current_user, check_group_ownership

client = TestClient(app)

AUTH_HEADERS = {"Authorization": "Bearer fake-test-jwt-token"}

def test_full_integration_flow():
    # Mock auth dependencies for unit/integration testing
    app.dependency_overrides[get_current_user] = lambda: {"sub": "test_user_id", "email": "test@example.com"}
    app.dependency_overrides[check_group_ownership] = lambda id: id

    # 1. Create Group
    resp_g = client.post("/groups", json={"name": "Integration Test Group", "currency": "INR"}, headers=AUTH_HEADERS)
    assert resp_g.status_code == 200
    group = resp_g.json()
    g_id = group["id"]

    # 2. Add 4 Members
    m_ids = []
    for name in ["Asha", "Ravi", "Karan", "Sneha"]:
        resp_m = client.post(f"/groups/{g_id}/members", json={"name": name}, headers=AUTH_HEADERS)
        assert resp_m.status_code == 200
        m_ids.append(resp_m.json()["id"])

    m1, m2, m3, m4 = m_ids

    # 3. Add Expenses in all 4 Split Modes:
    # 3a. Equal Split (1000 paise paid by m1)
    e1 = client.post(f"/groups/{g_id}/expenses", json={
        "description": "Equal Dinner",
        "category": "food",
        "amount_paise": 1000,
        "paid_by": m1,
        "split_type": "equal",
        "participants": [{"member_id": m} for m in m_ids]
    }, headers=AUTH_HEADERS)
    assert e1.status_code == 200

    # 3b. Exact Split (2000 paise paid by m2)
    e2 = client.post(f"/groups/{g_id}/expenses", json={
        "description": "Exact Taxi",
        "category": "travel",
        "amount_paise": 2000,
        "paid_by": m2,
        "split_type": "exact",
        "participants": [
            {"member_id": m1, "owed_paise": 500},
            {"member_id": m2, "owed_paise": 500},
            {"member_id": m3, "owed_paise": 500},
            {"member_id": m4, "owed_paise": 500}
        ]
    }, headers=AUTH_HEADERS)
    assert e2.status_code == 200

    # 3c. Percentage Split (3000 paise paid by m3)
    e3 = client.post(f"/groups/{g_id}/expenses", json={
        "description": "Percentage Movie",
        "category": "entertainment",
        "amount_paise": 3000,
        "paid_by": m3,
        "split_type": "percentage",
        "participants": [
            {"member_id": m1, "percentage": 25.0},
            {"member_id": m2, "percentage": 25.0},
            {"member_id": m3, "percentage": 25.0},
            {"member_id": m4, "percentage": 25.0}
        ]
    }, headers=AUTH_HEADERS)
    assert e3.status_code == 200

    # 3d. Shares Split (4000 paise paid by m4)
    e4 = client.post(f"/groups/{g_id}/expenses", json={
        "description": "Shares Drinks",
        "category": "utilities",
        "amount_paise": 4000,
        "paid_by": m4,
        "split_type": "shares",
        "participants": [
            {"member_id": m1, "shares": 1.0},
            {"member_id": m2, "shares": 1.0},
            {"member_id": m3, "shares": 1.0},
            {"member_id": m4, "shares": 1.0}
        ]
    }, headers=AUTH_HEADERS)
    assert e4.status_code == 200

    # 4. Check Balances (Sum must be 0)
    resp_b = client.get(f"/groups/{g_id}/balances", headers=AUTH_HEADERS)
    assert resp_b.status_code == 200
    balances = resp_b.json()
    assert sum(balances.values()) == 0

    # 5. Compare Settlement Plans (Greedy vs DP)
    resp_comp = client.post(f"/groups/{g_id}/settle/compare", headers=AUTH_HEADERS)
    assert resp_comp.status_code == 200
    comp_data = resp_comp.json()
    assert "greedy" in comp_data
    assert "dp" in comp_data

    dp_run_id = comp_data["dp"]["id"]

    # 6. Adopt DP Settlement Plan
    resp_adopt = client.post(f"/groups/{g_id}/settle/adopt", json={"run_id": dp_run_id}, headers=AUTH_HEADERS)
    assert resp_adopt.status_code == 200
    adopt_data = resp_adopt.json()
    assert adopt_data["status"] == "adopted"

    # 7. Fetch Payment Queue
    resp_q = client.get(f"/groups/{g_id}/payments/queue", headers=AUTH_HEADERS)
    assert resp_q.status_code == 200
    queue = resp_q.json()
    assert len(queue) > 0

    # 8. Pay all transactions in queue
    for txn in queue:
        t_id = txn["id"]
        resp_pay = client.post(f"/groups/{g_id}/payments/{t_id}/pay", headers=AUTH_HEADERS)
        assert resp_pay.status_code == 200

    # 9. Verify that after paying every transaction, ALL balances drive to exactly 0!
    resp_b_final = client.get(f"/groups/{g_id}/balances", headers=AUTH_HEADERS)
    assert resp_b_final.status_code == 200
    final_bals = resp_b_final.json()
    assert all(val == 0 for val in final_bals.values()), f"Expected all balances 0, got {final_bals}"
