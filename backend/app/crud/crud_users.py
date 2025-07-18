from typing import Dict, Tuple
import logging
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.users import Users, UserEventSubscription
from app.schemas.users import UsersCreate
from app.constants import UserLevel
from app.core.config import LevelConfig

logger = logging.getLogger(__name__)


class CRUDUsers(CRUDBase[Users, UsersCreate, None]):
    """사용자 CRUD 클래스"""
    
    def delete_user(self, db: Session, user: Users) -> bool:
        """
        사용자 계정을 삭제합니다.
        
        Args:
            db: 데이터베이스 세션
            user: 삭제할 사용자 객체
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            # 사용자와 관련된 모든 데이터 삭제 (cascade 설정으로 자동 처리)
            db.delete(user)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise ValueError(f"사용자 삭제 중 오류가 발생했습니다: {str(e)}")
    
    def update_user_exp(self, db: Session, user: Users, event_type: str) -> Tuple[Users, bool]:
        """
        사용자 경험치를 업데이트하고 레벨업 여부를 확인합니다.
        
        Args:
            db: 데이터베이스 세션
            user: 사용자 객체
            event_type: 경험치 필드명 (JSON 설정에서 정의된 것)
        
        Returns:
            Tuple[Users, bool]: (업데이트된 사용자, 레벨업 여부)
        """
        # DB에서 user 다시 조회
        user = db.query(Users).filter(Users.id == user.id).first()
        if not user:
            raise ValueError(f"사용자 ID {user.id}를 찾을 수 없습니다.")

        # 이미 최고 레벨이면 바로 반환
        if user.level == UserLevel.ADVANCED:
            return user, False

        # 유효한 이벤트 타입인지 확인
        if not LevelConfig.is_valid_exp_field(event_type):
            raise ValueError(f"유효하지 않은 이벤트 타입: {event_type}")

        # 현재 exp 가져오기 (기본값 설정)
        current_exp = user.exp or LevelConfig.get_default_exp()

        # 이벤트 타입에 따라 카운트 증가 (단순 증가)
        if event_type in current_exp:
            current_exp[event_type] += 1
        else:
            # 새로운 필드인 경우 1로 초기화
            current_exp[event_type] = 1

        # 레벨업 조건 체크
        level_up = False
        new_level = user.level

        level_up_config = LevelConfig.get_level_up_condition(user.level)
        if level_up_config:
            conditions = level_up_config.get("conditions", {})
            target_level_str = level_up_config.get("target_level")

            # 문자열을 UserLevel enum으로 변환
            target_level = UserLevel(target_level_str) if target_level_str else None

            # 모든 조건을 충족했는지 확인
            if self._check_level_up_conditions(current_exp, conditions):
                new_level = target_level
                level_up = True
                # 레벨업 시 카운트 초기화
                current_exp = LevelConfig.get_default_exp()

        # 사용자 정보 업데이트
        user.exp = current_exp
        user.level = new_level

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"경험치 커밋 중 오류 발생: {e}")
            raise

        db.refresh(user)
        return user, level_up
    
    def _check_level_up_conditions(self, current_exp: Dict[str, int], conditions: Dict[str, int]) -> bool:
        """
        레벨업 조건을 모두 충족했는지 확인
        
        Args:
            current_exp: 현재 경험치
            conditions: 레벨업 조건
            
        Returns:
            모든 조건 충족 여부
        """
        for field_name, required_value in conditions.items():
            if current_exp.get(field_name, 0) < required_value:
                return False
        return True
    
    def get_user_level_info(self, user: Users) -> Dict:
        """
        사용자의 상세 레벨 정보를 반환
        
        Args:
            user: 사용자 객체
            
        Returns:
            사용자 레벨 정보 딕셔너리
        """
        current_exp = user.exp or LevelConfig.get_default_exp()
        
        level_up_config = LevelConfig.get_level_up_condition(user.level)
        next_level_conditions = level_up_config.get("conditions", {}) if level_up_config else {}
        target_level_str = level_up_config.get("target_level") if level_up_config else None
        next_level = UserLevel(target_level_str) if target_level_str else None
        
        # 레벨업 가능 여부 확인
        can_level_up = (
            level_up_config and 
            self._check_level_up_conditions(current_exp, next_level_conditions)
        )
        
        level_names = LevelConfig.get_level_names()
        exp_fields = LevelConfig.get_exp_fields()
        
        return {
            "current_level": user.level,
            "level_display_name": level_names.get(user.level.value, str(user.level)),
            "exp": current_exp,
            "next_level": next_level,
            "next_level_conditions": next_level_conditions,
            "can_level_up": can_level_up,
            "exp_field_info": {
                field_name: {
                    "display_name": exp_fields.get(field_name, field_name),
                    "current_value": current_exp.get(field_name, 0),
                    "required_for_next_level": next_level_conditions.get(field_name)
                }
                for field_name in LevelConfig.get_exp_field_names()
            }
        }


class CRUDUserEventSubscription(CRUDBase[UserEventSubscription, None, None]):
    """사용자 이벤트 구독 CRUD 클래스"""
    
    def create_subscription(self, session: Session, user_id: int, event_id: int) -> UserEventSubscription:
        """
        사용자 이벤트 구독 생성 (일정 저장)
        
        Args:
            session: DB 세션
            user_id: 사용자 ID
            event_id: 이벤트 ID
            
        Returns:
            생성된 구독 객체
        """
        # 이미 구독 중인지 확인
        existing_subscription = (
            session.query(UserEventSubscription)
            .filter(
                UserEventSubscription.user_id == user_id,
                UserEventSubscription.event_id == event_id,
                UserEventSubscription.dropped_at.is_(None)
            )
            .first()
        )
        
        if existing_subscription:
            return existing_subscription
        
        # 새 구독 생성
        subscription = UserEventSubscription(
            user_id=user_id,
            event_id=event_id
        )
        session.add(subscription)
        session.commit()
        session.refresh(subscription)
        return subscription
    
    def get_user_subscriptions(self, session: Session, user_id: int) -> list[UserEventSubscription]:
        """
        사용자의 모든 이벤트 구독 조회 (저장된 일정 조회)
        
        Args:
            session: DB 세션
            user_id: 사용자 ID
            
        Returns:
            사용자의 구독 목록
        """
        subscriptions = (
            session.query(UserEventSubscription)
            .filter(
                UserEventSubscription.user_id == user_id,
                UserEventSubscription.dropped_at.is_(None)
            )
            .order_by(UserEventSubscription.subscribed_at.desc())
            .all()
        )
        return subscriptions


crud_users = CRUDUsers(Users)
crud_user_subscription = CRUDUserEventSubscription(UserEventSubscription)
