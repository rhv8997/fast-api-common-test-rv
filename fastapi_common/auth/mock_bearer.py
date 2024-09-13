from typing import TypeVar

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode
from pydantic import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from .models.bearer_credentials import BearerCredentials
from .models.jwt_credentials import JWTCredentials
from .models.standard_claims import StandardClaims


class MockBearer(HTTPBearer):
    def __init__(
        self,
        auto_error: bool = True,
    ):
        super().__init__(auto_error=auto_error)

    def verify_jwk_token(self, jwt_credentials: JWTCredentials) -> None:
        specified_jwk = self.get_jwk(jwt_credentials.header["kid"])
        key = jwk.construct(specified_jwk.model_dump(exclude_none=True))
        decoded_signature = base64url_decode(jwt_credentials.signature.encode())
        return key.verify(jwt_credentials.message.encode(), decoded_signature)

    def _mock_get_user_info(self) -> StandardClaims:
        mock_user = {"email": "fake@example.com"}
        return StandardClaims.model_validate(mock_user)

    async def __call__(self, request: Request) -> None:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Wrong authentication method, accepted methods are: [ Bearer ]",
                )

            jwt_token = credentials.credentials
            _, message, signature = jwt_token.rsplit(".")

            try:
                jwt_credentials = JWTCredentials(
                    jwt_token=jwt_token,
                    header=jwt.get_unverified_header(jwt_token),
                    claims=jwt.get_unverified_claims(jwt_token),
                    signature=signature,
                    message=message,
                )
            except JWTError:
                print("jwt error")
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Authorization header invalid",
                )

            user_info = StandardClaims.model_validate(jwt_credentials.claims)
            # API expects email to be present, but Cognito does not provide this in access token
            if user_info.email is None:
                user_info.email = self._mock_get_user_info().email

            request.state.user = BearerCredentials(
                info=user_info,
                credentials=jwt_credentials,
            )
            return None
