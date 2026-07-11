import streamlit as st
import pandas as pd
import altair as alt


def make_kpi_card(title, value, subtitle="", border_color="#d63384"):
    return f"""
    <div class="kpi-card" style="border-left: 5px solid {border_color}; font-family: 'Inter', sans-serif;">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """


def normalize_patient_id(series):
    ids = (
        series
        .dropna()
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    # Remove valores vazios ou nulos escritos como texto
    ids = ids[
        ~ids.str.lower().isin([
            "",
            "nan",
            "none",
            "null",
            "na",
            "não informado",
            "nao informado",
            "ignorado",
            "ignorada"
        ])
    ]

    invalidos = {
        "000000000000000",
        "111111111111111",
        "222222222222222",
        "333333333333333",
        "444444444444444",
        "555555555555555",
        "666666666666666",
        "777777777777777",
        "888888888888888",
        "999999999999999",
    }

    ids = ids[~ids.isin(invalidos)]

    def identificador_repetido(valor):
        valor = str(valor).strip()
        return len(valor) >= 6 and len(set(valor)) == 1

    ids = ids[~ids.apply(identificador_repetido)]

    return ids


def build_patient_base(df_aq, df_ar):
    registros = []

    if not df_aq.empty and "AP_CNSPCN" in df_aq.columns:
        temp = df_aq.copy()
        temp["paciente_id"] = normalize_patient_id(temp["AP_CNSPCN"])
        temp = temp.dropna(subset=["paciente_id"])
        temp["modalidade"] = "Quimioterapia"
        registros.append(temp[["paciente_id", "modalidade"]])

    if not df_ar.empty and "AP_CNSPCN" in df_ar.columns:
        temp = df_ar.copy()
        temp["paciente_id"] = normalize_patient_id(temp["AP_CNSPCN"])
        temp = temp.dropna(subset=["paciente_id"])
        temp["modalidade"] = "Radioterapia"
        registros.append(temp[["paciente_id", "modalidade"]])

    if not registros:
        return pd.DataFrame(columns=["paciente_id", "modalidade"])

    return pd.concat(registros, ignore_index=True)


def plot_venn_diagram(qty_quimio_only, qty_radio_only, qty_both, disease):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.0, 2.8), dpi=300)
    ax.set_axis_off()
    
    # Define cores baseadas na doença
    is_mama = disease == "Câncer de Mama"
    if is_mama:
        color_left = '#d63384'       # Rosa
        color_right = '#8a1f51'      # Rosa Escuro
        color_edge_left = '#a31d59'
        color_edge_right = '#591032'
    else:
        color_left = '#0065D8'       # Novo Azul
        color_right = '#003380'      # Azul Escuro
        color_edge_left = '#004aa6'
        color_edge_right = '#001f4d'
        
    # Desenhar os círculos
    circle_left = plt.Circle((-0.5, 0), 1.0, facecolor=color_left, alpha=0.55, edgecolor=color_edge_left, linewidth=2.0)
    circle_right = plt.Circle((0.5, 0), 1.0, facecolor=color_right, alpha=0.55, edgecolor=color_edge_right, linewidth=2.0)
    
    ax.add_patch(circle_left)
    ax.add_patch(circle_right)
    
    # Definir limites e proporção
    ax.set_xlim(-1.7, 1.7)
    ax.set_ylim(-1.2, 1.3)
    ax.set_aspect('equal')
    
    # Adicionar títulos acima dos círculos
    ax.text(-0.7, 1.05, "Fez Quimioterapia", fontsize=9, fontweight='bold', color='#333333', ha='center')
    ax.text(0.7, 1.05, "Fez Radioterapia", fontsize=9, fontweight='bold', color='#333333', ha='center')
    
    # Adicionar contagens e rótulos
    ax.text(-0.9, 0, f"{qty_quimio_only:,}".replace(",", ".") + "\npacientes", fontsize=9, fontweight='bold', color='#111111', ha='center', va='center')
    ax.text(0.9, 0, f"{qty_radio_only:,}".replace(",", ".") + "\npacientes", fontsize=9, fontweight='bold', color='#111111', ha='center', va='center')
    ax.text(0, 0, f"{qty_both:,}".replace(",", ".") + "\npacientes", fontsize=10, fontweight='bold', color='#000000', ha='center', va='center')
    
    plt.tight_layout()
    fig.patch.set_facecolor('none')  # Fundo transparente
    ax.set_facecolor('none')
    
    return fig


