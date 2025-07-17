#!/usr/bin/env python3
"""
백엔드 애플리케이션 시작 스크립트
- 데이터베이스 연결 확인
- 마이그레이션 실행
- 설정 검증
- 앱 시작
"""

import sys
import json
import time
import subprocess
from pathlib import Path

import asyncpg
import asyncio
from app.core.config import settings


async def check_database_connection():
    """데이터베이스 연결 확인"""
    print("🔍 데이터베이스 연결 확인 중...")
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = await asyncpg.connect(settings.DATABASE_URL)
            await conn.close()
            print("✅ 데이터베이스 연결 성공")
            return True
        except Exception as e:
            retry_count += 1
            print(f"⏳ 데이터베이스 연결 시도 {retry_count}/{max_retries} - {str(e)}")
            time.sleep(2)
    
    print("❌ 데이터베이스 연결 실패")
    return False


async def run_migrations():
    """PostgreSQL 마이그레이션 실행"""
    print("🔄 데이터베이스 마이그레이션 실행 중...")
    
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        # 마이그레이션 파일 읽기 (프로젝트 루트의 database/migrations)
        migration_file = Path(__file__).parent.parent / "database" / "migrations" / "002_update_user_exp_column_postgresql.sql"
        
        if migration_file.exists():
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # 마이그레이션 실행
            await conn.execute(migration_sql)
            print("✅ 마이그레이션 완료")
        else:
            print("⚠️ 마이그레이션 파일을 찾을 수 없습니다")
            
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 마이그레이션 실행 실패: {str(e)}")
        return False


def validate_level_config():
    """레벨 설정 파일 검증"""
    print("🔍 레벨 설정 파일 검증 중...")
    
    try:
        config_file = Path(__file__).parent / "app" / "core" / "level_config.json"
        
        if not config_file.exists():
            print("❌ level_config.json 파일이 없습니다")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 필수 키 확인
        required_keys = ['exp_fields', 'level_up_conditions', 'level_names']
        for key in required_keys:
            if key not in config:
                print(f"❌ level_config.json에 필수 키 '{key}'가 없습니다")
                return False
        
        print("✅ 레벨 설정 파일 검증 완료")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ level_config.json 파싱 오류: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 설정 파일 검증 실패: {str(e)}")
        return False


def create_required_directories():
    """필요한 디렉토리 생성"""
    print("📁 필요한 디렉토리 생성 중...")
    
    directories = [
        "logs",
        "static",
        "uploads"
    ]
    
    for directory in directories:
        dir_path = Path(__file__).parent / directory
        dir_path.mkdir(exist_ok=True)
    
    print("✅ 디렉토리 생성 완료")


async def initialize():
    """초기화 작업 실행"""
    print("🚀 백엔드 애플리케이션 초기화 시작")
    print("=" * 50)
    
    # 1. 필요한 디렉토리 생성
    create_required_directories()
    
    # 2. 데이터베이스 연결 확인
    if not await check_database_connection():
        print("❌ 초기화 실패: 데이터베이스 연결 불가")
        sys.exit(1)
    
    # 3. 마이그레이션 실행
    # 기존 run_migrations() 대신 shell 명령어로 alembic upgrade head 실행
    print("🔄 Alembic 마이그레이션 실행 중...")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # stderr와 stdout을 모두 출력하도록 수정
        error_message = result.stderr or result.stdout
        print(f"❌ Alembic 마이그레이션 실패: {error_message}")
        sys.exit(1)
    print("✅ Alembic 마이그레이션 완료")
    
    # 4. 설정 검증
    if not validate_level_config():
        print("❌ 초기화 실패: 설정 파일 오류")
        sys.exit(1)
    
    print("=" * 50)
    print("✅ 초기화 완료!")
    print("🎯 애플리케이션 시작 중...")


def start_app():
    """애플리케이션 시작"""
    # 애플리케이션 실행 명령어
    cmd = [
        "uvicorn", 
        "app.main:create_app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ]
    
    print(f"🚀 서버 시작: {' '.join(cmd)}")
    subprocess.run(cmd)


async def main():
    """메인 함수"""
    try:
        # 초기화 실행
        await initialize()
        
        # 앱 시작
        start_app()
        
    except KeyboardInterrupt:
        print("\n👋 애플리케이션 종료")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 