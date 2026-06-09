# =========================
# 1. IMPORT LIBRERIE
# =========================

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# =========================
# DIRECTORY PROGETTO
# =========================

try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd()

DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIGURES_DIR = BASE_DIR / "reports" / "figures"
OUTPUT_DIR = BASE_DIR / "reports" / "output"

DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# 2. MAPPING ISIN → TICKER
# =========================

etf_map = {
    "IE00BM67HS53": "XDWM.MI",      # Materials
    "IE00BM67HM91": "XDW0.DE",     # Energy
    "IE00BM67HV82": "XDWI.MI",      # Industrials
    "IE00BM67HQ30": "XDWU.MI",      # Utilities
    "IE00B5L01S80": "HPRD.L",      # Real Estate
    "IE00BM67HL84": "XDWF.DE",     # Financials
    "IE00BM67HK77": "XDWH.MI",      # Health Care
    "IE00BM67HN09": "XDWS.MI",      # Consumer Staples
    "IE00BM67HT60": "XDWT.MI",      # Information Technology
    "IE00BM67HP23": "XDWC.MI",      # Consumer Discretionary
    "IE00BM67HR47": "XWTS.MI"      # Communication Services
}


# =========================
# HTML PARSING JUSTETF
# =========================
####### ------ “Lo scraping è stato utilizzato volutamente come componente dimostrativa del progetto, 
####### ------  per mostrare capacità tecniche di raccolta dati automatizzata. Sono però consapevole 
####### ------  che in contesti finanziari reali la qualità e l’affidabilità del dato sono prioritarie, 
####### ------  quindi l’analisi dovrebbe sempre basarsi su fonti ufficiali o dati verificati.”
# =========================
# SCRAPING JUSTETF - ESPOSIZIONE GEOGRAFICA
# =========================

def scrape_justetf_country_exposure(isin):
    url = f"https://www.justetf.com/en/etf-profile.html?isin={isin}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    if response.status_code != 200:
        print(f"Errore HTTP per {isin}: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    countries_map = {
        "USA": "United States",
        "Giappone": "Japan",
        "Regno_Unito": "United Kingdom",
        "Francia": "France",
        "Germania": "Germany",
        "Svizzera": "Switzerland",
        "Canada": "Canada",
        "Paesi_Bassi": "Netherlands",
        "Australia": "Australia",
        "Danimarca": "Denmark",
        "Svezia": "Sweden",
        "Spagna": "Spain",
        "Taiwan": "Taiwan",
        "Corea_del_Sud": "South Korea",
        "Cina": "China",
        "India": "India",
        "Irlanda": "Ireland",
        "Hong_Kong": "Hong Kong",
        "Singapore": "Singapore",
        "Brasile": "Brazil"
    }

    exposure_data = {
    "ISIN": isin,
    "Fonte": "JustETF scraping",
    "Data_Estrazione": datetime.today().strftime("%Y-%m-%d"),
    "Validazione": "OK"
}

    for country in countries_map.keys():
        exposure_data[country] = 0.0

    country_rows = soup.find_all(
        attrs={"data-testid": "etf-holdings_countries_row"}
    )

    if not country_rows:
        print(f"ATTENZIONE: righe geografiche non trovate per {isin}")
        exposure_data["Altro"] = 100.0
        return exposure_data

    for row in country_rows:
        row_text = row.get_text(" ", strip=True)

        for column_name, justetf_country_name in countries_map.items():

            if justetf_country_name in row_text:

                values = row_text.split()

                for value in values:
                    cleaned_value = (
                        value
                        .replace("%", "")
                        .replace(",", ".")
                    )

                    try:
                        number = float(cleaned_value)

                        if 0 <= number <= 100:
                            exposure_data[column_name] = number
                            break

                    except ValueError:
                        continue

