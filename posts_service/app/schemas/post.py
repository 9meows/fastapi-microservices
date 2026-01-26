from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)
    category_id: PositiveInt


class Post(PostBase):
    id: int

    model_config = ConfigDict(from_attributes=True)