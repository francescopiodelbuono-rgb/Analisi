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