from typing import Any, List

from pydantic import BaseModel, computed_field

from fastapi_common.auth.models.jwt_credentials import JWTCredentials
from fastapi_common.auth.models.standard_claims import StandardClaims


class BearerCredentials(BaseModel):
    info: dict[str, Any] | None
    credentials: JWTCredentials

    @computed_field  # type: ignore[misc]
    @property
    def scopes(self) -> List[str]:
        if "scope" in self.credentials.claims:
            return self.credentials.claims["scope"].split(" ")
        return []

    @computed_field  # type: ignore[misc]
    @property
    def groups(self) -> List[str]:
        if "cognito:groups" in self.credentials.claims:
            return self.credentials.claims["cognito:groups"]
        return []

    def has_scope(self, *args: str) -> bool:
        return len([req for req in args if req not in self.scopes]) < 1

    def has_group(self, *args: str) -> bool:
        return len([req for req in args if req not in self.groups]) < 1
