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

def amount_transform(amount_plus, min_credit, bank):
  if bank == "Shinha":
    if amount_plus == 0 or amount_plus == None:
      amount = f"-{min_credit}"
      return amount
    else:
      return f"{amount_plus}"
  
  if bank == "Revolut":
    amount_plus = float(amount_plus)
    amount_plus = f"{amount_plus:.2f}"
    if ',' in amount_plus:
      amount_plus = amount_plus.replace(',', '.')
      return amount_plus
    return amount_plus
  
  if bank == "Ing":
    amount_plus = float(amount_plus)
    amount_plus = f"{amount_plus / 100:.2f}"
    if ',' in amount_plus:
      amount_plus = amount_plus.replace(',', '.')
    if min_credit == "credit":
      amount = f"-{min_credit}"
      return amount
    else:
      return f"{amount_plus}"
    
def balance_transform(balance:str):
  if balance == None or balance == "" or balance == "None":
    return "0"
  elif ',' in balance:
    return balance.replace(',', '.')
  else:
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
  currency = {"EUR": 0, "KRW": 1, "KES": 2, "GBP": 3,  "GBP": 4}

  return currency[data]