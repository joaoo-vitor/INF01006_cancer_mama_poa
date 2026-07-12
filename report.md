# Relatório Técnico do Projeto: Análise do Tratamento Oncológico no Rio Grande do Sul e Porto Alegre (2025)

## 1. Introdução e Objetivos

O presente relatório documenta o desenvolvimento, metodologia e resultados obtidos no projeto final da disciplina de **Projeto de Banco de Dados**. O objetivo principal é fornecer uma plataforma interativa de inteligência de dados que integre, saneie e visualize informações detalhadas a respeito da assistência oncológica no estado do Rio Grande do Sul e, de forma focada, na capital Porto Alegre para o ano de 2025. 

O foco analítico concentra-se em duas neoplasias malignas de grande impacto na saúde pública: o **Câncer de Mama** e o **Câncer de Colo de Útero (Cervical)**.

---

## 2. Metodologia

A metodologia de desenvolvimento do projeto seguiu um fluxo clássico de engenharia e análise de dados, compreendendo as etapas de extração (ETL), modelagem de banco de dados, higienização, agregação de dados e construção da interface analítica.

### 2.1. Fontes de Dados e Extração
Os dados foram originalmente extraídos do repositório FTP público do Departamento de Informática do SUS (**DATASUS**). Foram integrados três grandes sistemas de informação em saúde:
1. **SIA/SUS (Sistema de Informação Ambulatorial)**:
   - Arquivos do tipo **AQ** (Autorização de Procedimento de Alta Complexidade - Quimioterapia): Registro de sessões quimioterápicas ambulatoriais no Rio Grande do Sul (`AQRS25*.csv`).
   - Arquivos do tipo **AR** (Autorização de Procedimento de Alta Complexidade - Radioterapia): Registro de sessões de radioterapia ambulatoriais no estado (`ARRS25*.csv`).
2. **SIH/SUS (Sistema de Informação Hospitalar)**:
   - Arquivos do tipo **RD** (Autorização de Internação Hospitalar - AIH): Registros de internações e cirurgias oncológicas em leitos hospitalares do estado (`RDRS25*.csv`).
3. **SISCAN (Sistema de Informação do Câncer)**:
   - Contagens agregadas de exames preventivos e diagnósticos no ano de 2025 (`datasets/SISCAN`), cobrindo:
     - *Mamografia de Rastreamento*
     - *Citopatológico de Colo do Útero (Preventivo)*
     - *Histopatológico de Colo do Útero*
     - *Citopatológico de Mama*
     - *Histopatológico de Mama*

### 2.2. Higienização e Agregação de Dados (Data Cleaning)
Devido ao enorme volume e fragmentação mensal dos dados brutos do DATASUS, foi desenvolvido um pipeline de saneamento:
- **Remoção de Colunas**: Colunas desnecessárias ou zeradas (por exemplo, `AR_SMRD` no SIA e colunas marcadas como "zeradas" no SIH) foram eliminadas para otimizar o consumo de memória.
- **Script de Agregação**: O script `scripts/create_file_agreggations.sh` chama `create_file_agreggations.py` para consolidar os 12 arquivos mensais de cada modalidade e patologia (SIA/SIH) em 6 grandes datasets consolidados anuais (finalizados com `_agregado.csv`).
- **Limpeza do SISCAN**: Implementação de funções baseadas em Expressões Regulares (RegEx) para remover códigos numéricos de identificação prefixados e limpar strings (por exemplo, `2237822-HOSPITAL` para `HOSPITAL`), padronizando o texto em letras maiúsculas.
- **Tratamento de Codificação**: Leitura dos arquivos em codificação `Latin-1` (ISO-8859-1) e com delimitador ponto e vírgula (`;`), mapeando as variações ortográficas nos cabeçalhos de meses (como `MARÇO/2025` e `MARO/2025`) para chaves uniformes de três letras (`Jan` a `Dez`).

