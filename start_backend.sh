#!/bin/bash

# Activar el entorno virtual
source LLM_312/bin/activate

# Instalar/actualizar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p data
mkdir -p uploads

# Iniciar el servidor
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 