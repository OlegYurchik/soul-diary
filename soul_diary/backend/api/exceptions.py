import fastapi


class HTTPRegistrationNotSupported(fastapi.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Registration not supported.",
        )


class HTTPUserAlreadyExists(fastapi.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="User already exists.",
        )


class HTTPNotAuthenticated(fastapi.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )


class HTTPForbidden(fastapi.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )


class HTTPNotFound(fastapi.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Not found.",
        )
