import streamlit as st
import pandas as pd
import altair as alt
from plots import plot_custos_hospitalares

COLOR_MAMA = '#d63384'
COLOR_COLO = '#008080'

# Helper function to generate KPI cards
def make_kpi_card(title, value, subtitle="", border_color="#d63384"):
    return f"""
    <div class="kpi-card" style="border-left: 5px solid {border_color}; font-family: 'Inter', sans-serif;">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """

def render_financial_page(data_raw, filter_sia_func, filter_sih_func, selected_city, selected_months):
    st.markdown(f'<div class="section-title">💸 Gastos e Recursos Financeiros em {selected_city}</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-alert" style="background-color: #e3f2fd; border-left: 4px solid #1976d2; color: #0d47a1;">
        ℹ️ <b>Nota Comparativa:</b> Esta seção analisa e compara os custos de ambos os cânceres simultaneamente. 
        O filtro de "Tipo de Câncer" da barra lateral <b>não se aplica</b> a esta aba.
    </div>
    """, unsafe_allow_html=True)
    
    # Filtrar dados para ambos os cânceres
    df_aq_colo_f = filter_sia_func(data_raw['aq_colo'], selected_city, selected_months)
    df_aq_mama_f = filter_sia_func(data_raw['aq_mama'], selected_city, selected_months)
    
    df_ar_colo_f = filter_sia_func(data_raw['ar_colo'], selected_city, selected_months)
    df_ar_mama_f = filter_sia_func(data_raw['ar_mama'], selected_city, selected_months)
    
    df_rd_colo_f = filter_sih_func(data_raw['rd_colo'], selected_city, selected_months)
    df_rd_mama_f = filter_sih_func(data_raw['rd_mama'], selected_city, selected_months)
    
    # Calcular spends
    spend_chemo_colo = df_aq_colo_f['AP_VL_AP'].sum() if 'AP_VL_AP' in df_aq_colo_f.columns else 0
    spend_chemo_mama = df_aq_mama_f['AP_VL_AP'].sum() if 'AP_VL_AP' in df_aq_mama_f.columns else 0
    
    spend_radio_colo = df_ar_colo_f['AP_VL_AP'].sum() if 'AP_VL_AP' in df_ar_colo_f.columns else 0
    spend_radio_mama = df_ar_mama_f['AP_VL_AP'].sum() if 'AP_VL_AP' in df_ar_mama_f.columns else 0
    
    spend_hosp_colo = df_rd_colo_f['VAL_TOT'].sum() if 'VAL_TOT' in df_rd_colo_f.columns else 0
    spend_hosp_mama = df_rd_mama_f['VAL_TOT'].sum() if 'VAL_TOT' in df_rd_mama_f.columns else 0
    
    total_colo_spend = spend_chemo_colo + spend_radio_colo + spend_hosp_colo
    total_mama_spend = spend_chemo_mama + spend_radio_mama + spend_hosp_mama
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown(make_kpi_card("Câncer de Colo de Útero (Total)", f"R$ {total_colo_spend:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), "Custo total (Quimioterapia + Radioterapia + Internação)", COLOR_COLO), unsafe_allow_html=True)
    with col_f2:
        st.markdown(make_kpi_card("Câncer de Mama (Total)", f"R$ {total_mama_spend:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), "Custo total (Quimioterapia + Radioterapia + Internação)", COLOR_MAMA), unsafe_allow_html=True)
        
    st.markdown('<div class="section-title">📊 Despesas Acumuladas por Modalidade de Atendimento</div>', unsafe_allow_html=True)
    
    # DataFrame comparativo de tipo de custo
    spend_compare_df = pd.DataFrame([
        {"Câncer": "Colo de Útero", "Tipo": "Quimioterapia", "Valor": spend_chemo_colo},
        {"Câncer": "Colo de Útero", "Tipo": "Radioterapia", "Valor": spend_radio_colo},
        {"Câncer": "Colo de Útero", "Tipo": "Internação Hospitalar", "Valor": spend_hosp_colo},
        {"Câncer": "Câncer de Mama", "Tipo": "Quimioterapia", "Valor": spend_chemo_mama},
        {"Câncer": "Câncer de Mama", "Tipo": "Radioterapia", "Valor": spend_radio_mama},
        {"Câncer": "Câncer de Mama", "Tipo": "Internação Hospitalar", "Valor": spend_hosp_mama},
    ])
    
    chart_spend_split = alt.Chart(spend_compare_df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('Tipo:N', title='Tipo de Atendimento'),
        y=alt.Y('Valor:Q', title='Custo Acumulado (R$)'),
        color=alt.Color('Câncer:N', scale=alt.Scale(domain=['Colo de Útero', 'Câncer de Mama'], range=[COLOR_COLO, COLOR_MAMA])),
        xOffset='Câncer:N',
        tooltip=[alt.Tooltip('Câncer:N'), alt.Tooltip('Tipo:N'), alt.Tooltip('Valor:Q', title='Total (R$)', format=',.2f')]
    ).properties(
        width='container',
        height=350
    )
    st.altair_chart(chart_spend_split, use_container_width=True)
    
    st.markdown('<div class="section-title">🏥 Detalhamento de Custos Hospitalares Internos (VAL_SH vs. VAL_SP)</div>', unsafe_allow_html=True)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        # Passa o df bruto, a filtragem é interna
        chart_h_colo = plot_custos_hospitalares(data_raw['rd_colo'], "Colo de Útero", selected_city, selected_months)
        st.altair_chart(chart_h_colo, use_container_width=True)
    with col_c2:
        # Passa o df bruto, a filtragem é interna
        chart_h_mama = plot_custos_hospitalares(data_raw['rd_mama'], "Mama", selected_city, selected_months)
        st.altair_chart(chart_h_mama, use_container_width=True)