# =========================
# CONTROLLO QUALITÀ DATI
# =========================

        # =========================
    # CONTROLLO QUALITÀ DATI
    # =========================

    total_known = sum(
        value for key, value in exposure_data.items()
        if isinstance(value, (int, float))
    )

    exposure_data["Altro"] = max(0, 100 - total_known)

    somma_finale = sum(
        value for key, value in exposure_data.items()
        if isinstance(value, (int, float))
    )

    # Validazione automatica
    if somma_finale < 95 or somma_finale > 105:
        exposure_data["Validazione"] = "Da verificare"

    # Controlli specifici
    if exposure_data.get("USA", 0) > 95:
        exposure_data["Validazione"] = "Da verificare"

    print(
        f"{isin} | Somma esposizioni: "
        f"{somma_finale:.2f}% | "
        f"Validazione: {exposure_data['Validazione']}"
    )

    return exposure_data
    


# =========================
# 3. CREAZIONE DATAFRAME MAPPING
# =========================

mapping_df = pd.DataFrame(
    list(etf_map.items()),
    columns=["ISIN", "Ticker"]
)

print(mapping_df)


# =========================
# 4. LISTA TICKER
# =========================

tickers = mapping_df["Ticker"].tolist()

print("Ticker da scaricare:")
print(tickers)


# =========================
# 5. DOWNLOAD DATI DA YFINANCE
# =========================

prices = yf.download(
    tickers=tickers,
    start="2016-06-01",
    end=None,
    auto_adjust=True,
    progress=False
)


# =========================
# 6. ESTRAZIONE PREZZI DI CHIUSURA
# =========================

close_prices = prices["Close"]

print(close_prices.head())
print(close_prices.tail())

# =========================
# DOWNLOAD BENCHMARK MSCI WORLD
# =========================

benchmark_ticker = "URTH"

benchmark_data = yf.download(
    benchmark_ticker,
    start="2016-06-01",
    auto_adjust=True,
    progress=False
)

benchmark_prices = benchmark_data["Close"]

benchmark_output_file = DATA_RAW_DIR / "benchmark_msci_world.csv"

benchmark_prices.to_csv(
    benchmark_output_file,
    index=True,
    encoding="utf-8"
)

print(f"Benchmark salvato correttamente in: {benchmark_output_file}")

print("\nBenchmark MSCI World scaricato:")
print(benchmark_prices.head())




# =========================
# 7. CONTROLLO VALORI MANCANTI
# =========================

missing_values = close_prices.isna().sum()

print("Valori mancanti per ETF:")
print(missing_values)


# =========================
# 8. PULIZIA DATI
# =========================

close_prices = close_prices.dropna(how="all")

# Opzione più prudente: elimina solo righe dove mancano tutti i dati
# Non usiamo subito dropna totale perché alcuni ETF possono avere date diverse di quotazione


# =========================
# 9. RINOMINA COLONNE DA TICKER A ISIN
# =========================

ticker_to_isin = {ticker: isin for isin, ticker in etf_map.items()}

close_prices_isin = close_prices.rename(columns=ticker_to_isin)

print(close_prices_isin.head())


 

# =========================
# CREAZIONE COUNTRY EXPOSURE DA JUSTETF
# =========================

country_exposure_list = []

for isin in etf_map.keys():

    print(f"Scarico esposizione geografica per {isin}")

    exposure = scrape_justetf_country_exposure(isin)

    if exposure is not None:
        country_exposure_list.append(exposure)

country_exposure_df = pd.DataFrame(country_exposure_list)

country_exposure_file = DATA_PROCESSED_DIR / "country_exposure_reale.csv"

country_exposure_df.to_csv(
    country_exposure_file,
    index=False,
    encoding="utf-8")

print("\nFile country_exposure_reale.csv creato:")
print(country_exposure_df)


# =========================
# CONTROLLO QUALITÀ ESPOSIZIONI GEOGRAFICHE
# =========================

country_exposure_df["Somma"] = (
    country_exposure_df
    .select_dtypes(include="number")
    .sum(axis=1)
)

print("\nControllo somma esposizioni per ETF:")
print(country_exposure_df[["ISIN", "Somma"]])

anomalie = country_exposure_df[
    (country_exposure_df["Somma"] < 95) |
    (country_exposure_df["Somma"] > 105)
]

if not anomalie.empty:
    print("\nATTENZIONE: ci sono ETF con somma esposizioni anomala:")
    print(anomalie[["ISIN", "Somma"]])
else:
    print("\nControllo superato: tutte le esposizioni sono circa pari a 100%.")

