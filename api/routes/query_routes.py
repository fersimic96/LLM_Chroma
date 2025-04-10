from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, AsyncGenerator
import json
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain.prompts import ChatPromptTemplate

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    collections: List[str]

class Source(BaseModel):
    id: str
    content: str
    score: float
    metadata: dict

class QueryResponse(BaseModel):
    response: str
    sources: List[Source]

# Template para el prompt
PROMPT_TEMPLATE = """
Dada la siguiente información ayudarse con toda tu informacion para dar la respuesta ,

Información:
{context}

Por favor, proporciona una respuesta detallada brindando información para responder, también expándete en la temática según la información dada. Haz un análisis para cada criterio, según la información dada responde según todas las posibles fuentes. Referencia al párrafo de la información dada anteriormente [Número] o la fuente de información de LLM. "Usa la información de la web y pon el enlace." Finalmente, traduce la respuesta al español con inteligencia artificial para evitar errores de traducción, y solo da la respuesta en español.

Pregunta:
{question}
"""

QDRANT_PATH = "qdrant_db"

@router.post("/query")
async def query(request: QueryRequest):
    try:
        print(f"Procesando consulta para colecciones: {request.collections}")
        print(f"Query: {request.query}")
        
        # Obtener embedding de la consulta
        embedding_function = OpenAIEmbeddings()
        query_vector = embedding_function.embed_query(request.query)
        
        # Conectar a Qdrant
        client = QdrantClient(path=QDRANT_PATH)
        
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
        
        print(f"Encontrados {len(all_results)} resultados en total")
        
        if not all_results:
            return {"response": "No se encontró información relevante en las colecciones seleccionadas."}
        
        # Preparar el contexto
        context_text = "\n".join([
            f"{i+1}. [{result.payload['collection']}] {result.payload['texto']}" 
            for i, result in enumerate(all_results)
        ])
        
        # Configurar el prompt
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=request.query)
        
        # Preparar fuentes
        sources = []
        for i, result in enumerate(all_results):
            source_info = f"Fuente [{i+1}]: {result.payload['collection']} - {result.payload['Fuente']}, Página: {result.payload['pagina']}, Fragmento: {result.payload['texto'][:30]}..."
            sources.append(source_info)
            
        formatted_sources = "\n".join(sources)

        async def generate() -> AsyncGenerator[str, None]:
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
        
    except Exception as e:
        error_msg = f"Error al procesar consulta: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
