__all__ = (
    'AbstractDates',
)

from tortoise.models import Model
from tortoise import fields


class AbstractDates(Model):
    """Provides base created and updated dates."""
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
