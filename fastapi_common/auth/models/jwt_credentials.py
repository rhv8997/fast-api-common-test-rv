from typing import Any, Dict

from pydantic import BaseModel


class JWTCredentials(BaseModel):
    jwt_token: str
    header: Dict[str, Any]
    claims: Dict[str, Any]
    signature: str
    message: str
