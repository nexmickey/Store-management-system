#!/bin/sh
export FLASK_APP=source/main.py

sleep 0.3

echo "[+] Running database initialization..."
flask init-db

echo "[+] Starting Flask server..."
python source/main.py
