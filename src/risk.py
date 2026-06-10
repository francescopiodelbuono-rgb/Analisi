import numpy as np
import pandas as pd


def calculate_portfolio_returns(
    returns
):

    equal_weights = (
        np.ones(len(returns.columns))
        / len(returns.columns)
    )

    portfolio_returns = (
        returns.dot(equal_weights)
    )

    return portfolio_returns


def calculate_drawdown(
    portfolio_returns,
    initial_capital=10000
):

    cumulative_returns = (
        1 + portfolio_returns
    ).cumprod()

    portfolio_value = (
        cumulative_returns
        * initial_capital
    )

    running_max = (
        portfolio_value.cummax()
    )

    drawdown = (
        portfolio_value - running_max
    ) / running_max

    max_drawdown = drawdown.min()

    worst_date = drawdown.idxmin()

    peak_date = (
        portfolio_value
        .loc[:worst_date]
        .idxmax()
    )

    peak_value = (
        portfolio_value.loc[peak_date]
    )

    trough_value = (
        portfolio_value.loc[worst_date]
    )

    loss_amount = (
        trough_value - peak_value
    )

    drawdown_duration = (
        worst_date - peak_date
    )

    return {
        "portfolio_value": portfolio_value,
        "running_max": running_max,
        "drawdown": drawdown,
        "max_drawdown": max_drawdown,
        "worst_date": worst_date,
        "peak_date": peak_date,
        "peak_value": peak_value,
        "trough_value": trough_value,
        "loss_amount": loss_amount,
        "drawdown_duration": drawdown_duration
    }


def calculate_var(
    portfolio_returns,
    confidence_level=0.95,
    initial_capital=10000
):

    historical_var = np.percentile(
        portfolio_returns,
        (1 - confidence_level) * 100
    )

    portfolio_mean = (
        portfolio_returns.mean()
    )

    portfolio_std = (
        portfolio_returns.std()
    )

    z_score_95 = 1.65

    parametric_var = (
        portfolio_mean
        - z_score_95 * portfolio_std
    )

    historical_var_amount = (
        initial_capital
        * historical_var
    )

    parametric_var_amount = (
        initial_capital
        * parametric_var
    )

    return {
        "historical_var": historical_var,
        "parametric_var": parametric_var,
        "historical_var_amount": historical_var_amount,
        "parametric_var_amount": parametric_var_amount
    }


def calculate_rolling_volatility(
    portfolio_returns,
    benchmark_returns
):

    rolling_vol_30 = (
        portfolio_returns
        .rolling(window=30)
        .std()
        * np.sqrt(252)
    )

    rolling_vol_60 = (
        portfolio_returns
        .rolling(window=60)
        .std()
        * np.sqrt(252)
    )

    benchmark_rolling_vol_30 = (
        benchmark_returns
        .rolling(window=30)
        .std()
        * np.sqrt(252)
    )

    return {
        "rolling_vol_30": rolling_vol_30,
        "rolling_vol_60": rolling_vol_60,
        "benchmark_rolling_vol_30":
        benchmark_rolling_vol_30,
        "max_vol_30": rolling_vol_30.max(),
        "max_vol_60": rolling_vol_60.max(),
        "max_vol_30_date":
        rolling_vol_30.idxmax(),
        "max_vol_60_date":
        rolling_vol_60.idxmax()
    }