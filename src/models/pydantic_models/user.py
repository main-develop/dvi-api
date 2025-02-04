from pydantic import BaseModel, Field, EmailStr, SecretStr, ConfigDict, field_validator, ValidationError
from typing import Optional, Literal


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BaseUserPersonalInformation(BaseModelConfig):
    firstName: Optional[str] = Field(None, max_length=50)
    lastName: Optional[str] = Field(None, max_length=50)
    gender: Literal["Male", "Female", "Rather not say"] = "Rather not say"


class AuthenticateUser(BaseUserPersonalInformation):
    email: EmailStr
    password: SecretStr
    confirmPassword: Optional[str] = None
    rememberMe: Optional[bool] = False

    @field_validator("confirmPassword")
    @classmethod
    def check_passwords_match(cls, confirm_password, info):
        password = info.data["password"].get_secret_value()

        if confirm_password and confirm_password != password:
            raise ValidationError("Passwords do not match")
            
        return confirm_password


class UpdateUser(BaseUserPersonalInformation):
    pass


class ChangeUserEmail(BaseModelConfig):
    email: EmailStr
    password: SecretStr


class ChangeUserPassword(BaseModelConfig):
    newPassword: SecretStr
    oldPassword: SecretStr


class DeleteUser(BaseModelConfig):
    password: SecretStr
