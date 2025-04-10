from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
from langchain_community.embeddings import OpenAIEmbeddings
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ApiKeyConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

class ApiKeyRequest(BaseModel):
    api_key: str

class ApiKeyUpdate(BaseModel):
    api_key: str

# Variables para almacenar la API key validada
api_key_storage = {
    "openai_api_key": "",
    "is_valid": False,
    "timestamp": 0
}

def get_api_key_settings():
    """Devuelve la configuración actual de la API key"""
    return api_key_storage

def set_api_key_in_env():
    """Establece la API key en las variables de entorno"""
    if api_key_storage["is_valid"] and api_key_storage["openai_api_key"]:
        os.environ["OPENAI_API_KEY"] = api_key_storage["openai_api_key"]
        return True
    return False

@router.post("/validate_api_key")
async def validate_api_key(request: ApiKeyRequest):
    """Valida una API key de OpenAI"""
    try:
        # Si es la misma API key que ya está validada, devuelve éxito inmediatamente
        if request.api_key == api_key_storage["openai_api_key"] and api_key_storage["is_valid"]:
            return {"success": True, "message": "API key ya validada"}
            
        logger.info("Validando nueva API key...")
        
        # Guardar temporalmente la API key en variables de entorno
        os.environ["OPENAI_API_KEY"] = request.api_key
        
        # Intentar usar la API key con una operación simple
        embedding_function = OpenAIEmbeddings()
        _ = embedding_function.embed_query("Test")
        
        # Si llega aquí, la API key es válida
        api_key_storage["openai_api_key"] = request.api_key
        api_key_storage["is_valid"] = True
        api_key_storage["timestamp"] = int(__import__('time').time())
        
        logger.info("API key validada y actualizada correctamente")
        return {"success": True, "message": "API key validada correctamente"}
    
    except Exception as e:
        logger.error(f"Error al validar API key: {str(e)}")
        api_key_storage["is_valid"] = False
        return {"success": False, "message": f"API key inválida: {str(e)}"}

@router.post("/set-api-key")
async def set_api_key(api_key_update: ApiKeyUpdate):
    """Actualiza la API key de OpenAI"""
    try:
        ApiKeyConfig.set_api_key(api_key_update.api_key)
        logger.info("API key actualizada exitosamente")
        return {"message": "API key actualizada exitosamente"}
    except Exception as e:
        logger.error(f"Error al actualizar la API key: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar la API key")

@router.get("/verify-api-key")
async def verify_api_key():
    """Verifica si hay una API key configurada"""
    try:
        api_key = ApiKeyConfig.get_api_key()
        return {
            "has_api_key": bool(api_key),
            "status": "válida" if api_key else "no configurada"
        }
    except Exception as e:
        logger.error(f"Error al verificar la API key: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al verificar la API key")

@router.get("/api_key_status")
async def api_key_status():
    """Devuelve el estado de la API key"""
    return {
        "is_configured": api_key_storage["is_valid"],
        "timestamp": api_key_storage["timestamp"]
    }