# =========================
# SALVATAGGIO PREZZI ETF
# =========================

output_file = DATA_RAW_DIR / "prezzi_etf_portafoglio.csv"

close_prices_isin.to_csv(
    output_file,
    index=True,
    encoding="utf-8"
)

print(f"File salvato correttamente in: {output_file}")

# =========================
# DATA CLEANING
# =========================

# Percentuale valori mancanti
missing_percentage = (
    close_prices_isin.isna().mean() * 100
)

print("\nPercentuale valori mancanti:")
print(missing_percentage)


# Elimina ETF con troppi dati mancanti
threshold = 20

valid_columns = missing_percentage[
    missing_percentage < threshold
].index

close_prices_filtered = close_prices_isin[
    valid_columns
]

print("\nETF mantenuti:")
print(close_prices_filtered.columns)



# Forward fill piccoli buchi
close_prices_clean = close_prices_filtered.ffill()


# Elimina eventuali NaN residui
close_prices_clean = close_prices_clean.dropna()

# =========================
# 12. CALCOLO RENDIMENTI GIORNALIERI
# =========================

returns = close_prices_clean.pct_change().dropna()

print("\nRendimenti giornalieri:")
print(returns.head())

# =========================
# RENDIMENTI BENCHMARK
# =========================

benchmark_returns = benchmark_prices.pct_change().dropna()


print("\nDataset pulito:")
print(close_prices_clean.head())

print("\nDimensioni dataset:")
print(close_prices_clean.shape)

# =========================
# 11. SALVATAGGIO DATASET PULITO
# =========================

clean_output_file = DATA_PROCESSED_DIR / "prezzi_etf_portafoglio_clean.csv"

close_prices_clean.to_csv(clean_output_file)

print(f"File pulito salvato correttamente in: {clean_output_file}")


# =========================
# 12. CALCOLO RENDIMENTI GIORNALIERI
# =========================

returns = close_prices_clean.pct_change().dropna()

print("\nRendimenti giornalieri:")
print(returns.head())


# =========================
# 13. SALVATAGGIO RENDIMENTI
# =========================

returns_output_file = DATA_PROCESSED_DIR / "rendimenti_etf_portafoglio.csv"

returns.to_csv(returns_output_file)

print(f"Rendimenti salvati correttamente in: {returns_output_file}")

print("\nRendimenti percentuali:")
print((returns * 100).head())



# =========================
# MAX DRAWDOWN ANALYSIS
# =========================

# %%
# =========================
# MAX DRAWDOWN ANALYSIS
# =========================

# Portafoglio equiponderato iniziale
equal_weights = np.ones(len(returns.columns)) / len(returns.columns)

# Rendimenti giornalieri del portafoglio
portfolio_returns = returns.dot(equal_weights)

# Curva cumulata del portafoglio
cumulative_returns = (1 + portfolio_returns).cumprod()

# Capitale iniziale ipotetico
initial_capital = 10000

portfolio_value = cumulative_returns * initial_capital

# Massimo storico progressivo
running_max = portfolio_value.cummax()

# Drawdown percentuale
drawdown = (portfolio_value - running_max) / running_max

# Max Drawdown
max_drawdown = drawdown.min()

# Data peggior drawdown
worst_date = drawdown.idxmin()

# Data del picco precedente
peak_date = portfolio_value.loc[:worst_date].idxmax()

# Valore al picco
peak_value = portfolio_value.loc[peak_date]

# Valore minimo
trough_value = portfolio_value.loc[worst_date]

# Perdita monetaria
loss_amount = trough_value - peak_value

# Durata drawdown
drawdown_duration = worst_date - peak_date

print("\n=========================")
print("MAX DRAWDOWN ANALYSIS")
print("=========================")

print(f"Max Drawdown: {max_drawdown:.2%}")
print(f"Data picco precedente: {peak_date.date()}")
print(f"Data minimo drawdown: {worst_date.date()}")
print(f"Durata fino al minimo: {drawdown_duration.days} giorni")
print(f"Valore al picco: €{peak_value:,.2f}")
print(f"Valore al minimo: €{trough_value:,.2f}")
print(f"Perdita stimata: €{loss_amount:,.2f}")



