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
        # Usamos uma 'key' dinâmica para facilitar o reset
        descricao = st.text_input("O que comprou? (ex: Adubo, Diesel)", key="desc_input")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=50.0, value=None, format="%.2f", key="val_input")
    
    if st.button("Salvar Gasto"):
        if descricao and valor:
            # Salva o dado na lista
            st.session_state.meus_custos.append({"Descrição": descricao, "Valor": valor})
            st.success(f"Registrado: {descricao}")
            # O comando rerun limpa os campos automaticamente devido ao value=None e à lógica do Streamlit
            st.rerun()
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
    
    sacas = st.number_input("Quantas sacas você colheu no total?", min_value=1, value=None, key="sacas_input")

    if st.button("CALCULAR CUSTO POR SACA"):
        if sacas:
            custo_saca = total_acumulado / sacas
            custo_formatado = f"R$ {custo_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric(label="Custo Real por Saca", value=custo_formatado)
            
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
