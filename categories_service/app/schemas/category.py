from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1)


class Category(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)