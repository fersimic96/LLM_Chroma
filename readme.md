# ChatBot con Embeddings y Búsqueda Semántica

Este proyecto implementa un chatbot que utiliza embeddings y búsqueda semántica para responder preguntas basadas en documentos PDF.

## Características

### Gestión de Colecciones
- Creación de colecciones vectoriales en Qdrant
- Visualización de colecciones existentes con contador de vectores
- Estado en tiempo real de las colecciones (activo/error)

### Procesamiento de Documentos
- Carga múltiple de archivos PDF
- Procesamiento automático de texto y generación de embeddings
- Almacenamiento eficiente en colecciones vectoriales
- División inteligente de documentos en chunks para mejor procesamiento

### Búsqueda y Consultas
- Selección múltiple de colecciones para búsqueda
- Búsqueda semántica en tiempo real
- Respuestas generadas con GPT-3.5-turbo
- Streaming de respuestas para mejor experiencia de usuario
- Referencias a las fuentes originales con número de página

## Arquitectura

### Frontend (React)
- **CollectionSelector**: Permite seleccionar múltiples colecciones para búsqueda
- **EmbeddingUploader**: Gestiona la carga y procesamiento de PDFs
- **QueryForm**: Maneja las consultas del usuario
- **ResponseDisplay**: Muestra las respuestas en tiempo real con streaming

### Backend (FastAPI)
- **Rutas principales**:
  - `/qdrant-collections`: Gestión de colecciones (GET, POST)
  - `/upload-embeddings`: Procesamiento de PDFs y generación de embeddings
  - `/query`: Búsqueda semántica y generación de respuestas

### Base de Datos Vectorial
- Qdrant para almacenamiento y búsqueda de embeddings
- Optimización automática de índices
- Configuración de parámetros para mejor rendimiento

## Flujo de Trabajo

1. **Carga de Documentos**:
   ```
   Frontend (PDF) -> API (/upload-embeddings) -> Procesamiento -> Qdrant
   ```

2. **Consultas**:
   ```
   Usuario -> Selección de Colecciones -> Consulta -> API (/query) -> 
   Búsqueda en Qdrant -> GPT-3.5 -> Streaming de Respuesta
   ```

## Configuración

1. **Variables de Entorno**:
   ```
   OPENAI_API_KEY=tu_api_key
   ```

2. **Instalación**:
   ```bash
   # Backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

3. **Ejecución**:
   ```bash
   # Backend
   uvicorn api.main:app --reload

   # Frontend
   cd frontend
   npm run dev
   ```

## Uso

1. **Gestión de Colecciones**:
   - Crear una nueva colección desde la interfaz
   - Seleccionar la colección para cargar documentos
   - Verificar el contador de vectores y estado

2. **Carga de Documentos**:
   - Seleccionar archivos PDF
   - La interfaz mostrará el progreso y resultados
   - Los documentos se procesan y almacenan automáticamente

3. **Consultas**:
   - Seleccionar una o más colecciones
   - Escribir la pregunta en el campo de texto
   - Las respuestas se muestran en tiempo real con referencias

## Tecnologías

- Frontend: React, TailwindCSS
- Backend: FastAPI, Langchain
- Base de Datos: Qdrant
- ML: OpenAI (GPT-3.5-turbo, text-embedding-3-large)

## Estructura del Proyecto

```
ChatBot/
├── api/
│   ├── routes/
│   │   ├── database_routes.py   # Rutas para gestión de colecciones y consultas
│   │   └── query_routes.py      # Rutas para procesamiento de consultas
│   ├── main.py                  # Configuración principal de FastAPI
│   └── config.py               # Configuraciones y variables de entorno
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CollectionSelector.jsx  # Selector de colecciones
│   │   │   ├── EmbeddingUploader.jsx   # Carga de PDFs
│   │   │   ├── QueryForm.jsx           # Formulario de consultas
│   │   │   ├── ResponseDisplay.jsx      # Visualización de respuestas
│   │   │   └── Sidebar.jsx             # Barra lateral de navegación
│   │   ├── App.jsx                     # Componente principal
│   │   └── index.css                   # Estilos globales
│   ├── package.json
│   └── vite.config.js
├── qdrant_db/                  # Base de datos vectorial
│   ├── collections/            # Colecciones de vectores
│   └── meta.json              # Metadatos de colecciones
├── uploads/                    # Directorio temporal para PDFs
├── requirements.txt            # Dependencias de Python
└── .env                       # Variables de entorno
```

## Contribución

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores.