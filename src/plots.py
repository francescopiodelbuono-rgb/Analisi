import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from src.config import FIGURES_DIR


def save_current_figure(filename):
    output_file = FIGURES_DIR / filename

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Grafico salvato in: {output_file}")


def plot_max_drawdown(
    portfolio_value,
    running_max,
    drawdown,
    benchmark_value,
    worst_date,
    trough_value,
    max_drawdown,
    initial_capital=10000
):
    fig, ax1 = plt.subplots(figsize=(16, 8))

    ax1.fill_between(
        portfolio_value.index,
        portfolio_value,
        running_max,
        where=portfolio_value < running_max,
        alpha=0.20,
        label="Area Drawdown"
    )

    ax1.plot(
        portfolio_value.index,
        portfolio_value,
        linewidth=2,
        label="Portafoglio"
    )

    ax1.plot(
        benchmark_value.index,
        benchmark_value,
        linewidth=1,
        linestyle="-",
        label="MSCI World Benchmark (€10.000)"
    )

    threshold = -0.05
    running_max_filtered = pd.Series(np.nan, index=running_max.index)

    in_drawdown_zone = False
    peak_value = None

    for i in range(len(drawdown)):
        current_drawdown = drawdown.iloc[i]
        current_running_max = running_max.iloc[i]
        current_portfolio = portfolio_value.iloc[i]

        if current_drawdown <= threshold and not in_drawdown_zone:
            in_drawdown_zone = True
            peak_value = current_running_max

        if in_drawdown_zone:
            running_max_filtered.iloc[i] = peak_value

        if in_drawdown_zone and current_portfolio >= peak_value:
            in_drawdown_zone = False
            peak_value = None

    ax1.plot(
        running_max_filtered.index,
        running_max_filtered,
        linestyle="--",
        linewidth=2,
        label="Massimo Storico (>5% Drawdown)"
    )

    ax1.scatter(
        worst_date,
        trough_value,
        s=140,
        zorder=5,
        label="Max Drawdown"
    )

    return_at_drawdown = ((trough_value / initial_capital) - 1) * 100

    ax1.annotate(
        f"€{trough_value:,.0f}\nRendimento: {return_at_drawdown:.2f}%\nMax DD: {max_drawdown:.2%}",
        xy=(worst_date, trough_value),
        xytext=(55, 25),
        textcoords="offset points",
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.4",
            facecolor="white",
            alpha=0.95
        ),
        arrowprops=dict(
            arrowstyle="->",
            linewidth=1.5
        )
    )

    ax1.set_title(
        "Portfolio Performance and Maximum Drawdown",
        fontsize=18,
        fontweight="bold"
    )

    ax1.set_xlabel("Data", fontsize=12)
    ax1.set_ylabel("Valore Portafoglio (€)", fontsize=12)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()

    portfolio_return_percent = (
        (portfolio_value / initial_capital) - 1
    ) * 100

    ax2.set_ylim(
        portfolio_return_percent.min(),
        portfolio_return_percent.max()
    )

    ax2.set_ylabel("Rendimento Cumulato (%)", fontsize=12)

    lines1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(lines1, labels1, loc="upper left", frameon=True)

    plt.tight_layout()

    save_current_figure("max_drawdown.png")

    plt.show()

from scipy.stats import norm


def plot_var_distribution(
    portfolio_returns,
    historical_var,
    parametric_var
):
    plt.figure(figsize=(14, 7))

    plt.hist(
        portfolio_returns,
        bins=50,
        density=True,
        alpha=0.6,
        edgecolor="black",
        label="Rendimenti giornalieri"
    )

    x = np.linspace(
        portfolio_returns.min(),
        portfolio_returns.max(),
        1000
    )

    plt.plot(
        x,
        norm.pdf(
            x,
            portfolio_returns.mean(),
            portfolio_returns.std()
        ),
        linewidth=2,
        label="Distribuzione normale teorica"
    )

    plt.axvline(
        historical_var,
        linestyle="--",
        linewidth=2,
        label=f"VaR Storico 95%: {historical_var:.2%}"
    )

    plt.axvline(
        parametric_var,
        linestyle="--",
        linewidth=2,
        label=f"VaR Parametrico 95%: {parametric_var:.2%}"
    )

    plt.axvline(
        portfolio_returns.mean(),
        linestyle=":",
        linewidth=2,
        label=f"Media: {portfolio_returns.mean():.2%}"
    )

    plt.axvspan(
        portfolio_returns.min(),
        historical_var,
        alpha=0.2
    )

    plt.title(
        "Distribuzione Rendimenti Giornalieri e Value at Risk",
        fontsize=18,
        fontweight="bold"
    )

    plt.xlabel("Rendimento giornaliero", fontsize=13)
    plt.ylabel("Densità", fontsize=13)
    plt.grid(alpha=0.3)
    plt.legend(fontsize=12)

    save_current_figure("var_distribution.png")

    plt.show()

