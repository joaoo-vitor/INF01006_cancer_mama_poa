import streamlit as st
import pandas as pd
import altair as alt

def render_info_tab():
    st.markdown('<div class="section-title">🗃️ Origem dos dados</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-alert" style="background-color: #fff3e0; border-left: 4px solid #f57c00; color: #e65100;">
        Este painel foi consolidado a partir de diferentes bases de dados oficiais do Ministério da Saúde/DATASUS: 
        <ul style="margin-top: 8px; margin-bottom: 0px; padding-left: 20px; color: #e65100;">
            <li style="margin-bottom: 6px;"><strong>Quimioterapias e Radioterapias:</strong> Extraídas do <strong>SIA</strong> (Sistema de Informações Ambulatoriais) via servidor <strong>FTP do DATASUS</strong>.</li>
            <li style="margin-bottom: 6px;"><strong>Procedimentos:</strong> Extraídos do <strong>SIH</strong> (Sistema de Informações Hospitalares) via servidor <strong>FTP do DATASUS</strong>.</li>
            <li><strong>Exames:</strong> Obtidos do <strong>SISCAN</strong> (Sistema de Informação do Câncer) por meio da plataforma <strong>TABNET</strong>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚙️ Tratamento dos dados</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-alert" style="background-color: #fff3e0; border-left: 4px solid #f57c00; color: #e65100;">
        O pipeline de preparação, limpeza e estruturação das bases brutas envolveu as seguintes etapas:
        <ul style="margin-top: 8px; margin-bottom: 0px; padding-left: 20px; color: #e65100;">
            <li style="margin-bottom: 6px;"><strong>Conversão de Formato:</strong> Os arquivos extraídos do servidor FTP foram convertidos do formato compactado proprietário (<strong>.dbc</strong>) para texto plano (<strong>.csv</strong>).</li>
            <li style="margin-bottom: 6px;"><strong>Decodificação de Variáveis:</strong> As informações internas dos arquivos foram traduzidas e decodificadas com o suporte de arquivos de definição auxiliares (<strong>.cnv</strong>).</li>
            <li style="margin-bottom: 6px;"><strong>Mapeamento do SIGTAP:</strong> Utilizou-se a Tabela Unificada do SUS (SIGTAP) como referência para traduzir os códigos numéricos de tratamentos e procedimentos em descrições claras.</li>
            <li style="margin-bottom: 6px;"><strong>Definição de Escopo (CID):</strong> Os registros foram filtrados com base no Código Internacional de Doenças (CID) para isolar exclusivamente os casos de <strong>câncer de mama</strong> e <strong>câncer de colo de útero</strong>, descartando os demais dados.</li>
            <li><strong>Agregação Temporal:</strong> A produção, que é originalmente disponibilizada pelo DATASUS em arquivos mensais, foi consolidada e agrupada para compor o panorama anual de <strong>2025</strong>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Análises e visualizações</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="custom-alert" style="background-color: #fff3e0; border-left: 4px solid #f57c00; color: #e65100;">
        A etapa final envolveu a exploração analítica dos dados estruturados e a construção da interface interativa:
        <ul style="margin-top: 8px; margin-bottom: 0px; padding-left: 20px; color: #e65100;">
            <li style="margin-bottom: 6px;"><strong>Métricas Investigadas:</strong> Foram conduzidas análises aprofundadas sobre o tipo, a quantidade e os custos associados a cada exame, tratamento e procedimento.</li>
            <li style="margin-bottom: 6px;"><strong>Perfil e Geografia:</strong> Avaliou-se o perfil dos pacientes, bem como a distribuição geográfica e a regionalização dos atendimentos prestados.</li>
            <li style="margin-bottom: 6px;"><strong>Interface Gráfica:</strong> Construiu-se um dashboard composto por gráficos interativos, traduzindo dados complexos em representações visuais intuitivas.</li>
            <li><strong>Exploração Dinâmica:</strong> O painel permite a navegação personalizada através de filtros integrados por <strong>tipo de doença</strong>, <strong>cidade</strong> e <strong>mês do ano</strong>.</li>
        </ul
    </div>
    """, unsafe_allow_html=True)
