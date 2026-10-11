from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import db_client

from app.routers import (
    groups,
    members,
    expenses,
    balances,
    settlement,
    payments,
    allocate,
    insights,
    benchmark
)

app = FastAPI(
    title="Smart Bill-Splitting System API",
    description="DAA Assignment API for group expense splitting, debt settlement, and algorithm benchmarks.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Error Format Handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": str(exc.status_code), "message": str(exc.detail)}}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": str(exc.errors())}}
    )

# Register Routers
app.include_router(groups.router)
app.include_router(members.router)
app.include_router(expenses.router)
app.include_router(balances.router)
app.include_router(settlement.router)
app.include_router(payments.router)
app.include_router(allocate.router)
app.include_router(insights.router)
app.include_router(benchmark.router)

@app.get("/health")
@app.get("/api/health")
def health_check():
    db_ok = False
    try:
        res = db_client.table("groups").select("id").limit(1).execute()
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok",
        "db_connected": db_ok,
        "service": "Smart Bill-Splitting System API"
    }
