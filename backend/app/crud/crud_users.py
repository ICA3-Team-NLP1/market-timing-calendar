from app.crud.base import CRUDBase
from app.models.users import Users, UserEventSubscription
from app.schemas.users import UsersCreate


class CRUDUsers(CRUDBase[Users, UsersCreate, None]):
    """사용자 CRUD 클래스"""
    ...


class CRUDUserEventSubscription(CRUDBase[UserEventSubscription, None, None]):
    """사용자 이벤트 구독 CRUD 클래스"""
    ...


crud_users = CRUDUsers(Users)
crud_user_subscription = CRUDUserEventSubscription(UserEventSubscription)
