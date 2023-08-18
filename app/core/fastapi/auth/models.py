from typing import Dict

from starlette.authentication import BaseUser

__all__ = (
    'CustomUser',
)


class CustomUser(BaseUser):
    def __init__(self, id: int, **kwargs) -> None:  # noqa
        self.id = id
        self.email = kwargs.get('email')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.initials = kwargs.get('initials')
        self.device_id = kwargs.get('device_id')

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.initials or 'unknown'

    @property
    def identity(self) -> int:  # type: ignore
        return self.id

    def to_dict(self) -> Dict:
        return {
            'id': self.id,  # type: ignore # noqa
            'email': self.email,  # type: ignore # noqa
            'first_name': self.first_name,  # type: ignore # noqa
            'last_name': self.last_name,  # type: ignore # noqa
            'initials': self.initials,  # type: ignore # noqa
            'device_id': self.device_id,  # type: ignore # noqa
        }
