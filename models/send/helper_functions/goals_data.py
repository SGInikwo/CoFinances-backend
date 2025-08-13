import json
import pandas as pd
from datetime import datetime
from functools import partial

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


def update_row(row, cleintCurrency):
    original_currency = row['originalData']['originalCurrency']

    rate = get_conversion_rate(original_currency, cleintCurrency)

    # Map originalData keys to actual DataFrame column names
    mapping = {
        'originalActualBalance': 'actualBalance',
        'originalActualSaving': 'actualSaving',
        'originalActualInvesting': 'actualInvesting',
        'originalMonthlyInputSaving': 'monthlyInputSaving',
        'originalMonthlyInputInvesting': 'monthlyInputInvesting',
        'originalVirtualSaving': 'virtualSaving',
        'originalVirtualInvesting': 'virtualInvesting',
        'originalVirtualBalance': 'virtualBalance',
    }

    for orig_key, col_name in mapping.items():
        if orig_key in row['originalData']:
            row[col_name] = row['originalData'][orig_key] * rate

    return row


def currency_update_dataframe(goals, cleintCurrency):
    df = pd.DataFrame.from_dict(goals)

    # Step 1: Parse JSON strings into dictionaries
    df['originalData'] = df['originalData'].apply(json.loads)

    # Step 2: Apply conversion
    df = df.apply(partial(update_row, cleintCurrency=cleintCurrency), axis=1)

    # Step 3: Convert 'originalData' back to JSON string
    df['originalData'] = df['originalData'].apply(json.dumps)

    # Step 4: Update currency field
    df["currency"] = cleintCurrency

    return df.to_dict(orient='records')


def goals_dataframe(requests, transactions, goals, currency):
  # requests = ["amount", "startMonth", "startYear", "endMonth", "endYear", "isSaving"] #example of an request
  goals_df = pd.DataFrame.from_dict(goals)
  # goals_df["date"] = pd.to_datetime(goals_df["date"], format="%Y-%m")

  curremt_goals_df = goal_setup(requests, transactions, goals_df)

  # current_date = datetime.today().strftime('%Y-%m')

  updated_df = update_goals_df(goals_df, curremt_goals_df, currency)


  updated_df["date"] = updated_df["date"].astype(str)
  updated_df["status"] = updated_df["status"].astype(str)
  return updated_df.to_dict(orient='records')




