from typing import List, Optional

from pydantic import AnyHttpUrl, BaseModel


# todo: find an official schema
class OpenIDConfiguration(BaseModel):
    userinfo_endpoint: AnyHttpUrl
    jwks_uri: AnyHttpUrl
    issuer: AnyHttpUrl
    authorization_endpoint: AnyHttpUrl | None = None
    end_session_endpoint: AnyHttpUrl | None = None
    token_endpoint: AnyHttpUrl | None = None
    token_endpoint_auth_methods_supported: List[str] | None = None
    scopes_supported: List[str] | None = None
    introspection_endpoint: AnyHttpUrl | None = None
    response_types_supported: List[str] | None = None
    subject_types_supported: List[str] | None = None
    id_token_signing_alg_values_supported: List[str] | None = None
