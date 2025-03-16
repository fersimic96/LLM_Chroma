from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, AsyncGenerator
import json
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    database: str
    base_path: str = None

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

@router.post("/query")
async def query(request: QueryRequest):
    try:
        print(f"Procesando consulta para base de datos: {request.database}")
        print(f"Query: {request.query}")
        
        # Configurar embeddings y cargar la base de datos
        embeddings = OpenAIEmbeddings()
        base_path = request.base_path or "/Users/fernandosimich/Desktop/ChatBot"
        db_path = os.path.join(base_path, request.database)
        
        if not os.path.isdir(db_path):
            raise HTTPException(status_code=404, detail="Base de datos no encontrada")

        try:
            db = Chroma(
                persist_directory=db_path,
                embedding_function=embeddings
            )
            print(f"Base de datos cargada correctamente: {db_path}")
        except Exception as e:
            print(f"Error al cargar la base de datos: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al cargar la base de datos: {str(e)}"
            )

        # Realizar búsqueda de documentos similares
        results = db.similarity_search_with_score(request.query, k=20)
        print(f"Encontrados {len(results)} resultados")
        
        if not results:
            return {"response": "No se encontró información relevante en la base de datos."}
        
        # Preparar el contexto
        context_text = "\n".join([f"{i+1}. {doc.page_content}" for i, (doc, _score) in enumerate(results)])
        
        # Configurar el prompt
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=request.query)
        
        # Preparar fuentes
        sources = []
        for i, (doc, _score) in enumerate(results):
            metadata = doc.metadata
            source = metadata.get('Fuente', 'unknown.pdf')
            if source:
                source = os.path.basename(source)
            page = metadata.get('pagina', '0')
            chunk = metadata.get('chunk', '0')
            source_info = f"Fuente [{i+1}]: {source}:{page}:{chunk}, Fragmento: {doc.page_content[:30]}..."
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
