from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional, Union, List

class Category(BaseModel):
  name: str = Field(alias="categoryName")
  colour: str = Field(alias="categoryColor")

class CategoryRequest(BaseModel):
    category: Category
