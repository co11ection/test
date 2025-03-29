class APIError(Exception):
    status: str


class InvalidToken(APIError):
    status = "invalid_token"


class NotFound(APIError):
    status = "not_found"


class PsqlError(APIError):
    status = "database error"
