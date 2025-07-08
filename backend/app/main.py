from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

# FastAPI 앱 생성
app = FastAPI(
    title="Market Timing Calendar",
    description="마켓 타이밍 캘린더 API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS 설정 (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용, 프로덕션에서는 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# React 빌드 파일 경로 설정 - 절대경로 사용
static_dir = Path("/app/static")
print(f"Static directory: {static_dir}")
print(f"Static directory exists: {static_dir.exists()}")

# API 라우트들
@app.get("/api/health")
async def health_check():
    """API 헬스체크"""
    return {"status": "healthy", "service": "market-timing-calendar"}

@app.get("/api/test")
async def api_test():
    """API 테스트 엔드포인트"""
    return {"message": "API is working!", "backend": "FastAPI", "frontend": "React"}

# React 정적 파일 서빙 설정
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
            "static_dir_expected": str(static_dir)
        }

# python main.py로 직접 실행 가능하게 하는 코드
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )