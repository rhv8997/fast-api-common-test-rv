from typing import Any

import aiohttp
import requests
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode
from pydantic import AnyHttpUrl, BaseModel, computed_field
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from fastapi_common.auth.models.bearer_credentials import BearerCredentials

from .models.jwk import JWK
from .models.jwt_credentials import JWTCredentials
from .models.openid_configuration import OpenIDConfiguration
from .models.standard_claims import StandardClaims


# todo: an authentication backend would be better
class OAuthBearer(HTTPBearer):
    # e.g http://localhost:8002/default_issuer/.well-known/openid-configuration
    # technically openid spec not oauth, but most providers provide it and reduces needed arguments
    def __init__(
        self,
        well_known_endpoint: str,
        auto_error: bool = True,
        debug: bool = False,
    ):
        super().__init__(auto_error=auto_error)
        self.well_known_endpoint: AnyHttpUrl = AnyHttpUrl(well_known_endpoint)
        self.debug = debug
        self.update_config()
        self.refresh_jwks()
        self.aiohttp_session = None

    # todo: error handling on failed request
    def update_config(self):
        self.configuration = OpenIDConfiguration.model_validate(
            requests.get(self.well_known_endpoint).json()
        )

    # todo: error handling on failed request
    def refresh_jwks(self):
        response = requests.get(self.configuration.jwks_uri).json()
        self.kid_to_jwk: dict[str, JWK] = {
            key["kid"]: JWK.model_validate(key) for key in response["keys"]
        }

    def get_jwk(self, kid: str, refresh=True) -> JWK:
        try:
            return self.kid_to_jwk[kid]
        except KeyError:
            if refresh:
                self.refresh_jwks()
                return self.get_jwk(kid, False)
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "AUTH_INVALID_JWK",
                    "error_description": "Server was unable to get latest keys to verify token",
                },
            )

    def verify_jwk_token(self, jwt_credentials: JWTCredentials) -> bool:
        specified_jwk = self.get_jwk(jwt_credentials.header["kid"])
        key = jwk.construct(specified_jwk.model_dump(exclude_none=True))
        decoded_signature = base64url_decode(jwt_credentials.signature.encode())
        result = key.verify(jwt_credentials.message.encode(), decoded_signature)
        return result

    async def get_user_info(self, token) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"}
        if self.aiohttp_session is None:
            self.aiohttp_session = aiohttp.ClientSession()
        response = await self.aiohttp_session.get(
            str(self.configuration.userinfo_endpoint), headers=headers
        )
        if response.status != 200:
            raise HTTPException(
                status_code=response.status,
                detail=await response.json(),
            )
        result = await response.json()
        return result

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(
            request
        )
        if credentials is None:
            return credentials
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "AUTH_INVALID_SCHEME",
                    "error_description": "Wrong authentication method, accepted methods are: [ Bearer ]",
                },
            )

        jwt_token = credentials.credentials

        try:
            message, signature = jwt_token.rsplit(".", 1)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "AUTH_INVALID_JWT",
                    "error_description": "Error splitting JWT",
                },
            )

        try:
            jwt_credentials = JWTCredentials(
                jwt_token=jwt_token,
                header=jwt.get_unverified_header(jwt_token),
                claims=jwt.get_unverified_claims(jwt_token),
                signature=signature,
                message=message,
            )
        except JWTError as ex:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "AUTH_INVALID_JWT",
                    "error_description": "Error parsing JWT",
                },
            )

        if not self.verify_jwk_token(jwt_credentials):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail={
                    "error": "AUTH_INVALID_JWT",
                    "error_description": "JWT signature was invalid",
                },
            )
        if "openid" in jwt_credentials.claims["scope"]:
            user_info = await self.get_user_info(jwt_token)
        else:
            user_info = None
        # put in state, pretend we're an auth backend
        request.state.user = BearerCredentials(
            info=user_info, credentials=jwt_credentials
        )
        return credentials
