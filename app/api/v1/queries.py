from enum import Enum

from fastapi import Query
from pydantic import PositiveInt
from pydantic.dataclasses import dataclass


DEFAULT_PAGINATION_PAGE = 1
DEFAULT_PAGINATION_PAGE_SIZE = 50


@dataclass
class PaginationQuery:
    page: PositiveInt = Query(default=DEFAULT_PAGINATION_PAGE)
    size: PositiveInt = Query(default=DEFAULT_PAGINATION_PAGE_SIZE)


class RatingSort(str, Enum):
    ASC = "rating"
    DESC = "-rating"
