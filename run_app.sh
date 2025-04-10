#!/bin/bash

# Matar cualquier proceso que esté usando los puertos 5003 y 8000
echo "Terminando procesos existentes..."
lsof -ti:5003 | xargs kill -9 2>/dev/null || echo "Puerto 5003 libre"
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Puerto 8000 libre"

# Esperar un momento para asegurarse de que los puertos se liberen
sleep 1

# Iniciar el servidor backend
echo "Iniciando servidor backend..."
python -m api.server &
BACKEND_PID=$!

# Esperar a que el backend se inicie
sleep 3

# Iniciar el frontend
echo "Iniciando frontend..."
cd frontend && npm run dev &
FRONTEND_PID=$!

# Función para manejar la terminación del script
function cleanup {
  echo "Terminando procesos..."
  kill $BACKEND_PID 2>/dev/null
  kill $FRONTEND_PID 2>/dev/null
  exit
}

# Capturar señales para limpiar correctamente
trap cleanup SIGINT SIGTERM

# Mantener el script en ejecución
echo "Aplicación iniciada, presiona Ctrl+C para terminar"
wait 