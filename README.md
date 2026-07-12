# Tratamento do Câncer de Mama em Porto Alegre - 2025
Trabalho final da disciplina de Projeto de Banco de Dados: Análise do tratamento de câncer de mama e câncer de colo de útero em Porto Alegre em 2025.

## Datasets usados
Bases de dados em CSV usados para o trabalho.

- AQRSaamm são registros de quimioterapia no Rio Grande do Sul no ano 20aa e no mês mm. Dicionário de dados disponível em 'Dicionário SIA.pdf'

- ARRSaamm são registros de radioterapia no Rio Grande do Sul no ano 20aa e no mês mm. Dicionário de dados disponível em 'Dicionário SIA.pdf'.

- RDRSaamm são registros de internações hospitalares e dos procedimentos associados no Rio Grande do Sul no ano 20aa e no mês mm. Dicionário de dados disponível em 'Dicionário SIH.pdf'. 

- SISCANPOA25exame são registros de contagem de um determinado exame em hospitais da cidade de Porto Alegre em 2025.

- SISCANRS25exame são registros de contagem de um determinado exame em cidades do Rio Grande do Sul.

### Preparação dos dados (data cleaning)
Os dados foram baixados do repositório FTP do DataSUS, suas colunas foram convertidas usando arquivos de definição (DEF) e foram transformados em csv.

- SIA -> AR
Colunas removidas: AR_SMRD

- SIH -> RD
Várias colunas com a descrição dizendo "zerada" foram removidas.



## Como instalar o ambiente virtual para análise de dados?
Este projeto utiliza o **Pipenv** para gerenciar dependências e o ambiente virtual de forma integrada. Siga os passos abaixo para configurar o ambiente em sua máquina.

### Prerrequisitos
Certifique-se de ter o **Python** (versão 3.8 ou superior) instalado no seu sistema.

---
### 1. Instalar o Pipenv

Caso ainda não tenha o Pipenv instalado globalmente no seu sistema, execute o comando correspondente ao seu sistema operacional:
**Usando o Pip (Geral/Linux/Windows):**
```bash
pip install --user pipenv
```
**No macOS (usando Homebrew):**
```bash
brew install pipenv
```
Nota (Linux/Windows): Se o comando pipenv não for reconhecido após a instalação com --user, certifique-se de que o diretório de scripts do Python está adicionado ao PATH do seu sistema.

### 2. Instalar dependências: 
```bash
pipenv install
```
Assim, um novo ambiente virtual será criado ("INF01006_cancer_mama_poa") e você poderá utilizá-lo para as análises desse repositório.

---

## Como rodar o dashboard streamlit?

### Opção 1: Execução Automática Rápida (Recomendada 🌟)
Colocamos um script no diretório raiz do repositório chamado `run.sh`. Ele **instala automaticamente o ambiente virtual e dependências via Pipenv**, verifica se os seis arquivos agregados de dados existem na pasta `datasets/` (gerando-os se necessário), e inicia o painel do Streamlit.

Para executá-lo, use o terminal ou o **Git Bash** (no Windows) a partir da raiz do repositório:
```bash
sh run.sh
```

### Opção 2: Execução Passo a Passo (Alternativa Manual)
Se preferir executar cada passo manualmente, é **obrigatório** instalar o ambiente virtual primeiro. Siga esta ordem:

#### 1. Instalar o ambiente virtual do projeto:
```bash
pipenv install
```

#### 2. Gerar os dados agregados para 2025:
Entre no diretório `scripts/` e execute o script `create_file_agreggations.sh`:
```bash
cd scripts
sh create_file_agreggations.sh
cd ..
```
Isso vai criar os seis arquivos agregados unindo os dados do ano de 2025.

#### 3. Iniciar o dashboard do Streamlit:
A partir do diretório raiz do projeto, execute:
```bash
pipenv run streamlit run streamlit-app/app.py
```