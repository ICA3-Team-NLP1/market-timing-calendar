"""
테스트 공통 설정 및 Fixture
"""
import sys
import os
from pathlib import Path


# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 테스트 환경 변수 설정 (app 모듈 import 전에 설정)
DB_HOST: str = os.environ["DB_HOST"] if os.environ.get("DB_HOST") else "localhost"
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", f"postgresql://postgres:password@{DB_HOST}:5432/market_timing_test")
os.environ["FASTAPI_ENV"] = "test"
os.environ["DATABASE_URL"] = TEST_DB_URL

import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import create_app
from app import models
from app.core.config import settings
from app.core.database import SQLAlchemy


def _set_up_test_db():
    """
    테스트 DB 세팅
    :return:
    """
    global test_settings
    test_settings = settings
    db = SQLAlchemy()
    db.init_db(test_settings.DB_INFO)
    # 트랜잭션 내에서 테이블 삭제 및 생성
    with db.engine.begin() as conn:
        conn.execute(text("SET session_replication_role = replica;"))
        models.Base.metadata.drop_all(bind=conn)

        conn.execute(text("SET session_replication_role = DEFAULT;"))
        models.Base.metadata.create_all(bind=conn)
    return db


def _clear_all_table_data(session):
    """
    모든 테이블 데이터 삭제
    """
    # 외래키 제약조건 일시 비활성화
    session.execute(text("SET session_replication_role = replica;"))

    for table_name in models.Base.metadata.sorted_tables:
        session.execute(text(f"DELETE FROM {table_name};"))

    # 외래키 제약조건 재활성화
    session.execute(text("SET session_replication_role = DEFAULT;"))
    session.commit()


@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트 생성"""
    global _test_db
    _test_db = _set_up_test_db()
    app = create_app()
    return TestClient(app)


@pytest.fixture(scope="function")
def session():
    """DB 세션 fixture - 안전한 세션 관리"""
    global _test_db
    session = next(_test_db.session())
    _clear_all_table_data(session)
    yield session
    _clear_all_table_data(session)
    session.close()


@pytest.fixture
def auth_headers():
    """인증 헤더 생성"""
    return {"Authorization": "Bearer test-firebase-token"}


@pytest.fixture
def mock_firebase_token():
    """Firebase 인증 Mock"""
    with patch("app.core.firebase.firebase_auth.verify_token") as mock_auth:
        mock_auth.return_value = {
            "uid": "test-uid-123",
            "email": "test@example.com",
            "email_verified": True,
            "name": "테스트 사용자",
            "picture": "https://example.com/avatar.jpg",
        }
        yield mock_auth


@pytest.fixture
def mock_get_or_create_user():
    """get_or_create_user 의존성 Mock"""
    with patch("app.api.deps.get_or_create_user") as mock_user:
        mock_user.return_value = {
            "id": 1,
            "uid": "test-uid-123",
            "email": "test@example.com",
            "name": "테스트 사용자",
            "level": "BEGINNER",
            "exp": 0,
        }
        yield mock_user
