import streamlit as st
import pandas as pd
import altair as alt
import os
import re
import pydeck as pdk
import copy
from poa_coords_dict import POA_HEALTH_UNITS_COORDS

def get_month_abbreviation(col_name):
    col_upper = col_name.upper().strip()
    if 'JANEIRO' in col_upper: return 'Jan'
    if 'FEVEREIRO' in col_upper: return 'Fev'
    if 'MAR' in col_upper: return 'Mar'
    if 'ABRIL' in col_upper: return 'Abr'
    if 'MAIO' in col_upper: return 'Mai'
    if 'JUNHO' in col_upper: return 'Jun'
    if 'JULHO' in col_upper: return 'Jul'
    if 'AGOSTO' in col_upper: return 'Ago'
    if 'SETEMBRO' in col_upper: return 'Set'
    if 'OUTUBRO' in col_upper: return 'Out'
    if 'NOVEMBRO' in col_upper: return 'Nov'
    if 'DEZEMBRO' in col_upper: return 'Dez'
    return None

def load_and_prepare_siscan(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path, encoding='latin1', sep=';')
    if df.empty:
        return df
        
    first_col = df.columns[0]
    # Ignorar a linha de total
    df = df[df[first_col].astype(str).str.strip().str.upper() != 'TOTAL']
    
    def clean_local_name(name):
        if not isinstance(name, str):
            return ""
        cleaned = re.sub(r'^[\d\-/\s]+', '', name)
        return cleaned.strip().upper()
        
    df['Local'] = df[first_col].apply(clean_local_name)
    
    month_mapping = {}
    for col in df.columns:
        short_name = get_month_abbreviation(col)
        if short_name:
            month_mapping[col] = short_name
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
    df = df.rename(columns=month_mapping)
    return df

def hex_to_rgba(hex_str, alpha=180):
    hex_str = hex_str.lstrip('#')
    rgb = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return [rgb[0], rgb[1], rgb[2], alpha]

