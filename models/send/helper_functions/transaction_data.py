import datetime
from datetime import datetime, timedelta

def date_transform(date, type):
  if type == "Revolut":
    excel_start_date = datetime(1899, 12, 30)
    delta = timedelta(days=date)
    full_date = excel_start_date + delta

    parsed_date = datetime.strptime(str(full_date), "%Y-%m-%d %H:%M:%S")
    date = parsed_date.strftime("%Y-%m-%d")
    return date
  
  if type == "Ing":
    date_input = date

    parsed_date = datetime.strptime(str(date_input), "%Y%m%d")

    date = parsed_date.strftime("%Y-%m-%d")
    return date

def amount_transform(withdraw, deposit_or, bank):
  if bank == "Shinha":
    if withdraw != 0 or withdraw != None:
      amount = f"-{withdraw}"
      return amount
    else:
      return f"-{deposit_or}"
  
  if bank == "Revolut":
    amount = float(withdraw)
    amount = f"{amount:.2f}"
    if ',' in amount:
      amount = amount.replace(',', '.')
      return amount
    return amount
  
  if bank == "Ing":
    withdraw = float(withdraw)
    withdraw = f"{withdraw / 100:.2f}"
    if ',' in withdraw:
      withdraw = withdraw.replace(',', '.')
    if deposit_or == "Debit":
      amount = f"-{withdraw}"
      return amount
    else:
      return f"{withdraw}"
    
def balance_transform(balance, bank):
  if balance == None or balance == "" or balance == "None":
    return "0"
  if bank == "Shinha":
    return balance
  
  if bank == "Revolut":
    balance = float(balance)
    balance = f"{balance:.2f}"
    if ',' in balance:
      balance = balance.replace(',', '.')
      return balance
    return balance
  
  if bank == "Ing":
    balance = float(balance)
    balance = f"{balance / 100:.2f}"
    if ',' in balance:
      balance = balance.replace(',', '.')
    return balance

def is_valid_date(date_string: str) -> bool:
    try:
        # Attempt to parse the date string with the specified format
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        # If parsing fails, the format is incorrect
        return False
    
def get_currency(data):
  currency = {"EUR": 0, "KRW": 1, "KES": 2, "GBP": 3,  "USD": 4}

  return currency[data]