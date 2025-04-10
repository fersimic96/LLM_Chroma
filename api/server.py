import os
import sys
import uvicorn
import logging
from api.main import app

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Inicia el servidor backend con mejor manejo de errores"""
    try:
        port = int(os.environ.get("API_PORT", 8000))
        logger.info(f"Iniciando servidor en el puerto {port}")
        
        # Crear directorio de uploads si no existe
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            logger.info(f"Directorio de uploads creado: {uploads_dir}")
        
        uvicorn.run(
            "api.main:app", 
            host="0.0.0.0", 
            port=port,
            reload=True
        )
    except OSError as e:
        if e.errno == 48:  # Address already in use
            logger.error(f"Error: El puerto {port} ya está en uso.")
            logger.info("Intentando con el puerto 8001...")
            try:
                uvicorn.run(
                    "api.main:app",
                    host="0.0.0.0",
                    port=8001,
                    reload=True
                )
            except Exception as inner_e:
                logger.error(f"Error al iniciar en el puerto alternativo: {str(inner_e)}")
                sys.exit(1)
        else:
            logger.error(f"Error al iniciar el servidor: {str(e)}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error no esperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 