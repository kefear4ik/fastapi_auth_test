from dataclasses import dataclass
from typing import Optional

from app.services.base import BaseService


@dataclass(frozen=True)
class RedisCacheKey:
    path: str
    query_params: Optional[str]
    service: BaseService
    # TODO: update when cache logic will be provided
    # def __str__(self) -> str:
    #     return f"{self.service.es_index}::{self.path}::{self.query_params}"
