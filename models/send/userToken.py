from pydantic import BaseModel, Field
from typing import Optional, Union, List
from models.receive.transactions import Transactions_ing, Transactions_revolut, Transactions_shinha
import secrets


def get_insert_data(user_data):
  request_data = {
           "userId": user_data[0],
           "jwt": user_data[1],
        }
  return request_data


class Transactions(BaseModel):
  userId: str
  jwt: str