def render_exams_page(disease, theme_color, selected_city, selected_months):
    st.markdown('<div class="section-title">🔬 Rastreamento Oncológico Preventivo (SISCAN/SUS)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-alert" style="background-color: #fffde7; border-left: 4px solid #fbc02d; color: #f57f17;">
        📊 <b>Dados SISCAN (2025):</b> Esta seção apresenta os exames preventivos registrados no Sistema de Informação do Câncer (SISCAN/SUS) 
        para o estado do Rio Grande do Sul e Porto Alegre. Apenas o exame selecionado é considerado, o filtro de tipo de câncer não se aplica nessa página.
    </div>
    """, unsafe_allow_html=True)
    
    # Dicionário de arquivos e opções
    exam_options = {
        "Mamografia de Rastreamento": "mamografia",
        "Citopatológico de Colo do Útero (Preventivo)": "citoDoColo",
        "Histopatológico de Colo do Útero": "histoDoColo",
        "Citopatológico de Mama": "citoDeMama",
        "Histopatológico de Mama": "histoDeMama"
    }
    
    exam_files = {
        "citoDeMama": ("SISCANRS25citoDeMama.csv", "SISCANPOA25citoDeMama.csv"),
        "citoDoColo": ("SISCANRS25citoDoColo.csv", "SISCANPOA25citoDoColo.csv"),
        "histoDeMama": ("SISCANRS25histoDeMama.csv", "SISCANPOA25histoDeMama.csv"),
        "histoDoColo": ("SISCANRS25histoDoColo.csv", "SICANPOA25histoDoColo.csv"),
        "mamografia": ("SISCANRS25mamografia.csv", "SISCANPOA25mamografia.csv")
    }
    
    # 1. Seletor de Exame
    selected_exam_label = st.selectbox("Tipo de Exame:", list(exam_options.keys()))
    selected_exam_key = exam_options[selected_exam_label]
    
    # Determinar a cor e paleta com base no exame
    is_exam_mama = "mama" in selected_exam_key.lower() or "mamografia" in selected_exam_key.lower()
    active_color = '#d63384' if is_exam_mama else '#0065D8'
    active_scheme = 'purplered' if is_exam_mama else 'blues'
    
    # Caminhos
    app_dir = os.path.dirname(os.path.dirname(__file__))
    siscan_dir = os.path.join(app_dir, "datasets", "SISCAN")
    
    rs_filename, poa_filename = exam_files[selected_exam_key]
    rs_path = os.path.join(siscan_dir, rs_filename)
    poa_path = os.path.join(siscan_dir, poa_filename)
    
    # Carregar dados
    df_rs = load_and_prepare_siscan(rs_path)
    df_poa = load_and_prepare_siscan(poa_path)
    
    if df_rs.empty:
        st.warning("Não há dados disponíveis para o exame selecionado.")
        return
        
    # Mapeamento e Slicing de Meses
    all_months_list = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    months_in_range = all_months_list[selected_months[0]-1 : selected_months[1]]
    months_to_sum = [m for m in months_in_range if m in df_rs.columns]
    
    # Se não houver meses válidos
    if not months_to_sum:
        st.info("Nenhum dado registrado para o intervalo de meses selecionado.")
        return
        
    # --- GRÁFICO 1: Histórico Mensal ---
    st.markdown(f'<div class="section-title">📊 Evolução Mensal de Exames ({selected_city})</div>', unsafe_allow_html=True)
    
    city_filter = selected_city.upper().strip()
    if selected_city == "Todo o Estado":
        df_filtered = df_rs
    else:
        df_filtered = df_rs[df_rs['Local'] == city_filter]
        
    if df_filtered.empty:
        st.info(f"Nenhum exame preventivo registrado para {selected_city} no período.")
    else:
        # Sum por mês
        monthly_data = []
        full_month_names = {
            'Jan': 'Janeiro', 'Fev': 'Fevereiro', 'Mar': 'Março', 'Abr': 'Abril',
            'Mai': 'Maio', 'Jun': 'Junho', 'Jul': 'Julho', 'Ago': 'Agosto',
            'Set': 'Setembro', 'Out': 'Outubro', 'Nov': 'Novembro', 'Dez': 'Dezembro'
        }
        for m in months_in_range:
            val = df_filtered[m].sum() if m in df_filtered.columns else 0
            monthly_data.append({
                "Mes": m,
                "Quantidade": int(val),
                "MesCompleto": full_month_names[m]
            })
        monthly_df = pd.DataFrame(monthly_data)
        
        # Desenhar Barras + Linha
        bar = alt.Chart(monthly_df).mark_bar(
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
            color=active_color,
            opacity=0.85
        ).encode(
            x=alt.X('Mes:N', sort=None, title='Mês de Processamento'),
            y=alt.Y('Quantidade:Q', title='Volume de Exames'),
            tooltip=[
                alt.Tooltip('MesCompleto:N', title='Mês'),
                alt.Tooltip('Quantidade:Q', title='Exames', format=',d')
            ]
        )
        
        line = alt.Chart(monthly_df).mark_line(
            color=active_color,
            strokeWidth=3,
            point=alt.OverlayMarkDef(color=active_color, size=60)
        ).encode(
            x=alt.X('Mes:N', sort=None),
            y=alt.Y('Quantidade:Q')
        )
        
        chart_exams = (bar + line).properties(
            width='container',
            height=350
        )
        st.altair_chart(chart_exams, use_container_width=True)
        
    # --- GRÁFICO 2: Top 10 Cidades ---
    st.markdown('<div class="section-title">🏆 Top 10 Municípios em Volume de Exames Realizados</div>', unsafe_allow_html=True)
    
    # Soma dos meses no range
    df_rs['Total_Range'] = df_rs[months_to_sum].sum(axis=1)
    city_totals = df_rs.groupby('Local')['Total_Range'].sum().reset_index(name='Quantidade')
    city_totals = city_totals[city_totals['Quantidade'] > 0].sort_values(by='Quantidade', ascending=False)
    
    if city_totals.empty:
        st.info("Nenhum registro de exames para as cidades no período selecionado.")
    else:
        # Agrupar a partir do 11º como Outras Cidades
        if len(city_totals) > 10:
            top_10 = city_totals.head(10).copy()
            others_val = city_totals.iloc[10:]['Quantidade'].sum()
            others_row = pd.DataFrame([{"Local": "OUTRAS CIDADES", "Quantidade": others_val}])
            pie_df = pd.concat([top_10, others_row], ignore_index=True)
        else:
            pie_df = city_totals
            
        pie_df['Cidade'] = pie_df['Local'].str.title()
        total_exams = pie_df['Quantidade'].sum()
        pie_df['Porcentagem_Formatada'] = pie_df['Quantidade'].apply(
            lambda x: f"{(x / total_exams) * 100:.2f}" if total_exams > 0 else "0.00"
        )
        
        # Donut Chart
        chart_pie = alt.Chart(pie_df).mark_arc(innerRadius=50, outerRadius=90).encode(
            theta=alt.Theta(field='Quantidade', type='quantitative'),
            color=alt.Color(
                field='Cidade',
                type='nominal',
                scale=alt.Scale(scheme=active_scheme),
                title='Município'
            ),
            tooltip=[
                alt.Tooltip('Cidade:N', title='Cidade'),
                alt.Tooltip('Quantidade:Q', title='Exames Realizados', format=',d')
                alt.Tooltip("Porcentagem_Formatada:Q", title="Proporção", format=".2%")
            ]
        ).properties(
            height=350
        )
        st.altair_chart(chart_pie, use_container_width=True)
        
    # --- MAPA: Unidades de Porto Alegre (Pydeck) ---
    st.markdown('### 📍 Distribuição de Exames por Estabelecimento em Porto Alegre')
    
    if df_poa.empty:
        st.info("Nenhum dado disponível para estabelecimentos de Porto Alegre para o exame selecionado.")
    else:
        df_poa['Total_Range'] = df_poa[months_to_sum].sum(axis=1)
        poa_totals = df_poa.groupby('Local')['Total_Range'].sum().reset_index(name='Quantidade')
        poa_totals = poa_totals[poa_totals['Quantidade'] > 0].sort_values(by='Quantidade', ascending=False)
        
        # Cruzar coordenadas
        map_data = []
        total_exams_poa = poa_totals['Quantidade'].sum()
        
        for idx, row in poa_totals.iterrows():
            name = row['Local']
            qty = row['Quantidade']
            if name in POA_HEALTH_UNITS_COORDS:
                lat, lon = POA_HEALTH_UNITS_COORDS[name]
                map_data.append({
                    "Unidade": name.title(),
                    "Quantidade": int(qty),
                    "Porcentagem_Formatada": f"{(qty / total_exams_poa) * 100:.2f}" if total_exams_poa > 0 else "0.00",
                    "latitude": lat,
                    "longitude": lon
                })
        
        if map_data:
            map_df = pd.DataFrame(map_data)
            
            # Normalizar raio
            max_poa_qty = map_df['Quantidade'].max()
            map_df['radius'] = map_df['Quantidade'].apply(
                lambda x: (x / max_poa_qty) * 450 + 150 if max_poa_qty > 0 else 150
            )
            
            view_state = pdk.ViewState(
                latitude=-30.0346,
                longitude=-51.2177,
                zoom=11.0,
                pitch=0
            )
            
            rgba_fill = hex_to_rgba(active_color, 180)
            rgba_line = hex_to_rgba(active_color, 255)
            
            layer = pdk.Layer(
                "ScatterplotLayer",
                map_df,
                get_position="[longitude, latitude]",
                get_color=rgba_fill,
                get_radius="radius",
                pickable=True,
                filled=True,
                stroked=True,
                line_width_min_pixels=1.5,
                get_line_color=rgba_line
            )
            
            tooltip_style = {
                "html": "<b>{Unidade}</b><br/>Exames: <b>{Quantidade}</b><br/>Proporção na Capital: <b>{Porcentagem_Formatada}%</b>",
                "style": {"backgroundColor": active_color, "color": "white", "fontSize": "12px"}
            }
            
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip_style,
                map_style="light"
            ))
            
            # Tabela de detalhamento
            st.markdown('**Detalhamento dos Exames por Unidade (Porto Alegre):**')
            st.dataframe(
                map_df[["Unidade", "Quantidade", "Porcentagem_Formatada"]],
                column_config={
                    "Unidade": "Unidade de Saúde Executor",
                    "Quantidade": st.column_config.NumberColumn("Total de Exames", format="%d"),
                    "Porcentagem_Formatada": "Proporção na Capital (%)"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum estabelecimento de Porto Alegre com coordenadas registradas obteve exames para o período selecionado.")
