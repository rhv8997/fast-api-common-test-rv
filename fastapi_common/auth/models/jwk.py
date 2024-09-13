from pydantic import BaseModel


# todo: find an official schema
class JWK(BaseModel):
    alg: str
    e: str
    kid: str
    kty: str
    n: str
    use: str
