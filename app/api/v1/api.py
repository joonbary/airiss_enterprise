# app/api/v1/api.py
"""
AIRISS v4.0 API 라우터
모든 v1 엔드포인트 통합
"""

from fastapi import APIRouter
from app.api.v1.endpoints import analysis, employee

api_router = APIRouter()

# 분석 관련 엔드포인트
api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["analysis"]
)

# 직원 관련 엔드포인트
api_router.include_router(
    employee.router,
    prefix="/employee",
    tags=["employee"]
)

# 향후 추가 엔드포인트
# api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
# api_router.include_router(reports.router, prefix="/reports", tags=["reports"])