from app.crud.base import CRUDBase
from app.models.users import Users
from app.schemas.users import UsersCreate


class CRUDUsers(CRUDBase[Users, UsersCreate, None]):
    ...


crud_users = CRUDUsers(Users)
