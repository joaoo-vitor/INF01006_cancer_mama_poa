import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_chemotherapies_by_month(df):
    """
    Gera um gráfico de barras e linha mostrando o número de quimioterapias realizadas 
    no município de Porto Alegre para cada mês do ano de 2025.
    
    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados de quimioterapia (câncer de colo ou mama).
        
    Retorna:
        fig (matplotlib.figure.Figure): Objeto da figura do matplotlib.
        ax (matplotlib.axes.Axes): Objeto do eixo do matplotlib contendo o gráfico.
    """
    # 1. Filtrar pelo estabelecimento localizado em Porto Alegre (AP_UFMUN)
    df_filtered = df[df['AP_UFMUN'].astype(str).str.lower().str.strip() == 'porto alegre'].copy()
    
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
    
    # 3. Detectar o tipo de câncer (Mama vs Colo) para personalizar o visual
    is_mama = False
    if 'AQ_CID10' in df.columns:
        is_mama = df['AQ_CID10'].astype(str).str.startswith('C50').any()
    elif 'AP_PRIPAL' in df.columns:
        is_mama = df['AP_PRIPAL'].astype(str).str.lower().str.contains('mama').any()
        
    if is_mama:
        cancer_type = 'Câncer de Mama'
        main_color = '#d63384'  # Rosa (Outubro Rosa)
        bg_color = '#fce4ec'
    else:
        cancer_type = 'Câncer de Colo de Útero'
        main_color = '#008080'  # Teal/Ciano (Março Lilás/Teal)
        bg_color = '#e0f2f1'
        
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
    for idx, row in monthly_counts.iterrows():
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
    ax.set_title(
        f"Quimioterapias realizadas em Porto Alegre por Mês (2025)\n({cancer_type})",
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

def plot_stacked_chemotherapies_by_month(df_colo, df_mama):
    """
    Gera um gráfico de barras empilhadas mostrando a quantidade de quimioterapias
    realizadas no município de Porto Alegre para cada mês do ano de 2025,
    comparando Câncer de Colo de Útero e Câncer de Mama.
    
    Parâmetros:
        df_colo (pd.DataFrame): DataFrame contendo os dados de quimioterapia para câncer de colo.
        df_mama (pd.DataFrame): DataFrame contendo os dados de quimioterapia para câncer de mama.
        
    Retorna:
        fig (matplotlib.figure.Figure): Objeto da figura do matplotlib.
        ax (matplotlib.axes.Axes): Objeto do eixo do matplotlib contendo o gráfico.
    """
    # 1. Filtrar pelo estabelecimento localizado em Porto Alegre (AP_UFMUN)
    df_colo_filtered = df_colo[df_colo['AP_UFMUN'].astype(str).str.lower().str.strip() == 'porto alegre'].copy()
    df_mama_filtered = df_mama[df_mama['AP_UFMUN'].astype(str).str.lower().str.strip() == 'porto alegre'].copy()
    
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
    for idx, row in df_combined.iterrows():
        total = row['Total']
        mama = row['Mama']
        colo = row['Colo']
        
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
        
        # Rótulo interno para o segmento de Mama (se for significativo o suficiente)
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
            
        # Rótulo interno para o segmento de Colo (se for significativo o suficiente para ser visível)
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
    ax.set_title(
        "Quimioterapias em Porto Alegre por Mês (2025)\nComparativo de Câncer de Mama e Colo de Útero",
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

def _plot_residents_vs_non_residents(df, treatment_type):
    """
    Função auxiliar genérica para gerar um gráfico de barras empilhadas 
    contando os residentes de Porto Alegre vs pessoas de outros municípios
    para procedimentos (quimioterapia ou radioterapia) realizados em Porto Alegre.
    """
    # 1. Filtrar pelo estabelecimento localizado em Porto Alegre (AP_UFMUN)
    df_filtered = df[df['AP_UFMUN'].astype(str).str.lower().str.strip() == 'porto alegre'].copy()
    
    # 2. Classificar residentes de Porto Alegre vs outros municípios
    df_filtered['Residente'] = df_filtered['AP_MUNPCN'].astype(str).str.lower().str.strip() == 'porto alegre'
    
    # 3. Agrupar por mês e se é residente
    counts = df_filtered.groupby(['AP_MVM', 'Residente']).size().unstack(fill_value=0)
    
    # Garantir que ambas as colunas (True e False) existam
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
    
    # 4. Detectar dinamicamente o tipo de câncer (Mama, Colo, ou Ambos) para o título/cores
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
        label='Residente de Porto Alegre',
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
    ax.set_title(
        f"{treatment_type}s em Porto Alegre por Mês (2025)\nAtendimentos a Residentes vs. Não Residentes ({cancer_type})",
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

def plot_chemo_residents_vs_non_residents(df):
    """
    Gera um gráfico de barras empilhadas comparando a quantidade de quimioterapias 
    em Porto Alegre entre pacientes residentes e pacientes de outros municípios.
    """
    return _plot_residents_vs_non_residents(df, "Quimioterapia")

def plot_radio_residents_vs_non_residents(df):
    """
    Gera um gráfico de barras empilhadas comparando a quantidade de radioterapias 
    em Porto Alegre entre pacientes residentes e pacientes de outros municípios.
    """
    return _plot_residents_vs_non_residents(df, "Radioterapia")

def plot_chemo_stage_comparison(df_colo, df_mama):
    """
    Gera dois gráficos de rosca lado a lado comparando a proporção de estágios 
    iniciais (0, 1 e 2) vs. avançados/metastáticos (3 e 4) no início do tratamento 
    quimioterápico em Porto Alegre para Câncer de Colo de Útero e Câncer de Mama.
    
    Parâmetros:
        df_colo (pd.DataFrame): DataFrame contendo os dados de quimioterapia de colo.
        df_mama (pd.DataFrame): DataFrame contendo os dados de quimioterapia de mama.
        
    Retorna:
        fig (matplotlib.figure.Figure): Objeto da figura do matplotlib.
        axes (numpy.ndarray): Array de eixos do matplotlib contendo os gráficos.
    """
    # 1. Filtrar pelo estabelecimento localizado em Porto Alegre (AP_UFMUN)
    df_colo_poa = df_colo[df_colo['AP_UFMUN'].astype(str).str.lower().str.strip() == 'porto alegre'].copy()
    df_mama_poa = df_mama[df_mama['AP_UFMUN'].astype(str).str.lower().str.strip() == 'porto alegre'].copy()
    
    # Função para classificar o estágio
    def classify_stage(val):
        val_str = str(val).strip().upper()
        if val_str in ['0_ESTADIO', '0.0', '0']:
            return 'Inicial (Estágios 0-2)'
        elif val_str in ['1_ESTADIO', '1.0', '1']:
            return 'Inicial (Estágios 0-2)'
        elif val_str in ['2_ESTADIO', '2.0', '2']:
            return 'Inicial (Estágios 0-2)'
        elif val_str in ['3_ESTADIO', '3.0', '3']:
            return 'Avançado (Estágios 3-4)'
        elif val_str in ['4_ESTADIO', '4.0', '4']:
            return 'Avançado (Estágios 3-4)'
        else:
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
        # Customizar texto das porcentagens
        for autotext in autotexts_colo:
            autotext.set_fontsize(11)
            
        ax_colo.text(
            0, 0,
            f"Colo de Útero\nTotal\n{total_colo:,}".replace(',', '.'),
            ha='center', va='center',
            fontsize=13, fontweight='bold',
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
        # Customizar texto das porcentagens
        for autotext in autotexts_mama:
            autotext.set_fontsize(11)
            
        ax_mama.text(
            0, 0,
            f"Mama\nTotal\n{total_mama:,}".replace(',', '.'),
            ha='center', va='center',
            fontsize=13, fontweight='bold',
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
        "Estadiamento no Início do Tratamento Quimioterápico pelo SUS em Porto Alegre (2025)\nDiagnóstico Precoce vs. Diagnóstico Tardio",
        fontsize=16,
        fontweight='bold',
        color='#222222',
        y=0.98
    )
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.93])
    return fig, axes
