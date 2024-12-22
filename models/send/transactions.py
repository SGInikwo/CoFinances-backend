from pydantic import BaseModel, Field
from typing import Optional, Union, List
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import secrets

from models.send.helper_functions.transaction_data import amount_transform, balance_transform, date_transform, get_currency, is_valid_date

def get_insert_data(requests: Union[List[Transactions_ing], List[Transactions_revolut], List[Transactions_shinha]], user_data):
  data = []
  for request in requests:
    request_dict = dict(request)

    if isinstance(request, Transactions_ing):
        request_data = {
           "id": secrets.token_hex(8),
           "userId": user_data[0],
           "date": date_transform(request_dict["date"], "Ing"),
           "recipient": request_dict["name"],
           "currency": int(user_data[1]),
           "amount": amount_transform(request_dict["amount"], request_dict["debit_credit"], "Ing"),
           "transactionType": request_dict["transaction_type"],
           "transactionDetails": request_dict["notification"],
           "icon": 0,
           "userCurrency": int(user_data[1]),
           "balance": balance_transform(str(request_dict["balance"]))
        }
        data.append(request_data)
    elif isinstance(request, Transactions_revolut):
        request_data = {
           "id": secrets.token_hex(8),
           "userId": user_data[0],
           "date": date_transform(request_dict["start_date"], "Revolut"),
           "recipient": request_dict["description"],
           "currency": get_currency(request_dict["currency"]),
           "amount": amount_transform(request_dict["amount"], "None", "Revolut"),
           "transactionType": request_dict["type"],
           "transactionDetails": request_dict["description"],
           "icon": 0,
           "userCurrency": int(user_data[1]),
           "balance": balance_transform(str(request_dict["balance"]))
        }
        data.append(request_data)
    elif isinstance(request, Transactions_shinha):
        if is_valid_date(request_dict["date"]):
          request_data = {
            "id": secrets.token_hex(8),
            "userId": user_data[0],
            "date": request_dict["date"],
            "recipient": request_dict["recipient"],
            "currency": 1,
            "amount": amount_transform(request_dict["withdrawal"], request_dict["deposit"], "Shinha"),
            "transactionType": request_dict["transaction_place"],
            "transactionDetails": request_dict["description"],
            "icon": 0,
            "userCurrency": int(user_data[1]),
            "balance": balance_transform(str(request_dict["balance"]))
          }
          data.append(request_data)
    else:
        print("Unknown type")

  return data

class Transactions(BaseModel):
  id: str
  userId: str
  date: str
  recipient: str
  currency: int
  amount: str
  transactionType: str
  transactionDetails: str
  icon: int
  userCurrency: int
  balance: str

class TransactionResponse(BaseModel):
  transactionList: list[Transactions]
