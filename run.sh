#!/bin/bash

# Garantir que o ambiente virtual e dependências estão instalados
echo "Verificando dependências e instalando ambiente virtual... / Checking dependencies and installing virtual environment..."
pipenv install

# Define the aggregated files relative to root
FILES=(
  "datasets/AQRS25colo_agregado.csv"
  "datasets/AQRS25mama_agregado.csv"
  "datasets/ARRS25colo_agregado.csv"
  "datasets/ARRS25mama_agregado.csv"
  "datasets/RDRS25colo_agregado.csv"
  "datasets/RDRS25mama_agregado.csv"
)

# Flag to track if any file is missing
MISSING=0

for file in "${FILES[@]}"; do
  if [ ! -f "$file" ]; then
    echo "Ficheiro agregado em falta / Missing aggregated file: $file"
    MISSING=1
  fi
done

# If any file is missing, run the aggregation script
if [ $MISSING -eq 1 ]; then
  echo "Dados agregados não encontrados. Executando agregação automática..."
  echo "Aggregated data not found. Running automatic aggregation..."
  
  # Change to scripts directory to run the aggregation script correctly
  cd scripts || exit 1
  pipenv run bash create_file_agreggations.sh
  cd ..
else
  echo "Todos os dados agregados já existem / All aggregated data files exist."
fi

# Run the streamlit application
echo "Iniciando a aplicação Streamlit... / Starting Streamlit application..."
pipenv run streamlit run streamlit-app/app.py