def update_goals_df(goals_df, curremt_goals_df, currency):
  if goals_df.empty:
    print(f"\n\nupdate to see \n")
    total_input = (curremt_goals_df['monthlyInputSaving'] + curremt_goals_df['monthlyInputInvesting']).cumsum()
    # Update virtual values
    curremt_goals_df['virtualSaving'] = curremt_goals_df['monthlyInputSaving'].cumsum()
    curremt_goals_df['virtualInvesting'] = curremt_goals_df['monthlyInputInvesting'].cumsum()
    curremt_goals_df['virtualBalance'] = curremt_goals_df['actualBalance'] - total_input

    original_data = {
       'originalActualBalance': curremt_goals_df['actualBalance'], 
       'originalActualSaving': curremt_goals_df['actualSaving'],
       'originalActualInvesting': curremt_goals_df['actualInvesting'], 
       'originalMonthlyInputSaving': curremt_goals_df['monthlyInputSaving'], 
       'originalMonthlyInputInvesting': curremt_goals_df['monthlyInputInvesting'], 
       'originalVirtualSaving': curremt_goals_df['virtualSaving'], 
       'originalVirtualInvesting': curremt_goals_df['virtualInvesting'], 
       'originalVirtualBalance': curremt_goals_df['virtualBalance'],
    }
    curremt_goals_df['currency'] = currency
    curremt_goals_df['originalCurrency'] = currency
    curremt_goals_df['originalData'] = curremt_goals_df.apply(
        lambda row: json.dumps({
            'originalActualBalance': float(row['actualBalance']),
            'originalActualSaving': float(row['actualSaving']),
            'originalActualInvesting': float(row['actualInvesting']),
            'originalMonthlyInputSaving': float(row['monthlyInputSaving']),
            'originalMonthlyInputInvesting': float(row['monthlyInputInvesting']),
            'originalVirtualSaving': float(row['virtualSaving']),
            'originalVirtualInvesting': float(row['virtualInvesting']),
            'originalVirtualBalance': float(row['virtualBalance']),
            'originalCurrency': int(row['currency'])
        }),
        axis=1
    )

    print(f"curremt_goals_df:\n{curremt_goals_df}\n\n")
    return curremt_goals_df
  else:
    print(f"\n\nupdate to see second dataframe \n")
    # Get full date range
    min_date = goals_df['date'].min()
    max_date = curremt_goals_df['date'].max()
    full_date_range = pd.date_range(start=min_date, end=max_date, freq='MS').strftime('%Y-%m')

    # Identify missing months
    existing_dates = set(goals_df['date']).union(set(curremt_goals_df['date']))
    missing_dates = [d for d in full_date_range if d not in existing_dates]

    # Use last row of goals_df to create missing rows
    if not missing_dates:
        filled_df = pd.DataFrame()
    else:
        last_row = goals_df.sort_values('date').iloc[-1]
        last_transaction_row = curremt_goals_df.sort_values('date').iloc[-1]
        filled_df = pd.DataFrame([{
            'date': d,
            'actualBalance': last_transaction_row['actualBalance'],
            'actualSaving': last_transaction_row['actualSaving'],
            'actualInvesting': 0,
            'monthlyInputSaving': 0,
            'virtualSaving': last_row['virtualSaving'],
            'monthlyInputInvesting': 0,
            'virtualInvesting': last_row['virtualInvesting'],
            'virtualBalance': last_row['virtualBalance'],
            'status': -1
        } for d in missing_dates])

    # Combine everything
    combined_df = pd.concat([goals_df, filled_df, curremt_goals_df], ignore_index=True)
    print(f"at start combined_df:\n{combined_df}\n\n")
    combined_df = combined_df.drop_duplicates(subset=['date'], keep='last').sort_values('date').reset_index(drop=True)

    # Recalculate virtuals
    combined_df['virtualSaving'] = combined_df['monthlyInputSaving'].cumsum()
    combined_df['virtualInvesting'] = combined_df['monthlyInputInvesting'].cumsum()
    total_input = combined_df['monthlyInputSaving'] + combined_df['monthlyInputInvesting']
    combined_df['virtualBalance'] = combined_df['actualBalance'].iloc[0] - total_input.cumsum()

    combined_df['currency'] = currency
    combined_df['originalCurrency'] = currency
    combined_df['originalData'] = combined_df.apply(
        lambda row: json.dumps({
            'originalActualBalance': float(row['actualBalance']),
            'originalActualSaving': float(row['actualSaving']),
            'originalActualInvesting': float(row['actualInvesting']),
            'originalMonthlyInputSaving': float(row['monthlyInputSaving']),
            'originalMonthlyInputInvesting': float(row['monthlyInputInvesting']),
            'originalVirtualSaving': float(row['virtualSaving']),
            'originalVirtualInvesting': float(row['virtualInvesting']),
            'originalVirtualBalance': float(row['virtualBalance']),
            'originalCurrency': int(row['currency'])
        }),
        axis=1
    )
    combined_df = combined_df[['date', 'actualBalance', 'actualSaving', 'actualInvesting', 'monthlyInputSaving', 'virtualSaving', 'monthlyInputInvesting', 'virtualInvesting', 'virtualBalance', 'status', 'currency', 'originalCurrency', 'originalData']]

    print(f"combined_df:\n{combined_df}\n\n")


  return combined_df


