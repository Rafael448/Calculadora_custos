import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

st.set_page_config(page_title="Gestão de Safra - Nova Resende", layout="centered")

# --- FUNÇÃO PARA GERAR PDF ATUALIZADA ---
def gerar_pdf(dados, total, custo_saca, preco_venda, margem, nome_safra):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    # O título agora usa o nome que você escolheu [cite: 2026-03-01]
    pdf.cell(190, 10, f"Relatório de Custos: {nome_safra}", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 10, "Descrição", border=1)
    pdf.cell(90, 10, "Valor (R$)", border=1, ln=True)
    
    pdf.set_font("Arial", "", 12)
    for item in dados:
        v_f = f"{item['Valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pdf.cell(100, 10, item['Descrição'], border=1)
        pdf.cell(90, 10, f"R$ {v_f}", border=1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    t_f = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    pdf.cell(190, 10, f"Gasto Total Acumulado: R$ {t_f}", ln=True)
    
    if custo_saca > 0:
        cs_f = f"{custo_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pv_f = f"{preco_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pdf.cell(190, 10, f"Custo por Saca: R$ {cs_f}", ln=True)
        pdf.cell(190, 10, f"Meta de Venda ({margem}% lucro): R$ {pv_f}", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

st.title("☕ Gestor de Custos de Café")

# --- NOVO: CAMPO PARA NOME DA SAFRA ---
nome_safra = st.text_input("Identificação da Safra:", value="Safra 2026", help="Ex: Safra 2026, Talhão da Represa, Café Especial, etc.")
st.subheader(f"Lançamentos: {nome_safra}")

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

# --- TABELA E GRÁFICO ---
if st.session_state.meus_custos:
    df = pd.DataFrame(st.session_state.meus_custos)
    st.write("### 📋 Seus Lançamentos")
    st.table(df.assign(Valor=df["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))))
    
    fig = px.pie(df, values='Valor', names='Descrição', hole=0.3, title=f"Divisão de Custos - {nome_safra}")
    st.plotly_chart(fig, use_container_width=True)
    
    total_acumulado = df["Valor"].sum()

    # --- ESTRATÉGIA E EXPORTAÇÃO ---
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        sacas = st.number_input("Sacas colhidas:", min_value=1, value=None)
    with col_b:
        margem = st.number_input("Margem de Lucro desejada (%):", min_value=0, value=20)

    custo_saca = 0
    preco_venda = 0
    if sacas:
        custo_saca = total_acumulado / sacas
        preco_venda = custo_saca * (1 + (margem / 100))
        st.metric("Custo/Saca", f"R$ {custo_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.metric(f"Venda ({margem}% Lucro)", f"R$ {preco_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # --- BOTÃO PDF COM NOME DINÂMICO ---
    # O arquivo baixado agora terá o nome da safra [cite: 2026-03-01]
    pdf_bytes = gerar_pdf(st.session_state.meus_custos, total_acumulado, custo_saca, preco_venda, margem, nome_safra)
    nome_arquivo = f"relatorio_{nome_safra.lower().replace(' ', '_')}.pdf"
    
    st.download_button(
        label="📄 Baixar Relatório em PDF", 
        data=pdf_bytes, 
        file_name=nome_arquivo, 
        mime="application/pdf"
    )

    if st.button("Limpar Safra"):
        st.session_state.meus_custos = []
        st.rerun()
else:
    st.info("Nenhum gasto lançado ainda.")
