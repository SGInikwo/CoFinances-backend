from pydantic import BaseModel, Field
from typing import Optional, Union, List
from models.receive.transactions import Transactions_ing, Transactions_kb, Transactions_revolut, Transactions_shinha
import secrets

from models.send.helper_functions.transaction_data import amount_transform, balance_transform, currency_update_dataframe, current_analysis_dataframe, date_transform, earliest_date_dataframe, get_currency, is_valid_date, past_analysis_dataframe, transalte_korean_english

def get_insert_data(requests: Union[List[Transactions_ing], List[Transactions_revolut], List[Transactions_shinha], List[Transactions_kb]], clientCurrency, user_data):
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
           "balance": balance_transform(request_dict["balance"], "Ing"),
           "originalAmount": amount_transform(request_dict["amount"], request_dict["debit_credit"], "Ing"),
           "originalBalance": balance_transform(request_dict["balance"], "Ing"),
           "originalCurrency": int(clientCurrency),
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
           "balance": balance_transform(request_dict["balance"], "Revolut"),
           "originalAmount": amount_transform(request_dict["amount"], "None", "Revolut"),
           "originalBalance": balance_transform(request_dict["balance"], "Revolut"),
           "originalCurrency": int(clientCurrency),
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
            "balance": balance_transform(request_dict["balance"], "Shinha"),
            "originalAmount": amount_transform(request_dict["withdrawal"], request_dict["deposit"], "Shinha"),
            "originalBalance": balance_transform(request_dict["balance"], "Shinha"),
            "originalCurrency": int(clientCurrency),
          }
          data.append(request_data)
    elif isinstance(request, Transactions_kb):
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
            "balance": balance_transform(request_dict["balance"], "Shinha"),
            "originalAmount": amount_transform(request_dict["withdrawal"], request_dict["deposit"], "Shinha"),
            "originalBalance": balance_transform(request_dict["balance"], "Shinha"),
            "originalCurrency": int(clientCurrency),
          }
          data.append(request_data)
    else:
        print("Unknown type")

  data = transalte_korean_english(data) 
  date = earliest_date_dataframe(data)
  return data, date

def currency_response(transactions, cleintCurrency):
   response = currency_update_dataframe(transactions, cleintCurrency)
   return response

def current_analysis(transactions):
   response = current_analysis_dataframe(transactions)
   return response

def past_analysis(transactions, month, year):
   response = past_analysis_dataframe(transactions, month, year)
   return response



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
  originalAmount: str
  originalBalance: str
  originalCurrency: int

class TransactionResponse(BaseModel):
  transactionList: list[Transactions]