### 2.3. Arquitetura da Aplicação e Mapeamento Espacial
O painel de monitoramento foi desenvolvido na linguagem **Python** utilizando o framework **Streamlit**.
- **Visualização de Gráficos**: Utilizou-se a biblioteca **Altair** (baseada em Vega-Lite) para gráficos estatísticos responsivos e o **Matplotlib** para diagramas de Venn customizados.
- **Mapeamento Geográfico**: Integração da biblioteca **Pydeck** (baseada em deck.gl) para geração de mapas interativos tridimensionais (basemap do Mapbox). 
- **Centralização de Metadados**: Criação de dicionários estáticos (`CNES_HOSPITALS_MAP` e `POA_HOSPITALS_COORDS` em `config.py`, além de `POA_HEALTH_UNITS_COORDS` em `poa_coords_dict.py`) para associar as coordenadas geográficas de latitude e longitude dos 147 estabelecimentos de saúde aos dados de atendimentos baseados nos códigos de CNES.

---

## 3. Resultados: Descrição das Funcionalidades e Painéis

O dashboard é estruturado de forma modular e dinâmica, adaptando-se aos filtros globais definidos na barra lateral (*sidebar*).

### 3.1. Filtros da Barra Lateral
- **Seletor de Patologia (Doença)**: Altera completamente a temática visual e a carga de dados entre **Câncer de Mama** (paleta de tons rosa `#d63384`) e **Câncer de Colo de Útero** (paleta de tons azuis `#0065D8`).
- **Seletor de Município de Residência**: Filtra todos os dados entre "Todo o Estado", "Porto Alegre" e os demais municípios do Rio Grande do Sul.
- **Filtro de Intervalo Temporal**: Slider que permite definir o intervalo de meses de análise (entre 1 e 12).

---

### 3.2. Detalhamento das Abas do Dashboard

#### Aba 1: Página Inicial (Home)
Esta aba exibe uma visão consolidada de alto nível sobre a patologia selecionada:
* **Cards de KPIs**: Mostram o volume de atendimentos de quimioterapia (SIA), radioterapia (SIA), internações (SIH) e a proporção de letalidade hospitalar.
* **Evolução Temporal**: Gráfico composto de barras e linhas que mostra a soma mensal dos atendimentos no período selecionado, com uma linha de tendência integrada.
* **Comparativo de Estadiamento**: Dois gráficos de rosca (*donut charts*) que exibem a proporção de diagnósticos em estágio inicial contra estágio avançado para pacientes residentes e não residentes. O estadiamento avançado é enfatizado com tons mais escuros das cores temáticas.
* **Distribuição por CID e Idades**: Exibição de boxplot detalhado das idades dos pacientes agrupados pelo código da Classificação Internacional de Doenças (CID-10) e a representação de fatias em formato de pizza.

#### Aba 2: Informações Financeiras
Focada no impacto orçamentário dos procedimentos:
* **KPIs de Gasto**: Exibe o montante total gasto pelo SUS em Quimioterapias, Radioterapias e Internações.
* **Gráfico de Gastos Mensais**: Gráfico de linhas agrupadas mostrando o custo mensal de cada modalidade de tratamento ao longo do ano de 2025.
* **Tabela de Detalhamento por Estabelecimento**: Tabela interativa listando os hospitais que mais receberam verba pública no período, ordenados de forma decrescente.

#### Aba 3: Informações Demográficas
Apresenta o perfil socioeconômico e epidemiológico da população atendida:
* **Pirâmide Etária / Distribuição de Idades**: Um gráfico estatístico Altair combinando distribuições horizontais de densidade de idade por modalidade e patologia, facilitando a identificação da faixa etária de pico das doenças.
* **Raça/Cor Declarada**: Gráfico de pizza que reflete a autodeclaração de raça e cor dos pacientes.
* **Sexo Declarado**: Gráfico de rosca que exibe o gênero informado nos registros. Para evitar confusão visual com a cor da doença oncológica, esta visualização utiliza duas cores de controle fixas (`Rosa Bebê #ff5c8a` para feminino e `Azul Claro #4a90e2` para masculino) e conta com um algoritmo de redimensionamento proporcional mínimo (limite de 5%) para garantir que fatias muito pequenas permaneçam hoveráveis e interativas para exibição de *tooltips*.

