from pydantic import BaseModel, Field
from typing import Optional, Union

class Transactions_ing(BaseModel):
  date: int = Field(alias="Date")
  name: str = Field(alias="Name / Description")
  account: str = Field(alias="Account")
  couter_party: Optional[str] = Field(alias="Counterparty", default=None)
  code: str = Field(alias="Code")
  debit_credit: str = Field(alias="Debit/credit")
  amount: float = Field(alias="Amount (EUR)")
  transaction_type: str = Field(alias="Transaction type")
  notification: str = Field(alias="Notifications")
  balance: float = Field(alias="Resulting balance")
  tag: Optional[str] = Field(alias="Tag", default=None)

class Transactions_revolut(BaseModel):
  type: str = Field(alias="Type")
  product: str = Field(alias="Product")
  start_date: float = Field(alias="Started Date")
  complete_date: Optional[float] = Field(alias="Completed Date", default=None)
  description: Union[str, float] = Field(alias="Description")
  amount: float = Field(alias="Amount")
  fee: float = Field(alias="Fee")
  currency: str = Field(alias="Currency")
  state: str = Field(alias="State")
  balance: Optional[float] = Field(alias="Balance", default=None)

class Transactions_shinha(BaseModel):
  date: str = Field(alias="거래내역조회")
  time: str = Field(alias="__EMPTY")
  description: Optional[str] = Field(alias="__EMPTY_1", default=None)
  withdrawal: Optional[Union[str, int]] = Field(alias="__EMPTY_2", default=None)
  deposit: Optional[Union[str, int]] = Field(alias="__EMPTY_3", default=None)
  recipient: Optional[str] = Field(alias="__EMPTY_4", default=None)
  balance: Optional[Union[str, int]] = Field(alias="__EMPTY_5", default=None)
  transaction_place: Optional[str] = Field(alias="__EMPTY_6", default=None)