import streamlit as st
import pandas as pd

# Carrega os dados do Excel gerado pelo MVP
df = pd.read_excel("DCF_PSI_MVP.xlsx")

st.set_page_config(page_title="Dashboard DCF PSI-20", layout="wide")
st.title("📊 Dashboard DCF — Bolsa Portuguesa (PSI-20)")

# Sidebar — filtros
st.sidebar.header("Filtros")
desconto_min, desconto_max = st.sidebar.slider(
    "Desconto (%)", 
    float(df["Desconto (%)"].min()), 
    float(df["Desconto (%)"].max()), 
    (float(df["Desconto (%)"].min()), float(df["Desconto (%)"].max()))
)

crescimento_min, crescimento_max = st.sidebar.slider(
    "Crescimento FCF (%)",
    float(df["Crescimento FCF (%)"].min()),
    float(df["Crescimento FCF (%)"].max()),
    (float(df["Crescimento FCF (%)"].min()), float(df["Crescimento FCF (%)"].max()))
)

# Filtra DataFrame
df_filtrado = df[
    (df["Desconto (%)"] >= desconto_min) & (df["Desconto (%)"] <= desconto_max) &
    (df["Crescimento FCF (%)"] >= crescimento_min) & (df["Crescimento FCF (%)"] <= crescimento_max)
]

# Mostra tabela
st.subheader("Ranking das Empresas")
st.dataframe(df_filtrado)

# Mostra análise detalhada
st.subheader("Análises Automáticas / GPT")
empresa_selecionada = st.selectbox("Escolhe uma empresa:", df_filtrado["Empresa"].tolist())
analise_texto = df_filtrado[df_filtrado["Empresa"] == empresa_selecionada]["Análise GPT"].values[0]
st.write(analise_texto)
