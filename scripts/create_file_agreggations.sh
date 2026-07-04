#!/bin/bash

echo "Starting CSV aggregations..."

python create_file_agreggations.py -d "../datasets/AQ/colo" -f "AQRS25*.csv" -o "../datasets/AQRS25colo_agregado.csv"
python create_file_agreggations.py -d "../datasets/AQ/mama" -f "AQRS25*.csv" -o "../datasets/AQRS25mama_agregado.csv"

python create_file_agreggations.py -d "../datasets/AR/colo" -f "ARRS25*.csv" -o "../datasets/ARRS25colo_agregado.csv"
python create_file_agreggations.py -d "../datasets/AR/mama" -f "ARRS25*.csv" -o "../datasets/ARRS25mama_agregado.csv"

python create_file_agreggations.py -d "../datasets/RD/colo" -f "RDRS25*.csv" -o "../datasets/RDRS25colo_agregado.csv"
python create_file_agreggations.py -d "../datasets/RD/mama" -f "RDRS25*.csv" -o "../datasets/RDRS25mama_agregado.csv"

echo "All aggregations completed!"