from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI
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

@router.post("/validate_api_key")
async def validate_api_key(request: ApiKeyRequest):
    try:
        logger.info("Validando nueva API key...")
        
        # Crear un cliente de OpenAI con la API key proporcionada
        client = OpenAI(api_key=request.api_key)
        
        # Intentar hacer una llamada simple para validar la API key
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input="Test"
        )
        
        # Si llegamos aquí, la API key es válida
        # Guardar la API key usando ApiKeyConfig
        ApiKeyConfig.set_api_key(request.api_key)
        logger.info("API key validada y actualizada correctamente")
        
        # Devolver una respuesta más detallada
        return {
            "status": "success",
            "message": "API key válida y configurada correctamente",
            "details": {
                "model": "text-embedding-ada-002",
                "organization": client.organization,  # Esto mostrará la organización asociada a la API key
                "validated": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error al validar API key: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail={
                "status": "error",
                "message": "API key inválida",
                "error": str(e)
            }
        )

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