## Setup Function# This function sets up the goals DataFrame based on the provided requests, transactions, and goals data
def goal_setup(requests, transactions, goals_df):
  print(f"amount: {requests.goals.amount}\n\n")

  df = pd.DataFrame.from_dict(transactions)
  # goals_df = pd.DataFrame.from_dict(goals)

  print(F"goals df:\n{goals_df}\n\n")

  df = correct_initial_data(df)

  if requests.goals.isSaving:
      df['monthlyInputSaving'] = int(requests.goals.amount)
      df['monthlyInputInvesting'] = 0
  else:
      df['monthlyInputSaving'] = 0
      df['monthlyInputInvesting'] = int(requests.goals.amount)

  df['virtualSaving'] = df['actualSaving'] + df['monthlyInputSaving']
  df['virtualInvesting'] = df['actualInvesting'] + df['monthlyInputInvesting']
  df['virtualBalance'] = df['actualBalance'] - df['virtualSaving'] - df['virtualInvesting']
  df['status'] = 0

  df = df[['date', 'actualBalance', 'actualSaving', 'actualInvesting', 'monthlyInputSaving', 'virtualSaving', 'monthlyInputInvesting', 'virtualInvesting', 'virtualBalance', 'status']]

  print(f"before goals df:\n{df}\n\n")

  if goals_df.empty:
    goals_df = pd.DataFrame(columns=df.columns)
    goals_df = pd.DataFrame().reindex_like(df).iloc[0:0]

    print(f"goals df:\n{goals_df}\n\n")

    df = df.groupby('date').agg(
          actualBalance=('actualBalance', 'last'),
          actualSaving=('actualSaving', 'last'),
          actualInvesting=('actualInvesting', 'last'),
          monthlyInputSaving=('monthlyInputSaving', 'last'),
          virtualSaving=('virtualSaving', 'last'),
          monthlyInputInvesting=('monthlyInputInvesting', 'last'),
          virtualInvesting=('virtualInvesting', 'last'),
          virtualBalance=('virtualBalance', 'last'),
          status=('status', 'last')
    ).reset_index()

  print(f"after goals df:\n{df}\n\n")

  # Define start and end dates
  startMonth = requests.goals.startMonth.zfill(2)
  endMonth = requests.goals.endMonth.zfill(2)
  start_date = pd.Timestamp(f"{requests.goals.startYear}-{startMonth}-01")
  end_date = pd.Timestamp(f"{requests.goals.endYear}-{endMonth}-01")
  all_dates = pd.date_range(start=start_date, end=end_date, freq='MS').strftime('%Y-%m')

  df = resolve_missing_data(df, all_dates)

  print(f"final df:\n{df}\n\n")
  return df


## Functionality
def get_current_month():
   return datetime.now().strftime("%Y-%m")

def correct_initial_data(df):
  df['date'] = pd.to_datetime(df['date'])
  df['month'], df['year'] = df['date'].dt.month_name(), df['date'].dt.year.astype(int)
  df['date'] = df['date'].dt.strftime('%Y-%m')

  print(f"current dates:\n{df['date']}\n\n")

  df[['amount_num', 'balance_num']] = df[['amount', 'balance']].apply(pd.to_numeric, errors='coerce')

  df['actualBalance'] = (
        df.sort_values('date', ascending=True)
        .groupby(['year', 'month'])['balance_num']
        .transform('last')
        .astype(int)
    )
  df['actualSpend'] = (
        df.groupby(['year', 'month'])['amount_num']
        .transform(lambda x: x[x < 0].sum())
        .astype(int)
    )
  df['actualSaving'] = (
        df.groupby(['year', 'month'])['amount_num']
        .transform(lambda x: x[df['recipient'].str.contains('Spaarrekening|Trade Republic', case=False, na=False)].sum())
        .astype(int)
    )
  df['actualInvesting'] = (
        df.groupby(['year', 'month'])['amount_num']
        .transform(lambda x: x[df['recipient'].str.contains('Spaarrekening|Trade Republic', case=False, na=False)].sum())
        .astype(int)
    )
  return df
   
def resolve_missing_data(df, all_dates):
  # Find missing dates
  existing_dates = df['date'].tolist()
  missing_dates = sorted(set(all_dates) - set(existing_dates))

  print(f"missing data:\n{missing_dates}\n\n")

  # Create missing rows
  new_rows = pd.DataFrame({'date': missing_dates})
  new_rows['actualBalance'] = df['actualBalance'].iloc[0]
  new_rows['actualSaving'] = df['actualSaving'].iloc[0]
  new_rows['actualInvesting'] = df['actualInvesting'].iloc[0]
  new_rows['monthlyInputSaving'] = df['monthlyInputSaving'].iloc[0]
  new_rows['virtualSaving'] = df['virtualSaving'].iloc[0]
  new_rows['monthlyInputInvesting'] = df['monthlyInputInvesting'].iloc[0]
  new_rows['virtualInvesting'] = df['virtualInvesting'].iloc[0]
  new_rows['virtualBalance'] = df['virtualBalance'].iloc[0]
  new_rows['status'] = -1

  # Append missing rows to df
  df = pd.concat([df, new_rows], ignore_index=True).sort_values('date')
  df = df.fillna(0)
  df[df.columns.difference(['date'])] = df[df.columns.difference(['date'])].astype(int)
  df = df[df['date'].isin(missing_dates)].reset_index(drop=True)
  return df



