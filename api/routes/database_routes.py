from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import logging
import sys
import subprocess
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar el directorio raíz del proyecto al PYTHONPATH
api_dir = Path(__file__).resolve().parent.parent
if str(api_dir) not in sys.path:
    sys.path.append(str(api_dir))

from config import PathConfig

router = APIRouter()

class DatabasePathRequest(BaseModel):
    path: str

class PathUpdate(BaseModel):
    base_path: str

@router.post("/select_folder")
async def select_folder():
    """Abre un diálogo para seleccionar una carpeta y devuelve la ruta seleccionada."""
    # AppleScript para mostrar el diálogo de selección de carpeta
    script = '''
    tell application "System Events"
        activate
        set folderPath to POSIX path of (choose folder with prompt "Seleccionar carpeta de bases de datos")
    end tell
    '''
    
    try:
        logger.info("Abriendo diálogo de selección de carpeta...")
        # Ejecutar el AppleScript
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode != 0:
            logger.error(f"Error al ejecutar osascript: {result.stderr}")
            raise HTTPException(status_code=400, detail="No se seleccionó ninguna carpeta")
            
        # Obtener la ruta seleccionada (eliminar el salto de línea al final)
        selected_path = result.stdout.strip()
        
        if not selected_path:
            logger.error("No se seleccionó ninguna carpeta (ruta vacía)")
            raise HTTPException(status_code=400, detail="No se seleccionó ninguna carpeta")
            
        logger.info(f"Carpeta seleccionada: {selected_path}")
        return {"selected_path": selected_path}
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar osascript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al seleccionar la carpeta: {str(e)}")

@router.post("/update_path")
async def update_path(path_update: PathUpdate):
    """Actualiza la ruta base para las bases de datos."""
    logger.info(f"Actualizando ruta base a: {path_update.base_path}")
    
    try:
        # Actualizar la ruta base usando PathConfig
        PathConfig.set_base_path(path_update.base_path)
        logger.info(f"Ruta base actualizada a: {PathConfig.get_base_path()}")
        return {"status": "success", "base_path": PathConfig.get_base_path()}
    except ValueError as e:
        logger.error(f"Error al actualizar la ruta: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al actualizar la ruta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/databases")
async def list_databases():
    """Lista todas las bases de datos disponibles en el directorio especificado."""
    base_path = PathConfig.get_base_path()
    logger.info(f"Listando bases de datos desde: {base_path}")
    
    # Verificar que hay una ruta base configurada
    if not base_path:
        logger.warning("No se ha especificado una ruta base")
        raise HTTPException(status_code=400, detail="No se ha especificado una ruta base")

    try:
        # Buscar directorios que empiecen con 'chroma'
        databases = []
        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)
            if os.path.isdir(full_path) and item.startswith('chroma'):
                databases.append(item)
                logger.info(f"Base de datos encontrada: {item}")

        logger.info(f"Total bases de datos encontradas: {len(databases)}")
        return {"databases": databases, "base_path": base_path}

    except Exception as e:
        logger.error(f"Error al listar bases de datos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-database-path")
async def set_database_path(request: DatabasePathRequest):
    try:
        # Actualizar la ruta base usando PathConfig
        PathConfig.set_base_path(request.path)
        logger.info(f"Ruta de base de datos actualizada a: {request.path}")
        return {"message": "Ruta de base de datos actualizada", "path": request.path}
    except ValueError as e:
        logger.error(f"Error al actualizar la ruta: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error en set_database_path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
