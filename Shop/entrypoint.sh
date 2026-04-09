#!/bin/sh
export FLASK_APP=source_owner/main.py

sleep 0.3

echo "[+] Running database initialization..."
flask init-db

echo "[+] Starting Flask server..."
python source_owner/main.py
