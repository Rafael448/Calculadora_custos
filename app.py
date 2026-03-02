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
    pdf.cell(190, 10, f"Gasto Total Acumulado: R$ {t_f}", ln=True)
    
    if custo_saca > 0:
        cs_f = f"{custo_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        lr_f = f"{lucro_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pv_f = f"{preco_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pdf.cell(190, 10, f"Custo por Saca: R$ {cs_f}", ln=True)
        pdf.cell(190, 10, f"Lucro Desejado por Saca: R$ {lr_f}", ln=True)
        pdf.cell(190, 10, f"Preco Alvo de Venda: R$ {pv_f}", ln=True)
    
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
    
    # Tabela visual formatada
    df_visual = df.copy()
    df_visual["Valor"] = df_visual["Valor"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.table(df_visual)
    
    # BOTÃO DE EXCLUIR (RESTAURADO)
    with st.expander("🗑️ Excluir um lançamento errado"):
        opcoes = [f"{i} - {item['Descrição']} (R$ {item['Valor']})" for i, item in enumerate(st.session_state.meus_custos)]
        item_para_excluir = st.selectbox("Selecione o item para apagar:", opcoes)
        if st.button("Confirmar Exclusão"):
            indice = int(item_para_excluir.split(" - ")[0])
            st.session_state.meus_custos.pop(indice)
            st.rerun()

    # Gráfico
    fig = px.pie(df, values='Valor', names='Descrição', hole=0.3, title="Distribuição de Gastos")
    st.plotly_chart(fig, use_container_width=True)
    
    total_acumulado = df["Valor"].sum()

    # --- NOVA ESTRATÉGIA DE LUCRO (R$ POR SACA) ---
    st.divider()
    st.write("### 🎯 Meta de Venda")
    
    col_a, col_b = st.columns(2)
    with col_a:
        sacas = st.number_input("Sacas colhidas:", min_value=1, value=None)
    with col_b:
        lucro_por_saca = st.number_input("Lucro desejado POR SACA (R$):", min_value=0.0, value=200.0, step=10.0)

    custo_saca = 0
    preco_venda = 0
    if sacas:
        custo_saca = total_acumulado / sacas
        # Nova Lógica: Preço de Venda = Custo + Lucro fixo desejado
        preco_venda = custo_saca + lucro_por_saca
        
        c_f = f"R$ {custo_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        v_f = f"R$ {preco_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        l_f = f"R$ {lucro_por_saca:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        st.metric("Seu Custo por Saca", c_f)
        st.metric(f"Preço para lucrar {l_f}/saca", v_f)
        st.write(f"ℹ️ *Para ganhar {l_f} limpo em cada saca, você deve vender a {v_f}.*")

    # --- EXPORTAÇÃO PDF ---
    pdf_bytes = gerar_pdf(st.session_state.meus_custos, total_acumulado, custo_saca, preco_venda, lucro_por_saca, nome_safra)
    nome_arq = f"relatorio_{nome_safra.lower().replace(' ', '_')}.pdf"
    
    st.download_button(label="📄 Baixar Relatório PDF", data=pdf_bytes, file_name=nome_arq, mime="application/pdf")

    if st.button("Limpar Safra"):
        st.session_state.meus_custos = []
        st.rerun()
else:
    st.info("Nenhum gasto lançado ainda.")
