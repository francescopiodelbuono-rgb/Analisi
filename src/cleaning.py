import pandas as pd

from src.config import (
    DATA_PROCESSED_DIR,
    OUTPUT_DIR
)


def calculate_missing_percentage(prices):

    missing_percentage = (
        prices.isna().mean() * 100
    )

    return missing_percentage


def max_consecutive_missing(series):

    first_valid = series.first_valid_index()
    last_valid = series.last_valid_index()

    if first_valid is None or last_valid is None:
        return len(series)

    missing = series.loc[
        first_valid:last_valid
    ].isna()

    missing_groups = (
        missing.ne(missing.shift())
        .cumsum()
    )

    return int(
        missing.groupby(missing_groups)
        .sum()
        .max()
    )


def create_data_quality_report(
    prices,
    missing_percentage
):

    quality_df = pd.DataFrame({
        "Prima_Data_Valida": prices.apply(
            lambda series: series.first_valid_index()
        ),

        "Ultima_Data_Valida": prices.apply(
            lambda series: series.last_valid_index()
        ),

        "Osservazioni_Mancanti": (
            prices.isna().sum()
        ),

        "Percentuale_Mancante": (
            missing_percentage
        ),

        "Massimo_Gap_Interno": prices.apply(
            max_consecutive_missing
        )
    })

    output_file = (
        OUTPUT_DIR /
        "qualita_dati_etf.csv"
    )

    quality_df.to_csv(output_file)

    print(
        f"\nReport qualità dati salvato in:"
        f"\n{output_file}"
    )

    return quality_df


def clean_price_data(
    prices,
    threshold=20,
    max_forward_fill_days=2
):

    missing_percentage = (
        calculate_missing_percentage(prices)
    )

    valid_columns = (
        missing_percentage[
            missing_percentage < threshold
        ].index
    )

    filtered_prices = prices[
        valid_columns
    ]

    clean_prices = (
        filtered_prices
        .ffill(limit=max_forward_fill_days)
        .dropna()
    )

    output_file = (
        DATA_PROCESSED_DIR /
        "prezzi_etf_portafoglio_clean.csv"
    )

    clean_prices.to_csv(output_file)

    print(
        f"\nDataset pulito salvato in:"
        f"\n{output_file}"
    )

    return clean_prices, missing_percentage