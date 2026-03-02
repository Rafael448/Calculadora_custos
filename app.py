import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="Gestão de Safra - Nova Resende", layout="centered")

# --- FUNÇÃO PARA GERAR PDF ATUALIZADA ---
def gerar_pdf(dados, total, custo_saca, preco_venda, lucro_real, nome_safra):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, f"Relatorio de Custos: {nome_safra}", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "Descricao", border=1)
    pdf.cell(90, 10, "Valor (R$)", border=1, ln=True)
    
    pdf.set_font("Arial", "", 12)
    for item in dados:
        v_f = f"{item['Valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pdf.cell(100, 10, item['Descrição'], border=1)
        pdf.cell(90, 10, f"R$ {v_f}", border=1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    t_f = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    pdf.cell(190, 10, f"CUSTO TOTAL DA PRODUCAO: R$ {t_f}", ln=True)
    
    if custo_saca > 0:
        cs_f = f"{custo_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pv_f = f"{preco_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pdf.cell(190, 10, f"PRECO PARA COBRIR CUSTOS (Empate): R$ {cs_f}", ln=True)
        pdf.cell(190, 10, f"PRECO ALVO PARA VENDA (Com Lucro): R$ {pv_f}", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

st.title("☕ Gestor de Custos de Café")

# Identificação da Safra
nome_safra = st.text_input("Identificação da Safra:", value="Safra 2026")

if 'meus_custos' not in st.session_state:
    st.session_state.meus_custos = []

# --- ÁREA DE LANÇAMENTO ---
with st.form("formulario_gasto", clear_on_submit=True):
    st.write("➕ **Lançar Novo Gasto**")
    col1, col2 = st.columns(2)
    with col1:
        descricao = st.text_input("O que comprou?")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=50.0, value=None)
    
    if st.form_submit_button("Salvar Gasto"):
        if descricao and valor:
            st.session_state.meus_custos.append({"Descrição": descricao, "Valor": valor})
            st.rerun()

# --- TABELA, EXCLUSÃO E GRÁFICO ---
if st.session_state.meus_custos:
    df = pd.DataFrame(st.session_state.meus_custos)
    st.write(f"### 📋 Lançamentos: {nome_safra}")
    
    df_visual = df.copy()
    df_visual["Valor"] = df_visual["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.table(df_visual)
    
    with st.expander("🗑️ Excluir um lançamento errado"):
        opcoes = [f"{i} - {item['Descrição']} (R$ {item['Valor']})" for i, item in enumerate(st.session_state.meus_custos)]
        item_para_excluir = st.selectbox("Selecione o item para apagar:", opcoes)
        if st.button("Confirmar Exclusão"):
            indice = int(item_para_excluir.split(" - ")[0])
            st.session_state.meus_custos.pop(indice)
            st.rerun()

    total_acumulado = df["Valor"].sum()
    t_f = f"R$ {total_acumulado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Destaque para o Custo Total
    st.warning(f"💰 **CUSTO TOTAL DA OPERAÇÃO:** {t_f}")

    # Gráfico
    fig = px.pie(df, values='Valor', names='Descrição', hole=0.3, title="Distribuição Financeira")
    st.plotly_chart(fig, use_container_width=True)

    # --- ANÁLISE DE PREÇO ---
    st.divider()
    st.write("### 🧮 Cálculo de Preço de Venda")
    
    col_a, col_b = st.columns(2)
    with col_a:
        sacas = st.number_input("Total de Sacas colhidas:", min_value=1, value=None)
    with col_b:
        lucro_por_saca = st.number_input("Lucro limpo por saca (R$):", min_value=0.0, value=200.0)

    if sacas:
        custo_por_saca = total_acumulado / sacas
        preco_alvo = custo_por_saca + lucro_por_saca
        
        c_s_f = f"R$ {custo_por_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        p_a_f = f"R$ {preco_alvo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        st.error(f"⚠️ **PREÇO DE COBERTURA (Mínimo):** {c_s_f}")
        st.write("*(Abaixo disso, você terá prejuízo)*")
        
        st.success(f"✅ **PREÇO ALVO (Com Lucro):** {p_a_f}")
        st.write(f"*(Preço ideal para cobrir os custos e te sobrar R$ {lucro_por_saca:,.2f} por saca)*")

        # --- EXPORTAÇÃO PDF ---
        pdf_bytes = gerar_pdf(st.session_state.meus_custos, total_acumulado, custo_por_saca, preco_alvo, lucro_por_saca, nome_safra)
        st.download_button(label="📄 Baixar Relatório PDF", data=pdf_bytes, file_name=f"safra_{nome_safra}.pdf", mime="application/pdf")

    if st.button("Limpar Safra"):
        st.session_state.meus_custos = []
        st.rerun()
else:
    st.info("Nenhum gasto lançado ainda.")
