import streamlit as st

# Cores do Sistema de Design
COLOR_MAMA = '#d63384'  # Rosa (Outubro Rosa)
COLOR_COLO = '#0065D8'  # Novo Azul (Câncer de Colo)
COLOR_MIXED = '#0d6efd' # Azul Geral

# Coordenadas geográficas dos municípios do RS para mapeamento
RS_CITY_COORDS = {
    'porto alegre': (-30.0346, -51.2177),
    'pelotas': (-31.7654, -52.3376),
    'caxias do sul': (-29.1678, -51.1794),
    'passo fundo': (-28.2584, -52.4089),
    'santa maria': (-29.6842, -53.8069),
    'ijuí': (-28.3877, -53.9189),
    'ijui': (-28.3877, -53.9189),
    'são leopoldo': (-29.7594, -51.1442),
    'sao leopoldo': (-29.7594, -51.1442),
    'santa cruz do sul': (-29.7181, -52.4306),
    'taquara': (-29.6514, -50.7806),
    'lajeado': (-29.4664, -51.9614),
    'rio grande': (-32.0350, -52.0986),
    'erechim': (-27.6341, -52.2739),
    'uruguaiana': (-29.7547, -57.0864),
    'cruz alta': (-28.6386, -53.6067),
    'canoas': (-29.9181, -51.1781),
    'santo ângelo': (-28.2992, -54.2631),
    'santo angelo': (-28.2992, -54.2631),
    'bento gonçalves': (-29.1683, -51.5178),
    'bento goncalves': (-29.1683, -51.5178),
    'santa rosa': (-27.8711, -54.4789),
    'santiago': (-29.1914, -54.8656),
    'são gabriel': (-30.3364, -54.2656),
    'sao gabriel': (-30.3364, -54.2656),
    'são borja': (-28.6583, -56.0044),
    'sao borja': (-28.6583, -56.0044),
    'bagé': (-31.3314, -54.1061),
    'bage': (-31.3314, -54.1061),
    'carazinho': (-28.2842, -52.7856),
    'cachoeira do sul': (-30.0392, -52.8894)
}

# Injeção de CSS global (Premium)
def inject_global_css(theme_color):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .main-header {{
        position: relative;
        color: white;
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(29, 53, 87, 0.15);
        overflow: hidden;
        z-index: 1;
    }}
    
    .main-header h1, .main-header p {{
        position: relative;
        z-index: 2;
    }}
    
    .main-header h1 {{
        margin: 0;
        font-weight: 700;
        font-size: 2.5rem;
    }}
    
    .main-header p {{
        margin: 0.5rem 0 0 0;
        font-weight: 300;
        font-size: 1.1rem;
        opacity: 0.9;
    }}
    
    /* Pseudo-elementos com transição de opacidade para cross-fade suave dos gradientes */
    .main-header::before, .main-header::after {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: -1;
        transition: opacity 0.6s ease-in-out;
    }}
    
    /* Gradiente Rosa (Mama) */
    .main-header::before {{
        background: linear-gradient(135deg, #8f2f5f 0%, #e072a9 100%);
        opacity: var(--opacity-mama, 1);
    }}
    
    /* Gradiente Azul (Colo) */
    .main-header::after {{
        background: linear-gradient(135deg, #1d3557 0%, #0065d8 100%);
        opacity: var(--opacity-colo, 0);
    }}
    
    /* Personaliza o botão primário (Aba ativa) para herdar a cor do tema */
    button[kind="primary"] {{
        background-color: {theme_color} !important;
        border-color: {theme_color} !important;
        color: white !important;
        font-weight: 600 !important;
        transition: background-color 0.3s ease, border-color 0.3s ease;
    }}
    
    /* Layout dos Cards de KPI */
    .kpi-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 25px;
    }}
    
    .kpi-card {{
        flex: 1;
        min-width: 220px;
        background-color: #ffffff;
        border-radius: 10px;
        padding: 18px 22px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }}
    
    .kpi-title {{
        font-size: 12px;
        color: #777777;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }}
    
    .kpi-value {{
        font-size: 28px;
        font-weight: 700;
        color: #111111;
        margin-bottom: 2px;
    }}
    
    .kpi-subtitle {{
        font-size: 11px;
        color: #999999;
    }}
    
    /* Seções */
    .section-title {{
        font-size: 20px;
        font-weight: 600;
        color: #222222;
        margin-top: 25px;
        margin-bottom: 15px;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 8px;
    }}
    
    /* Alerts custom */
    .custom-alert {{
        padding: 12px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 14px;
        line-height: 1.5;
    }}
    </style>
    """, unsafe_allow_html=True)

# Função para atualizar dinamicamente as cores do gradiente de fundo com transição de opacidade
def update_header_gradient(disease):
    if disease == "Câncer de Mama":
        opacity_mama = "1"
        opacity_colo = "0"
    else:  # Câncer de Colo de Útero (Novo Azul)
        opacity_mama = "0"
        opacity_colo = "1"
        
    st.markdown(f"""
    <style>
    :root {{
        --opacity-mama: {opacity_mama};
        --opacity-colo: {opacity_colo};
    }}
    </style>
    """, unsafe_allow_html=True)

# Função auxiliar para gerar KPI Cards com bordas temáticas
def make_kpi_card(title, value, subtitle="", border_color="#d63384"):
    return f"""
    <div class="kpi-card" style="border-left: 5px solid {border_color}; font-family: 'Inter', sans-serif;">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """
