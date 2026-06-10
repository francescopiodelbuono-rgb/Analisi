import numpy as np
import pandas as pd


def calculate_basic_performance_metrics(
    portfolio_returns,
    benchmark_returns,
    drawdown,
    risk_free_rate=0.02
):

    portfolio_annual_return = (
        portfolio_returns.mean() * 252
    )

    portfolio_annual_volatility = (
        portfolio_returns.std() * np.sqrt(252)
    )

    portfolio_sharpe = (
        (portfolio_annual_return - risk_free_rate)
        / portfolio_annual_volatility
    )

    portfolio_max_drawdown = (
        drawdown.min()
    )

    benchmark_annual_return = (
        benchmark_returns.mean() * 252
    )

    benchmark_annual_volatility = (
        benchmark_returns.std() * np.sqrt(252)
    )

    benchmark_sharpe = (
        (benchmark_annual_return - risk_free_rate)
        / benchmark_annual_volatility
    )

    benchmark_cumulative = (
        1 + benchmark_returns
    ).cumprod()

    benchmark_running_max = (
        benchmark_cumulative.cummax()
    )

    benchmark_drawdown = (
        benchmark_cumulative
        - benchmark_running_max
    ) / benchmark_running_max

    benchmark_max_drawdown = (
        benchmark_drawdown.min()
    )

    return {
        "portfolio_annual_return":
        portfolio_annual_return,

        "portfolio_annual_volatility":
        portfolio_annual_volatility,

        "portfolio_sharpe":
        portfolio_sharpe,

        "portfolio_max_drawdown":
        portfolio_max_drawdown,

        "benchmark_annual_return":
        benchmark_annual_return,

        "benchmark_annual_volatility":
        benchmark_annual_volatility,

        "benchmark_sharpe":
        benchmark_sharpe,

        "benchmark_max_drawdown":
        benchmark_max_drawdown
    }