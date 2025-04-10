from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
import os
import logging
import sys
import subprocess
from pathlib import Path
import shutil
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de rutas
UPLOAD_DIR = "uploads"
QDRANT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "qdrant_db")

# Template para el prompt
PROMPT_TEMPLATE = """
Dada la siguiente información ayudarse con toda tu informacion para dar la respuesta ,

Información:
{context}

Por favor, proporciona una respuesta detallada brindando información para responder, también expándete en la temática según la información dada. Haz un análisis para cada criterio, según la información dada responde según todas las posibles fuentes. Referencia al párrafo de la información dada anteriormente [Número] o la fuente de información de LLM. "Usa la información de la web y pon el enlace." Finalmente, traduce la respuesta al español con inteligencia artificial para evitar errores de traducción, y solo da la respuesta en español.

Pregunta:
{question}
"""

router = APIRouter()

def get_qdrant_client():
    """Obtiene el cliente de Qdrant con la ruta configurada"""
    try:
        # Asegurarse de que el directorio existe
        os.makedirs(QDRANT_PATH, exist_ok=True)
        
        client = QdrantClient(path=QDRANT_PATH)
        logger.info(f"Cliente Qdrant inicializado con ruta: {QDRANT_PATH}")
        return client
    except Exception as e:
        logger.error(f"Error al inicializar cliente Qdrant: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al conectar con la base de datos vectorial"
        )

def verify_qdrant_connection():
    """Verifica la conexión a Qdrant y asegura que el directorio existe"""
    try:
        client = get_qdrant_client()
        # Intentar una operación simple para verificar la conexión
        client.get_collections()
        logger.info("Conexión a Qdrant verificada exitosamente")
        return True
    except Exception as e:
        logger.error(f"Error al conectar con Qdrant: {str(e)}")
        return False

# Verificar conexión al iniciar
verify_qdrant_connection()

class DatabasePathRequest(BaseModel):
    path: str

class PathUpdate(BaseModel):
    base_path: str

class CollectionCreate(BaseModel):
    collection_name: str

class QueryRequest(BaseModel):
    query: str
    collections: List[str]

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
    """Actualiza la ruta base para las bases de datos y configura Qdrant."""
    logger.info(f"Actualizando ruta base a: {path_update.base_path}")
    
    try:
        # Actualizar la ruta base usando PathConfig
        PathConfig.set_base_path(path_update.base_path)
        logger.info(f"Ruta base actualizada a: {PathConfig.get_base_path()}")
        
        # Configurar y verificar Qdrant
        qdrant_path = os.path.join(path_update.base_path, "qdrant_db")
        os.makedirs(qdrant_path, exist_ok=True)
        
        # Verificar la conexión a Qdrant
        if not verify_qdrant_connection():
            raise HTTPException(
                status_code=500,
                detail="No se pudo establecer conexión con la base de datos vectorial"
            )
        
        return {
            "status": "success",
            "base_path": PathConfig.get_base_path(),
            "qdrant_path": qdrant_path
        }
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

def process_pdf(pdf_path):
    """Procesar un archivo PDF usando pdfplumber"""
    text_chunks = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                text_chunks.append({
                    'text': text,
                    'page': page_num + 1
                })
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    final_chunks = []
    for chunk in text_chunks:
        splits = text_splitter.split_text(chunk['text'])
        for split in splits:
            final_chunks.append({
                'text': split,
                'page': chunk['page']
            })
    
    return final_chunks

@router.get("/qdrant-collections")
async def list_collections():
    """Lista todas las colecciones disponibles en Qdrant"""
    try:
        client = get_qdrant_client()
        collections_list = client.get_collections()
        
        # Obtener detalles de cada colección
        collections_info = []
        for collection in collections_list.collections:
            try:
                collection_info = client.get_collection(collection.name)
                vectors_count = collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else 0
                
                # Agregar información detallada de la colección
                collections_info.append({
                    "name": collection.name,
                    "vectors_count": vectors_count,
                    "status": "active" if collection_info.status == "green" else "error"
                })
                logger.info(f"Colección {collection.name}: {vectors_count} vectores")
            except Exception as e:
                logger.error(f"Error al obtener detalles de la colección {collection.name}: {str(e)}")
                collections_info.append({
                    "name": collection.name,
                    "vectors_count": 0,
                    "status": "error"
                })
        
        return {"collections": collections_info}
    except Exception as e:
        logger.error(f"Error al listar colecciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener las colecciones"
        )

