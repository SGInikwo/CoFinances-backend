import pandas as pd
import datetime
from datetime import datetime, timedelta

from models.send.helper_functions.transactionSummary_data import get_conversion_rate

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

def currency_update_dataframe(transactions, cleintCurrency):
  df = pd.DataFrame.from_dict(transactions)

  # Convert 'amount' and 'balance' to userCurrency
  df[['amount', 'balance']] = df.apply(
      lambda row: row[['originalAmount', 'originalBalance']].astype(float) * get_conversion_rate(row['originalCurrency'], cleintCurrency),
      axis=1
  )

  df["currency"] = cleintCurrency
  df["amount"] = df["amount"].astype(str)
  df["balance"] = df["balance"].astype(str)
  
  return df.to_dict(orient='records')


def earliest_date_dataframe(transactions):
  df = pd.DataFrame.from_dict(transactions)

  # Ensure date column is datetime
  df['date'] = pd.to_datetime(df['date'])

  month_day_list = df[['date']].apply(lambda x: {'month': x['date'].month, 'year': x['date'].year}, axis=1).tolist()


  # earliest_month = df['date'].min().month
  # earliest_year = df['date'].min().year

  return month_day_list