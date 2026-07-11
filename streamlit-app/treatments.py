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