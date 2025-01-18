# main.py

import numpy as np
# import pandas_ta as ta
import pandas as pd
import yfinance as yf
# import matplotlib.pyplot as plt
import APIKeys

from openai import OpenAI
# from config import openai_api_key

from pydantic import BaseModel


# If you're storing your API key directly in code (not recommended for production):
openai_api_key = APIKeys.OPENAI
client = OpenAI(api_key=openai_api_key)
GPT_MODEL = "gpt-4o-mini"

# store user query and agent response
query_response_dict = {}

# @app.get("/stock_data/")
def stock_data(user_query: str):
    """
    Get stock ticker from User's query
    Return analysis based on technical indicators and respond with analysis from GPT model.
    """
    user_prompt = (
        "<instructions>You are a professional financial analyst..."
        f"The user's query is: {user_query}>\n"
    )

    ticker_response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": user_prompt}]
    )
    stock_ticker = ticker_response.choices[0].message.content.strip()

    # defult 1 year period (Adjust as needed)
    start_date = "2024-01-17"
    end_date = "2025-01-17"

    stock = yf.Ticker(stock_ticker)
    stock_history = stock.history(start=start_date, end=end_date, interval="1d")

    # stock_history["RSI_5"] = ta.rsi(stock_history["Close"], length=5)
    # bollinger = ta.bbands(stock_history["Close"], length=5, std=2)
    # stock_history = stock_history.join(bollinger)

    closing_prices = stock_history["Close"]
    max_price = closing_prices.max()
    min_price = closing_prices.min()
    latest_price = closing_prices.iloc[-1] if not closing_prices.empty else None
    daily_returns = closing_prices.pct_change()
    sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() else None
    annualized_vol = daily_returns.std() * np.sqrt(252) if daily_returns.std() else None
    # relative_strength_index = stock_history["RSI_5"]
    # bollinger_upper = stock_history["BBU_5_2.0"]
    # bollinger_lower = stock_history["BBL_5_2.0"]

    structured_prompt = (
        "<instructions>You are a professional financial analyst specializing in time series...\n"
        f"Stock Analysis for {stock_ticker}:\n"
        f"- Date Range: {start_date} to {end_date}\n"
        f"- Closing Prices: {closing_prices.tolist()}\n"
        f"- Maximum Closing Price: {max_price}\n"
        f"- Minimum Closing Price: {min_price}\n"
        f"- Latest Closing Price: {latest_price}\n"
        f"- Sharpe Ratio: {sharpe_ratio}\n"
        f"- Annualized Volatility: {annualized_vol}\n"
        # f"- Relative Strength Index: {relative_strength_index.tolist()}\n"
        # f"- Bollinger Upper Band: {bollinger_upper.tolist()}\n"
        # f"- Bollinger Lower Band: {bollinger_lower.tolist()}\n"
        "</data>"
    )

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": structured_prompt}]
    )

    query_response_dict[user_query] = response.choices[0].message.content.strip()

    return {
        "user_query": user_query,
        "stock_ticker": stock_ticker,
        "response": response.choices[0].message.content
    }


# @app.get("/fundamental_analysis/")
def fundamental_analysis(user_query: str):
    user_prompt = (
        "<instructions>You are a professional financial analyst..."
        f"The user's query is: {user_query}>\n"
    )

    ticker_response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": user_prompt}]
    )
    stock_ticker = ticker_response.choices[0].message.content.strip()

    stock = yf.Ticker(stock_ticker)
    stock_balance_sheet = stock.balance_sheet
    stock_cash_flow = stock.cash_flow
    stock_financials = stock.financials

    fundamental_prompt = (
        "<instructions>You are a professional financial analyst specializing in company fundamental analysis...\n"
        f"- Balance Sheet:\n{stock_balance_sheet}\n\n"
        f"- Cash Flow Statement:\n{stock_cash_flow}\n\n"
        f"- Income Statement:\n{stock_financials}\n"
    )

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": fundamental_prompt}]
    )

    query_response_dict[user_query] = response.choices[0].message.content.strip()

    return {"user_query": user_query, "response": response.choices[0].message.content}
