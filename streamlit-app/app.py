import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Configuração de caminhos do Python para importações relativas e do plots.py
app_dir = os.path.dirname(__file__)
sys.path.append(app_dir)
sys.path.append(os.path.join(app_dir, '../visualizations'))

# Importação dos módulos das páginas divididas
from home import render_home_page
from financial import render_financial_page
from demographic import render_demographic_page
from geographic import render_geographic_page
from exams import render_exams_page
from treatments import render_treatments_page
from patients import render_patients_page

# Importações de configurações e estilos globais
from config import (
    COLOR_MAMA,
    COLOR_COLO,
    RS_CITY_COORDS,
    inject_global_css,
    update_header_gradient
)

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Monitoramento de Câncer - Rio Grande do Sul (2025)",
    page_icon="🎗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# (Design system colors, CSS template, coordinates and helpers are configured in config.py)

# Carga de dados otimizada com Cache do Streamlit (usando caminhos absolutos baseados no diretório-pai)
@st.cache_data
def load_datasets():
    base_path = os.path.join(os.path.dirname(__file__), '../datasets')
    
    datasets = {
        'aq_colo': os.path.join(base_path, 'AQRS25colo_agregado.csv'),
        'aq_mama': os.path.join(base_path, 'AQRS25mama_agregado.csv'),
        'ar_colo': os.path.join(base_path, 'ARRS25colo_agregado.csv'),
        'ar_mama': os.path.join(base_path, 'ARRS25mama_agregado.csv'),
        'rd_colo': os.path.join(base_path, 'RDRS25colo_agregado.csv'),
        'rd_mama': os.path.join(base_path, 'RDRS25mama_agregado.csv')
    }
    
    data = {}
    for key, path in datasets.items():
        if os.path.exists(path):
            data[key] = pd.read_csv(path, low_memory=False)
        else:
            st.error(f"Arquivo não encontrado: {path}")
            data[key] = pd.DataFrame()
            
    return data

data = load_datasets()

# Montar opções de cidades a partir dos datasets
@st.cache_data
def get_rs_cities():
    cities = set()
    for df_name in ['aq_colo', 'aq_mama', 'ar_colo', 'ar_mama']:
        if df_name in data and 'AP_UFMUN' in data[df_name].columns:
            cities.update(data[df_name]['AP_UFMUN'].dropna().str.title().str.strip())
    for df_name in ['rd_colo', 'rd_mama']:
        if df_name in data and 'MUNIC_MOV' in data[df_name].columns:
            cities.update(data[df_name]['MUNIC_MOV'].dropna().str.title().str.strip())
    return sorted(list(cities))

cities_list = get_rs_cities()

# ----------------- BARRA LATERAL (CONTROLES GERAIS) -----------------
st.sidebar.markdown('<div class="sidebar-header">🎗️ Controle de Filtros</div>', unsafe_allow_html=True)

# Filtro de Doença
disease = st.sidebar.radio(
    "Tipo de Câncer:",
    ["Câncer de Mama", "Câncer de Colo de Útero"]
)
theme_color = COLOR_MAMA if disease == "Câncer de Mama" else COLOR_COLO
disease_suffix = "mama" if disease == "Câncer de Mama" else "colo"

# Aplica injeção de CSS global e degradê de cabeçalho dinâmico e animado
inject_global_css(theme_color)
update_header_gradient(disease)

# Filtro de Município
selected_city = st.sidebar.selectbox(
    "Município do Estabelecimento:",
    ["Todo o Estado"] + cities_list
)

