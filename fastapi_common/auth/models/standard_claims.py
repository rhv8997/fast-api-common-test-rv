from datetime import datetime
from typing import Optional

from pydantic import AnyUrl, BaseModel, EmailStr


class StandardClaims(BaseModel):
    sub: str | None = None
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    middle_name: str | None = None
    nickname: str | None = None
    preferred_username: str | None = None
    profile: str | None = None
    picture: AnyUrl | None = None
    website: AnyUrl | None = None
    email: EmailStr | None = None
    email_verified: bool | None = None
    gender: str | None = None
    birthdate: datetime | None = None
    zoneinfo: str | None = None
    locale: str | None = None
    phone_number: str | None = None
    phone_number_verified: bool | None = None
    updated_at: datetime | None = None
    # todo: type address properly
    # address: str |  | None