@router.post("/qdrant-collections")
async def create_collection(collection: CollectionCreate):
    """Crea una nueva colección en Qdrant con parámetros optimizados"""
    try:
        client = get_qdrant_client()
        # Verificar si la colección ya existe
        collections = client.get_collections().collections
        if any(col.name == collection.collection_name for col in collections):
            return {"message": f"La colección {collection.collection_name} ya existe"}

        # Crear colección con parámetros optimizados
        client.create_collection(
            collection_name=collection.collection_name,
            vectors_config=models.VectorParams(
                size=1536,  # Tamaño de embeddings de OpenAI
                distance=models.Distance.COSINE
            ),
            optimizers_config=models.OptimizersConfigDiff(
                indexing_threshold=20000,  # Optimizado para rendimiento
                memmap_threshold=10000
            )
        )
        logger.info(f"Colección {collection.collection_name} creada exitosamente")
        return {"message": f"Colección {collection.collection_name} creada exitosamente"}
    except Exception as e:
        logger.error(f"Error al crear la colección: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-embeddings")
async def upload_embeddings(files: List[UploadFile] = File(...), collection_name: str = Form(...)):
    """Procesa múltiples archivos PDF y genera embeddings para almacenar en Qdrant"""
    try:
        # Validar que hay archivos
        if not files:
            raise HTTPException(status_code=400, detail="No se proporcionaron archivos")

        client = get_qdrant_client()
        total_chunks = 0
        total_embeddings = 0

        for file in files:
            # Validar el tipo de archivo
            if not file.filename.endswith('.pdf'):
                logger.warning(f"Omitiendo {file.filename}: no es un archivo PDF")
                continue

            # Guardar el archivo temporalmente
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            try:
                content = await file.read()
                with open(file_path, "wb") as buffer:
                    buffer.write(content)
            except Exception as e:
                logger.error(f"Error al guardar el archivo {file.filename}: {str(e)}")
                continue

            try:
                # Extraer texto del PDF
                text_chunks = process_pdf(file_path)
                if not text_chunks:
                    logger.warning(f"No se pudo extraer texto del archivo {file.filename}")
                    continue

                # Generar embeddings
                embeddings = []
                for chunk in text_chunks:
                    try:
                        embedding = get_embedding_function().embed_query(chunk['text'])
                        embeddings.append((chunk, embedding))
                    except Exception as e:
                        logger.error(f"Error al generar embedding: {str(e)}")
                        continue

                if not embeddings:
                    logger.warning(f"No se pudieron generar embeddings para {file.filename}")
                    continue

                # Almacenar en Qdrant
                points = []
                for i, (chunk, embedding) in enumerate(embeddings):
                    points.append(models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "text": chunk['text'],
                            "page": chunk['page'],
                            "source": file.filename
                        }
                    ))

                client.upsert(
                    collection_name=collection_name,
                    points=points
                )

                total_chunks += len(text_chunks)
                total_embeddings += len(embeddings)
                logger.info(f"Archivo {file.filename} procesado: {len(embeddings)} embeddings generados")

            except Exception as e:
                logger.error(f"Error procesando {file.filename}: {str(e)}")
                continue
            finally:
                # Limpiar archivo temporal
                if os.path.exists(file_path):
                    os.remove(file_path)

        if total_embeddings == 0:
            raise HTTPException(status_code=400, detail="No se pudieron procesar los archivos")

        return {
            "message": "Archivos procesados exitosamente",
            "total_chunks": total_chunks,
            "total_embeddings": total_embeddings
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error en el proceso de embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en el procesamiento")

def get_embedding_function():
    """Retorna la función de embedding configurada con OpenAI"""
    try:
        return OpenAIEmbeddings()
    except Exception as e:
        logger.error(f"Error al inicializar OpenAIEmbeddings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al inicializar el servicio de embeddings. Verifica tu API key de OpenAI."
        )

@router.post("/query")
async def query(request: QueryRequest):
    """Procesa una consulta sobre múltiples colecciones de Qdrant"""
    try:
        logger.info(f"Procesando consulta para colecciones: {request.collections}")
        logger.info(f"Query: {request.query}")
        
        # Obtener embedding de la consulta
        embedding_function = OpenAIEmbeddings()
        query_vector = embedding_function.embed_query(request.query)
        
        # Conectar a Qdrant
        client = get_qdrant_client()
        
        # Verificar que las colecciones existen
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        for collection in request.collections:
            if collection not in collection_names:
                raise HTTPException(
                    status_code=404, 
                    detail=f"La colección {collection} no existe"
                )
        
        # Buscar documentos similares en todas las colecciones seleccionadas
        all_results = []
        for collection_name in request.collections:
            results = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=10  # Reducimos el límite por colección para no saturar
            )
            # Agregar el nombre de la colección a los resultados
            for result in results:
                result.payload['collection'] = collection_name
            all_results.extend(results)
        
        # Ordenar todos los resultados por score
        all_results.sort(key=lambda x: x.score, reverse=True)
        # Tomar los 20 mejores resultados
        all_results = all_results[:20]
        
        logger.info(f"Encontrados {len(all_results)} resultados en total")
        
        if not all_results:
            return {"response": "No se encontró información relevante en las colecciones seleccionadas."}
        
        # Preparar el contexto
        context_text = "\n".join([
            f"{i+1}. [{result.payload['collection']}] {result.payload['text']}" 
            for i, result in enumerate(all_results)
        ])
        
        # Configurar el prompt
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format_messages(
            context=context_text,
            question=request.query
        )
        
        # Preparar fuentes
        sources = []
        for i, result in enumerate(all_results):
            source_info = f"Fuente [{i+1}]: {result.payload['collection']} - {result.payload['source']}, Página: {result.payload['page']}, Fragmento: {result.payload['text'][:30]}..."
            sources.append(source_info)
            
        formatted_sources = "\n".join(sources)

        async def generate():
            # Generar respuesta con GPT en modo streaming
            model = ChatOpenAI(
                streaming=True,
                temperature=0.7,
                model_name="gpt-3.5-turbo"
            )

            collected_chunks = []
            async for chunk in model.astream(prompt):
                content = chunk.content
                collected_chunks.append(content)
                # Enviar el chunk actual y el texto acumulado
                yield f"data: {json.dumps({'delta': content, 'text': ''.join(collected_chunks)})}\n\n"
            
            # Enviar mensaje final con fuentes
            full_response = ''.join(collected_chunks)
            final_response = f"{full_response}\n\nFuentes:\n{formatted_sources}"
            yield f"data: {json.dumps({'delta': '', 'text': final_response, 'done': True})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error en el proceso de consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collection-files/{collection_name}")
