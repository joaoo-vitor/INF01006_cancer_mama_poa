import streamlit as st
import pandas as pd
import altair as alt

def render_exams_page(disease, theme_color):
    st.markdown('<div class="section-title">🔬 Rastreamento Oncológico Preventivo (SISCAN/Tabnet)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-alert" style="background-color: #fffde7; border-left: 4px solid #fbc02d; color: #f57f17;">
        ⚠️ <b>Dados Simulados:</b> Esta seção utiliza uma estrutura e amostragem de dados fictícios para fins de modelagem de tela. 
        Planilhas reais exportadas do SISCAN/Tabnet podem ser integradas diretamente neste painel posteriormente.
    </div>
    """, unsafe_allow_html=True)
    
    # Mock de exames diagnósticos no estado (SISCAN)
    state_exams = pd.DataFrame([
        {"Exame": "Mamografia de Rastreamento", "Região": "Metropolitana", "Quantidade": 145200},
        {"Exame": "Mamografia de Rastreamento", "Região": "Serra", "Quantidade": 48500},
        {"Exame": "Mamografia de Rastreamento", "Região": "Sul", "Quantidade": 32100},
        {"Exame": "Mamografia de Rastreamento", "Região": "Norte", "Quantidade": 29800},
        {"Exame": "Mamografia de Rastreamento", "Região": "Vales", "Quantidade": 22400},
        {"Exame": "Preventivo de Colo de Útero", "Região": "Metropolitana", "Quantidade": 284000},
        {"Exame": "Preventivo de Colo de Útero", "Região": "Serra", "Quantidade": 89400},
        {"Exame": "Preventivo de Colo de Útero", "Região": "Sul", "Quantidade": 64200},
        {"Exame": "Preventivo de Colo de Útero", "Região": "Norte", "Quantidade": 55100},
        {"Exame": "Preventivo de Colo de Útero", "Região": "Vales", "Quantidade": 41300},
    ])
    
    poa_exam_units = pd.DataFrame([
        {"Unidade de Saúde": "Hospital Fêmina", "Tipo de Exame": "Mamografia de Rastreamento", "Quantidade": 12500},
        {"Unidade de Saúde": "Hospital de Clínicas de Porto Alegre", "Tipo de Exame": "Mamografia de Rastreamento", "Quantidade": 9800},
        {"Unidade de Saúde": "Santa Casa de Misericórdia", "Tipo de Exame": "Mamografia de Rastreamento", "Quantidade": 8400},
        {"Unidade de Saúde": "Hospital Conceição", "Tipo de Exame": "Mamografia de Rastreamento", "Quantidade": 7600},
        {"Unidade de Saúde": "Centro de Saúde IAPI", "Tipo de Exame": "Preventivo de Colo de Útero", "Quantidade": 5400},
        {"Unidade de Saúde": "Centro de Saúde Modelo", "Tipo de Exame": "Preventivo de Colo de Útero", "Quantidade": 4800},
        {"Unidade de Saúde": "Centro de Saúde Santa Marta", "Tipo de Exame": "Preventivo de Colo de Útero", "Quantidade": 3900},
        {"Unidade de Saúde": "Ambulatório de Especialidades Zona Sul", "Tipo de Exame": "Preventivo de Colo de Útero", "Quantidade": 3100},
    ])
    
    # Seleção automática baseada no tipo de câncer da barra lateral para integrar a visualização
    exam_type_mapped = "Mamografia de Rastreamento" if disease == "Câncer de Mama" else "Preventivo de Colo de Útero"
    
    st.markdown(f'<div class="section-title">📊 Volume Estadual de Exames: {exam_type_mapped}</div>', unsafe_allow_html=True)
    
    exam_filtered = state_exams[state_exams['Exame'] == exam_type_mapped]
    
    # Exames por Região
    chart_exams = alt.Chart(exam_filtered).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=theme_color).encode(
        x=alt.X('Região:N', sort='-y', title='Região de Saúde do Estado'),
        y=alt.Y('Quantidade:Q', title='Volume de Exames'),
        tooltip=[alt.Tooltip('Região:N'), alt.Tooltip('Quantidade:Q', title='Volume de Exames', format=',d')]
    ).properties(
        width='container',
        height=320
    )
    st.altair_chart(chart_exams, use_container_width=True)
    
    # Detalhe Unidades Porto Alegre
    st.markdown(f'<div class="section-title">🏥 Unidades de Saúde Executoras em Porto Alegre ({exam_type_mapped})</div>', unsafe_allow_html=True)
    
    poa_filtered = poa_exam_units[poa_exam_units['Tipo de Exame'] == exam_type_mapped]
    
    chart_poa_units = alt.Chart(poa_filtered).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=theme_color).encode(
        y=alt.Y('Unidade de Saúde:N', sort='-x', title='Estabelecimento de Saúde'),
        x=alt.X('Quantidade:Q', title='Total de Exames Efetuados'),
        tooltip=[alt.Tooltip('Unidade de Saúde:N'), alt.Tooltip('Quantidade:Q', title='Quantidade', format=',d')]
    ).properties(
        width='container',
        height=320
    )
    st.altair_chart(chart_poa_units, use_container_width=True)
