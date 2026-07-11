import streamlit as st
import pandas as pd
import altair as alt
from config import CNES_HOSPITALS_MAP
AP_CODUNI_dict = CNES_HOSPITALS_MAP


def render_treatments_page(df_aq, df_ar, selected_city, selected_months, theme_color, disease, max_types=8, max_hospitals=5):

    
    def simplify(data, max, new_label):
        acc = data[max:].sum()
        data = data.drop(labels=data.index[max:])
        data[new_label] = acc

        return data

    # 1. Distribuição de tipos de quimioterapia
    st.markdown(f'<div class="section-title">📊 Volume Estadual de Quimioterapias para {disease}</div>', unsafe_allow_html=True)

    chemio_types = df_aq["AP_PRIPAL"].value_counts()

    if not chemio_types.empty:

        if len(chemio_types) > max_types:
            chemio_types = simplify(chemio_types, max_types, "Outras quimioterapias")

        chemio_types = pd.DataFrame({"Quimioterapia" : chemio_types.index, "Quantidade" : chemio_types.values})

        chemio_chart = alt.Chart(chemio_types).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=theme_color).encode(
            x=alt.X('Quimioterapia:N', title="Tipos de quimioterapia", sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Quantidade:Q', title="Quantidade de quimioterapias"),
            tooltip=[alt.Tooltip('Quimioterapia:N', title="Tipo"), alt.Tooltip('Quantidade:Q', title='Quantidade', format=',d')]
        ).properties(
            width='container',
            height=350
        )

        st.altair_chart(chemio_chart, use_container_width=True)
    else:
        st.warning("Sem dados disponíveis para esta combinação de filtros.")

    # 2. Número de quimioterapias por unidades de saúde
    st.markdown(f'<div class="section-title">🏥 Quimioterapias para {disease} por Hospital</div>', unsafe_allow_html=True)

    chemio_hospitals = df_aq["AP_CODUNI"].astype(str).map(AP_CODUNI_dict).value_counts()

    if not chemio_hospitals.empty:
        if len(chemio_hospitals) > max_hospitals:
            chemio_hospitals = simplify(chemio_hospitals, max_hospitals, "Outros hospitais")

        chemio_hospitals = pd.DataFrame({"Hospital" : chemio_hospitals.index, "Quantidade" : chemio_hospitals.values})

        chemio_hospitals_chart = alt.Chart(chemio_hospitals).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=theme_color).encode(
            x=alt.X("Quantidade:Q", title="Quantidade de quimioterapias"),
            y=alt.Y("Hospital:N", title="Hospitais", sort=None),
            tooltip=[alt.Tooltip('Hospital:N', title="Unidade de Saúde"), alt.Tooltip('Quantidade:Q', title='Quantidade', format=',d')]
            ).properties(
            width='container',
            height=350
        )

        st.altair_chart(chemio_hospitals_chart, use_container_width=True)
    else:
        st.warning("Sem dados disponíveis para esta combinação de filtros.")

    # 3. Número de radioterapias por unidade de saúde
    st.markdown(f'<div class="section-title">🏥 Radioterapias para {disease} por Hospital</div>', unsafe_allow_html=True)

    radio_hospitals = df_ar["AP_CODUNI"].astype(str).map(AP_CODUNI_dict).value_counts()

    if not radio_hospitals.empty:
        if len(radio_hospitals) > max_hospitals:
            radio_hospitals = simplify(radio_hospitals, max_hospitals, "Outros hospitais")

        radio_hospitals = pd.DataFrame({"Hospital" : radio_hospitals.index, "Quantidade" : radio_hospitals.values})

        radio_hospitals_chart = alt.Chart(radio_hospitals).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=theme_color).encode(
            x=alt.X('Quantidade:Q', title="Quantidade de radioterapias"),
            y=alt.Y('Hospital:N', title="Hospitais", sort=None),
            tooltip=[alt.Tooltip('Hospital:N', title="Unidade de Saúde"), alt.Tooltip('Quantidade:Q', title='Quantidade', format=',d')]
        ).properties(
            width='container',
            height=350
        )

        st.altair_chart(radio_hospitals_chart, use_container_width=True)
    else:
        st.warning("Sem dados disponíveis para esta combinação de filtros.")