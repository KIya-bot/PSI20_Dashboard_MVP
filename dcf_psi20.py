import yfinance as yf
import pandas as pd
import numpy as np


# ==============================
# CONFIGURAÇÕES GERAIS
# ==============================

RISK_FREE_RATE = 0.025        # 2.5% (Europa)
MARKET_RISK_PREMIUM = 0.055  # 5.5%
TERMINAL_GROWTH = 0.02       # crescimento de longo prazo (inflação)
PROJECTION_YEARS = 5

# PSI (tickers Yahoo Finance)
TICKERS = [
    "EDP.LS", "EDPR.LS", "GALP.LS", "BCP.LS", "JMT.LS",
    "NOS.LS", "SON.LS", "REN.LS", "CTT.LS", "ALTR.LS",
    "SEM.LS", "SCP.LS", "IBS.LS", "MOTA.LS", "NVG.LS",
    "VAF.LS", "IMP.LS", "COFINA.LS", "RAM.LS", "GLINT.LS"
]

# ==============================
# FUNÇÕES AUXILIARES
# ==============================

def calcular_cagr(valores):
    valores = valores.dropna()
    if len(valores) < 2 or valores.iloc[-1] <= 0:
        return None
    anos = len(valores) - 1
    return (valores.iloc[0] / valores.iloc[-1]) ** (1 / anos) - 1


def calcular_dcf(fcf_atual, crescimento, wacc):
    fcf_futuro = []
    for t in range(1, PROJECTION_YEARS + 1):
        fcf_futuro.append(fcf_atual * ((1 + crescimento) ** t))

    fcf_descontado = [
        fcf / ((1 + wacc) ** t)
        for t, fcf in enumerate(fcf_futuro, start=1)
    ]

    valor_terminal = (
        fcf_futuro[-1] * (1 + TERMINAL_GROWTH)
    ) / (wacc - TERMINAL_GROWTH)

    valor_terminal_descontado = valor_terminal / ((1 + wacc) ** PROJECTION_YEARS)

    return sum(fcf_descontado) + valor_terminal_descontado


# ==============================
# LOOP PRINCIPAL
# ==============================

resultados = []

for ticker in TICKERS:
    try:
        acao = yf.Ticker(ticker)
        info = acao.info

        preco_atual = info.get("currentPrice")
        shares = info.get("sharesOutstanding")
        beta = info.get("beta")

        if preco_atual is None or shares is None or beta is None:
            continue

        # Cost of Equity (WACC simplificado)
        wacc = RISK_FREE_RATE + beta * MARKET_RISK_PREMIUM

        # Free Cash Flow histórico
        cashflow = acao.cashflow
        if cashflow is None or "Free Cash Flow" not in cashflow.index:
            continue

        fcf_series = cashflow.loc["Free Cash Flow"]
        crescimento = calcular_cagr(fcf_series)

        if crescimento is None or crescimento <= -0.5:
            continue

        fcf_atual = fcf_series.iloc[0]

        # DCF
        enterprise_value = calcular_dcf(fcf_atual, crescimento, wacc)

        # Dívida e Caixa
        balance = acao.balance_sheet
        total_debt = balance.loc["Total Debt"].iloc[0] if "Total Debt" in balance.index else 0
        cash = balance.loc["Cash And Cash Equivalents"].iloc[0] if "Cash And Cash Equivalents" in balance.index else 0

        equity_value = enterprise_value - total_debt + cash
        preco_justo = equity_value / shares

        desconto = (preco_justo - preco_atual) / preco_atual * 100

        resultados.append({
            "Empresa": ticker,
            "Preço Atual (€)": round(preco_atual, 2),
            "Preço Justo DCF (€)": round(preco_justo, 2),
            "Desconto (%)": round(desconto, 2),
            "Crescimento FCF (%)": round(crescimento * 100, 2),
            "WACC (%)": round(wacc * 100, 2)
        })

    except Exception as e:
        continue

# ==============================
# RESULTADOS
# ==============================



# Normalização simples para score

df = pd.DataFrame(resultados)

# Normalização simples para score
df["Score Desconto"] = (df["Desconto (%)"] - df["Desconto (%)"].min()) / (df["Desconto (%)"].max() - df["Desconto (%)"].min())
df["Score Crescimento"] = (df["Crescimento FCF (%)"] - df["Crescimento FCF (%)"].min()) / (df["Crescimento FCF (%)"].max() - df["Crescimento FCF (%)"].min())
df["Score Risco"] = 1 - (df["WACC (%)"] - df["WACC (%)"].min()) / (df["WACC (%)"].max() - df["WACC (%)"].min())

df["Score Final"] = (
    0.5 * df["Score Desconto"] +
    0.3 * df["Score Crescimento"] +
    0.2 * df["Score Risco"]
)

df = df.sort_values(by="Score Final", ascending=False)

def gerar_analise(row):
    return (
        f"A empresa {row['Empresa']} apresenta um desconto de "
        f"{row['Desconto (%)']:.1f}% face ao valor justo estimado. "
        f"O crescimento histórico do Free Cash Flow é de "
        f"{row['Crescimento FCF (%)']:.1f}% ao ano, "
        f"com um custo de capital (WACC) de "
        f"{row['WACC (%)']:.1f}%. "
        f"Este conjunto de fatores justifica a sua posição no ranking."
    )

df["Análise Automática"] = df.apply(gerar_analise, axis=1)



df.to_excel("DCF_PSI_MVP.xlsx", index=False)

echo "# PSI20_Dashboard_MVP" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/KIya-bot/PSI20_Dashboard_MVP.git
git push -u origin main
