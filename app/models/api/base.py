__all__ = (
    'SuccessResponse',
)


from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True
