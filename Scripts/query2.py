import argparse
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from get_embedding_function import get_embedding_function
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from qdrant_client import QdrantClient
import os

# Cargar variables de entorno
load_dotenv() 
# La API key de OpenAI debe configurarse en un archivo .env:
# OPENAI_API_KEY=tu_api_key

QDRANT_PATH = "qdrant_db"
COLLECTION_NAME = "documentos"

PROMPT_TEMPLATE = """
Dada la siguiente información ayudarse con toda tu informacion para dar la respuesta ,

Información:
{context}

Contexto:

Por favor, proporciona una respuesta detallada brindando informacion para responder,  también expándete en la temática segun la informacion dada.
Haz haz un análisis para cada criterio, segun la informacion dada responde segun todas las posibles fuentes,,
referencia al párrafo de la "Información" dada anteriormente [Número] o la fuente de informacion de LLM.
"Usa la informacion de de informacion  como la de la web y pone el enlace."
Finalmente, traduce la respuesta al español con inteligencia artificial para evitar errores de traducción, y solo da la respuesta en español.

Pregunta:
{question}
"""

def main():
    # Configuración de la memoria de conversación
    memory = ConversationBufferMemory(return_messages=True)
    llm = ChatOpenAI()
    conversation = ConversationChain(llm=llm, verbose=True, memory=memory)

    print("Inicia la conversación (escribe 'Finish' para terminar):")
    
    while True:
        # Leer la entrada del usuario
        user_input = input("Usuario: ")
        
        if user_input.lower() == 'finish':
            break
        
        # Guardar el contexto actual
        conversation.predict(input=user_input)

        # Hacer una consulta a RAG.
        rag_response = query_rag(user_input)

        # Mostrar la respuesta de RAG
        print("Respuesta de RAG:")
        print(rag_response)
        print(" ")
    
    print("Conversación terminada.")

def query_rag(query_text: str):
    # Obtener embedding de la consulta
    embedding_function = get_embedding_function()
    query_vector = embedding_function.embed_query(query_text)
    
    # Conectar a Qdrant
    client = QdrantClient(path=QDRANT_PATH)
    
    # Buscar documentos similares
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=20
    )
    
    # Formatear el contexto
    context_text = "\n".join([f"{i+1}. {result.payload['texto']}" for i, result in enumerate(results)])
    
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    
    #model = ChatOpenAI(model_name="gpt-4")
    model = ChatOpenAI()
    response = model.invoke(prompt)
    response_content = response.content

    # Formatear las fuentes
    sources = [f"Fuente {[i+1]}: {result.payload['Fuente']}, Página: {result.payload['pagina']}, Fragmento: {result.payload['texto'][:30]}..." 
              for i, result in enumerate(results)]
    formatted_sources = "\n".join(sources)

    return f"Respuesta:\n{response_content}\nFuentes:\n{formatted_sources}"

def query_translate(query_text: str):
    query_text = str(query_text)
    prompt_template = "Context: {context}\nQuestion: {question}"
    context = "Correct spelling errors and improve the query, only give the question as an answer"
    question = "Translate to english: " + query_text

    prompt_1 = prompt_template.format(context=context, question=question)

    model = ChatOpenAI()
    response = model.invoke(prompt_1)
    response_content = response.content

    return response_content

if __name__ == "__main__":
    main()
