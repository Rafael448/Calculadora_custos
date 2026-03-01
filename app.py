import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão de Safra - Nova Resende", layout="centered")

st.title("☕ Gestor de Custos de Café")
st.subheader("Vá lançando seus custos durante a safra")

# Criar um banco de dados temporário na memória
if 'meus_custos' not in st.session_state:
    st.session_state.meus_custos = []

# --- ÁREA DE LANÇAMENTO ---
with st.expander("➕ Lançar Novo Gasto", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        descricao = st.text_input("O que comprou? (ex: Adubo, Diesel)")
    with col2:
        # value=None deixa o campo vazio inicialmente
        valor = st.number_input("Valor (R$)", min_value=0.0, step=50.0, value=None, format="%.2f")
    
    if st.button("Salvar Gasto"):
        # Verifica se tem descrição e se o valor foi preenchido
        if descricao and valor:
            st.session_state.meus_custos.append({"Descrição": descricao, "Valor": valor})
            st.success(f"Registrado: {descricao}")
        else:
            st.warning("Por favor, preencha a descrição e o valor.")

# --- TABELA DE GASTOS ---
if st.session_state.meus_custos:
    st.write("### 📋 Seus Lançamentos")
    
    df = pd.DataFrame(st.session_state.meus_custos)
    
    # --- FORMATAÇÃO VISUAL (R$ 1.000,00) ---
    df_visual = df.copy()
    df_visual["Valor"] = df_visual["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    st.table(df_visual)
    
    # Cálculo do total
    total_acumulado = df["Valor"].sum()
    total_formatado = f"R$ {total_acumulado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    st.info(f"**Gasto Acumulado até agora:** {total_formatado}")

    # --- ÁREA DE CÁLCULO FINAL ---
    st.divider()
    st.write("### 🧮 Fechamento da Safra")
    
    # Campo de sacas também começa vazio para facilitar
    sacas = st.number_input("Quantas sacas você colheu no total?", min_value=1, value=None)

    if st.button("CALCULAR CUSTO POR SACA"):
        if sacas:
            custo_saca = total_acumulado / sacas
            
            custo_formatado = f"R$ {custo_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric(label="Custo Real por Saca", value=custo_formatado)
            
            # Mensagem simples sem balões
            if custo_saca < 1000:
                st.success("Excelente! Seu custo está competitivo.")
            else:
                st.warning("Atenção ao custo! Tente negociar melhor na próxima.")
        else:
            st.error("Digite a quantidade de sacas para calcular.")

    if st.button("Limpar Tudo (Nova Safra)"):
        st.session_state.meus_custos = []
        st.rerun()

else:
    st.info("Nenhum gasto lançado ainda.")
