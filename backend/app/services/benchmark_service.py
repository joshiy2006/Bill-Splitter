import random
import time
import uuid
from typing import List, Dict, Any
from app.db import db_client
from app.algorithms.greedy import settle_greedy
from app.algorithms.dp_optimal import settle_dp, DpSizeError

def generate_random_zero_sum_balances(n: int) -> Dict[str, int]:
    """Generates a random zero-sum balance set with n non-zero members."""
    member_ids = [f"m_{i}" for i in range(n)]
    raw_vals = [random.randint(100, 10000) for _ in range(n // 2)]
    pos_sum = sum(raw_vals)

    # Distribute negative debts
    neg_vals = []
    rem = pos_sum
    for i in range(n - len(raw_vals) - 1):
        v = random.randint(1, rem - (n - len(raw_vals) - 1 - i))
        neg_vals.append(-v)
        rem -= v
    neg_vals.append(-rem)

    all_vals = raw_vals + neg_vals
    random.shuffle(all_vals)

    return {member_ids[i]: all_vals[i] for i in range(n)}


def execute_benchmark(owner_id: str, n_list: List[int], trials: int = 5) -> List[Dict[str, Any]]:
    """
    Executes benchmark over n values, measuring runtime and transaction count for Greedy vs DP.
    Persists results in benchmark_runs table.
    """
    series = []

    for n in n_list:
        if n < 2 or n > 20:
            continue

        greedy_times = []
        dp_times = []
        greedy_txns_list = []
        dp_txns_list = []

        for _ in range(trials):
            bals = generate_random_zero_sum_balances(n)

            # Greedy run
            t0 = time.perf_counter()
            g_res = settle_greedy(bals)
            t1 = time.perf_counter()
            greedy_times.append((t1 - t0) * 1000.0)
            greedy_txns_list.append(g_res["txn_count"])

            # DP run if n <= 18
            if n <= 18:
                t2 = time.perf_counter()
                try:
                    dp_res = settle_dp(bals)
                    t3 = time.perf_counter()
                    dp_times.append((t3 - t2) * 1000.0)
                    dp_txns_list.append(dp_res["txn_count"])
                except Exception:
                    dp_times.append(0.0)
                    dp_txns_list.append(0.0)
            else:
                dp_times.append(0.0)
                dp_txns_list.append(0.0)

        mean_g_ms = sum(greedy_times) / trials
        mean_dp_ms = sum(dp_times) / trials if n <= 18 else 0.0
        mean_g_txns = sum(greedy_txns_list) / trials
        mean_dp_txns = sum(dp_txns_list) / trials if n <= 18 else 0.0

        point = {
            "n": n,
            "trials": trials,
            "greedy_ms": round(mean_g_ms, 3),
            "dp_ms": round(mean_dp_ms, 3),
            "greedy_txns": round(mean_g_txns, 2),
            "dp_txns": round(mean_dp_txns, 2)
        }
        series.append(point)

        # Store in DB
        db_rec = dict(point, id=str(uuid.uuid4()), owner_id=owner_id)
        try:
            db_client.table("benchmark_runs").insert(db_rec).execute()
        except Exception:
            pass

    return series


def fetch_user_benchmarks(owner_id: str) -> List[Dict[str, Any]]:
    """Retrieves previously stored benchmark runs for current user."""
    try:
        res = db_client.table("benchmark_runs").select("*").eq("owner_id", owner_id).order("n", desc=False).execute()
        return res.data or []
    except Exception:
        return []
