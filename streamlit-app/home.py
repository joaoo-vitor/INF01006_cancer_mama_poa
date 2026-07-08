import streamlit as st
from plots import (
    plot_chemotherapies_by_month_altair,
    plot_chemo_stage_comparison_altair,
    plot_distribuicao_permanencia,
    plot_hospitalizacoes_por_cid_altair
)

# Helper function to generate KPI cards
def make_kpi_card(title, value, subtitle="", border_color="#d63384"):
    return f"""
    <div class="kpi-card" style="border-left: 5px solid {border_color}; font-family: 'Inter', sans-serif;">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """

def render_home_page(df_aq, df_ar, df_rd, data_raw, selected_city, selected_months, theme_color, disease):
    st.markdown(f'<div class="section-title">📊 Visão Geral - {disease} ({selected_city})</div>', unsafe_allow_html=True)
    
    # Calcular métricas para os KPIs
    total_chemo = len(df_aq)
    total_radio = len(df_ar)
    total_hosp = len(df_rd)
    avg_stay = df_rd['DIAS_PERM'].mean() if total_hosp > 0 else 0
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(make_kpi_card("Sessões de Quimioterapia", f"{total_chemo:,}".replace(',', '.'), "Registros SIA/SUS", theme_color), unsafe_allow_html=True)
    with col2:
        st.markdown(make_kpi_card("Sessões de Radioterapia", f"{total_radio:,}".replace(',', '.'), "Registros SIA/SUS", theme_color), unsafe_allow_html=True)
    with col3:
        st.markdown(make_kpi_card("Internações Hospitalares", f"{total_hosp:,}".replace(',', '.'), "Registros SIH/SUS", theme_color), unsafe_allow_html=True)
    with col4:
        st.markdown(make_kpi_card("Média de Permanência", f"{avg_stay:.1f} dias", "Tempo de Internação Médio", theme_color), unsafe_allow_html=True)
        
    st.markdown('<div class="section-title">📈 Evolução Mensal e Estadiamento Clínico</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        chart_monthly = plot_chemotherapies_by_month_altair(data_raw[f"aq_{'mama' if disease == 'Câncer de Mama' else 'colo'}"], selected_city, selected_months, theme_color)
        st.altair_chart(chart_monthly, use_container_width=True)
    with c2:
        chart_stages = plot_chemo_stage_comparison_altair(data_raw['aq_colo'], data_raw['aq_mama'], selected_city, selected_months)
        col_l, col_c, col_r = st.columns([1, 5, 1])
        with col_c:
            st.altair_chart(chart_stages, use_container_width=False)
        
    st.markdown('<div class="section-title">🏥 Tempo de Permanência Hospitalar por CID (SIH/SUS)</div>', unsafe_allow_html=True)
    
    if not df_rd.empty:
        chart_permanencia = plot_distribuicao_permanencia(data_raw[f"rd_{'mama' if disease == 'Câncer de Mama' else 'colo'}"], disease.replace("Câncer de ", ""), selected_city, selected_months)
        st.altair_chart(chart_permanencia, use_container_width=True)
    else:
        st.info("Nenhuma internação registrada para os filtros selecionados.")
        
    st.markdown('<div class="section-title">📊 Distribuição de Internações por CID (SIH/SUS)</div>', unsafe_allow_html=True)
    
    if not df_rd.empty:
        chart_pie = plot_hospitalizacoes_por_cid_altair(data_raw[f"rd_{'mama' if disease == 'Câncer de Mama' else 'colo'}"], disease.replace("Câncer de ", ""), selected_city, selected_months)
        st.altair_chart(chart_pie)
    else:
        st.info("Nenhuma internação registrada para os filtros selecionados.")
