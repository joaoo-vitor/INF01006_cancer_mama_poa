import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

# Desativa o limite de 5000 linhas do Altair para evitar MaxRowsError no Jupyter Notebook
alt.data_transformers.disable_max_rows()

def plot_chemotherapies_by_month(df, city='Porto Alegre', months=None):
    """
    Gera um gráfico de barras e linha mostrando o número de quimioterapias realizadas 
    no município especificado para cada mês do ano de 2025 (Matplotlib).
    """
    # 1. Filtrar pelo estabelecimento localizado no município (AP_UFMUN)
    df_filtered = df.copy()
    if city and city != "Todo o Estado":
        df_filtered = df_filtered[df_filtered['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
        
    # Filtrar por meses
    if months:
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_filtered = df_filtered[(df_filtered['AP_MVM'] >= start_m) & (df_filtered['AP_MVM'] <= end_m)]
        
    # 2. Agrupar por mês de processamento/movimento (AP_MVM)
    monthly_counts = df_filtered.groupby('AP_MVM').size().reset_index(name='Quantidade')
    
    # Mapeamento para garantir que todos os 12 meses estejam no eixo X e com nomes corretos em português
    months_map = {
        202501: 'Jan', 202502: 'Fev', 202503: 'Mar', 202504: 'Abr',
        202505: 'Mai', 202506: 'Jun', 202507: 'Jul', 202508: 'Ago',
        202509: 'Set', 202510: 'Out', 202511: 'Nov', 202512: 'Dez'
    }
    
    # Criar um DataFrame de base com todos os meses de 2025 para evitar buracos
    all_months = pd.DataFrame({'AP_MVM': list(months_map.keys()), 'Mes': list(months_map.values())})
    
    # Fazer merge e preencher meses sem registros com 0
    monthly_counts = pd.merge(all_months, monthly_counts, on='AP_MVM', how='left').fillna({'Quantidade': 0})
    monthly_counts['Quantidade'] = monthly_counts['Quantidade'].astype(int)
    
    if months:
        monthly_counts = monthly_counts.iloc[months[0]-1:months[1]]
    
    # 3. Detectar o tipo de câncer (Mama vs Colo) para personalizar o visual
    is_mama = False
    if 'AQ_CID10' in df.columns:
        is_mama = df['AQ_CID10'].astype(str).str.startswith('C50').any()
    elif 'AP_PRIPAL' in df.columns:
        is_mama = df['AP_PRIPAL'].astype(str).str.lower().str.contains('mama').any()
        
    if is_mama:
        cancer_type = 'Câncer de Mama'
        main_color = '#d63384'  # Rosa (Outubro Rosa)
    else:
        cancer_type = 'Câncer de Colo de Útero'
        main_color = '#008080'  # Teal/Ciano (Março Lilás/Teal)
        
    # Configurar estilo moderno do Seaborn
    sns.set_theme(style="whitegrid")
    
    # Criar a figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Gráfico de Barras com transparência sutil
    sns.barplot(
        data=monthly_counts,
        x='Mes',
        y='Quantidade',
        color=main_color,
        alpha=0.7,
        ax=ax,
        edgecolor=main_color,
        linewidth=1.5
    )
    
    # Gráfico de Linha por cima para realçar a tendência
    sns.lineplot(
        data=monthly_counts,
        x='Mes',
        y='Quantidade',
        color=main_color,
        marker='o',
        linewidth=2.5,
        markersize=8,
        ax=ax
    )
    
    # Adicionar os valores acima de cada barra/ponto
    for idx, row in monthly_counts.reset_index(drop=True).iterrows():
        ax.text(
            idx,
            row['Quantidade'] + (monthly_counts['Quantidade'].max() * 0.015),
            f"{row['Quantidade']:,}".replace(',', '.'),
            ha='center',
            va='bottom',
            fontsize=10,
            fontweight='bold',
            color='#333333'
        )
        
    # Customizar títulos e labels
    location_title = city if city else "Rio Grande do Sul"
    ax.set_title(
        f"Quimioterapias realizadas em {location_title} por Mês (2025)\n({cancer_type})",
        fontsize=14,
        fontweight='bold',
        pad=20,
        color='#222222'
    )
    ax.set_xlabel("Mês de Processamento (2025)", fontsize=11, labelpad=10, color='#444444')
    ax.set_ylabel("Número de Procedimentos", fontsize=11, labelpad=10, color='#444444')
    
    # Ajustar limites do eixo Y para dar espaço aos rótulos dos dados
    ax.set_ylim(0, monthly_counts['Quantidade'].max() * 1.15)
    
    # Remover bordas desnecessárias
    sns.despine(left=True, bottom=True)
    
    plt.tight_layout()
    return fig, ax

def plot_stacked_chemotherapies_by_month(df_colo, df_mama, city='Porto Alegre', months=None):
    """
    Gera um gráfico de barras empilhadas mostrando a quantidade de quimioterapias
    realizadas no município especificado para cada mês do ano de 2025 (Matplotlib).
    """
    # 1. Filtrar pelo estabelecimento localizado no município (AP_UFMUN)
    df_colo_filtered = df_colo.copy()
    df_mama_filtered = df_mama.copy()
    if city and city != "Todo o Estado":
        df_colo_filtered = df_colo_filtered[df_colo_filtered['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
        df_mama_filtered = df_mama_filtered[df_mama_filtered['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
        
    # Filtrar por meses
    if months:
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_colo_filtered = df_colo_filtered[(df_colo_filtered['AP_MVM'] >= start_m) & (df_colo_filtered['AP_MVM'] <= end_m)]
        df_mama_filtered = df_mama_filtered[(df_mama_filtered['AP_MVM'] >= start_m) & (df_mama_filtered['AP_MVM'] <= end_m)]
        
    # 2. Agrupar por mês de processamento/movimento (AP_MVM)
    colo_counts = df_colo_filtered.groupby('AP_MVM').size().reset_index(name='Colo')
    mama_counts = df_mama_filtered.groupby('AP_MVM').size().reset_index(name='Mama')
    
    # Mapeamento para garantir que todos os 12 meses estejam no eixo X
    months_map = {
        202501: 'Jan', 202502: 'Fev', 202503: 'Mar', 202504: 'Abr',
        202505: 'Mai', 202506: 'Jun', 202507: 'Jul', 202508: 'Ago',
        202509: 'Set', 202510: 'Out', 202511: 'Nov', 202512: 'Dez'
    }
    
    all_months = pd.DataFrame({'AP_MVM': list(months_map.keys()), 'Mes': list(months_map.values())})
    
    # Fazer merge e preencher meses sem registros com 0
    df_combined = pd.merge(all_months, colo_counts, on='AP_MVM', how='left').fillna(0)
    df_combined = pd.merge(df_combined, mama_counts, on='AP_MVM', how='left').fillna(0)
    
    df_combined['Colo'] = df_combined['Colo'].astype(int)
    df_combined['Mama'] = df_combined['Mama'].astype(int)
    df_combined['Total'] = df_combined['Colo'] + df_combined['Mama']
    
    if months:
        df_combined = df_combined.iloc[months[0]-1:months[1]]
        
    # Configurar estilo moderno do Seaborn
    sns.set_theme(style="whitegrid")
    
    # Criar a figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Cores
    color_mama = '#d63384'  # Rosa para Mama
    color_colo = '#008080'  # Teal para Colo
    
    # Gráfico de Barras Empilhadas
    # Mama na base (bottom=0)
    ax.bar(
        df_combined['Mes'],
        df_combined['Mama'],
        label='Câncer de Mama',
        color=color_mama,
        alpha=0.75,
        edgecolor=color_mama,
        linewidth=1.2
    )
    
    # Colo empilhado em cima do Mama (bottom=Mama)
    ax.bar(
        df_combined['Mes'],
        df_combined['Colo'],
        bottom=df_combined['Mama'],
        label='Câncer de Colo de Útero',
        color=color_colo,
        alpha=0.75,
        edgecolor=color_colo,
        linewidth=1.2
    )
    
    # Adicionar os rótulos de dados
    for idx, row in df_combined.reset_index(drop=True).iterrows():
        total = row['Total']
        mama = row['Mama']
        colo = row['Colo']
        
        if total == 0:
            continue
            
        # Rótulo de Total no topo da barra empilhada
        ax.text(
            idx,
            total + (df_combined['Total'].max() * 0.015),
            f"{total:,}".replace(',', '.'),
            ha='center',
            va='bottom',
            fontsize=10,
            fontweight='bold',
            color='#222222'
        )
        
        # Rótulo interno para o segmento de Mama
        if mama > (df_combined['Total'].max() * 0.05):
            ax.text(
                idx,
                mama / 2,
                f"{mama:,}".replace(',', '.'),
                ha='center',
                va='center',
                fontsize=9,
                color='white',
                fontweight='semibold'
            )
            
        # Rótulo interno para o segmento de Colo
        if colo > (df_combined['Total'].max() * 0.05):
            ax.text(
                idx,
                mama + (colo / 2),
                f"{colo:,}".replace(',', '.'),
                ha='center',
                va='center',
                fontsize=9,
                color='white',
                fontweight='semibold'
            )
            
    # Customizar títulos e labels
    location_title = city if city else "Rio Grande do Sul"
    ax.set_title(
        f"Quimioterapias em {location_title} por Mês (2025)\nComparativo de Câncer de Mama e Colo de Útero",
        fontsize=14,
        fontweight='bold',
        pad=20,
        color='#222222'
    )
    ax.set_xlabel("Mês de Processamento (2025)", fontsize=11, labelpad=10, color='#444444')
    ax.set_ylabel("Número de Procedimentos", fontsize=11, labelpad=10, color='#444444')
    
    # Ajustar limites do eixo Y para dar espaço aos rótulos dos dados
    ax.set_ylim(0, df_combined['Total'].max() * 1.15)
    
    # Adicionar legenda moderna
    ax.legend(
        loc='upper right',
        frameon=True,
        facecolor='white',
        edgecolor='none',
        shadow=True,
        title="Tipo de Câncer",
        title_fontsize='10'
    )
    
    # Remover bordas desnecessárias
    sns.despine(left=True, bottom=True)
    
    plt.tight_layout()
    return fig, ax

def _plot_residents_vs_non_residents(df, treatment_type, city='Porto Alegre', months=None):
    """
    Função auxiliar genérica para gerar um gráfico de barras empilhadas 
    contando os residentes do município de escolha vs pessoas de outros municípios (Matplotlib).
    """
    # 1. Filtrar pelo estabelecimento localizado no município (AP_UFMUN)
    df_filtered = df.copy()
    if city and city != "Todo o Estado":
        df_filtered = df_filtered[df_filtered['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
        
    # Filtrar por meses
    if months:
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_filtered = df_filtered[(df_filtered['AP_MVM'] >= start_m) & (df_filtered['AP_MVM'] <= end_m)]
        
    # 2. Classificar residentes da cidade selecionada vs outros municípios
    city_name = city if (city and city != "Todo o Estado") else 'Porto Alegre'
    df_filtered['Residente'] = df_filtered['AP_MUNPCN'].astype(str).str.lower().str.strip() == city_name.lower().strip()
    
    # 3. Agrupar por mês e se é residente
    counts = df_filtered.groupby(['AP_MVM', 'Residente']).size().unstack(fill_value=0)
    
    # Garantir que ambas as colunas existam
    if True not in counts.columns:
        counts[True] = 0
    if False not in counts.columns:
        counts[False] = 0
        
    counts = counts.rename(columns={True: 'Residente', False: 'Não Residente'})
    counts = counts[['Residente', 'Não Residente']]
    
    # Mapeamento de meses de 2025
    months_map = {
        202501: 'Jan', 202502: 'Fev', 202503: 'Mar', 202504: 'Abr',
        202505: 'Mai', 202506: 'Jun', 202507: 'Jul', 202508: 'Ago',
        202509: 'Set', 202510: 'Out', 202511: 'Nov', 202512: 'Dez'
    }
    
    df_months = pd.DataFrame(index=months_map.keys())
    counts = df_months.join(counts).fillna(0).astype(int)
    counts['Mes'] = counts.index.map(months_map)
    
    if months:
        counts = counts.iloc[months[0]-1:months[1]]
        
    # 4. Detectar dinamicamente o tipo de câncer
    is_colo = False
    is_mama = False
    
    for col in ['AQ_CID10', 'AR_CID10']:
        if col in df.columns:
            cids = df[col].astype(str)
            if cids.str.startswith('C50').any():
                is_mama = True
            if cids.str.startswith('C53').any() or cids.str.startswith('C54').any():
                is_colo = True
                
    if 'AP_PRIPAL' in df.columns:
        vals = df['AP_PRIPAL'].astype(str).str.lower()
        if vals.str.contains('mama').any():
            is_mama = True
        if vals.str.contains('colo').any() or vals.str.contains('uterino').any():
            is_colo = True
            
    if is_mama and is_colo:
        cancer_type = 'Câncer de Mama e Colo de Útero'
        color_res = '#0d6efd'   # Azul Escuro
        color_nres = '#9ec5fe'  # Azul Claro
    elif is_mama:
        cancer_type = 'Câncer de Mama'
        color_res = '#d63384'   # Rosa Escuro
        color_nres = '#ff9ebb'  # Rosa Claro
    else:
        cancer_type = 'Câncer de Colo de Útero'
        color_res = '#008080'   # Teal Escuro
        color_nres = '#80cbc4'  # Teal Claro/Mint
        
    # Estilo Seaborn
    sns.set_theme(style="whitegrid")
    
    # Criar a figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Barras empilhadas
    # Residentes na base
    ax.bar(
        counts['Mes'],
        counts['Residente'],
        label=f'Residente de {city_name}',
        color=color_res,
        alpha=0.8,
        edgecolor=color_res,
        linewidth=1.2
    )
    
    # Não Residentes no topo
    ax.bar(
        counts['Mes'],
        counts['Não Residente'],
        bottom=counts['Residente'],
        label='Residente de Outro Município',
        color=color_nres,
        alpha=0.8,
        edgecolor=color_nres,
        linewidth=1.2
    )
    
    # Adicionar os rótulos de dados
    max_val = (counts['Residente'] + counts['Não Residente']).max()
    for idx, row in counts.reset_index(drop=True).iterrows():
        res = row['Residente']
        nres = row['Não Residente']
        total = res + nres
        
        if total == 0:
            continue
            
        # Total no topo da barra
        ax.text(
            idx,
            total + (max_val * 0.015),
            f"{total:,}".replace(',', '.'),
            ha='center',
            va='bottom',
            fontsize=10,
            fontweight='bold',
            color='#222222'
        )
        
        # Residentes (interno)
        if res > (max_val * 0.05):
            ax.text(
                idx,
                res / 2,
                f"{res:,}".replace(',', '.'),
                ha='center',
                va='center',
                fontsize=9,
                color='white',
                fontweight='semibold'
            )
            
        # Não Residentes (interno)
        if nres > (max_val * 0.05):
            ax.text(
                idx,
                res + (nres / 2),
                f"{nres:,}".replace(',', '.'),
                ha='center',
                va='center',
                fontsize=9,
                color='#222222',
                fontweight='semibold'
            )
            
    # Título e labels
    location_title = city if city else "Rio Grande do Sul"
    ax.set_title(
        f"{treatment_type}s em {location_title} por Mês (2025)\nAtendimentos a Residentes vs. Não Residentes ({cancer_type})",
        fontsize=14,
        fontweight='bold',
        pad=20,
        color='#222222'
    )
    ax.set_xlabel("Mês de Processamento (2025)", fontsize=11, labelpad=10, color='#444444')
    ax.set_ylabel("Número de Procedimentos", fontsize=11, labelpad=10, color='#444444')
    
    ax.set_ylim(0, max_val * 1.15)
    
    # Legenda
    ax.legend(
        loc='upper right',
        frameon=True,
        facecolor='white',
        edgecolor='none',
        shadow=True,
        title="Origem do Paciente",
        title_fontsize='10'
    )
    
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    return fig, ax

def plot_chemo_residents_vs_non_residents(df, city='Porto Alegre', months=None):
    """
    Gera um gráfico de barras empilhadas comparando a quantidade de quimioterapias 
    no município selecionado entre pacientes residentes e pacientes de outros municípios.
    """
    return _plot_residents_vs_non_residents(df, "Quimioterapia", city, months)

def plot_radio_residents_vs_non_residents(df, city='Porto Alegre', months=None):
    """
    Gera um gráfico de barras empilhadas comparando a quantidade de radioterapias 
    no município selecionado entre pacientes residentes e pacientes de outros municípios.
    """
    return _plot_residents_vs_non_residents(df, "Radioterapia", city, months)

def plot_chemo_stage_comparison(df_colo, df_mama, city='Porto Alegre', months=None):
    """
    Gera dois gráficos de rosca lado a lado comparando a proporção de estágios 
    iniciais (0, 1 e 2) vs. avançados/metastáticos (3 e 4) no início do tratamento 
    quimioterápico em Porto Alegre/RS (Matplotlib).
    """
    # 1. Filtrar pelo estabelecimento localizado no município (AP_UFMUN)
    df_colo_poa = df_colo.copy()
    df_mama_poa = df_mama.copy()
    if city and city != "Todo o Estado":
        df_colo_poa = df_colo_poa[df_colo_poa['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
        df_mama_poa = df_mama_poa[df_mama_poa['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
        
    # Filtrar por meses
    if months:
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_colo_poa = df_colo_poa[(df_colo_poa['AP_MVM'] >= start_m) & (df_colo_poa['AP_MVM'] <= end_m)]
        df_mama_poa = df_mama_poa[(df_mama_poa['AP_MVM'] >= start_m) & (df_mama_poa['AP_MVM'] <= end_m)]
        
    # Função para classificar o estágio
    def classify_stage(val):
        val_str = str(val).strip().upper()
        if val_str in ['0_ESTADIO', '0.0', '0', '1_ESTADIO', '1.0', '1', '2_ESTADIO', '2.0', '2']:
            return 'Inicial (Estágios 0-2)'
        elif val_str in ['3_ESTADIO', '3.0', '3', '4_ESTADIO', '4.0', '4']:
            return 'Avançado (Estágios 3-4)'
        return None
            
    # Classificar e contar
    colo_stages = df_colo_poa['AQ_ESTADI'].apply(classify_stage).dropna().value_counts()
    mama_stages = df_mama_poa['AQ_ESTADI'].apply(classify_stage).dropna().value_counts()
    
    # Garantir a presença de ambas as categorias
    categories = ['Inicial (Estágios 0-2)', 'Avançado (Estágios 3-4)']
    colo_data = [colo_stages.get(cat, 0) for cat in categories]
    mama_data = [mama_stages.get(cat, 0) for cat in categories]
    
    # Configurar estilo moderno do Seaborn
    sns.set_theme(style="white")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    # Cores
    colors_colo = ['#008080', '#e57373'] # Teal vs Soft Red
    colors_mama = ['#d63384', '#e57373'] # Pink vs Soft Red
    
    # --- Donut Chart Colo ---
    ax_colo = axes[0]
    total_colo = sum(colo_data)
    if total_colo > 0:
        wedges_colo, _, autotexts_colo = ax_colo.pie(
            colo_data,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_colo,
            pctdistance=0.7,
            textprops=dict(color='white', weight='bold', fontsize=12),
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
        )
        for autotext in autotexts_colo:
            autotext.set_fontsize(11)
            
        location_label = city if city else "Todo o Estado"
        ax_colo.text(
            0, 0,
            f"Colo de Útero\n{location_label}\n{total_colo:,}".replace(',', '.'),
            ha='center', va='center',
            fontsize=12, fontweight='bold',
            color='#333333'
        )
    ax_colo.set_title("Câncer de Colo de Útero", fontsize=14, fontweight='bold', pad=10, color='#222222')
    
    # --- Donut Chart Mama ---
    ax_mama = axes[1]
    total_mama = sum(mama_data)
    if total_mama > 0:
        wedges_mama, _, autotexts_mama = ax_mama.pie(
            mama_data,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors_mama,
            pctdistance=0.7,
            textprops=dict(color='white', weight='bold', fontsize=12),
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
        )
        for autotext in autotexts_mama:
            autotext.set_fontsize(11)
            
        ax_mama.text(
            0, 0,
            f"Mama\n{location_label}\n{total_mama:,}".replace(',', '.'),
            ha='center', va='center',
            fontsize=12, fontweight='bold',
            color='#333333'
        )
    ax_mama.set_title("Câncer de Mama", fontsize=14, fontweight='bold', pad=10, color='#222222')
    
    # Adicionar legenda única para a figura
    fig.legend(
        wedges_mama, 
        categories,
        loc='lower center',
        ncol=2,
        frameon=True,
        facecolor='white',
        edgecolor='none',
        shadow=True,
        fontsize=11
    )
    
    # Título Geral
    fig.suptitle(
        f"Estadiamento no Início do Tratamento Quimioterápico em {location_label} (2025)\nDiagnóstico Precoce vs. Diagnóstico Tardio",
        fontsize=16,
        fontweight='bold',
        color='#222222',
        y=0.98
    )
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.93])
    return fig, axes

def plot_distribuicao_permanencia(df, tipo_cancer="", city='Porto Alegre', months=None):
    """
    Gera um gráfico boxplot de distribuição do tempo de permanência hospitalar (DIAS_PERM)
    por Diagnóstico Principal (DIAG_PRINC) de forma horizontal utilizando o Altair.
    Garante que todos os rótulos do eixo Y (CID-10) apareçam legivelmente.
    """
    df_filtered = df.copy()
    if city and city != "Todo o Estado":
        df_filtered = df_filtered[df_filtered['MUNIC_MOV'].astype(str).str.lower().str.strip() == city.lower().strip()]
    if months:
        df_filtered['ANO_MES'] = df_filtered['ANO_CMPT'].astype(int) * 100 + df_filtered['MES_CMPT'].astype(int)
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_filtered = df_filtered[(df_filtered['ANO_MES'] >= start_m) & (df_filtered['ANO_MES'] <= end_m)]
        
    df_plot = df_filtered[['DIAG_PRINC', 'DIAS_PERM']].dropna()
    
    location_label = city if city else "Rio Grande do Sul"
    
    boxplot = alt.Chart(df_plot).mark_boxplot(
        extent='min-max',
        size=20,
        color='#2b5c8f'
    ).encode(
        y=alt.Y(
            'DIAG_PRINC:N', 
            title='Diagnóstico Principal (CID-10)',
            scale=alt.Scale(padding=0.5),
            axis=alt.Axis(
                labelFontSize=10
            )
        ),
        x=alt.X(
            'DIAS_PERM:Q', 
            title='Tempo de Permanência (Dias)'
        ),
        tooltip=[
            alt.Tooltip('DIAG_PRINC:N', title='CID'),
            alt.Tooltip('DIAS_PERM:Q', title='Dias de Internação')
        ]
    ).properties(
        title={
            "text": f"Tempo de Permanência Hospitalar por CID - Câncer de {tipo_cancer}",
            "subtitle": f"Internações SIH/SUS no município de {location_label}"
        },
        width='container',
        height=350
    ).configure_title(
        fontSize=15,
        subtitleFontSize=11,
        anchor='start'
    )
    
    return boxplot

def plot_hospitalizacoes_por_cid_altair(df, tipo_cancer="", city='Porto Alegre', months=None):
    """
    Gera um gráfico de pizza mostrando a quantidade de internações por Diagnóstico Principal (DIAG_PRINC/CID-10).
    """
    df_filtered = df.copy()
    if city and city != "Todo o Estado":
        df_filtered = df_filtered[df_filtered['MUNIC_MOV'].astype(str).str.lower().str.strip() == city.lower().strip()]
    if months:
        df_filtered['ANO_MES'] = df_filtered['ANO_CMPT'].astype(int) * 100 + df_filtered['MES_CMPT'].astype(int)
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_filtered = df_filtered[(df_filtered['ANO_MES'] >= start_m) & (df_filtered['ANO_MES'] <= end_m)]
        
    df_plot = df_filtered[['DIAG_PRINC']].dropna()
    
    location_label = city if city else "Rio Grande do Sul"
    
    pie = alt.Chart(df_plot).mark_arc().encode(
        theta=alt.Theta('count():Q', title='Quantidade de Internações'),
        color=alt.Color(
            'DIAG_PRINC:N', 
            title='Código CID-10', 
            scale=alt.Scale(scheme='tableau10')
        ),
        tooltip=[
            alt.Tooltip('DIAG_PRINC:N', title='CID-10'),
            alt.Tooltip('count():Q', title='Internações')
        ]
    ).properties(
        title={
            "text": f"Distribuição de Internações por CID - Câncer de {tipo_cancer}",
            "subtitle": f"Volume total e proporcional de internações hospitalares em {location_label} (SIH/SUS)"
        },
        width='container',
        height=380
    ).configure_title(
        fontSize=15,
        subtitleFontSize=11,
        anchor='start'
    )
    
    return pie

def plot_custos_hospitalares(df, tipo_cancer="", city='Porto Alegre', months=None):
    """
    Gera um gráfico de barras empilhadas comparando o total gasto (VAL_SH vs VAL_SP)
    por Diagnóstico Principal (DIAG_PRINC) utilizando o Altair.
    """
    df_filtered = df.copy()
    if city and city != "Todo o Estado":
        df_filtered = df_filtered[df_filtered['MUNIC_MOV'].astype(str).str.lower().str.strip() == city.lower().strip()]
    if months:
        df_filtered['ANO_MES'] = df_filtered['ANO_CMPT'].astype(int) * 100 + df_filtered['MES_CMPT'].astype(int)
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_filtered = df_filtered[(df_filtered['ANO_MES'] >= start_m) & (df_filtered['ANO_MES'] <= end_m)]
        
    df_gasto = df_filtered[['DIAG_PRINC', 'VAL_SH', 'VAL_SP']].dropna()
    df_agrupado = df_gasto.groupby('DIAG_PRINC', as_index=False)[['VAL_SH', 'VAL_SP']].sum()
    
    df_long = df_agrupado.melt(
        id_vars=['DIAG_PRINC'], 
        value_vars=['VAL_SH', 'VAL_SP'],
        var_name='Tipo de Custo', 
        value_name='Valor (R$)'
    )
    
    mapeamento_nomes = {
        'VAL_SH': 'Serviços Hospitalares (VAL_SH)',
        'VAL_SP': 'Serviços Profissionais (VAL_SP)'
    }
    df_long['Tipo de Custo'] = df_long['Tipo de Custo'].map(mapeamento_nomes)

    location_label = city if city else "Rio Grande do Sul"

    grafico_barras = alt.Chart(df_long).mark_bar().encode(
        x=alt.X(
            'DIAG_PRINC:N', 
            title='Diagnóstico Principal (CID-10)',
            axis=alt.Axis(
                labelAngle=-45, 
                labelLimit=0, 
                labelOverlap=False,
                labelFontSize=10
            )
        ),
        y=alt.Y(
            'Valor (R$):Q', 
            title='Gasto Total Acumulado (R$)'
        ),
        color=alt.Color(
            'Tipo de Custo:N',
            title='Divisão dos Custos',
            scale=alt.Scale(scheme='tableau10')
        ),
        tooltip=[
            alt.Tooltip('DIAG_PRINC:N', title='CID'),
            alt.Tooltip('Tipo de Custo:N', title='Tipo de Gasto'),
            alt.Tooltip('Valor (R$):Q', title='Total (R$)', format=',.2f')
        ]
    ).properties(
        title={
            "text": f"Comparativo de Gastos Hospitalares (VAL_SH vs VAL_SP) - Câncer de {tipo_cancer}",
            "subtitle": f"Valores acumulados de internações no município de {location_label}"
        },
        width='container',
        height=550
    ).configure_title(
        fontSize=15,
        subtitleFontSize=11,
        anchor='middle'
    )
    
    return grafico_barras


# ==========================================
# NOVAS VERSÕES ALTAIR (PARA O STREAMLIT)
# ==========================================

def plot_chemotherapies_by_month_altair(df, city='Porto Alegre', months=None, color='#008080'):
    """
    Gera uma visualização interativa do Altair mostrando o número de quimioterapias por mês.
    """
    df_filtered = df.copy()
    if city and city != "Todo o Estado":
        df_filtered = df_filtered[df_filtered['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
    if months:
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_filtered = df_filtered[(df_filtered['AP_MVM'] >= start_m) & (df_filtered['AP_MVM'] <= end_m)]
        
    monthly_counts = df_filtered.groupby('AP_MVM').size().reset_index(name='Quantidade')
    
    months_map = {
        202501: 'Jan', 202502: 'Fev', 202503: 'Mar', 202504: 'Abr',
        202505: 'Mai', 202506: 'Jun', 202507: 'Jul', 202508: 'Ago',
        202509: 'Set', 202510: 'Out', 202511: 'Nov', 202512: 'Dez'
    }
    all_months = pd.DataFrame({'AP_MVM': list(months_map.keys()), 'Mes': list(months_map.values())})
    monthly_counts = pd.merge(all_months, monthly_counts, on='AP_MVM', how='left').fillna({'Quantidade': 0})
    monthly_counts['Quantidade'] = monthly_counts['Quantidade'].astype(int)
    
    if months:
        monthly_counts = monthly_counts.iloc[months[0]-1:months[1]]
        
    # Detectar o tipo de câncer (Mama vs Colo)
    is_mama = False
    if 'AQ_CID10' in df.columns:
        is_mama = df['AQ_CID10'].astype(str).str.startswith('C50').any()
    elif 'AP_PRIPAL' in df.columns:
        is_mama = df['AP_PRIPAL'].astype(str).str.lower().str.contains('mama').any()
    cancer_type = 'Câncer de Mama' if is_mama else 'Câncer de Colo de Útero'
    
    location_label = city if city else "Rio Grande do Sul"
    
    # Gráfico de barras interativo
    bar = alt.Chart(monthly_counts).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=color, opacity=0.85).encode(
        x=alt.X('Mes:N', sort=None, title='Mês de Processamento'),
        y=alt.Y('Quantidade:Q', title='Número de Procedimentos'),
        tooltip=[alt.Tooltip('Mes:N', title='Mês'), alt.Tooltip('Quantidade:Q', title='Procedimentos')]
    )
    
    # Linha e marcadores por cima
    line = alt.Chart(monthly_counts).mark_line(color=color, strokeWidth=3, point=alt.OverlayMarkDef(color=color, size=60)).encode(
        x=alt.X('Mes:N', sort=None),
        y=alt.Y('Quantidade:Q')
    )
    
    chart = (bar + line).properties(
        title={
            "text": f"Quimioterapias em {location_label} por Mês (2025)",
            "subtitle": f"Análise de procedimentos para {cancer_type} - SIA/SUS"
        },
        width='container',
        height=350
    ).configure_title(
        fontSize=15,
        subtitleFontSize=11,
        anchor='start',
        color='#333333'
    )
    return chart

def plot_stacked_chemotherapies_by_month_altair(df_colo, df_mama, city='Porto Alegre', months=None):
    """
    Gera um gráfico comparativo de barras empilhadas interativo no Altair para ambos os cânceres.
    """
    df_colo_f = df_colo.copy()
    df_mama_f = df_mama.copy()
    if city and city != "Todo o Estado":
        df_colo_f = df_colo_f[df_colo_f['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
        df_mama_f = df_mama_f[df_mama_f['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
    if months:
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_colo_f = df_colo_f[(df_colo_f['AP_MVM'] >= start_m) & (df_colo_f['AP_MVM'] <= end_m)]
        df_mama_f = df_mama_f[(df_mama_f['AP_MVM'] >= start_m) & (df_mama_f['AP_MVM'] <= end_m)]
        
    colo_counts = df_colo_f.groupby('AP_MVM').size().reset_index(name='Colo')
    mama_counts = df_mama_f.groupby('AP_MVM').size().reset_index(name='Mama')
    
    months_map = {
        202501: 'Jan', 202502: 'Fev', 202503: 'Mar', 202504: 'Abr',
        202505: 'Mai', 202506: 'Jun', 202507: 'Jul', 202508: 'Ago',
        202509: 'Set', 202510: 'Out', 202511: 'Nov', 202512: 'Dez'
    }
    all_months = pd.DataFrame({'AP_MVM': list(months_map.keys()), 'Mes': list(months_map.values())})
    df_combined = pd.merge(all_months, colo_counts, on='AP_MVM', how='left').fillna(0)
    df_combined = pd.merge(df_combined, mama_counts, on='AP_MVM', how='left').fillna(0)
    
    df_combined['Colo'] = df_combined['Colo'].astype(int)
    df_combined['Mama'] = df_combined['Mama'].astype(int)
    
    if months:
        df_combined = df_combined.iloc[months[0]-1:months[1]]
        
    df_long = df_combined.melt(id_vars=['Mes'], value_vars=['Colo', 'Mama'], var_name='Cancer', value_name='Quantidade')
    df_long['Cancer'] = df_long['Cancer'].map({'Colo': 'Câncer de Colo de Útero', 'Mama': 'Câncer de Mama'})
    
    location_label = city if city else "Rio Grande do Sul"
    
    chart = alt.Chart(df_long).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('Mes:N', sort=None, title='Mês de Processamento'),
        y=alt.Y('Quantidade:Q', title='Número de Procedimentos'),
        color=alt.Color('Cancer:N', scale=alt.Scale(domain=['Câncer de Colo de Útero', 'Câncer de Mama'], range=['#008080', '#d63384']), title='Tipo de Câncer'),
        tooltip=[alt.Tooltip('Mes:N', title='Mês'), alt.Tooltip('Cancer:N', title='Câncer'), alt.Tooltip('Quantidade:Q', title='Procedimentos')]
    ).properties(
        title={
            "text": f"Comparativo de Quimioterapias em {location_label} por Mês (2025)",
            "subtitle": "Gráfico de barras empilhadas comparando câncer de mama e colo de útero"
        },
        width='container',
        height=350
    ).configure_title(
        fontSize=15,
        subtitleFontSize=11,
        anchor='start'
    )
    return chart

def plot_residents_vs_non_residents_altair(df, treatment_type="Quimioterapia", city='Porto Alegre', months=None):
    """
    Gera um gráfico de barras empilhadas interativo no Altair comparando residentes vs. não residentes.
    """
    df_filtered = df.copy()
    if city and city != "Todo o Estado":
        df_filtered = df_filtered[df_filtered['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
    if months:
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_filtered = df_filtered[(df_filtered['AP_MVM'] >= start_m) & (df_filtered['AP_MVM'] <= end_m)]
        
    city_name = city if (city and city != "Todo o Estado") else 'Porto Alegre'
    df_filtered['Residente'] = df_filtered['AP_MUNPCN'].astype(str).str.lower().str.strip() == city_name.lower().strip()
    counts = df_filtered.groupby(['AP_MVM', 'Residente']).size().unstack(fill_value=0)
    
    if True not in counts.columns:
        counts[True] = 0
    if False not in counts.columns:
        counts[False] = 0
        
    counts = counts.rename(columns={True: f'Residente de {city_name}', False: 'Residente de Outro Município'})
    
    months_map = {
        202501: 'Jan', 202502: 'Fev', 202503: 'Mar', 202504: 'Abr',
        202505: 'Mai', 202506: 'Jun', 202507: 'Jul', 202508: 'Ago',
        202509: 'Set', 202510: 'Out', 202511: 'Nov', 202512: 'Dez'
    }
    df_months = pd.DataFrame(index=months_map.keys())
    counts = df_months.join(counts).fillna(0).astype(int)
    counts['Mes'] = counts.index.map(months_map)
    
    if months:
        counts = counts.iloc[months[0]-1:months[1]]
        
    df_long = counts.melt(id_vars=['Mes'], value_vars=[f'Residente de {city_name}', 'Residente de Outro Município'], var_name='Origem', value_name='Quantidade')
    
    # Cores
    is_colo = False
    is_mama = False
    for col in ['AQ_CID10', 'AR_CID10']:
        if col in df.columns:
            cids = df[col].astype(str)
            if cids.str.startswith('C50').any():
                is_mama = True
            if cids.str.startswith('C53').any() or cids.str.startswith('C54').any():
                is_colo = True
    if 'AP_PRIPAL' in df.columns:
        vals = df['AP_PRIPAL'].astype(str).str.lower()
        if vals.str.contains('mama').any():
            is_mama = True
        if vals.str.contains('colo').any() or vals.str.contains('uterino').any():
            is_colo = True
            
    resident_label = f'Residente de {city_name}'
    if is_mama and is_colo:
        color_range = ['#0d6efd', '#9ec5fe']
        cancer_type = 'Mama e Colo de Útero'
    elif is_mama:
        color_range = ['#d63384', '#ff9ebb']
        cancer_type = 'Câncer de Mama'
    else:
        color_range = ['#008080', '#80cbc4']
        cancer_type = 'Câncer de Colo de Útero'
        
    location_label = city if city else "Rio Grande do Sul"
    
    chart = alt.Chart(df_long).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('Mes:N', sort=None, title='Mês de Processamento'),
        y=alt.Y('Quantidade:Q', title='Número de Procedimentos'),
        color=alt.Color('Origem:N', scale=alt.Scale(domain=[resident_label, 'Residente de Outro Município'], range=color_range), title='Origem do Paciente'),
        tooltip=[alt.Tooltip('Mes:N', title='Mês'), alt.Tooltip('Origem:N', title='Origem'), alt.Tooltip('Quantidade:Q', title='Procedimentos')]
    ).properties(
        title={
            "text": f"{treatment_type}s em {location_label} (2025)",
            "subtitle": f"Origem dos pacientes atendidos ({cancer_type})"
        },
        width='container',
        height=350
    ).configure_title(
        fontSize=15,
        subtitleFontSize=11,
        anchor='start'
    )
    return chart

def plot_chemo_stage_comparison_altair(df_colo, df_mama, city='Porto Alegre', months=None):
    """
    Gera dois gráficos de pizza (rosca) lado a lado no Altair compartilhando a mesma legenda.
    """
    df_colo_poa = df_colo.copy()
    df_mama_poa = df_mama.copy()
    if city and city != "Todo o Estado":
        df_colo_poa = df_colo_poa[df_colo_poa['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
        df_mama_poa = df_mama_poa[df_mama_poa['AP_UFMUN'].astype(str).str.lower().str.strip() == city.lower().strip()]
    if months:
        start_m = 202500 + months[0]
        end_m = 202500 + months[1]
        df_colo_poa = df_colo_poa[(df_colo_poa['AP_MVM'] >= start_m) & (df_colo_poa['AP_MVM'] <= end_m)]
        df_mama_poa = df_mama_poa[(df_mama_poa['AP_MVM'] >= start_m) & (df_mama_poa['AP_MVM'] <= end_m)]
        
    def classify_stage(val):
        val_str = str(val).strip().upper()
        if val_str in ['0_ESTADIO', '0.0', '0', '1_ESTADIO', '1.0', '1', '2_ESTADIO', '2.0', '2']:
            return 'Inicial (Estágios 0-2)'
        elif val_str in ['3_ESTADIO', '3.0', '3', '4_ESTADIO', '4.0', '4']:
            return 'Avançado (Estágios 3-4)'
        return None
        
    colo_stages = df_colo_poa['AQ_ESTADI'].apply(classify_stage).dropna().value_counts().reset_index()
    colo_stages.columns = ['Estagio', 'Quantidade']
    colo_stages['Cancer'] = 'Colo de Útero'
    
    mama_stages = df_mama_poa['AQ_ESTADI'].apply(classify_stage).dropna().value_counts().reset_index()
    mama_stages.columns = ['Estagio', 'Quantidade']
    mama_stages['Cancer'] = 'Câncer de Mama'
    
    # Common color scale definition
    color_scale = alt.Scale(
        domain=['Inicial (Estágios 0-2)', 'Avançado (Estágios 3-4)'],
        range=['#008080', '#e57373'] # Teal and Soft Red
    )

    if colo_stages.empty:
        colo_stages = pd.DataFrame(columns=['Estagio', 'Quantidade', 'Cancer', 'Porcentagem'])
    else:
        total_colo = colo_stages['Quantidade'].sum()
        colo_stages['Porcentagem'] = colo_stages['Quantidade'] / total_colo if total_colo > 0 else 0.0

    if mama_stages.empty:
        mama_stages = pd.DataFrame(columns=['Estagio', 'Quantidade', 'Cancer', 'Porcentagem'])
    else:
        total_mama = mama_stages['Quantidade'].sum()
        mama_stages['Porcentagem'] = mama_stages['Quantidade'] / total_mama if total_mama > 0 else 0.0

    location_label = city if city else "Rio Grande do Sul"

    # Donut Chart for Colo
    if not colo_stages.empty:
        chart_colo = alt.Chart(colo_stages).mark_arc(innerRadius=50, outerRadius=90).encode(
            theta=alt.Theta(field='Quantidade', type='quantitative'),
            color=alt.Color(field='Estagio', type='nominal', scale=color_scale, title='Estágio UICC'),
            tooltip=[
                alt.Tooltip('Cancer:N', title='Câncer'),
                alt.Tooltip('Estagio:N', title='Estágio'),
                alt.Tooltip('Quantidade:Q', title='Casos'),
                alt.Tooltip('Porcentagem:Q', title='Porcentagem', format='.1%')
            ]
        ).properties(
            title={
                "text": "Colo de Útero",
                "subtitle": f"Total: {colo_stages['Quantidade'].sum():,}".replace(',', '.'),
                "anchor": "middle"
            },
            width=200,
            height=250
        )
    else:
        chart_colo = alt.Chart(pd.DataFrame({'Estagio': ['Sem dados'], 'Quantidade': [1]})).mark_arc(innerRadius=50, outerRadius=90).encode(
            theta=alt.Theta(field='Quantidade', type='quantitative'),
            color=alt.value('#e0e0e0'),
            tooltip=[alt.Tooltip('Estagio:N', title='Status')]
        ).properties(
            title={
                "text": "Colo de Útero (Sem dados)",
                "anchor": "middle"
            },
            width=200,
            height=250
        )

    # Donut Chart for Mama
    if not mama_stages.empty:
        chart_mama = alt.Chart(mama_stages).mark_arc(innerRadius=50, outerRadius=90).encode(
            theta=alt.Theta(field='Quantidade', type='quantitative'),
            color=alt.Color(field='Estagio', type='nominal', scale=color_scale, title='Estágio UICC'),
            tooltip=[
                alt.Tooltip('Cancer:N', title='Câncer'),
                alt.Tooltip('Estagio:N', title='Estágio'),
                alt.Tooltip('Quantidade:Q', title='Casos'),
                alt.Tooltip('Porcentagem:Q', title='Porcentagem', format='.1%')
            ]
        ).properties(
            title={
                "text": "Câncer de Mama",
                "subtitle": f"Total: {mama_stages['Quantidade'].sum():,}".replace(',', '.'),
                "anchor": "middle"
            },
            width=200,
            height=250
        )
    else:
        chart_mama = alt.Chart(pd.DataFrame({'Estagio': ['Sem dados'], 'Quantidade': [1]})).mark_arc(innerRadius=50, outerRadius=90).encode(
            theta=alt.Theta(field='Quantidade', type='quantitative'),
            color=alt.value('#e0e0e0'),
            tooltip=[alt.Tooltip('Estagio:N', title='Status')]
        ).properties(
            title={
                "text": "Câncer de Mama (Sem dados)",
                "anchor": "middle"
            },
            width=200,
            height=250
        )

    # Combine charts with shared legend
    combined = alt.hconcat(
        chart_colo, chart_mama, spacing=40
    ).resolve_scale(
        color='shared'
    ).properties(
        title={
            "text": f"Estadiamento no Início da Quimioterapia em {location_label} (2025)",
            "subtitle": "Comparativo proporcional de Diagnóstico Precoce (Estágios 0-2) vs. Diagnóstico Tardio (Estágios 3-4)"
        }
    ).configure_title(
        fontSize=15,
        subtitleFontSize=11,
        anchor='middle'
    ).configure_legend(
        orient='bottom',
        columns=2,
        titleFontSize=11,
        labelFontSize=10
    )

    return combined