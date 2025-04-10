import os
import json
from dotenv import load_dotenv
from pathlib import Path
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
QDRANT_PATH = os.path.join(BASE_DIR, "data")

# Configuración de la API Key
class ApiKeyConfig:
    _api_key = None
    _config_file = os.path.join(os.path.dirname(__file__), 'config.json')

    @classmethod
    def _load_from_file(cls):
        try:
            if os.path.exists(cls._config_file):
                with open(cls._config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key')
        except Exception as e:
            logger.error(f"Error al cargar la configuración: {e}")
        return None

    @classmethod
    def _save_to_file(cls, api_key):
        try:
            os.makedirs(os.path.dirname(cls._config_file), exist_ok=True)
            config = {}
            if os.path.exists(cls._config_file):
                with open(cls._config_file, 'r') as f:
                    config = json.load(f)
            config['api_key'] = api_key
            with open(cls._config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            logger.error(f"Error al guardar la configuración: {e}")

    @classmethod
    def get_api_key(cls):
        if cls._api_key is None:
            # Intentar cargar desde archivo primero
            cls._api_key = cls._load_from_file()
            if cls._api_key is None:
                # Si no está en archivo, intentar desde variable de entorno
                cls._api_key = os.getenv("OPENAI_API_KEY")
        return cls._api_key

    @classmethod
    def set_api_key(cls, api_key):
        if not api_key:
            raise ValueError("La API key no puede estar vacía")
        cls._api_key = api_key
        # Guardar en archivo
        cls._save_to_file(api_key)
        # También actualizar la variable de entorno
        os.environ["OPENAI_API_KEY"] = api_key
        return True

# Crear directorios necesarios
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(QDRANT_PATH, exist_ok=True)

# Configuración de la aplicación
class Settings:
    PROJECT_NAME = "ChatBot Simich"
    VERSION = "1.0.0"
    API_V1_STR = "/api/v1"
    
    # Configuración del servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Configuración de CORS
    CORS_ORIGINS = [
        "http://localhost:5003",  # Frontend dev server
        "http://127.0.0.1:5003",
    ]

settings = Settings()

# Exportar configuraciones
__all__ = ["UPLOAD_DIR", "QDRANT_PATH", "ApiKeyConfig", "settings"]

# Configuración de rutas
class PathConfig:
    _base_path = ""
    
    @classmethod
    def get_base_path(cls):
        return cls._base_path
    
    @classmethod
    def set_base_path(cls, path):
        if not os.path.exists(path):
            raise ValueError(f"El directorio {path} no existe")
        cls._base_path = path
        return cls._base_path
