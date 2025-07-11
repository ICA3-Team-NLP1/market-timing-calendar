from pydantic import BaseModel


class UsersCreate(BaseModel):
    uid: str
    name: str
    email: str
