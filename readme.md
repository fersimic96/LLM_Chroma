# ChatBot con FastAPI y React

Un chatbot inteligente que utiliza FastAPI para el backend y React para el frontend, con capacidad de procesamiento de documentos PDF y respuestas en tiempo real utilizando OpenAI.

## Características

- **Backend (FastAPI)**
  - Streaming de respuestas en tiempo real
  - Integración con OpenAI para generación de respuestas
  - Sistema de bases de datos vectoriales con ChromaDB
  - Procesamiento de documentos PDF
  - Manejo de API keys y configuración segura
  - Endpoints modulares y bien organizados

- **Frontend (React)**
  - Interfaz moderna con Tailwind CSS
  - Componentes UI interactivos
  - Selector de bases de datos
  - Visualización de respuestas en tiempo real
  - Gestión de API keys
  - Diseño responsivo

## Requisitos

- Python 3.12.3
- Node.js y npm
- Entorno virtual (LLM_312)
- API key de OpenAI

## Configuración

1. **Backend**
   ```bash
   # Crear y activar entorno virtual
   python -m venv LLM_312
   source LLM_312/bin/activate  # En Windows: LLM_312\Scripts\activate
   
   # Instalar dependencias
   pip install -r requirements.txt
   
   # Configurar variables de entorno
   # Crear archivo .env con:
   OPENAI_API_KEY=tu_api_key
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   ```

## Ejecución

1. **Backend**
   ```bash
   # En el directorio raíz
   uvicorn api.main:app --reload
   # El servidor se ejecutará en http://localhost:8000
   ```

2. **Frontend**
   ```bash
   # En el directorio frontend
   npm run dev
   # La aplicación estará disponible en http://localhost:5003
   ```

## Estructura del Proyecto

```
ChatBot/
├── api/
│   ├── routes/
│   │   ├── api_key_routes.py
│   │   ├── database_routes.py
│   │   └── query_routes.py
│   ├── main.py
│   └── config.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   └── App.jsx
│   └── package.json
├── data/
│   └── (archivos PDF)
├── requirements.txt
└── .env
```

## Endpoints API

- `POST /query`: Procesa consultas y devuelve respuestas en streaming
- `POST /update_path`: Actualiza la ruta base de documentos
- `POST /set-database-path`: Configura la ruta de la base de datos
- `GET /databases`: Lista las bases de datos disponibles

## Características de Seguridad

- Protección de API keys mediante variables de entorno
- Archivos sensibles excluidos via .gitignore
- Validación de entradas
- Manejo seguro de rutas de archivos

## Licencia

Este proyecto está bajo la Licencia MIT.