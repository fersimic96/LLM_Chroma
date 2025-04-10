from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.routes import database_routes, api_key_routes
import os
import logging
from pathlib import Path
from api.routes.api_key_routes import set_api_key_in_env, get_api_key_settings

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorio de uploads si no existe
uploads_dir = Path("uploads")
if not uploads_dir.exists():
    uploads_dir.mkdir(parents=True)

# Middleware para configurar la API key en cada solicitud
@app.middleware("http")
async def api_key_middleware(request, call_next):
    # Si hay una API key válida en el sistema, configurarla para esta solicitud
    set_api_key_in_env()
    
    # Continuar con la solicitud
    response = await call_next(request)
    return response

# Incluir rutas de la API
app.include_router(api_key_routes.router, tags=["API Key"])
app.include_router(database_routes.router, tags=["Database"])

@app.get("/")
async def root():
    """Endpoint principal para verificar que la API está funcionando"""
    api_key_status = get_api_key_settings()["is_valid"]
    return {
        "status": "online",
        "api_key_configured": api_key_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 