# =========================
# BENCHMARK VALUE - €10.000 INIZIALI
# =========================

benchmark_returns_aligned = benchmark_returns.reindex(
    portfolio_returns.index
).dropna()

portfolio_returns_aligned = portfolio_returns.reindex(
    benchmark_returns_aligned.index
)

benchmark_value = (
    1 + benchmark_returns_aligned
).cumprod() * initial_capital

portfolio_value_aligned = (
    1 + portfolio_returns_aligned
).cumprod() * initial_capital

# %%
# =========================
# GRAFICO PROFESSIONALE PORTAFOGLIO + MAX DRAWDOWN
# =========================

fig, ax1 = plt.subplots(figsize=(16, 8))

# Area drawdown: distanza tra massimo storico e valore portafoglio
ax1.fill_between(
    portfolio_value.index,
    portfolio_value,
    running_max,
    where=portfolio_value < running_max,
    alpha=0.20,
    label="Area Drawdown"
)

# Valore portafoglio
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
    color="gold",
    label="MSCI World Benchmark (€10.000)"
)

# =========================
# MASSIMO STORICO SOLO IN DRAWDOWN > 5%
# =========================

threshold = -0.05

running_max_filtered = pd.Series(
    np.nan,
    index=running_max.index
)

in_drawdown_zone = False
peak_value = None

for i in range(len(drawdown)):

    current_drawdown = drawdown.iloc[i]
    current_running_max = running_max.iloc[i]
    current_portfolio = portfolio_value.iloc[i]

    # Attiva visualizzazione quando drawdown supera -5%
    if current_drawdown <= threshold and not in_drawdown_zone:
        in_drawdown_zone = True
        peak_value = current_running_max

    # Mantiene linea fino al recupero del massimo
    if in_drawdown_zone:
        running_max_filtered.iloc[i] = peak_value

    # Disattiva quando massimo viene recuperato/superato
    if in_drawdown_zone and current_portfolio >= peak_value:
        in_drawdown_zone = False
        peak_value = None

# Grafico massimo storico filtrato
ax1.plot(
    running_max_filtered.index,
    running_max_filtered,
    linestyle="--",
    linewidth=2,
    color="orange",
    label="Massimo Storico (>5% Drawdown)"
)

# Punto Max Drawdown
ax1.scatter(
    worst_date,
    trough_value,
    color="red",
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
    color="red",
    bbox=dict(
        boxstyle="round,pad=0.4",
        edgecolor="red",
        facecolor="white",
        alpha=0.95
    ),
    arrowprops=dict(
        arrowstyle="->",
        color="red",
        linewidth=1.5
    )
)

# Asse sinistro
ax1.set_title(
    "Portfolio Performance and Maximum Drawdown",
    fontsize=18,
    fontweight="bold"
)

ax1.set_xlabel("Data", fontsize=12)
ax1.set_ylabel("Valore Portafoglio (€)", fontsize=12)

ax1.grid(True, alpha=0.3)

# Asse destro rendimento cumulato
ax2 = ax1.twinx()

portfolio_return_percent = ((portfolio_value / initial_capital) - 1) * 100

ax2.set_ylim(
    portfolio_return_percent.min(),
    portfolio_return_percent.max()
)

ax2.set_ylabel("Rendimento Cumulato (%)", fontsize=12)

# Legenda
lines1, labels1 = ax1.get_legend_handles_labels()
ax1.legend(lines1, labels1, loc="upper left", frameon=True)

plt.tight_layout()
plt.show()



# =========================
# VALUE AT RISK ANALYSIS
# =========================

### Ho utilizzato il Parametric VaR con z-score come modello semplificato e interpretabile, 
### consapevole dei limiti dell’ipotesi di normalità dei rendimenti. 
### Per questo ho affiancato anche un Historical VaR basato sulla distribuzione empirica.

confidence_level = 0.95

# =========================
# VAR STORICO
# =========================

historical_var = np.percentile(
    portfolio_returns,
    (1 - confidence_level) * 100
)

# =========================
# VAR PARAMETRICO
# =========================

portfolio_mean = portfolio_returns.mean()
portfolio_std = portfolio_returns.std()

