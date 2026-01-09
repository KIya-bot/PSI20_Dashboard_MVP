# dashboard_mvp.py - PSI20 MVP em tempo real com delay
import yfinance as yf
import pandas as pd
import streamlit as st
import time

# -----------------------------
# Configurações da página
# -----------------------------
st.set_page_config(page_title="Dashboard PSI-20", layout="wide")
st.title("📊 Dashboard PSI-20 - DCF em Tempo Real")

# -----------------------------
# Lista de empresas e tickers
# -----------------------------
tickers = {
    "EDP": "EDP.LS",
    "GALP": "GALP.LS",
    "BCP": "BCP.LS",
    "REN": "REN.LS",
    "MOTA": "MOTA.LS",
    "CTT": "CTT.LS",
    "SONAE": "SON.LS",
    "SONAE SGPS": "SONA.LS",
    "THE NAVIGATOR": "NVG.LS",
    "CUF": "CUF.LS",
    "NOS": "NOS.LS",
    "CINF": "CINF.LS",
    "IMOP": "IMP.LS",
    "COFINA": "COFI.LS",
    "JERONIMO": "JER.LS",
    "BES": "BES.LS",
    "EDPR": "EDPR.LS",
    "RENOVA": "RNVA.LS",
    "EURONEXT": "ENX.LS"
}

# -----------------------------
# Função para puxar dados (com delay)
# -----------------------------
def pegar_dados(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y")
        preco_atual = hist["Close"].iloc[-1]
        receita = t.info.get("totalRevenue", None)
        lucro = t.info.get("netIncomeToCommon", None)
        dcf = lucro * 10 if lucro else None
        desconto = ((dcf - preco_atual)/preco_atual*100) if dcf else None
        time.sleep(1.5)  # Delay para evitar rate limit
        return preco_atual, receita, lucro, dcf, desconto
    except Exception as e:
        st.warning(f"Erro ao puxar dados de {ticker}: {e}")
        return None, None, None, None, None

# -----------------------------
# Puxar dados para todas as empresas
# -----------------------------
data_list = []
for empresa, ticker in tickers.items():
    preco_atual, receita, lucro, dcf, desconto = pegar_dados(ticker)
    data_list.append({
        "Empresa": empresa,
        "Ticker": ticker,
        "Preço Atual (€)": preco_atual,
        "Receita (€)": receita,
        "Lucro (€)": lucro,
        "DCF Estimado (€)": dcf,
        "Desconto (%)": desconto
    })

# -----------------------------
# Criar DataFrame e ranking
# -----------------------------
df = pd.DataFrame(data_list)
df_sorted = df.sort_values(by="Desconto (%)", ascending=False)

# -----------------------------
# Mostrar tabela ranking
# -----------------------------
st.subheader("Ranking por Desconto (%)")
st.dataframe(df_sorted.style.format({"Desconto (%)": "{:.2f}"}))

# -----------------------------
# Seleção de empresa para detalhes
# -----------------------------
empresa_selecionada = st.selectbox("Escolhe uma empresa:", df["Empresa"].tolist())
detalhes = df[df["Empresa"] == empresa_selecionada].iloc[0]

st.subheader(f"Detalhes de {empresa_selecionada}")
st.write(f"**Preço Atual:** €{detalhes['Preço Atual (€)']:.2f}" if detalhes['Preço Atual (€)'] else "N/A")
st.write(f"**DCF Estimado:** €{detalhes['DCF Estimado (€)']:.2f}" if detalhes['DCF Estimado (€)'] else "N/A")
st.write(f"**Desconto:** {detalhes['Desconto (%)']:.2f}%" if detalhes['Desconto (%)'] else "N/A")
st.write(f"**Receita:** €{detalhes['Receita (€)']}" if detalhes['Receita (€)'] else "N/A")
st.write(f"**Lucro:** €{detalhes['Lucro (€)']}" if detalhes['Lucro (€)'] else "N/A")
