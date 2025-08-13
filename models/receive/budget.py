from pydantic import BaseModel, Field
from typing import Optional, List

class Budget(BaseModel):
    id: Optional[str] = Field(default=None, alias="$id")
    actual: float
    budget: float
    date: str  # 'yyyy-mm'
    category: str

class BudgetRequest(BaseModel):
    budget: List[Budget]