class BackendException(Exception):
    pass


class RegistrationNotSupportedException(BackendException):
    pass


class UserAlreadyExistsException(BackendException):
    pass


class IncorrectCredentialsException(BackendException):
    pass


class NonAuthenticatedException(BackendException):
    pass


class SenseNotFoundException(BackendException):
    pass