def render_patients_page(df_aq, df_ar, df_rd, selected_city, selected_months, theme_color, disease):
    st.markdown(
        f'<div class="section-title">🧍 Pacientes Únicos e Intensidade de Tratamento - {disease} ({selected_city})</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="custom-alert" style="background-color: #f3e5f5; border-left: 4px solid #8e24aa; color: #4a148c;">
        <b>Nota metodológica:</b> esta análise usa a coluna <b>AP_CNSPCN</b> para identificar pacientes únicos
        nas bases de quimioterapia e radioterapia. Os totais de procedimentos não representam casos novos de câncer,
        mas sim registros de atendimento no SUS.
    </div>
    """, unsafe_allow_html=True)

    if "AP_CNSPCN" not in df_aq.columns and "AP_CNSPCN" not in df_ar.columns:
        st.error("Não encontrei a coluna AP_CNSPCN nas bases de quimioterapia/radioterapia.")
        return

    patients_df = build_patient_base(df_aq, df_ar)

    if patients_df.empty:
        st.warning("Não há pacientes identificáveis para os filtros selecionados.")
        return

    total_proc_aq = len(df_aq)
    total_proc_ar = len(df_ar)
    total_proc_rd = len(df_rd)

    pacientes_quimio = set()
    pacientes_radio = set()

    if not df_aq.empty and "AP_CNSPCN" in df_aq.columns:
        pacientes_quimio = set(normalize_patient_id(df_aq["AP_CNSPCN"]))

    if not df_ar.empty and "AP_CNSPCN" in df_ar.columns:
        pacientes_radio = set(normalize_patient_id(df_ar["AP_CNSPCN"]))

    pacientes_total = pacientes_quimio | pacientes_radio
    pacientes_ambos = pacientes_quimio & pacientes_radio
    pacientes_so_quimio = pacientes_quimio - pacientes_radio
    pacientes_so_radio = pacientes_radio - pacientes_quimio

    total_pacientes = len(pacientes_total)
    total_procedimentos_sia = total_proc_aq + total_proc_ar
    media_proc_por_paciente = total_procedimentos_sia / total_pacientes if total_pacientes > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            make_kpi_card(
                "Pacientes únicos",
                f"{total_pacientes:,}".replace(",", "."),
                "Identificados por AP_CNSPCN",
                theme_color
            ),
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            make_kpi_card(
                "Procedimentos SIA",
                f"{total_procedimentos_sia:,}".replace(",", "."),
                "Quimioterapia + Radioterapia",
                theme_color
            ),
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            make_kpi_card(
                "Média por paciente",
                f"{media_proc_por_paciente:.2f}".replace(".", ","),
                "Procedimentos SIA / paciente",
                theme_color
            ),
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            make_kpi_card(
                "Internações",
                f"{total_proc_rd:,}".replace(",", "."),
                "Registros SIH/SUS",
                theme_color
            ),
            unsafe_allow_html=True
        )

    st.markdown('<div class="section-title">📊 Procedimentos x Pacientes por Modalidade</div>', unsafe_allow_html=True)

    modalidade_df = pd.DataFrame([
        {
            "Modalidade": "Quimioterapia",
            "Procedimentos": total_proc_aq,
            "Pacientes únicos": len(pacientes_quimio)
        },
        {
            "Modalidade": "Radioterapia",
            "Procedimentos": total_proc_ar,
            "Pacientes únicos": len(pacientes_radio)
        }
    ])

    modalidade_long = modalidade_df.melt(
        id_vars="Modalidade",
        value_vars=["Procedimentos", "Pacientes únicos"],
        var_name="Métrica",
        value_name="Quantidade"
    )

    is_mama = disease == "Câncer de Mama"
    metric_colors = ['#d63384', '#e87cb4'] if is_mama else ['#0065D8', '#66b2ff']

    chart_modalidade = alt.Chart(modalidade_long).mark_bar(
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4
    ).encode(
        x=alt.X("Modalidade:N", title="Modalidade de tratamento"),
        y=alt.Y("Quantidade:Q", title="Quantidade"),
        color=alt.Color(
            "Métrica:N", 
            scale=alt.Scale(
                domain=["Procedimentos", "Pacientes únicos"],
                range=metric_colors
            ),
            title="Métrica"
        ),
        xOffset="Métrica:N",
        tooltip=[
            alt.Tooltip("Modalidade:N"),
            alt.Tooltip("Métrica:N"),
            alt.Tooltip("Quantidade:Q", title="Quantidade")
        ]
    ).properties(
        height=350
    )

    st.altair_chart(chart_modalidade, use_container_width=True)

    st.markdown('<div class="section-title">🏥 Pacientes e Procedimentos por Município Executor</div>', unsafe_allow_html=True)

    municipios = []

    if not df_aq.empty and "AP_UFMUN" in df_aq.columns and "AP_CNSPCN" in df_aq.columns:
        temp = df_aq.copy()
        temp["paciente_id"] = normalize_patient_id(temp["AP_CNSPCN"])
        temp = temp.dropna(subset=["paciente_id"])
        agg = temp.groupby("AP_UFMUN").agg(
            procedimentos=("AP_CNSPCN", "count"),
            pacientes_unicos=("paciente_id", "nunique")
        ).reset_index()
        agg["modalidade"] = "Quimioterapia"
        agg = agg.rename(columns={"AP_UFMUN": "municipio"})
        municipios.append(agg)

    if not df_ar.empty and "AP_UFMUN" in df_ar.columns and "AP_CNSPCN" in df_ar.columns:
        temp = df_ar.copy()
        temp["paciente_id"] = normalize_patient_id(temp["AP_CNSPCN"])
        temp = temp.dropna(subset=["paciente_id"])
        agg = temp.groupby("AP_UFMUN").agg(
            procedimentos=("AP_CNSPCN", "count"),
            pacientes_unicos=("paciente_id", "nunique")
        ).reset_index()
        agg["modalidade"] = "Radioterapia"
        agg = agg.rename(columns={"AP_UFMUN": "municipio"})
        municipios.append(agg)

    if municipios:
        municipio_df = pd.concat(municipios, ignore_index=True)
        municipio_resumo = municipio_df.groupby("municipio").agg(
            procedimentos=("procedimentos", "sum"),
            pacientes_unicos=("pacientes_unicos", "sum")
        ).reset_index()

        municipio_resumo["media_proc_por_paciente"] = (
            municipio_resumo["procedimentos"] / municipio_resumo["pacientes_unicos"]
        )

        municipio_resumo = municipio_resumo.sort_values("procedimentos", ascending=False).head(15)

        st.dataframe(
            municipio_resumo,
            column_config={
                "municipio": "Município executor",
                "procedimentos": st.column_config.NumberColumn("Procedimentos", format="%d"),
                "pacientes_unicos": st.column_config.NumberColumn("Pacientes únicos", format="%d"),
                "media_proc_por_paciente": st.column_config.NumberColumn("Média proc./paciente", format="%.2f"),
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
        '<div class="section-title">📌 Distribuição da intensidade de tratamento por paciente</div>',
        unsafe_allow_html=True
    )

    intensidade = patients_df.groupby("paciente_id").agg(
        total_procedimentos=("modalidade", "count")
    ).reset_index()

    def classificar_faixa(qtd):
        if qtd == 1:
            return "1 procedimento"
        elif qtd <= 5:
            return "2 a 5 procedimentos"
        elif qtd <= 10:
            return "6 a 10 procedimentos"
        elif qtd <= 20:
            return "11 a 20 procedimentos"
        else:
            return "Mais de 20 procedimentos"

    intensidade["Faixa"] = intensidade["total_procedimentos"].apply(classificar_faixa)

    faixas_ordem = [
        "1 procedimento",
        "2 a 5 procedimentos",
        "6 a 10 procedimentos",
        "11 a 20 procedimentos",
        "Mais de 20 procedimentos"
    ]

    faixa_df = (
        intensidade["Faixa"]
        .value_counts()
        .reindex(faixas_ordem, fill_value=0)
        .reset_index()
    )

    faixa_df.columns = ["Faixa de procedimentos", "Pacientes"]

    chart_faixas = alt.Chart(faixa_df).mark_bar(
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4,
        color=theme_color
    ).encode(
        x=alt.X(
            "Faixa de procedimentos:N",
            sort=faixas_ordem,
            title="Quantidade de procedimentos no ano"
        ),
        y=alt.Y("Pacientes:Q", title="Pacientes únicos"),
        tooltip=[
            alt.Tooltip("Faixa de procedimentos:N"),
            alt.Tooltip("Pacientes:Q", title="Pacientes")
        ]
    ).properties(
        height=350
    )

    st.altair_chart(chart_faixas, use_container_width=True)

    st.dataframe(
        faixa_df,
        column_config={
            "Faixa de procedimentos": "Faixa de procedimentos no ano",
            "Pacientes": st.column_config.NumberColumn("Pacientes únicos", format="%d")
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("""
    <div class="custom-alert" style="background-color: #eeeeee; border-left: 4px solid #616161; color: #212121;">
        <b>Como interpretar:</b> um paciente com muitos procedimentos não significa necessariamente piora clínica.
        Pode indicar apenas maior número de sessões registradas, principalmente em tratamentos de quimioterapia
        ou radioterapia. Esta análise serve para diferenciar volume de atendimentos de quantidade de pessoas.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🔁 Sobreposição entre Quimioterapia e Radioterapia</div>', unsafe_allow_html=True)

    # Renderizar o Diagrama de Venn com proporções e tamanho menores no final da página
    fig_venn = plot_venn_diagram(
        len(pacientes_so_quimio),
        len(pacientes_so_radio),
        len(pacientes_ambos),
        disease
    )
    col_v_l, col_v_c, col_v_r = st.columns([1.5, 3, 1.5])
    with col_v_c:
        st.pyplot(fig_venn, clear_figure=True, width="content")