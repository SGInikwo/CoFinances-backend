import pandas as pd
from datetime import datetime

def unique_dicts(lst):
    seen = set()
    unique_list = []
    
    for d in lst:
        key = tuple(sorted(d.items()))  # Sort to ensure consistent order
        if key not in seen:
            seen.add(key)
            unique_list.append(d)

    return unique_list

def earliest_date_dataframe(transactions):
  df = pd.DataFrame.from_dict(transactions)

  # Ensure date column is datetime
  df['date'] = pd.to_datetime(df['date'])

  month_day_list = df[['date']].apply(lambda x: {'month': x['date'].month, 'year': x['date'].year}, axis=1).tolist()
  month_day_list = unique_dicts(month_day_list)
  return month_day_list