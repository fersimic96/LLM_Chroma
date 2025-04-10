from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configurar logging para uvicorn y FastAPI
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("fastapi").setLevel(logging.INFO)

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5003",  # Frontend dev server
        "http://127.0.0.1:5003",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Asegurarse de que existan los directorios necesarios
Path("data").mkdir(exist_ok=True)
Path("uploads").mkdir(exist_ok=True)

# Importar y configurar los routers
from api.routes import database_routes, query_routes, api_key_routes

app.include_router(database_routes.router)
app.include_router(query_routes.router)
app.include_router(api_key_routes.router)

@app.get("/")
async def root():
    return {"message": "API funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 