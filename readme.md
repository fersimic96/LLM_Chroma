# Chatbot Simich

Un chatbot inteligente construido con FastAPI y React que permite consultar múltiples bases de datos vectoriales usando ChromaDB y OpenAI.



## Tecnologías

### Backend
- Python 3.12.3
- FastAPI y Uvicorn
- LangChain y ChromaDB
- OpenAI
- Spacy y herramientas NLP
- Bibliotecas para procesamiento de documentos (pypdf, pdfplumber)

### Frontend
- React
- Tailwind CSS
- JavaScript moderno

## Estructura del Proyecto

```
ChatBot/
├── api/                # Backend FastAPI
│   └── main.py        # Endpoints y lógica principal
├── frontend/          # Frontend React
│   ├── src/
│   │   ├── App.jsx    # Componente principal
│   │   └── ...
│   └── ...
└── chroma*/           # Bases de datos vectoriales
```

## Funcionalidades

### Consulta de Bases de Datos
- Selección dinámica de bases de datos disponibles
- Búsqueda semántica en documentos
- Respuestas contextuales basadas en el contenido de los documentos

### Formato de Respuestas
- Respuestas detalladas y bien estructuradas
- Referencias a las fuentes con:
  - Nombre del archivo PDF
  - Número de página
  - Número de chunk
  - Fragmento relevante del texto

### Interfaz de Usuario
- Diseño limpio y moderno
- Selector de bases de datos
- Historial de mensajes
- Indicador de carga
- Separación clara entre respuestas y fuentes

## Configuración del Entorno

1. Activar el entorno virtual:
```bash
source LLM_312/bin/activate
```

2. Variables de entorno necesarias:
```
OPENAI_API_KEY=tu_api_key
```

## Ejecución

### Backend
```bash
cd api
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

## Uso

1. Seleccionar una base de datos del menú desplegable
2. Escribir una consulta en el campo de texto
3. Recibir una respuesta detallada con:
   - Análisis completo del tema
   - Referencias a las fuentes consultadas
   - Fragmentos relevantes del contenido

## Mantenimiento

El proyecto utiliza un entorno virtual Python (LLM_312) que contiene todas las dependencias necesarias para el funcionamiento del backend.