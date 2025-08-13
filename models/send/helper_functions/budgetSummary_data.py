import pandas as pd

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
  df[['budgetCategory', 'actualCategory']] = df.apply(
      lambda row: row[['originalBudgetCategory', 'originalActualCategory']].astype(float) * get_conversion_rate(row['originalCurrency'], cleintCurrency),
      axis=1
  )

  df["currency"] = cleintCurrency
  # df["budget"] = df["budget"].astype(str)
  # df["actual"] = df["actual"].astype(str)
  return df.to_dict(orient='records')

def create_dataframe(budgets, category, uCurrency):
    df = pd.DataFrame.from_dict(budgets)
    category_dict = dict(category)

    # Convert 'amount' and 'balance' temporarily for calculations
    df[['budget_num', 'actual_num']] = df[['budget', 'actual']].apply(pd.to_numeric, errors='coerce')

    # Calculate monthlyBalance, monthlyExpenses, monthlySavings, and monthlyIncome

    df['budgetCategory'] = (
        df.groupby(['date', 'category'])['budget_num']
        .transform(lambda x: x[x > 0].sum())
        # .astype(str)
    )

    df['actualCategory'] = (
        df.groupby(['date', 'category'])['actual_num']
        .transform(lambda x: x[x > 0].sum())
        # .astype(str)
    )

    # Drop temporary numeric columns and unwanted columns
    print(f"Category dict: {category_dict}")
    df["categoryId"] = df["category"].map(category_dict)
    df["categoryName"] = df["category"]

    df['currency'] = uCurrency
    df['originalCurrency'] = uCurrency
    
    df["date"] = df["date"].astype(str)
    # df["amount"] = df["amount"].astype(str)

    # Select the desired columns
    df = df[['categoryName', 'budgetCategory', 'actualCategory', 'categoryId', 'date']]
    return df