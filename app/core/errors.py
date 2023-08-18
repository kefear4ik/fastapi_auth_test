from http import HTTPStatus
from typing import Optional, List


class BaseHTTPError(Exception):
    detail: List = []
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST

    def __init__(self, detail: Optional[List] = None) -> None:
        if detail is not None:
            self.detail = detail


class ServiceError(Exception):
    status_code: int = 400

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code


class VerificationCodeServiceError(ServiceError):
    pass


class UserServiceError(ServiceError):
    pass