def plot_rolling_volatility(
    rolling_vol_30,
    rolling_vol_60,
    benchmark_rolling_vol_30,
    max_vol_30,
    max_vol_60,
    max_vol_30_date,
    max_vol_60_date
):
    plt.figure(figsize=(15, 7))

    plt.plot(
        rolling_vol_30.index,
        rolling_vol_30 * 100,
        linewidth=2,
        label="Rolling Volatility 30 giorni"
    )

    plt.plot(
        rolling_vol_60.index,
        rolling_vol_60 * 100,
        linewidth=2,
        linestyle="--",
        label="Rolling Volatility 60 giorni"
    )

    plt.plot(
        benchmark_rolling_vol_30.index,
        benchmark_rolling_vol_30 * 100,
        linewidth=2,
        linestyle=":",
        label="MSCI World Rolling Volatility 30 giorni"
    )

    plt.scatter(
        max_vol_30_date,
        max_vol_30 * 100,
        s=120,
        zorder=5
    )

    plt.scatter(
        max_vol_60_date,
        max_vol_60 * 100,
        s=120,
        zorder=5
    )

    plt.annotate(
        f"30g: {max_vol_30:.2%}",
        xy=(max_vol_30_date, max_vol_30 * 100),
        xytext=(30, 10),
        textcoords="offset points",
        fontweight="bold",
        arrowprops=dict(arrowstyle="->")
    )

    plt.annotate(
        f"60g: {max_vol_60:.2%}",
        xy=(max_vol_60_date, max_vol_60 * 100),
        xytext=(30, -20),
        textcoords="offset points",
        fontweight="bold",
        arrowprops=dict(arrowstyle="->")
    )

    plt.title(
        "Confronto Rolling Volatility Annualizzata",
        fontsize=18,
        fontweight="bold"
    )

    plt.xlabel("Data", fontsize=13)
    plt.ylabel("Volatilità annualizzata (%)", fontsize=13)
    plt.grid(alpha=0.3)
    plt.legend(fontsize=12)

    save_current_figure("rolling_volatility.png")

    plt.show()
def plot_efficient_frontier(
    results,
    best_volatility,
    best_return,
    min_vol_volatility,
    min_vol_return
):
    plt.figure(figsize=(14, 8))

    plt.scatter(
        results[1, :],
        results[0, :],
        c=results[2, :],
        cmap="viridis",
        s=12,
        alpha=0.7
    )

    plt.colorbar(label="Sharpe Ratio")

    plt.scatter(
        best_volatility,
        best_return,
        marker="*",
        s=350,
        label="Max Sharpe Portfolio"
    )

    plt.scatter(
        min_vol_volatility,
        min_vol_return,
        marker="D",
        s=180,
        label="Minimum Volatility Portfolio"
    )

    plt.title(
        "Efficient Frontier - Portfolio Optimization",
        fontsize=18,
        fontweight="bold"
    )

    plt.xlabel("Volatilità annualizzata", fontsize=12)
    plt.ylabel("Rendimento atteso annualizzato", fontsize=12)
    plt.legend()
    plt.grid(alpha=0.3)

    frontier_df = pd.DataFrame({
        "Volatilità": results[1, :],
        "Rendimento": results[0, :]
    })

    frontier_df = frontier_df.sort_values("Volatilità")

    vol_bins = np.linspace(
        frontier_df["Volatilità"].min(),
        frontier_df["Volatilità"].max(),
        80
    )

    frontier_points = []

    for i in range(len(vol_bins) - 1):
        subset = frontier_df[
            (frontier_df["Volatilità"] >= vol_bins[i])
            & (frontier_df["Volatilità"] < vol_bins[i + 1])
        ]

        if not subset.empty:
            best_point = subset.loc[
                subset["Rendimento"].idxmax()
            ]
            frontier_points.append(best_point)

    frontier_line = pd.DataFrame(frontier_points)

    frontier_line["Rendimento_Smoothed"] = (
        frontier_line["Rendimento"]
        .rolling(window=15, center=True)
        .mean()
    )

    frontier_line = frontier_line.dropna()

    plt.plot(
        frontier_line["Volatilità"],
        frontier_line["Rendimento_Smoothed"],
        linewidth=3,
        label="Frontiera Efficiente"
    )

    save_current_figure("efficient_frontier.png")

    plt.show()
