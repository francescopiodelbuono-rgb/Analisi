import pandas as pd
import yfinance as yf

from src.config import (
    ETF_MAP,
    DATA_RAW_DIR
)


def create_mapping_dataframe():

    mapping_df = pd.DataFrame(
        list(ETF_MAP.items()),
        columns=["ISIN", "Ticker"]
    )

    return mapping_df


def get_tickers():

    mapping_df = create_mapping_dataframe()

    tickers = mapping_df["Ticker"].tolist()

    return tickers


def download_etf_prices(
    start_date="2016-06-01"
):

    tickers = get_tickers()

    prices = yf.download(
        tickers=tickers,
        start=start_date,
        end=None,
        auto_adjust=True,
        progress=False
    )

    close_prices = prices["Close"]

    ticker_to_isin = {
        ticker: isin
        for isin, ticker in ETF_MAP.items()
    }

    close_prices = close_prices.rename(
        columns=ticker_to_isin
    )

    output_file = (
        DATA_RAW_DIR /
        "prezzi_etf_portafoglio.csv"
    )

    close_prices.to_csv(
        output_file,
        index=True,
        encoding="utf-8"
    )

    print(
        f"\nPrezzi ETF salvati in: "
        f"{output_file}"
    )

    return close_prices


def download_benchmark(
    benchmark_ticker="SWDA.MI",
    start_date="2016-06-01"
):

    benchmark_data = yf.download(
        benchmark_ticker,
        start=start_date,
        auto_adjust=True,
        progress=False
    )

    benchmark_prices = benchmark_data["Close"]

    output_file = (
        DATA_RAW_DIR /
        "benchmark_msci_world.csv"
    )

    benchmark_prices.to_csv(
        output_file,
        index=True,
        encoding="utf-8"
    )

    print(
        f"\nBenchmark salvato in: "
        f"{output_file}"
    )

    return benchmark_prices