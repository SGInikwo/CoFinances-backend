import pandas as pd

def get_conversion_rate(from_currency, to_currency):
    currency = {0:  "EUR", 1: "KRW", 2: "KES", 3: "GBP", 4: "USD"}

    from_currency = int(from_currency)
    to_currency = int(from_currency)

    from_currency = currency[from_currency]
    to_currency = currency[to_currency]

    exchange_table = pd.read_csv('./exchange_rates.csv', index_col=0)
    # Return 1 if both currencies are the same
    if from_currency == to_currency:
        return 1
    else:
        return exchange_table.loc[from_currency, to_currency]
    

def create_dataframe(transactions, uCurrency):
    df = pd.DataFrame.from_dict(transactions)

    # Convert 'date' to datetime and extract year, month, day
    df['date'] = pd.to_datetime(df['date'])
    df['day'], df['month'], df['year'] = df['date'].dt.day.astype(int), df['date'].dt.month_name(), df['date'].dt.year.astype(int)

    # Convert 'amount' and 'balance' to userCurrency
    df[['amount', 'balance']] = df.apply(
        lambda row: row[['amount', 'balance']].astype(float) * get_conversion_rate(row['currency'], uCurrency),
        axis=1
    )

    # Convert 'amount' and 'balance' temporarily for calculations
    df[['amount_num', 'balance_num']] = df[['amount', 'balance']].apply(pd.to_numeric, errors='coerce')

    # Calculate monthlyBalance, monthlyExpenses, monthlySavings, and monthlyIncome
    df['monthlyBalance'] = (
    df.sort_values('date', ascending=True)
    .groupby(['year', 'month'])['balance_num']
    .transform('last')
    .astype(str)
)

    df['monthlyExpenses'] = (
        df.groupby(['year', 'month'])['amount_num']
        .transform(lambda x: x[x < 0].sum())
        .astype(str)
    )

    df['monthlySavings'] = (
        df.groupby(['year', 'month'])['amount_num']
        .transform(lambda x: x[df['recipient'].str.contains('Spaarrekening|Trade Republic', case=False, na=False)].sum())
        .astype(str)
    )

    df['monthlyIncome'] = (
        df.groupby(['year', 'month'])['amount_num']
        .transform(lambda x: x[x > 0].sum())
        .astype(str)
    )

    # Drop temporary numeric columns and unwanted columns
    # df.drop(columns=['amount_num', 'balance_num', 'date_str'], inplace=True)
    df["transactionId"] = df["id"]
    df["monthlyInvestment"] = ""

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")  # Adjust format as needed
    # max_date = df["date"].max().strftime("%Y-%m-%d")
    df["date"] = df["date"].astype(str)
    df["amount"] = df["amount"].astype(str)

    # Select the desired columns
    df = df[['day', 'month', 'year', 'monthlyBalance', 'monthlyExpenses', 'monthlySavings', "monthlyInvestment", "transactionId", 'monthlyIncome', 'date', 'amount']]
    
    return df


# def summary_dataframe(transactions, month=None, year=None):
#     df = pd.DataFrame.from_dict(transactions)

#     # Ensure date column is datetime
#     df['date'] = pd.to_datetime(df['date'])

#     # Get latest month's data
#     if month == "null" and year == "null":
#         latest_month = df['date'].max().month
#         latest_year = df['date'].max().year
#     else:
#         temp_data = {'month_name': [month], "year": [year]}
#         temp_df = pd.DataFrame(temp_data)

#         temp_df['month_number'] = pd.to_datetime(temp_df['month_name'], format='%B').dt.month
#         temp_df['year'] = pd.to_datetime(temp_df['year']).dt.year

#         latest_month = temp_df['month_number'].max()
#         latest_year = temp_df['year'].max()

#     latest_data = df[(df['date'].dt.month == latest_month) & (df['date'].dt.year == latest_year)]

#     # Extract balance, expenses, and savings
#     latest_summary = latest_data[['monthlyBalance', 'monthlyExpenses', 'monthlySavings']].drop_duplicates()

#     latest_summary = latest_summary.to_dict(orient='records')

#     return latest_summary[0]

def summary_dataframe(transactions, month=None, year=None):
    df = pd.DataFrame.from_dict(transactions)

    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'])

    # Get latest month's data
    if month == "null" and year == "null":
        # Get the latest and second latest date
        latest_date = df['date'].max()
        second_latest_date = df[df['date'] < latest_date]['date'].max()

        # Get the latest month and year from the dates
        latest_month = latest_date.month
        latest_year = latest_date.year
        second_latest_month = second_latest_date.month
        second_latest_year = second_latest_date.year
    else:
        temp_data = {'month_name': [month], "year": [year]}
        temp_df = pd.DataFrame(temp_data)

        temp_df['month_number'] = pd.to_datetime(temp_df['month_name'], format='%B').dt.month
        temp_df['year'] = pd.to_datetime(temp_df['year']).dt.year

        latest_month = temp_df['month_number'].max()
        latest_year = temp_df['year'].max()

        # Find second latest month and year based on the same logic
        second_latest_month = latest_month - 1 if latest_month > 1 else 12
        second_latest_year = latest_year if latest_month > 1 else latest_year - 1

    # Get the data for both the latest and second latest month
    latest_data = df[(df['date'].dt.month == latest_month) & (df['date'].dt.year == latest_year)]
    second_latest_data = df[(df['date'].dt.month == second_latest_month) & (df['date'].dt.year == second_latest_year)]

    # Extract balance, expenses, and savings for both months
    latest_summary = latest_data[['monthlyBalance', 'monthlyExpenses', 'monthlySavings']].drop_duplicates()
    second_latest_summary = second_latest_data[['monthlyBalance', 'monthlyExpenses', 'monthlySavings']].drop_duplicates()

    # Combine latest and second latest data into a single summary
    combined_summary = {
        'monthlyBalance': latest_summary['monthlyBalance'].values[0] if not latest_summary.empty else None,
        'monthlyExpenses': latest_summary['monthlyExpenses'].values[0] if not latest_summary.empty else None,
        'monthlySavings': latest_summary['monthlySavings'].values[0] if not latest_summary.empty else None,
        'earliestBalance': second_latest_summary['monthlyBalance'].values[0] if not second_latest_summary.empty else None,
        'earliestExpenses': second_latest_summary['monthlyExpenses'].values[0] if not second_latest_summary.empty else None,
        'earliestSavings': second_latest_summary['monthlySavings'].values[0] if not second_latest_summary.empty else None
    }

    return combined_summary

def monthly_dataframe(summary):
    df = pd.DataFrame.from_dict(summary)

    df = df.groupby(["month", "year"]).agg({'monthlyExpenses': 'first'}).reset_index()


    return df[["month", "year"]].to_dict(orient='records')