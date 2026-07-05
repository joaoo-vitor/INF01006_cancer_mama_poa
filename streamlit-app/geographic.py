import streamlit as st
import pandas as pd
import altair as alt
import json
import urllib.request
import unicodedata
import copy
from plots import plot_residents_vs_non_residents_altair

@st.cache_data
def load_rs_geojson():
    url = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-43-mun.json"
    try:
        with urllib.request.urlopen(url) as response:
            geojson = json.loads(response.read().decode('utf-8', errors='ignore'))
        return geojson
    except Exception as e:
        st.error(f"Erro ao carregar o mapa de municípios do Rio Grande do Sul: {e}")
        return None

def normalize_name(name):
    if not name:
        return ""
    n = str(name).lower().strip()
    # Normalize unicode to strip accents
    n = ''.join(c for c in unicodedata.normalize('NFD', n) if unicodedata.category(c) != 'Mn')
    # Replace common spelling anomalies
    n = n.replace('-', ' ').replace("'", "")
    return n

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
    
    # Calcular contagens por município prestador
    counts = {}
    if map_metric == "Quimioterapia (SIA)" and not df_aq_f.empty:
        counts = df_aq_f['AP_UFMUN'].dropna().astype(str).apply(normalize_name).value_counts().to_dict()
    elif map_metric == "Radioterapia (SIA)" and not df_ar_f.empty:
        counts = df_ar_f['AP_UFMUN'].dropna().astype(str).apply(normalize_name).value_counts().to_dict()
    elif not df_rd_f.empty:
        counts = df_rd_f['MUNIC_MOV'].dropna().astype(str).apply(normalize_name).value_counts().to_dict()
        
    st.markdown('<div class="section-title">📍 Mapa Coroplético da Concentração de Atendimentos (RS)</div>', unsafe_allow_html=True)
    
    # Carrega GeoJSON
    geojson = load_rs_geojson()
    
    if geojson and counts:
        # Clona os dados do cache para evitar efeitos colaterais
        geojson_data = copy.deepcopy(geojson)
        
        # Insere a quantidade correspondente em cada feição do mapa
        for feature in geojson_data['features']:
            raw_name = feature['properties']['name']
            norm_name = normalize_name(raw_name)
            feature['properties']['Quantidade'] = counts.get(norm_name, 0)
            feature['properties']['Nome'] = raw_name.title()
            
        # Converte para estrutura compatível do Altair (FeatureCollection completo)
        geodata = alt.Data(values=geojson_data)
        
        is_mama = disease == "Câncer de Mama"
        color_scheme = 'purplered' if is_mama else 'blues'
        
        # 1. Camada de fundo: desenha todos os municípios em cinza claro para servir de contorno base
        background = alt.Chart(geodata).mark_geoshape(
            fill='#f4f4f4',
            stroke='#ffffff',
            strokeWidth=0.3
        )
        
        # 2. Camada de dados: desenha apenas os municípios com atendimentos > 0
        foreground = alt.Chart(geodata).mark_geoshape(
            stroke='#ffffff',
            strokeWidth=0.4
        ).encode(
            color=alt.Color(
                'properties.Quantidade:Q',
                title='Procedimentos',
                scale=alt.Scale(scheme=color_scheme)
            ),
            tooltip=[
                alt.Tooltip('properties.Nome:N', title='Município'),
                alt.Tooltip('properties.Quantidade:Q', title='Procedimentos', format=',d')
            ]
        ).transform_filter(
            'datum.properties.Quantidade > 0'
        )
        
        # Cria o mapa coroplético no Altair combinando as duas camadas e aplicando a projeção explicitamente centrada no RS
        choropleth = (background + foreground).project(
            type='mercator',
            center=[-53.5, -30.0],
            scale=4500
        ).properties(
            width='container',
            height=500
        )
        
        st.altair_chart(choropleth, use_container_width=True)
        
        # Exibe a tabela ordenada das cidades com atendimentos registrados
        st.markdown('**Detalhamento dos Atendimentos por Município Prestador:**')
        table_data = pd.DataFrame([
            {"municipio": key.title(), "quantidade": val}
            for key, val in counts.items() if val > 0
        ]).sort_values(by='quantidade', ascending=False)
        
        if not table_data.empty:
            st.dataframe(
                table_data,
                column_config={
                    "municipio": "Município Executor do Tratamento",
                    "quantidade": st.column_config.NumberColumn("Total de Procedimentos", format="%d")
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.warning("Sem dados disponíveis ou falha ao carregar as geometrias do estado.")
        
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
        chart_res_chemo = plot_residents_vs_non_residents_altair(df_aq, "Quimioterapia", "Porto Alegre", selected_months)
        st.altair_chart(chart_res_chemo, use_container_width=True)
    with col_geo2:
        chart_res_radio = plot_residents_vs_non_residents_altair(df_ar, "Radioterapia", "Porto Alegre", selected_months)
        st.altair_chart(chart_res_radio, use_container_width=True)