z_score_95 = 1.65

parametric_var = portfolio_mean - z_score_95 * portfolio_std

print("\n=========================")
print("VALUE AT RISK ANALYSIS")
print("=========================")

print(f"VaR storico giornaliero al 95%: {historical_var:.2%}")
print(f"VaR parametrico giornaliero al 95%: {parametric_var:.2%}")

# Perdita stimata su capitale iniziale
historical_var_amount = initial_capital * historical_var
parametric_var_amount = initial_capital * parametric_var

print(f"Perdita stimata VaR storico su €{initial_capital:,.0f}: €{historical_var_amount:,.2f}")
print(f"Perdita stimata VaR parametrico su €{initial_capital:,.0f}: €{parametric_var_amount:,.2f}")

# =========================
# GRAFICO DISTRIBUZIONE + VAR
# =========================

from scipy.stats import norm

plt.figure(figsize=(14, 7))

# Istogramma rendimenti
plt.hist(
    portfolio_returns,
    bins=50,
    density=True,
    alpha=0.6,
    edgecolor="black",
    label="Rendimenti giornalieri"
)

# Curva normale teorica
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

# Linea VaR storico
plt.axvline(
    historical_var,
    linestyle="--",
    linewidth=2,
    label=f"VaR Storico 95%: {historical_var:.2%}"
)

# Linea VaR parametrico
plt.axvline(
    parametric_var,
    linestyle="--",
    linewidth=2,
    color="red",
    label=f"VaR Parametrico 95%: {parametric_var:.2%}"
)

# Media rendimenti
plt.axvline(
    portfolio_returns.mean(),
    linestyle=":",
    linewidth=2,
    label=f"Media: {portfolio_returns.mean():.2%}"
)

# Area rischio estremo
plt.axvspan(
    portfolio_returns.min(),
    historical_var,
    alpha=0.2
)

# Titolo
plt.title(
    "Distribuzione Rendimenti Giornalieri e Value at Risk",
    fontsize=18,
    fontweight="bold"
)

plt.xlabel(
    "Rendimento giornaliero",
    fontsize=13
)

plt.ylabel(
    "Densità",
    fontsize=13
)

plt.grid(alpha=0.3)

plt.legend(fontsize=12)

plt.show()

### La vicinanza tra i due VaR suggerisce una buona stabilità 
### statistica del portafoglio nel periodo analizzato

# =========================
# ROLLING VOLATILITY ANALYSIS
# =========================

# Rolling volatility 30 giorni
rolling_vol_30 = (
    portfolio_returns
    .rolling(window=30)
    .std()
    * np.sqrt(252)
)

# Rolling volatility 60 giorni
rolling_vol_60 = (
    portfolio_returns
    .rolling(window=60)
    .std()
    * np.sqrt(252)
)

# Rolling volatility benchmark MSCI World
benchmark_rolling_vol_30 = (
    benchmark_returns
    .rolling(window=30)
    .std()
    * np.sqrt(252)
)

# Massimi volatilità
max_vol_30 = rolling_vol_30.max()
max_vol_60 = rolling_vol_60.max()

# Date massimi
max_vol_30_date = rolling_vol_30.idxmax()
max_vol_60_date = rolling_vol_60.idxmax()

print("\n=========================")
print("ROLLING VOLATILITY ANALYSIS")
print("=========================")

print(f"\nMassima rolling volatility 30 giorni: {max_vol_30:.2%}")
print(f"Data massimo 30 giorni: {max_vol_30_date.date()}")

print(f"\nMassima rolling volatility 60 giorni: {max_vol_60:.2%}")
print(f"Data massimo 60 giorni: {max_vol_60_date.date()}")

# =========================
# GRAFICO ROLLING VOLATILITY
# =========================

plt.figure(figsize=(15, 7))

# Rolling 30 giorni
plt.plot(
    rolling_vol_30.index,
    rolling_vol_30 * 100,
    linewidth=2,
    label="Rolling Volatility 30 giorni"
)

# Rolling 60 giorni
plt.plot(
    rolling_vol_60.index,
    rolling_vol_60 * 100,
    linewidth=2,
    linestyle="--",
    label="Rolling Volatility 60 giorni"
)

