import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv()

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
            print(f"Error loading config: {e}")
        return None

    @classmethod
    def _save_to_file(cls, api_key):
        try:
            config = {}
            if os.path.exists(cls._config_file):
                with open(cls._config_file, 'r') as f:
                    config = json.load(f)
            config['api_key'] = api_key
            with open(cls._config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    @classmethod
    def get_api_key(cls):
        if cls._api_key is None:
            # Intentar cargar desde archivo primero
            cls._api_key = cls._load_from_file()
            if cls._api_key is None:
                # Si no está en archivo, intentar desde variable de entorno
                cls._api_key = os.environ.get("OPENAI_API_KEY")
        return cls._api_key

    @classmethod
    def set_api_key(cls, api_key):
        cls._api_key = api_key
        # Guardar en archivo
        cls._save_to_file(api_key)
        # También actualizar la variable de entorno
        os.environ["OPENAI_API_KEY"] = api_key

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
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        # Agrega aquí los dominios de producción cuando los tengas
    ]
    
    # Configuración de OpenAI
    OPENAI_API_KEY = ApiKeyConfig.get_api_key()
    if not OPENAI_API_KEY:
        raise ValueError("No se encontró OPENAI_API_KEY en las variables de entorno")
    
    # Configuración de la base de datos
    DEFAULT_DB_PATH = os.getenv("DEFAULT_DB_PATH", "/Users/fernandosimich/Desktop/ChatBot")

settings = Settings()
