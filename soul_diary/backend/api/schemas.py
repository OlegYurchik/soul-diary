from pydantic import BaseModel, constr


class CredentialsRequest(BaseModel):
    username: constr(min_length=4, max_length=64, strip_whitespace=True)
    password: constr(min_length=8, max_length=64)


class TokenResponse(BaseModel):
    token: constr(min_length=32, max_length=32)


class OptionsResponse(BaseModel):
    registration_enabled: bool