# Benchmark MSCI World
plt.plot(
    benchmark_rolling_vol_30.index,
    benchmark_rolling_vol_30 * 100,
    linewidth=2,
    linestyle=":",
    label="MSCI World Rolling Volatility 30 giorni"
)

# Punto massimo 30 giorni
plt.scatter(
    max_vol_30_date,
    max_vol_30 * 100,
    color="red",
    s=120,
    zorder=5
)

# Punto massimo 60 giorni
plt.scatter(
    max_vol_60_date,
    max_vol_60 * 100,
    color="orange",
    s=120,
    zorder=5
)


# Annotazione massimo 30 giorni
plt.annotate(
    f"30g: {max_vol_30:.2%}",
    xy=(max_vol_30_date, max_vol_30 * 100),
    xytext=(30, 10),
    textcoords="offset points",
    color="red",
    fontweight="bold",
    arrowprops=dict(
        arrowstyle="->",
        color="red"
    )
)

# Annotazione massimo 60 giorni
plt.annotate(
    f"60g: {max_vol_60:.2%}",
    xy=(max_vol_60_date, max_vol_60 * 100),
    xytext=(30, -20),
    textcoords="offset points",
    color="orange",
    fontweight="bold",
    arrowprops=dict(
        arrowstyle="->",
        color="orange"
    )
)

plt.title(
    "Confronto Rolling Volatility Annualizzata",
    fontsize=18,
    fontweight="bold"
)


plt.xlabel("Data", fontsize=13)

plt.ylabel(
    "Volatilità annualizzata (%)",
    fontsize=13
)

plt.grid(alpha=0.3)

plt.legend(fontsize=12)

plt.show()


# %%
# =========================
# 14. PORTFOLIO OPTIMIZATION
# =========================

# Numero di giorni di borsa in un anno
trading_days = 252

# Rendimento medio annualizzato
mean_returns = returns.mean() * trading_days

# Matrice di covarianza annualizzata
cov_matrix = returns.cov() * trading_days

# Matrice di correlazione
corr_matrix = returns.corr()


print("\nRendimenti medi annualizzati:")
print(mean_returns)

print("\nMatrice di covarianza annualizzata:")
print(cov_matrix)

print("\nMatrice di correlazione annualizzata:")
print(corr_matrix)


# =========================
# 15. SIMULAZIONE MONTE CARLO
# =========================

num_portfolios = 50000

np.random.seed(42)

results = np.zeros((3, num_portfolios))
weights_record = []

for i in range(num_portfolios):
    weights = np.random.random(len(returns.columns))
    weights = weights / np.sum(weights)

    portfolio_return = np.sum(weights * mean_returns)

    portfolio_volatility = np.sqrt(
        np.dot(weights.T, np.dot(cov_matrix, weights))
    )

    sharpe_ratio = portfolio_return / portfolio_volatility

    results[0, i] = portfolio_return
    results[1, i] = portfolio_volatility
    results[2, i] = sharpe_ratio

    weights_record.append(weights)




    # =========================
# 16. MIGLIOR PORTAFOGLIO
# =========================

max_sharpe_index = np.argmax(results[2])

best_return = results[0, max_sharpe_index]
best_volatility = results[1, max_sharpe_index]
best_sharpe = results[2, max_sharpe_index]
best_weights = weights_record[max_sharpe_index]

best_portfolio = pd.DataFrame({
    "ISIN": returns.columns,
    "Peso": best_weights
})

best_portfolio["Peso %"] = best_portfolio["Peso"] * 100

print("\nMIGLIOR PORTAFOGLIO PER SHARPE RATIO:")
print(best_portfolio)

print("\nRendimento atteso annuo:")
print(best_return)

print("\nVolatilità annua:")
print(best_volatility)

print("\nSharpe Ratio:")
print(best_sharpe)

# =========================
# EFFICIENT FRONTIER
# =========================

# Portafoglio a minima volatilità
min_vol_index = np.argmin(results[1])

min_vol_return = results[0, min_vol_index]
min_vol_volatility = results[1, min_vol_index]
min_vol_sharpe = results[2, min_vol_index]
min_vol_weights = weights_record[min_vol_index]

