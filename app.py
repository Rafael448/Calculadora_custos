import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão de Safra - Nova Resende", layout="centered")

st.title("☕ Gestor de Custos de Café")
st.subheader("Vá lançando seus custos durante a safra")

# Criar um banco de dados temporário na memória do navegador
if 'meus_custos' not in st.session_state:
    st.session_state.meus_custos = []

# --- ÁREA DE LANÇAMENTO ---
with st.expander("➕ Lançar Novo Gasto", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        descricao = st.text_input("O que comprou? (ex: Adubo, Diesel)")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=50.0)
    
    if st.button("Salvar Gasto"):
        if descricao and valor > 0:
            st.session_state.meus_custos.append({"Descrição": descricao, "Valor": valor})
            st.success(f"Registrado: {descricao}")

# --- TABELA DE GASTOS ---
if st.session_state.meus_custos:
    st.write("### 📋 Seus Lançamentos")
    
    # Cria uma tabela (DataFrame) com os dados
    df = pd.DataFrame(st.session_state.meus_custos)
    
    # --- TRUQUE DE FORMATAÇÃO BRASILEIRA ---
    # Criamos uma cópia para não atrapalhar a conta matemática depois
    df_visual = df.copy()
    
    # Aplica a formatação: R$ 1.000,00
    df_visual["Valor"] = df_visual["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    # Mostra a tabela bonitinha
    st.table(df_visual)
    
    # Calcula o total matemático (usando a tabela original 'df', não a visual)
    total_acumulado = df["Valor"].sum()
    
    # Formata o total também para ficar bonito na caixa azul
    total_formatado = f"R$ {total_acumulado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.info(f"**Gasto Acumulado até agora:** {total_formatado}")

    # --- ÁREA DE CÁLCULO FINAL ---
    st.divider()
    st.write("### 🧮 Fechamento da Safra")
    sacas = st.number_input("Quantas sacas você colheu no total?", min_value=1)

    if st.button("CALCULAR CUSTO POR SACA"):
        custo_saca = total_acumulado / sacas
        
        # Formata o resultado final
        custo_formatado = f"R$ {custo_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        st.metric(label="Custo Real por Saca", value=custo_formatado)
        
        if custo_saca < 1000:
            st.balloons()
            st.success("Excelente! Seu custo está muito competitivo.")
        else:
            st.warning("Atenção ao custo! Tente negociar melhor os próximos insumos.")

    if st.button("Limpar Tudo (Nova Safra)"):
        st.session_state.meus_custos = []
        st.rerun()
else:
    st.info("Nenhum gasto lançado ainda. Use o formulário acima para começar.")