async def get_collection_files(collection_name: str):
    """Obtiene los archivos almacenados en una colección específica, agrupados por archivo"""
    try:
        client = get_qdrant_client()
        
        # Verificar si la colección existe
        collections = client.get_collections().collections
        if not any(col.name == collection_name for col in collections):
            raise HTTPException(status_code=404, detail=f"Colección {collection_name} no encontrada")
        
        # Obtener el recuento total de vectores en la colección
        collection_info = client.get_collection(collection_name)
        vectors_count = collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else 0
        
        if vectors_count == 0:
            return {"files": []}
        
        # Consultar los primeros 1000 vectores para obtener metadatos
        # Esto es para obtener una muestra representativa de los archivos
        scroll_result = client.scroll(
            collection_name=collection_name,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )
        
        points = scroll_result[0]  # Obtener los puntos de la respuesta
        
        # Agrupar los puntos por archivo
        files_map = {}
        for point in points:
            if 'source' in point.payload:
                file_name = point.payload['source']
                
                if file_name not in files_map:
                    files_map[file_name] = {
                        'name': file_name,
                        'vectors': 0,
                        'pages': set(),
                        'chunks': 0
                    }
                
                files_map[file_name]['vectors'] += 1
                
                if 'page' in point.payload:
                    files_map[file_name]['pages'].add(point.payload['page'])
                
                files_map[file_name]['chunks'] += 1
        
        # Convertir a lista y formatear
        files_list = []
        for file_name, file_info in files_map.items():
            files_list.append({
                'name': file_info['name'],
                'vectors': file_info['vectors'],
                'pages': len(file_info['pages']),
                'chunks': file_info['chunks']
            })
        
        # Ordenar por nombre
        files_list.sort(key=lambda x: x['name'])
        
        return {"files": files_list}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error al obtener archivos de la colección {collection_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos: {str(e)}")

@router.delete("/collection-files/{collection_name}/{file_name}")
async def delete_collection_file(collection_name: str, file_name: str):
    """Elimina todos los vectores de un archivo específico en una colección"""
    try:
        client = get_qdrant_client()
        
        # Verificar si la colección existe
        collections = client.get_collections().collections
        if not any(col.name == collection_name for col in collections):
            raise HTTPException(status_code=404, detail=f"Colección {collection_name} no encontrada")
        
        # Eliminar por filtro - eliminar todos los puntos con el mismo source
        delete_result = client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="source",
                            match=models.MatchValue(value=file_name)
                        )
                    ]
                )
            )
        )
        
        # Verificar si se eliminaron puntos
        if delete_result.status != "completed":
            logger.warning(f"Operación de eliminación completada con estado: {delete_result.status}")
        
        return {"message": f"Archivo {file_name} eliminado de la colección {collection_name}"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error al eliminar archivo {file_name} de la colección {collection_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar archivo: {str(e)}")
