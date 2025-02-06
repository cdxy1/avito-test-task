from pydantic import BaseModel


class UserSchema(BaseModel):
    username: str
    role: str
    is_active: bool


class UserInSchema(UserSchema):
    password: str
