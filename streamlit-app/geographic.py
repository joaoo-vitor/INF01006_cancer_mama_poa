import streamlit as st
import pandas as pd
import altair as alt
import json
import urllib.request
import unicodedata
import copy
from plots import plot_residents_vs_non_residents_altair
from config import CNES_HOSPITALS_MAP, POA_HOSPITALS_COORDS

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
        total_qty = sum(counts.values()) if counts else 0
        
        # Insere a quantidade e porcentagem correspondente em cada feição do mapa
        for feature in geojson_data['features']:
            raw_name = feature['properties']['name']
            norm_name = normalize_name(raw_name)
            qty = counts.get(norm_name, 0)
            feature['properties']['Quantidade'] = qty
            feature['properties']['Porcentagem'] = qty / total_qty if total_qty > 0 else 0.0
            feature['properties']['Nome'] = raw_name.title()
            
        import base64
        # Converte o GeoJSON para uma URL base64 para evitar que o Streamlit converta em DataFrame incorretamente
        geojson_str = json.dumps(geojson_data)
        geojson_base64 = base64.b64encode(geojson_str.encode('utf-8')).decode('utf-8')
        geojson_url = f"data:application/json;base64,{geojson_base64}"
        geodata = alt.Data(url=geojson_url, format=alt.DataFormat(property='features', type='json'))
        
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
                alt.Tooltip('properties.Quantidade:Q', title='Procedimentos', format=',d'),
                alt.Tooltip('properties.Porcentagem:Q', title='Porcentagem', format='.2%')
            ]
        ).transform_filter(
            'datum.properties && datum.properties.Quantidade > 0'
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
            {
                "municipio": key.title(), 
                "quantidade": val,
                "porcentagem": (val / total_qty) * 100 if total_qty > 0 else 0.0
            }
            for key, val in counts.items() if val > 0
        ]).sort_values(by='quantidade', ascending=False)
        
        if not table_data.empty:
            st.dataframe(
                table_data,
                column_config={
                    "municipio": "Município Executor do Tratamento",
                    "quantidade": st.column_config.NumberColumn("Total de Procedimentos", format="%d"),
                    "porcentagem": st.column_config.NumberColumn("Porcentagem (%)", format="%.2f%%")
                },
                use_container_width=True,
                hide_index=True
            )
    else:
        st.warning("Sem dados disponíveis ou falha ao carregar as geometrias do estado.")
        
    # 🏥 Zoom em Porto Alegre e seus Hospitais Prestadores
    st.markdown('<div class="section-title">🏥 Atendimentos Detalhados por Hospital em Porto Alegre</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-alert" style="background-color: #e3f2fd; border-left: 4px solid #1e88e5; color: #0d47a1;">
        🔍 <b>Visão Zoom na Capital:</b> Distribuição proporcional dos atendimentos selecionados nos hospitais prestadores localizados em Porto Alegre.
    </div>
    """, unsafe_allow_html=True)

    # Calcular contagens por CNES de Porto Alegre
    hosp_counts = {cnes: 0 for cnes in POA_HOSPITALS_COORDS.keys()}
    
    if map_metric == "Quimioterapia (SIA)" and not df_aq_f.empty:
        if "AP_CODUNI" in df_aq_f.columns:
            aq_counts = df_aq_f["AP_CODUNI"].astype(str).value_counts().to_dict()
            for cnes in hosp_counts.keys():
                hosp_counts[cnes] = aq_counts.get(cnes, 0)
    elif map_metric == "Radioterapia (SIA)" and not df_ar_f.empty:
        if "AP_CODUNI" in df_ar_f.columns:
            ar_counts = df_ar_f["AP_CODUNI"].astype(str).value_counts().to_dict()
            for cnes in hosp_counts.keys():
                hosp_counts[cnes] = ar_counts.get(cnes, 0)
    elif not df_rd_f.empty:
        # Internações (SIH)
        if "CNES" in df_rd_f.columns:
            rd_counts = df_rd_f["CNES"].astype(str).value_counts().to_dict()
            for cnes in hosp_counts.keys():
                hosp_counts[cnes] = rd_counts.get(cnes, 0)
                
    total_poa_hosp = sum(hosp_counts.values())

    if total_poa_hosp > 0:
        # Criar base de dados para os pontos
        hosp_data = []
        for cnes, qty in hosp_counts.items():
            if qty > 0:
                name = CNES_HOSPITALS_MAP.get(cnes, f"CNES {cnes}")
                lat, lon = POA_HOSPITALS_COORDS[cnes]
                hosp_data.append({
                    "Hospital": name,
                    "CNES": cnes,
                    "Quantidade": qty,
                    "Porcentagem": (qty / total_poa_hosp) * 100,
                    "Porcentagem_Formatada": f"{(qty / total_poa_hosp) * 100:.2f}",
                    "latitude": lat,
                    "longitude": lon
                })
        hosp_df = pd.DataFrame(hosp_data)
        
        import pydeck as pdk
        
        # Helper para converter hex para RGBA
        def hex_to_rgba(hex_str, alpha=180):
            hex_str = hex_str.lstrip('#')
            rgb = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
            return [rgb[0], rgb[1], rgb[2], alpha]
            
        # Normalizar os tamanhos dos círculos (raio em metros)
        max_qty = hosp_df['Quantidade'].max()
        # Escala do raio: de 150m a 600m com base no maior volume de atendimentos
        hosp_df['radius'] = hosp_df['Quantidade'].apply(
            lambda x: (x / max_qty) * 450 + 150 if max_qty > 0 else 150
        )
        
        view_state = pdk.ViewState(
            latitude=-30.0346,
            longitude=-51.2177,
            zoom=11.5,
            pitch=0
        )
        
        rgba_fill = hex_to_rgba(theme_color, 180)
        rgba_line = hex_to_rgba(theme_color, 255)
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            hosp_df,
            get_position="[longitude, latitude]",
            get_color=rgba_fill,
            get_radius="radius",
            pickable=True,
            filled=True,
            stroked=True,
            line_width_min_pixels=1.5,
            get_line_color=rgba_line
        )
        
        tooltip = {
            "html": "<b>{Hospital}</b><br/><b>CNES:</b> {CNES}<br/><b>Atendimentos:</b> {Quantidade}<br/><b>Proporção na Capital:</b> {Porcentagem_Formatada}%",
            "style": {"backgroundColor": "#1e88e5" if theme_color == '#0065D8' else "#d63384", "color": "white", "fontSize": "12px"}
        }
        
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        ))
        
        # Tabela com o detalhamento dos hospitais de Porto Alegre
        st.markdown('**Detalhamento dos Atendimentos por Hospital (Porto Alegre):**')
        hosp_table = hosp_df.sort_values(by='Quantidade', ascending=False)
        st.dataframe(
            hosp_table[["Hospital", "CNES", "Quantidade", "Porcentagem"]],
            column_config={
                "Hospital": "Hospital de Porto Alegre",
                "CNES": "Código CNES",
                "Quantidade": st.column_config.NumberColumn("Total de Atendimentos", format="%d"),
                "Porcentagem": st.column_config.NumberColumn("Proporção na Capital (%)", format="%.2f%%")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum atendimento registrado nos hospitais de Porto Alegre para a modalidade e filtros selecionados.")
        
    st.write("")
        
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
