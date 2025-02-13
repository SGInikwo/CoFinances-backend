import pandas as pd
import datetime
import calendar

from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder


from models.send.helper_functions.transactionSummary_data import get_conversion_rate
import re
from deep_translator import GoogleTranslator


def is_not_korean(text):
    # Regex for detecting Hangul characters (Korean alphabet)
    return not bool(re.search('[\uac00-\ud7af]', text))

def translate_text(text):
    if isinstance(text, str) and not text.isdigit():
        # Use GoogleTranslator from deep_translator
        return GoogleTranslator(source='ko', target='en').translate(text)
    return text  # Keep numbers unchanged

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
  
  if type == "kb":
    date_input = date
    parsed_date = datetime.strptime(str(date_input), "%Y.%m.%d %H:%M:%S")
    date = parsed_date.strftime("%Y-%m-%d")
    return date

def amount_transform(withdraw, deposit_or, bank):
  if bank == "korean":
    if withdraw != 0 and withdraw != None:
      amount = f"-{withdraw}"
      return amount
    else:
      return f"{deposit_or}"
  
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
    # Define acceptable date formats
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y.%m.%d %H:%M:%S"]

    for fmt in formats:
        try:
            datetime.strptime(date_string, fmt)
            return True  # Valid date format found
        except:
            continue  # Try the next format
    
    return False  # No valid format found
    
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
  return month_day_list


def current_analysis_dataframe(transactions):
  df = pd.DataFrame.from_dict(transactions)
  # Ensure the `date` column is in datetime format
  df["date"] = pd.to_datetime(df["date"])
  # Convert `amount` to numeric
  df["amount"] = pd.to_numeric(df["amount"])
  df = df[df['amount'] < 0].copy()
  # Group by date and calculate the total amount for each date
  grouped = df.groupby("date")["amount"].sum()
  # Find the date with the highest total amount
  max_amount_date = grouped.idxmin()
  # Filter the rows corresponding to this date
  filtered_df = df[df["date"] == max_amount_date].copy()
  filtered_df["date"] = filtered_df["date"].astype(str)
  return filtered_df.to_dict(orient='records')


def past_analysis_dataframe(transactions, month, year):
    df = pd.DataFrame.from_dict(transactions)

    # Convert the 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    df = df[df['amount'] < 0].copy()

    if month == "null" and year == "null":
        # Get the latest and second latest date
        latest_date = df['date'].max()

        # Get the latest month and year from the dates
        month = latest_date.month
        year = latest_date.year
    else:
      month = datetime.strptime(month, "%B").month
      year = int(year)

    # Get the last day of the month
    last_day = calendar.monthrange(year, month)[1]

    # Calculate the target date
    target_date = datetime(year, month, last_day)
    
    # Filter for the last 5 months from the target date
    start_date = target_date - pd.DateOffset(months=5)
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= target_date)].copy()
    
    # Group by year-month and sum up the amounts
    filtered_df["year_month"] = filtered_df["date"].dt.to_period("M").astype(str)

    monthly_expenses = filtered_df.groupby("year_month")["amount"].sum().sort_index(ascending=False)
    
    # Get the top 3 months with the highest negative amounts
    top_expenses = monthly_expenses.nsmallest(3).sort_index(ascending=False).to_dict()  # Smallest amounts for negative values


    # Extract the latest 5 months based on the given month and year
    latest_5_months = monthly_expenses.nsmallest(5).sort_index(ascending=False).to_dict()
    
    return jsonable_encoder({"last_5": latest_5_months, "top_3": top_expenses})

def transalte_korean_english(transactions):
  print(f'this is: {transactions[0]["transactionDetails"]}')
  if is_not_korean(transactions[0]["transactionDetails"]):
    print("not korean")
    return transactions
  
  df = pd.DataFrame(transactions)
  print(df)

  df_translated = df.map(translate_text)

  print(df_translated)

  return df_translated.to_dict(orient='records')