from pydantic import BaseModel, EmailStr
from db.models.user import UserRole


class UserModel(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: UserRole = UserRole.user.value


class Config:
    use_enum_values = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str