# Filtro de Período (meses de 2025)
selected_months = st.sidebar.slider(
    "Período (Meses de 2025):",
    min_value=1,
    max_value=12,
    value=(1, 12)
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size: 11px; color: #777777; line-height: 1.4;">
    💡 <b>Dica de Uso:</b><br>
    • O filtro de <i>Câncer</i> é ignorado na aba <b>Financeiras</b> (compara ambos).<br>
    • O filtro de <i>Município</i> é ignorado na aba <b>Geográfica</b> (exibe o mapa do RS).
</div>
""", unsafe_allow_html=True)

# Funções auxiliares para filtrar dados
def filter_sia_data(df, city, months):
    if df.empty:
        return df
    df_f = df.copy()
    if city and city != "Todo o Estado" and 'AP_UFMUN' in df_f.columns:
        df_f = df_f[df_f['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
    if months and 'AP_MVM' in df_f.columns:
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_f = df_f[(df_f['AP_MVM'] >= start_m) & (df_f['AP_MVM'] <= end_m)]
    return df_f

def filter_sih_data(df, city, months):
    if df.empty:
        return df
    df_f = df.copy()
    if city and city != "Todo o Estado" and 'MUNIC_MOV' in df_f.columns:
        df_f = df_f[df_f['MUNIC_MOV'].astype(str).str.lower().str.strip() == city.lower().strip()]
    if months and 'ANO_CMPT' in df_f.columns and 'MES_CMPT' in df_f.columns:
        df_f['ANO_MES'] = df_f['ANO_CMPT'].astype(int) * 100 + df_f['MES_CMPT'].astype(int)
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_f = df_f[(df_f['ANO_MES'] >= start_m) & (df_f['ANO_MES'] <= end_m)]
    return df_f


# ----------------- TÍTULO PRINCIPAL E NAVEGAÇÃO POR ABAS -----------------
st.markdown("""
<div class="main-header">
    <h1>🎗️ Painel de Tratamento do Câncer de Mama/Colo de Útero no Rio Grande do Sul (2025)</h1>
    <p">Análise integrada do tratamento de Câncer de Mama e Câncer de Colo de Útero em 2025 pelo SUS no RS com foco em Porto Alegre.</p>
</div>    
""", unsafe_allow_html=True)

# Definição das Abas dentro da página
tab_home, tab_finance, tab_demo, tab_geo, tab_patients, tab_exams, tab_treatments = st.tabs([
    "🏠 Página Inicial", 
    "💸 Informações Financeiras", 
    "👥 Informações Demográficas", 
    "🗺️ Análise Geográfica", 
    "🧍 Pacientes Únicos",
    "🔬 Exames (SISCAN)",
    "Tratamentos"
])


# ================= RENDERS DE CADA ABA CHAMANDO OS SUB-MÓDULOS =================

with tab_home:
    # Filtra os dados de acordo com a seleção atual
    df_aq_f = filter_sia_data(data[f'aq_{disease_suffix}'], selected_city, selected_months)
    df_ar_f = filter_sia_data(data[f'ar_{disease_suffix}'], selected_city, selected_months)
    df_rd_f = filter_sih_data(data[f'rd_{disease_suffix}'], selected_city, selected_months)
    
    render_home_page(
        df_aq=df_aq_f,
        df_ar=df_ar_f,
        df_rd=df_rd_f,
        data_raw=data,
        selected_city=selected_city,
        selected_months=selected_months,
        theme_color=theme_color,
        disease=disease
    )

with tab_finance:
    render_financial_page(
        data_raw=data,
        filter_sia_func=filter_sia_data,
        filter_sih_func=filter_sih_data,
        selected_city=selected_city,
        selected_months=selected_months
    )

with tab_demo:
    df_aq_f = filter_sia_data(data[f'aq_{disease_suffix}'], selected_city, selected_months)
    df_ar_f = filter_sia_data(data[f'ar_{disease_suffix}'], selected_city, selected_months)
    df_rd_f = filter_sih_data(data[f'rd_{disease_suffix}'], selected_city, selected_months)
    
    render_demographic_page(
        df_aq=df_aq_f,
        df_ar=df_ar_f,
        df_rd=df_rd_f,
        selected_city=selected_city,
        selected_months=selected_months,
        theme_color=theme_color,
        disease=disease
    )

with tab_geo:
    render_geographic_page(
        data_raw=data,
        filter_sia_func=filter_sia_data,
        filter_sih_func=filter_sih_data,
        selected_months=selected_months,
        theme_color=theme_color,
        disease=disease,
        RS_CITY_COORDS=RS_CITY_COORDS
    )

with tab_patients:
    df_aq_f = filter_sia_data(data[f'aq_{disease_suffix}'], selected_city, selected_months)
    df_ar_f = filter_sia_data(data[f'ar_{disease_suffix}'], selected_city, selected_months)
    df_rd_f = filter_sih_data(data[f'rd_{disease_suffix}'], selected_city, selected_months)

    render_patients_page(
        df_aq=df_aq_f,
        df_ar=df_ar_f,
        df_rd=df_rd_f,
        selected_city=selected_city,
        selected_months=selected_months,
        theme_color=theme_color,
        disease=disease
    )

with tab_exams:
    render_exams_page(
        disease=disease,
        theme_color=theme_color
    )

with tab_treatments:
    df_aq_f = filter_sia_data(data[f'aq_{disease_suffix}'], selected_city, selected_months)
    df_ar_f = filter_sia_data(data[f'ar_{disease_suffix}'], selected_city, selected_months)

    render_treatments_page(
        df_aq=df_aq_f,
        df_ar=df_ar_f,
        selected_city=selected_city,
        selected_months=selected_months,
        theme_color=theme_color,
        disease=disease
    )