min_vol_portfolio = pd.DataFrame({
    "ISIN": returns.columns,
    "Peso": min_vol_weights
})

min_vol_portfolio["Peso %"] = min_vol_portfolio["Peso"] * 100

print("\nPORTAFOGLIO A MINIMA VOLATILITÀ:")
print(min_vol_portfolio)

print("\nRendimento atteso annuo min volatility:")
print(min_vol_return)

print("\nVolatilità annua min volatility:")
print(min_vol_volatility)

print("\nSharpe Ratio min volatility:")
print(min_vol_sharpe)


# =========================
# GRAFICO EFFICIENT FRONTIER
# =========================

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
    color="red",
    label="Max Sharpe Portfolio"
)

plt.scatter(
    min_vol_volatility,
    min_vol_return,
    marker="D",
    s=180,
    color="orange",
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

# =========================
# LINEA FRONTIERA EFFICIENTE SMUSSATA
# =========================

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
        (frontier_df["Volatilità"] >= vol_bins[i]) &
        (frontier_df["Volatilità"] < vol_bins[i + 1])
    ]

    if not subset.empty:
        best_point = subset.loc[subset["Rendimento"].idxmax()]
        frontier_points.append(best_point)

frontier_line = pd.DataFrame(frontier_points)

# Smussamento della frontiera
frontier_line["Rendimento_Smoothed"] = (
    frontier_line["Rendimento"]
    .rolling(window=15, center=True)
    .mean()
)

frontier_line = frontier_line.dropna()

plt.plot(
    frontier_line["Volatilità"],
    frontier_line["Rendimento_Smoothed"],
    color="black",
    linewidth=3,
    label="Frontiera Efficiente"
)

plt.show()


# =========================
# ESPOSIZIONE GEOGRAFICA DEL MIGLIOR PORTAFOGLIO
# =========================

# Unisce i pesi del miglior portafoglio con le esposizioni geografiche
portfolio_country = best_portfolio.merge(
    country_exposure_df,
    on="ISIN",
    how="left"
)

portfolio_country = portfolio_country.fillna(0)
print("\nControllo dati geografici usati nel portafoglio:")
print(
    portfolio_country[
        ["ISIN", "Peso", "USA", "Giappone", "Germania", "Altro"]
    ]
)


print("\nPortafoglio con esposizioni geografiche:")
print(portfolio_country)

country_columns = [
    col for col in country_exposure_df.columns
    if col not in [
        "ISIN",
        "Somma",
        "Fonte",
        "Data_Estrazione",
        "Validazione"
    ]
]


# Calcolo esposizione geografica ponderata
portfolio_geo_exposure = {}

for country in country_columns:
    portfolio_geo_exposure[country] = (
        portfolio_country["Peso"] * portfolio_country[country]
    ).sum()

portfolio_geo_exposure = pd.Series(portfolio_geo_exposure)

print("\nSomma esposizione portafoglio:")
print(portfolio_geo_exposure.sum())

# Normalizza eventuali piccoli scostamenti
portfolio_geo_exposure = portfolio_geo_exposure / portfolio_geo_exposure.sum() * 100

print("\nEsposizione geografica del miglior portafoglio:")
print(portfolio_geo_exposure)

# =========================
# GRAFICO TORTA ESPOSIZIONE GEOGRAFICA
# =========================

portfolio_geo_exposure_filtered = portfolio_geo_exposure[
    portfolio_geo_exposure > 1
]

plt.figure(figsize=(10, 10))

