from pydantic import AnyHttpUrl, BaseModel


class Auth(BaseModel):
    well_known_endpoint: AnyHttpUrl