#### Aba 4: Análise Geográfica
Exibe a distribuição territorial e fluxos migratórios dos tratamentos:
* **Mapa Coroplético da Concentração de Atendimentos**: Renderização do mapa do estado do Rio Grande do Sul colorido de acordo com o volume de atendimentos de cada município prestador. A porcentagem relativa do município em relação ao estado é calculada dinamicamente e exibida no *tooltip* ao passar o cursor.
* **Tabela de Detalhamento por Município**: Apresenta os totais e as porcentagens exatas de representação territorial.
* **Mapa de Zoom em Porto Alegre (Pydeck)**: Exibição específica da capital utilizando Pydeck. Pontos georreferenciados representam hospitais de Porto Alegre, e o tamanho de cada bolha (raio em metros) é proporcional à quantidade medida. É influenciada diretamente pelo tipo de tratamento selecionado em um seletor local (Quimioterapias, Radioterapias e Internações).
* **Fluxo Migratório Hospitalar (Interior ➔ Porto Alegre)**: Gráfico de barras horizontais indicando a quantidade de atendimentos realizados na capital para pacientes residentes em outros municípios. O *tooltip* exibe o nome completo do mês em português (e.g. "Agosto" ao invés de "Ago").

#### Aba 5: Rastreamento Preventivo (Exames SISCAN)
Aba totalmente reformulada com dados reais do SISCAN de 2025:
* **Seletor de Exame**: Permite analisar separadamente cinco exames de rastreamento oncológico preventivo.
* **Evolução Mensal (Barras + Linha)**: Exibe a evolução do exame selecionado de acordo com a localidade e intervalo temporal.
* **Donut Chart dos Top 10 Municípios**: Gráfico de rosca exibindo a fatia de mercado das 10 principais cidades gaúchas na realização desse exame, consolidando as demais em "Outras Cidades".
* **Mapa de Unidades de Saúde (Pydeck)**: Mapa detalhado de Porto Alegre georreferenciando as 147 unidades de saúde com bolhas dimensionadas conforme o volume de exames de prevenção efetuados.

#### Aba 6: Pacientes
Focada na intersecção terapêutica:
* **Sobreposição Quimioterapia x Radioterapia**: Gráfico de Diagrama de Venn customizado gerado dinamicamente com Matplotlib que exibe a sobreposição de pacientes que realizaram apenas quimioterapia, apenas radioterapia ou ambas as modalidades de forma concomitante no período. A paleta do gráfico e dos círculos translúcidos adapta-se ao tom da doença selecionada.

#### Aba 7: Tratamentos
Exibe informações médicas operacionais:
* **Tipos de Tratamento**: Gráfico Altair com a distribuição dos tipos de quimioterapia administrados (paliativa, adjuvante, curativa, etc.).
* **Hospitais Prestadores**: Ranking dos principais estabelecimentos executantes da assistência oncológica.

---

## 4. Referências Bibliográficas

1. **BRASIL. Ministério da Saúde.** *DATASUS - Departamento de Informática do SUS*. Disponível em: <http://datasus.saude.gov.br/>. Acesso em: 12 jul. 2026.
2. **BRASIL. Ministério da Saúde.** *Tabnet: Indicadores de Saúde*. Disponível em: <http://www2.datasus.gov.br/DATASUS/index.php?area=02>. Acesso em: 12 jul. 2026.
3. **BRASIL. Ministério da Saúde.** *Repositório FTP Público do DATASUS (SIA/SUS e SIH/SUS)*. Endereço FTP: <ftp://ftp.datasus.gov.br/dissemin/publicos/>. Acesso em: 12 jul. 2026.
4. **BRASIL. Ministério da Saúde. Secretaria de Atenção à Saúde.** *Informe Técnico do SIH (Sistema de Informação Hospitalar)*. Coordenação-Geral de Sistemas de Informação, Brasília, DF. (Documento de definição de colunas e dicionário de dados do arquivo RD).
5. **BRASIL. Ministério da Saúde. Secretaria de Atenção à Saúde.** *Informe Técnico do SIA (Sistema de Informação Ambulatorial)*. Coordenação-Geral de Sistemas de Informação, Brasília, DF. (Documento de definição de colunas e dicionário de dados dos arquivos AQ e AR).
6. **BRASIL. Ministério da Saúde. Instituto Nacional de Câncer José Alencar Gomes da Silva (INCA).** *SISCAN - Sistema de Informação do Câncer: Diretrizes Técnicas e Manuais de Operação*. Rio de Janeiro: INCA, 2025.
