import uvicorn
from pathlib import Path
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI 앱 라이프사이클 관리"""
    try:
        logger.info("애플리케이션 시작 완료")
        yield

    except Exception as e:
        logger.error("애플리케이션 시작 실패: {str(e)}")
        raise
    finally:
        # 정리 작업
        ...


# FastAPI 앱 생성
def create_app():
    app = FastAPI(
        lifespan=lifespan,
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url=settings.OPENAPI_URL,
    )

    # CORS 설정 (개발용)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 개발용, 프로덕션에서는 도메인 지정
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API 라우터 등록
    from app.api.index import router
    from app.api.v1.api import api_router as v1_api_router

    app.include_router(router, prefix="/api")
    app.include_router(v1_api_router, prefix="/api/v1")

    # React 정적 파일 서빙 설정
    static_dir = Path("/app/static")
    if static_dir.exists():
        # /static 경로로 정적 파일들 (JS, CSS, 이미지 등) 서빙
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

        # assets 폴더가 있다면 별도 마운트 (Vite는 보통 /assets에 빌드 파일들을 생성)
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/")
        async def serve_react_app():
            """메인 페이지 - React 앱 서빙"""
            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            raise HTTPException(status_code=404, detail="Frontend index.html not found")

        # React Router를 위한 fallback (SPA 라우팅 지원)
        @app.get("/{full_path:path}")
        async def serve_react_router(full_path: str):
            """
            React Router를 위한 fallback
            API 경로가 아닌 모든 경로를 React 앱으로 라우팅
            """
            # API 경로는 제외
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="API endpoint not found")

            # static, assets 경로도 제외
            if full_path.startswith(("static/", "assets/")):
                raise HTTPException(status_code=404, detail="Static file not found")

            # 나머지 모든 경로는 React 앱으로
            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            raise HTTPException(status_code=404, detail="Frontend not found")

    else:
        print("⚠️  Static directory not found - Frontend will not be served")

        @app.get("/")
        async def no_frontend():
            """Frontend가 없을 때 보여줄 메시지"""
            return {
                "message": "Backend is running!",
                "note": "Frontend not found in static directory",
                "api_docs": "/api/docs",
                "static_dir_expected": str(static_dir),
            }

    return app


if __name__ == "__main__":
    uvicorn.run("main:create_app", host="0.0.0.0", port=8000, reload=True)