plt.pie(
    portfolio_geo_exposure_filtered,
    labels=portfolio_geo_exposure_filtered.index,
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Esposizione geografica del portafoglio ottimale")

plt.show()


# Filtra ETF con peso > 3%
best_portfolio_filtered = best_portfolio[
    best_portfolio["Peso %"] > 3
]
# Crea piccoli spazi tra gli spicchi
explode = [0.01] * len(best_portfolio_filtered)

plt.figure(figsize=(10, 10))

sector_map = {
    "IE00BM67HS53": "Materials",
    "IE00BM67HM91": "Energy",
    "IE00BM67HV82": "Industrials",
    "IE00BM67HQ30": "Utilities",
    "IE00B5L01S80": "Real Estate",
    "IE00BM67HL84": "Financials",
    "IE00BM67HK77": "Health Care",
    "IE00BM67HN09": "Consumer Staples",
    "IE00BM67HT60": "Technology",
    "IE00BM67HP23": "Consumer Discretionary",
    "IE00BM67HR47": "Communication Services"
}

best_portfolio_filtered["Sector"] = (
    best_portfolio_filtered["ISIN"]
    .map(sector_map)
)

plt.pie(
    best_portfolio_filtered["Peso %"],
    labels=best_portfolio_filtered["Sector"],
    autopct="%1.1f%%",
    startangle=90,
    explode=explode
)

plt.title("Composizione Portafoglio Ottimale")


plt.show()

# =========================
# CONFRONTO PORTAFOGLIO vs BENCHMARK
# =========================

risk_free_rate = 0.02

# =========================
# METRICHE PORTAFOGLIO
# =========================

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

portfolio_max_drawdown = drawdown.min()

# =========================
# METRICHE BENCHMARK
# =========================

benchmark_cumulative = (
    1 + benchmark_returns_aligned
).cumprod()

benchmark_running_max = (
    benchmark_cumulative.cummax()
)

benchmark_drawdown = (
    benchmark_cumulative - benchmark_running_max
) / benchmark_running_max

benchmark_max_drawdown = benchmark_drawdown.min()

benchmark_annual_return = (
    benchmark_returns_aligned.mean() * 252
)

benchmark_annual_volatility = (
    benchmark_returns_aligned.std() * np.sqrt(252)
)

benchmark_sharpe = (
    (benchmark_annual_return - risk_free_rate)
    / benchmark_annual_volatility
)

# =========================
# TABELLA CONFRONTO
# =========================

comparison_df = pd.DataFrame({
    "Portafoglio": [
        portfolio_annual_return,
        portfolio_annual_volatility,
        portfolio_sharpe,
        portfolio_max_drawdown
    ],
    "Benchmark MSCI World": [
        benchmark_annual_return,
        benchmark_annual_volatility,
        benchmark_sharpe,
        benchmark_max_drawdown
    ]
},
index=[
    "Rendimento Annualizzato",
    "Volatilità Annualizzata",
    "Sharpe Ratio",
    "Max Drawdown"
])

# Conversione percentuali
comparison_df.loc[
    [
        "Rendimento Annualizzato",
        "Volatilità Annualizzata",
        "Max Drawdown"
    ]
] = (
    comparison_df.loc[
        [
            "Rendimento Annualizzato",
            "Volatilità Annualizzata",
            "Max Drawdown"
        ]
    ] * 100
)

# =========================
# STAMPA PROFESSIONALE CONFRONTO
# =========================
# %%
print("\n" + "="*60)
print("CONFRONTO PORTAFOGLIO vs BENCHMARK MSCI WORLD")
print("="*60)

print(f"{'Metrica':<30} {'Portafoglio':>15} {'Benchmark':>15}")

print("-"*60)

print(
    f"{'Rendimento Annualizzato':<30} "
    f"{portfolio_annual_return*100:>14.2f}% "
    f"{float(benchmark_annual_return.iloc[0])*100:>14.2f}%"
)

print(
    f"{'Volatilità Annualizzata':<30} "
    f"{portfolio_annual_volatility*100:>14.2f}% "
    f"{float(benchmark_annual_volatility.iloc[0])*100:>14.2f}%"
)

print(
    f"{'Sharpe Ratio':<30} "
    f"{portfolio_sharpe:>15.2f} "
    f"{float(benchmark_sharpe.iloc[0]):>15.2f}"
)

print(
    f"{'Max Drawdown':<30} "
    f"{portfolio_max_drawdown*100:>14.2f}% "
    f"{float(benchmark_max_drawdown.iloc[0])*100:>14.2f}%"
)

print("="*60)


####### 1. Max Drawdown
####### 2. VaR storico e parametrico
####### 3. Rolling volatility
####### 4. Efficient Frontier
####### 5. Benchmark comparison


# %%

#tracking error
#information ratio
#beta vs benchmark
#alpha
#rolling correlation
#rolling beta