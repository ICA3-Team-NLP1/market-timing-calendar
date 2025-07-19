"""
설정 기반 데이터 마이그레이션을 위한 유틸리티 함수들
"""
from sqlalchemy.orm import Session
from app.models.users import Users
from app.core.database import db
from app.core.config import LevelConfig
import json


def migrate_user_exp_to_current_config():
    """
    모든 사용자의 exp 데이터를 현재 설정에 맞게 마이그레이션합니다.
    
    기존 데이터는 보존하되, 새로운 필드는 0으로 초기화하고
    설정에서 제거된 필드는 삭제합니다.
    """
    # DB 초기화
    if db._session is None:
        from app.core.config import settings
        db.init_db(settings.DB_INFO)
        db.startup()
    
    session = next(db.session())
    
    try:
        users = session.query(Users).all()
        migrated_count = 0
        
        for user in users:
            old_exp = user.exp or {}
            new_exp = LevelConfig.get_default_exp()
            
            # 기존 데이터 중 현재 설정에 있는 것만 보존
            preserved_fields = []
            for field_name in LevelConfig.get_exp_field_names():
                if field_name in old_exp:
                    new_exp[field_name] = old_exp[field_name]
                    preserved_fields.append(f"{field_name}={old_exp[field_name]}")
            
            # 제거된 필드들 확인
            removed_fields = [k for k in old_exp.keys() if k not in LevelConfig.get_exp_field_names()]
            
            user.exp = new_exp
            migrated_count += 1
            
            print(f"사용자 {user.uid} 마이그레이션:")
            print(f"  - 보존된 필드: {', '.join(preserved_fields) if preserved_fields else '없음'}")
            print(f"  - 제거된 필드: {', '.join(removed_fields) if removed_fields else '없음'}")
            print(f"  - 새로운 exp: {new_exp}")
        
        session.commit()
        print(f"\n✅ 성공적으로 {migrated_count}명의 사용자 exp 데이터를 마이그레이션했습니다.")
        
        # 현재 설정 정보 출력
        print(f"\n📋 현재 설정:")
        print(f"  - 경험치 필드: {list(LevelConfig.get_exp_fields().keys())}")
        print(f"  - 레벨업 조건: {json.dumps({str(k): v for k, v in LevelConfig.get_level_up_conditions().items()}, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 마이그레이션 중 오류 발생: {e}")
        
    finally:
        session.close()


def reset_all_user_exp():
    """
    모든 사용자의 exp를 현재 설정 기준으로 0으로 초기화합니다.
    
    주의: 이 함수는 모든 경험치 데이터를 삭제합니다!
    """
    # DB 초기화
    if db._session is None:
        from app.core.config import settings
        db.init_db(settings.DB_INFO)
        db.startup()
    
    session = next(db.session())
    
    try:
        users = session.query(Users).all()
        reset_count = 0
        
        for user in users:
            user.exp = LevelConfig.get_default_exp()
            reset_count += 1
        
        session.commit()
        print(f"✅ 성공적으로 {reset_count}명의 사용자 exp 데이터를 초기화했습니다.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 초기화 중 오류 발생: {e}")
        
    finally:
        session.close()


def validate_user_exp_data():
    """
    모든 사용자의 exp 데이터가 현재 설정과 일치하는지 검증합니다.
    """
    # DB 초기화
    if db._session is None:
        from app.core.config import settings
        db.init_db(settings.DB_INFO)
        db.startup()
    
    session = next(db.session())

    try:
        users = session.query(Users).all()
        invalid_users = []

        for user in users:
            current_exp = user.exp or {}
            expected_fields = set(LevelConfig.get_exp_field_names())
            actual_fields = set(current_exp.keys())

            if expected_fields != actual_fields:
                invalid_users.append({
                    "uid": user.uid,
                    "expected_fields": expected_fields,
                    "actual_fields": actual_fields,
                    "missing_fields": expected_fields - actual_fields,
                    "extra_fields": actual_fields - expected_fields
                })

        if invalid_users:
            print(f"❌ {len(invalid_users)}명의 사용자가 설정과 일치하지 않습니다:")
            for user_info in invalid_users:
                print(f"  - {user_info['uid']}: 누락 필드={user_info['missing_fields']}, 추가 필드={user_info['extra_fields']}")
        else:
            print(f"✅ 모든 {len(users)}명의 사용자 exp 데이터가 현재 설정과 일치합니다.")
            
    except Exception as e:
        print(f"❌ 검증 중 오류 발생: {e}")
        
    finally:
        session.close()

def show_current_config():
    """현재 레벨 설정 정보를 출력합니다."""
    print("📋 현재 레벨 설정:")
    print(f"경험치 필드:")
    for field_name, display_name in LevelConfig.get_exp_fields().items():
        print(f"  - {field_name}: {display_name}")

    print(f"\n레벨업 조건:")
    for level, config in LevelConfig.get_level_up_conditions().items():
        level_name = LevelConfig.get_level_names().get(level, str(level))
        target_level_name = LevelConfig.get_level_names().get(config["target_level"], str(config["target_level"]))
        print(f"  - {level_name} → {target_level_name}:")
        for field, value in config["conditions"].items():
            field_display = LevelConfig.get_exp_fields().get(field, field)
            print(f"    * {field_display}: {value}회")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법:")
        print("  python migration_utils.py migrate    # 현재 설정으로 마이그레이션")
        print("  python migration_utils.py reset      # 모든 경험치 초기화")
        print("  python migration_utils.py validate   # 데이터 검증")
        print("  python migration_utils.py config     # 현재 설정 표시")
        sys.exit(1)

    command = sys.argv[1]

    if command == "migrate":
        migrate_user_exp_to_current_config()
    elif command == "reset":
        confirm = input("⚠️  모든 사용자의 경험치가 0으로 초기화됩니다. 계속하시겠습니까? (yes/no): ")
        if confirm.lower() == "yes":
            reset_all_user_exp()
        else:
            print("취소되었습니다.")
    elif command == "validate":
        validate_user_exp_data()
    elif command == "config":
        show_current_config()
    else:
        print(f"알 수 없는 명령어: {command}") 