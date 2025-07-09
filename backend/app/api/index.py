from datetime import datetime

from fastapi import APIRouter
from starlette.responses import Response

router = APIRouter()


@router.get("/")
async def index():
    """기본 엔드포인트"""
    return Response(f"UTC: {datetime.now().strftime('%Y.%m.%d %H:%M:%S')}")


@router.get("/health")
async def health_check():
    """헬스체크"""
    return {"status": "healthy", "service": "Market Timing Calendar", "version": "1.0.0"}
