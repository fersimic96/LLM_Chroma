import argparse
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
import spacy
from get_embedding_function import get_embedding_function
import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv() 
os.environ["OPENAI_API_KEY"] 

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Dada la siguiente información,tomar como informacion valida para dar la respuesta y darla con coherencia en la consulta:

Informacion:
{context}

Context:

Por favor, proporciona una respuesta detallada y amplia en funcion de informacion  , ademas de correlacionar con la web , tambien explayate en la tematica.
 Si hay diferentes conclusiones que puedas analizar en "Informacion" hacer analisis para cada criterio, explayarse en cada una de ellas para no sesgar la información, 
 referencia al parrafo  de la "Informacion" dada anteriormente  [Número]. 
"Si no encuentra informacion relevante del contexto brindado, responder no hay informacion adecuada"
Finalmente, traduce la respuesta al español con inteligencia artificial para evitar errores de traducción, y solo dar la respuesta en español.

Question:
{question}
"""


def main():
    # Crear la interfaz de línea de comandos.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="El texto de la consulta.")
    args = parser.parse_args()
    query_text = args.query_text
    aux=query_translate(query_text)
    print(aux)
    # Primero, hacemos una consulta a RAG.
    rag_response = query_rag(aux)

    # Luego, hacemos una consulta a Mistral con la respuesta de RAG.
    mistral_response = query_mistral(rag_response)
    print(" ")
    print("Finish")



def query_rag(query_text: str):
    # Cargar la base de datos.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Buscar en la base de datos.
    results = db.similarity_search_with_score(query_text, k=20)

    # Sew podria agregar codigo para hacer una búsqueda en la web con tu texto de consulta
    # y añadir los resultados a tu contexto.
    # Por ejemplo:
    # web_results = web_search(query_text)
    # context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results] + web_results)

    context_text = "\n".join([f"{i+1}. {doc.page_content}" for i, (doc, _score) in enumerate(results)])
    print(" ")
    query_text = str(query_text)

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    #model = ChatOpenAI()
    model = Ollama(model="mistral")

    
    response_content = model.invoke(prompt)
    #response_content = response.content
  

   
    #sources = [f"Fuente {[i+1]}: {doc.metadata.get('id', None)}, Fragmento: {doc.page_content[:30]}..." for i, (doc, _score) in enumerate(results)]
    #formatted_sources = "\n".join(sources)

    
    # formatted_response = f"Respuesta: {response_text}\nFuentes:\n{formatted_sources}"
    # print(formatted_response)
    #print(f"Respuesta:\n{response_content}\nFuentes:\n{formatted_sources}")
    #return response



    # response_content = response.content

    sources = [f"Fuente {[i+1]}: {doc.metadata.get('id', None)}, Fragmento: {doc.page_content[:30]}..." for i, (doc, _score) in enumerate(results)]
    formatted_sources = "\n".join(sources)

    # # Se imprime solo el contenido de la respuesta y las fuentes
    print(f"Respuesta:\n{response_content}\nFuentes:\n{formatted_sources}")

    return response_content

PROMPT2_TEMPLATE = """
Dada la siguiente información:

{context}

Por favor, proporciona una respuesta detallada y precisa a la siguiente pregunta,  en español, utilizando la información proporcionada anteriormente como taxativa y cualquier 
información relevante que puedas encontrar en la web y dar la respuesta traducida con inteligencia artificial en español

{question}
"""
def query_mistral(query_text: str):
    # instancia del modelo Mistral.
    model = Ollama(model="mistral")
    # model = ChatOpenAI()
    #'query_text' es una cadena de forma estricta
    query_text = str(query_text)

    prompt2_template = ChatPromptTemplate.from_template(PROMPT2_TEMPLATE)
    prompt2 = prompt2_template.format(context="Dame informacion adecuada, tomando como informacion estricta lo siguiente: " + query_text, question="Explayarse con informacion de la web adecuada y enviar la respuesta traducida al español con IA, dame las fuentes que utilizaste con los links")

    # Hacer una consulta a Mistral con el texto de la consulta.
    
    response_text2 = model.invoke(prompt2)
    print(response_text2)
    return response_text2

def query_translate(query_text: str):
    # instancia del modelo Mistral.
   
    # model = ChatOpenAI()
    #'query_text' es una cadena de forma estricta
    query_text = str(query_text)

    prompt_template = "Context: {context}\nQuestion: {question}"
    context = "Correct spelling errors and improve the query, only give the question as an answer"
    question = "Translate to english: " + query_text

    prompt_1 = prompt_template.format(context=context, question=question)

    model = ChatOpenAI()
    # model = Ollama(model="mistral")

    
    response = model.invoke(prompt_1)
    response_content = response.content
    
    r=response_content
    return r


if __name__ == "__main__":
    main()
