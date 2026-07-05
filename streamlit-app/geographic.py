import streamlit as st
import pandas as pd
import altair as alt
from plots import plot_residents_vs_non_residents_altair

def render_geographic_page(data_raw, filter_sia_func, filter_sih_func, selected_months, theme_color, disease, RS_CITY_COORDS):
    st.markdown(f'<div class="section-title">🗺️ Volume e Fluxo de Atendimentos no Rio Grande do Sul - {disease}</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-alert" style="background-color: #fff3e0; border-left: 4px solid #f57c00; color: #e65100;">
        🗺️ <b>Análise Estadual Geral:</b> Esta seção analisa a distribuição de atendimentos em todo o estado. 
        O filtro de "Município" da barra lateral <b>não se aplica</b> a esta aba (exibe todos os municípios de RS no mapa).
    </div>
    """, unsafe_allow_html=True)
    
    disease_suffix = "mama" if disease == "Câncer de Mama" else "colo"
    df_aq = data_raw[f'aq_{disease_suffix}']
    df_ar = data_raw[f'ar_{disease_suffix}']
    df_rd = data_raw[f'rd_{disease_suffix}']
    
    # Filtrar apenas por período (município sempre "Todo o Estado")
    df_aq_f = filter_sia_func(df_aq, None, selected_months)
    df_ar_f = filter_sia_func(df_ar, None, selected_months)
    df_rd_f = filter_sih_func(df_rd, None, selected_months)
    
    map_metric = st.selectbox(
        "Métrica do Mapa de Atendimentos:",
        ["Quimioterapia (SIA)", "Radioterapia (SIA)", "Internações (SIH)"]
    )
    
    # Montar contagem por município prestador
    map_df = pd.DataFrame()
    if map_metric == "Quimioterapia (SIA)" and not df_aq_f.empty:
        city_counts = df_aq_f['AP_UFMUN'].dropna().value_counts().reset_index()
        city_counts.columns = ['municipio', 'quantidade']
    elif map_metric == "Radioterapia (SIA)" and not df_ar_f.empty:
        city_counts = df_ar_f['AP_UFMUN'].dropna().value_counts().reset_index()
        city_counts.columns = ['municipio', 'quantidade']
    elif not df_rd_f.empty:
        city_counts = df_rd_f['MUNIC_MOV'].dropna().value_counts().reset_index()
        city_counts.columns = ['municipio', 'quantidade']
    else:
        city_counts = pd.DataFrame(columns=['municipio', 'quantidade'])
        
    if not city_counts.empty:
        lats, lons, quants, names = [], [], [], []
        for _, row in city_counts.iterrows():
            m_key = str(row['municipio']).lower().strip()
            if m_key in RS_CITY_COORDS:
                coords = RS_CITY_COORDS[m_key]
                lats.append(coords[0])
                lons.append(coords[1])
                quants.append(row['quantidade'])
                names.append(str(row['municipio']).title())
                
        map_df = pd.DataFrame({
            'lat': lats,
            'lon': lons,
            'quantidade': quants,
            'municipio': names
        })
        
    st.markdown('<div class="section-title">📍 Concentração Geográfica dos Atendimentos Oncológicos</div>', unsafe_allow_html=True)
    if not map_df.empty:
        max_q = map_df['quantidade'].max()
        map_df['tamanho'] = map_df['quantidade'].apply(lambda x: 10 + (x / max_q) * 200)
        
        # Mapa
        st.map(map_df, latitude='lat', longitude='lon', size='tamanho', color=theme_color)
        
        # Tabela ordenada
        st.dataframe(
            map_df[['municipio', 'quantidade']].sort_values(by='quantidade', ascending=False),
            column_config={
                "municipio": "Município Executor do Tratamento",
                "quantidade": st.column_config.NumberColumn("Total de Procedimentos", format="%d")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Sem dados de geolocalização no período selecionado.")
        
    # Centralização e Fluxo na Capital (Porto Alegre)
    st.markdown('<div class="section-title">✈️ Fluxo Migratório Hospitalar (Interior ➔ Porto Alegre)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-alert" style="background-color: #e8f5e9; border-left: 4px solid #4caf50; color: #1b5e20;">
        📈 <b>Centralização dos Tratamentos:</b> Por concentrar os principais centros de referência oncológica do estado, 
        a capital (Porto Alegre) atende uma quantidade massiva de pacientes residentes em outros municípios gaúchos.
    </div>
    """, unsafe_allow_html=True)
    
    col_geo1, col_geo2 = st.columns(2)
    with col_geo1:
        # Passa o df bruto, a filtragem é interna
        chart_res_chemo = plot_residents_vs_non_residents_altair(df_aq, "Quimioterapia", "Porto Alegre", selected_months)
        st.altair_chart(chart_res_chemo, use_container_width=True)
    with col_geo2:
        # Passa o df bruto, a filtragem é interna
        chart_res_radio = plot_residents_vs_non_residents_altair(df_ar, "Radioterapia", "Porto Alegre", selected_months)
        st.altair_chart(chart_res_radio, use_container_width=True)
