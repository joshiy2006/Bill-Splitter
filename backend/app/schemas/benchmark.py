from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BenchmarkRunRequest(BaseModel):
    n_list: List[int] = Field(default=[2, 4, 6, 8, 10, 12, 14, 16, 18], description="List of n (non-zero members) between 2 and 20")
    trials: int = Field(default=5, ge=1, le=20)

class BenchmarkSeriesPoint(BaseModel):
    n: int
    trials: int
    greedy_ms: float
    dp_ms: float
    greedy_txns: float
    dp_txns: float

class BenchmarkResponse(BaseModel):
    series: List[BenchmarkSeriesPoint]
