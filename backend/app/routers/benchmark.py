from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.deps import get_current_user
from app.schemas.benchmark import BenchmarkRunRequest, BenchmarkResponse
from app.services.benchmark_service import execute_benchmark, fetch_user_benchmarks

router = APIRouter(prefix="/benchmark", tags=["Algorithm Benchmark"])

@router.post("", response_model=BenchmarkResponse)
def run_benchmark_endpoint(req: BenchmarkRunRequest, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub") or user.get("id") or "test_user"
    series = execute_benchmark(owner_id=user_id, n_list=req.n_list, trials=req.trials)
    return {"series": series}


@router.get("", response_model=BenchmarkResponse)
def get_benchmark_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub") or user.get("id") or "test_user"
    series = fetch_user_benchmarks(user_id)
    return {"series": series}
