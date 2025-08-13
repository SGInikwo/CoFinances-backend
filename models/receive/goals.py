from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional, Union, List

class Goals(BaseModel):
    amount: Optional[Union[str, int]] = Field(default=None)
    endMonth: Optional[str] = Field(default=None)
    endYear: Optional[str] = Field(default=None)
    isSaving: Optional[int] = Field(default=None)  # Assuming isSaving is 1 for saving, 0 for investing
    startMonth: Optional[str] = Field(default=None)
    startYear: Optional[str] = Field(default=None)


class GoalsRequest(BaseModel):
    goals: Goals

    class Config:
        # Allow extra fields that are not defined in the model
        extra = "ignore"