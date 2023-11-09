import yfinance as yf
import pandas as pd
import numpy as np


def sharpe(prices):
    returns = prices["Close"].pct_change()
    arithmetic_mean_returns = returns.mean()

    geometric_mean_returns = np.geomspace(1, 1 + arithmetic_mean_returns, 252)[-1] - 1

    standard_deviation = returns.std()

    sharpe_ratio = (arithmetic_mean_returns - 0.03) / (
        standard_deviation * np.sqrt(252)
    )

    return round(sharpe_ratio, 3)


def beta(prices):
    sp500 = yf.Ticker("^GSPC")
    sp500_df = sp500.history(period="1y")

    stock_returns = prices["Close"] / prices["Close"].shift(1) - 1
    market_returns = sp500_df["Close"] / sp500_df["Close"].shift(1) - 1

    stock_returns = stock_returns.dropna()
    market_returns = market_returns.dropna()

    covariance = np.cov(stock_returns, market_returns)[0, 1]
    variance = np.var(market_returns)

    beta = covariance / variance

    return round(beta, 3)


def piotroski_f_score(income_statement, cashflow, balance_sheet):
    f_score = 0

    # Criteria 1: Positive Net Income
    if income_statement.loc["Net Income"].iloc[0] > 0:
        f_score += 1

    # Criteria 2: Positive Operating Cash Flow
    if cashflow.loc["Operating Cash Flow"].iloc[0] > 0:
        f_score += 1

    # Criteria 3: Cash Flow from Operations > Net Income
    if (
        cashflow.loc["Operating Cash Flow"].iloc[0]
        > income_statement.loc["Net Income"].iloc[0]
    ):
        f_score += 1

    # Criteria 4: Lower Ratio of Long-Term Debt to Total Assets compared to the previous year
    long_term_debt = balance_sheet.loc["Long Term Debt"]
    total_assets = balance_sheet.loc["Total Assets"]
    criteria_4 = long_term_debt.iloc[1] > long_term_debt.iloc[0]

    # Criteria 5: Higher Current Ratio compared to the previous year
    current_assets = balance_sheet.loc["Current Assets"]
    current_liabilities = balance_sheet.loc["Current Liabilities"]

    if (current_assets / current_liabilities).iloc[1] < (
        current_assets / current_liabilities
    ).iloc[0]:
        f_score += 1

    # Criteria 6: No new shares were issued in the last year
    ordinary_shares_number = balance_sheet.loc["Ordinary Shares Number"]
    share_issued = balance_sheet.loc["Share Issued"]

    if (ordinary_shares_number.iloc[0] == ordinary_shares_number.iloc[1]) & (
        share_issued.iloc[0] == share_issued.iloc[1]
    ):
        f_score += 1

    # Criteria 7: Higher Gross Margin compared to the previous year
    gross_margin = (
        income_statement.loc["Gross Profit"]
        / income_statement.loc["Total Revenue"]
        * 100
    )

    if gross_margin.iloc[0] > gross_margin.iloc[1]:
        f_score += 1

    # Criteria 8: Higher Asset Turnover compared to the previous year
    total_revenue = income_statement.loc["Total Revenue"]
    if (total_revenue / total_assets).iloc[1] < (total_revenue / total_assets).iloc[0]:
        f_score += 1

    # Criteria 9: Higher Return on Assets (ROA) compared to the previous year
    return_on_assets = income_statement.loc["Net Income"] / total_assets
    if return_on_assets.iloc[0] > return_on_assets.iloc[1]:
        f_score += 1

    return f_score


def altman_z_score(balance_sheet, income_statement):
    print(balance_sheet)
    print(income_statement)

    working_capital = (
        balance_sheet.loc["Current Assets"].iloc[0]
        - balance_sheet.loc["Current Liabilities"].iloc[0]
    )
    retained_earnings = balance_sheet.loc["Retained Earnings"].iloc[0]
    ebit = income_statement.loc["EBIT"].iloc[0]
    total_assets = balance_sheet.loc["Total Assets"].iloc[0]
    total_liabilities = balance_sheet.loc[
        "Total Liabilities Net Minority Interest"
    ].iloc[0]
    sales = income_statement.loc["Total Revenue"].iloc[0]

    z1 = 1.2 * working_capital / total_assets
    z2 = 1.4 * retained_earnings / total_assets
    z3 = 3.3 * ebit / total_assets
    z4 = 0.6 * total_assets / total_liabilities
    z5 = 1.0 * sales / total_assets

    altman_z = z1 + z2 + z3 + z4 + z5

    return round(altman_z, 3)


def analyze(symbol):
    ticker = yf.Ticker(symbol)

    prices = ticker.history(period="1y")
    income_statement = ticker.income_stmt
    cashflow = ticker.cashflow
    balance_sheet = ticker.balance_sheet

    result = {}

    result["sharpe"] = sharpe(prices)
    result["beta"] = beta(prices)
    result["piotroski"] = piotroski_f_score(income_statement, cashflow, balance_sheet)
    result["altman"] = altman_z_score(balance_sheet, income_statement)

    return result
