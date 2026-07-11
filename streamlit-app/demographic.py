import streamlit as st
import pandas as pd
import altair as alt
from config import GENDER_ROSE, GENDER_BLUE

def render_demographic_page(df_aq, df_ar, df_rd, selected_city, selected_months, theme_color, disease):
    st.markdown(f'<div class="section-title">👥 Perfil dos Pacientes em Atendimento - {disease} ({selected_city})</div>', unsafe_allow_html=True)
    
    # 1. Distribuição de Idades
    st.markdown('<div class="section-title">🎂 Distribuição de Idades por Canal de Atendimento</div>', unsafe_allow_html=True)
    
    ages = []
    if not df_aq.empty and 'AP_NUIDADE' in df_aq.columns:
        ages.append(pd.DataFrame({'Idade': df_aq['AP_NUIDADE'], 'Fonte': 'Quimioterapia (SIA)'}))
    if not df_ar.empty and 'AP_NUIDADE' in df_ar.columns:
        ages.append(pd.DataFrame({'Idade': df_ar['AP_NUIDADE'], 'Fonte': 'Radioterapia (SIA)'}))
    if not df_rd.empty and 'IDADE' in df_rd.columns:
        ages.append(pd.DataFrame({'Idade': df_rd['IDADE'], 'Fonte': 'Internação (SIH)'}))
        
    if ages:
        df_ages = pd.concat(ages, ignore_index=True).dropna()
        df_ages['Idade'] = df_ages['Idade'].astype(int)
        
        is_mama = disease == "Câncer de Mama"
        age_colors = ['#d63384', '#e87cb4', '#8a1f51'] if is_mama else ['#0065D8', '#66b2ff', '#003380']

        chart_age = alt.Chart(df_ages).mark_area(
            opacity=0.6,
            interpolate='step'
        ).encode(
            x=alt.X('Idade:Q', bin=alt.Bin(maxbins=30), title='Idade do Paciente (Anos)'),
            y=alt.Y('count():Q', stack=None, title='Frequência de Atendimentos'),
            color=alt.Color(
                'Fonte:N', 
                scale=alt.Scale(
                    domain=['Quimioterapia (SIA)', 'Radioterapia (SIA)', 'Internação (SIH)'],
                    range=age_colors
                ), 
                title='Fonte dos Dados'
            ),
            tooltip=[alt.Tooltip('Idade:Q', title='Faixa de Idade'), alt.Tooltip('count():Q', title='Pacientes')]
        ).properties(
            width='container',
            height=350
        )
        st.altair_chart(chart_age, use_container_width=True)
    else:
        st.warning("Sem dados de idade disponíveis para esta combinação de filtros.")
        
    # 2. Raça/Cor e Gênero
    st.markdown('<div class="section-title">🎨 Raça/Cor e Gênero Declarados</div>', unsafe_allow_html=True)
    
    c_demo1, c_demo2 = st.columns(2)
    
    with c_demo1:
        # Raça/Cor Normalizada
        races = []
        if not df_aq.empty and 'AP_RACACOR' in df_aq.columns:
            races.append(df_aq['AP_RACACOR'].astype(str))
        if not df_ar.empty and 'AP_RACACOR' in df_ar.columns:
            races.append(df_ar['AP_RACACOR'].astype(str))
        if not df_rd.empty and 'RACA_COR' in df_rd.columns:
            races.append(df_rd['RACA_COR'].astype(str))
            
        if races:
            df_races = pd.concat(races, ignore_index=True).to_frame(name='Raca')
            
            def normalize_race(val):
                v = str(val).strip().upper()
                if 'BRANCA' in v: return 'Branca'
                if 'PARDA' in v: return 'Parda'
                if 'PRETA' in v: return 'Preta'
                if 'AMARELA' in v: return 'Amarela'
                if 'INDÍGENA' in v or 'INDIGENA' in v: return 'Indígena'
                return 'Não Informada'
                
            df_races['Raça/Cor'] = df_races['Raca'].apply(normalize_race)
            race_counts = df_races['Raça/Cor'].value_counts().reset_index()
            
            chart_race = alt.Chart(race_counts).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=theme_color).encode(
                x=alt.X('Raça/Cor:N', sort='-y', title='Raça ou Cor Declarada'),
                y=alt.Y('count:Q', title='Volume de Casos'),
                tooltip=[alt.Tooltip('Raça/Cor:N'), alt.Tooltip('count:Q', title='Quantidade')]
            ).properties(
                height=300
            )
            st.altair_chart(chart_race, use_container_width=True)
        else:
            st.info("Sem dados de Raça/Cor cadastrados.")
            
    with c_demo2:
        # Gênero
        genders = []
        if not df_aq.empty and 'AP_SEXO' in df_aq.columns:
            genders.append(df_aq['AP_SEXO'].astype(str))
        if not df_ar.empty and 'AP_SEXO' in df_ar.columns:
            genders.append(df_ar['AP_SEXO'].astype(str))
        if not df_rd.empty and 'SEXO' in df_rd.columns:
            genders.append(df_rd['SEXO'].astype(str))
            
        if genders:
            df_genders = pd.concat(genders, ignore_index=True).to_frame(name='Sexo')
            df_genders['Gênero'] = df_genders['Sexo'].map({'F': 'Feminino', 'M': 'Masculino'}).fillna('Não Informado')
            gender_counts = df_genders['Gênero'].value_counts().reset_index()
            
            # Garantir tamanho mínimo de fatia de 5% do total para categorias com count > 0, para fins de visualização legível/hover
            total_cases = gender_counts['count'].sum()
            if total_cases > 0:
                min_threshold = total_cases * 0.05
                gender_counts['DisplayValue'] = gender_counts['count'].apply(lambda x: max(x, min_threshold) if x > 0 else 0)
            else:
                gender_counts['DisplayValue'] = gender_counts['count']
                
            chart_gender = alt.Chart(gender_counts).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field='DisplayValue', type='quantitative'),
                color=alt.Color(
                    'Gênero:N', 
                    scale=alt.Scale(
                        domain=['Feminino', 'Masculino', 'Não Informado'], 
                        range=[GENDER_ROSE, GENDER_BLUE, '#adb5bd']
                    ),
                    title='Gênero'
                ),
                tooltip=[
                    alt.Tooltip('Gênero:N'),
                    alt.Tooltip('count:Q', title='Quantidade Real')
                ]
            ).properties(
                height=300
            )
            st.altair_chart(chart_gender, use_container_width=True)
        else:
            st.info("Sem dados de gênero cadastrados.")
