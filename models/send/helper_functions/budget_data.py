import pandas as pd

def unique_dicts(lst):
    seen = set()
    unique_list = []
    
    for d in lst:
        key = tuple(sorted(d.items()))  # Sort to ensure consistent order
        if key not in seen:
            seen.add(key)
            unique_list.append(d)

    return unique_list

def get_conversion_rate(from_currency, to_currency):
    currency = {0:  "EUR", 1: "KRW", 2: "KES", 3: "GBP", 4: "USD"}

    from_currency = int(from_currency)
    to_currency = int(to_currency)

    from_currency = currency[from_currency]
    to_currency = currency[to_currency]

    exchange_table = pd.read_csv('./exchange_rates.csv', index_col=0)
    # Return 1 if both currencies are the same
    if from_currency == to_currency:
        return 1
    else:
        return exchange_table.loc[from_currency, to_currency]

def currency_update_dataframe(budgets, cleintCurrency):
  df = pd.DataFrame.from_dict(budgets)
  # Convert 'amount' and 'balance' to userCurrency
  df[['budget', 'actual']] = df.apply(
      lambda row: row[['originalBudget', 'originalActual']].astype(float) * get_conversion_rate(row['originalCurrency'], cleintCurrency),
      axis=1
  )

  df["currency"] = cleintCurrency
  # df["budget"] = df["budget"].astype(str)
  # df["actual"] = df["actual"].astype(str)
  return df.to_dict(orient='records')

def earliest_date_dataframe(transactions):
  df = pd.DataFrame.from_dict(transactions)

  # Ensure date column is datetime
  df['date'] = pd.to_datetime(df['date'])

  print(df['date'])

  month_day_list = df[['date']].apply(lambda x: {'month': x['date'].month, 'year': x['date'].year}, axis=1).tolist()
  month_day_list = unique_dicts(month_day_list)
  return month_day_list


def update_budget_actuals(data, dates, user_data):
    from database.transaction_dao import TransactionDao
    # from database.category_dao import CategoryDao

    # categories = CategoryDao(user_data[2]).get_all_category_name()
    # category_dict = dict(categories)

    # swapped = {value: key for key, value in category_dict.items()}
    print(f"data to see: {data}")

    for date in dates:
        transactions = TransactionDao(user_data[2]).get_transactions(user_data, month=date["month"], year=date["year"])

        if not transactions:
            continue

        df = pd.DataFrame.from_dict(transactions)

        df[['amount_num']] = df[['amount']].apply(pd.to_numeric, errors='coerce')

        df["category"] = df["categoryId"].apply(lambda x: x["name"] if isinstance(x, dict) else None)

        category_expenses = (
            df[df['amount_num'] < 0]
            .groupby("category")['amount_num']
            .sum()
            .to_dict()
        )

        # Update `data` list with actuals for this date
        for row in data:
            if row['update'] == True:
                if (
                    row["date"] == f"{date['year']}-{str(date['month']).zfill(2)}"
                    and row["category"] in category_expenses
                ):
                    # Expenses are negative, but we might want them as positive in actuals
                    row["actual"] = abs(category_expenses[row["category"]])
                    row["originalActual"] = abs(category_expenses[row["category"]])
        
    print(f"Updated data: {data}")
    return data