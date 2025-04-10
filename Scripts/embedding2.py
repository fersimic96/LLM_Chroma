import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
from get_embedding_function import get_embedding_function
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import uuid

# Cargar variables de entorno
load_dotenv()

# Configuración de Qdrant
QDRANT_PATH = "qdrant_db"
COLLECTION_NAME = "documentos"
VECTOR_SIZE = 1536  # Tamaño de los embeddings de Azure OpenAI text-embedding-3-large

def create_qdrant_collection(client):
    """Crear una colección en Qdrant si no existe"""
    collections = client.get_collections().collections
    exists = any(col.name == COLLECTION_NAME for col in collections)
    
    if exists:
        print(f"Eliminando colección '{COLLECTION_NAME}' existente...")
        client.delete_collection(collection_name=COLLECTION_NAME)
    
    print(f"Creando colección '{COLLECTION_NAME}'...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Colección '{COLLECTION_NAME}' creada.")

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
    
    # Dividir el texto en chunks más pequeños
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
    
    print(f"Documento dividido en {len(final_chunks)} chunks")
    return final_chunks

def main():
    # Crear cliente de Qdrant
    client = QdrantClient(path=QDRANT_PATH)
    
    # Crear colección si no existe
    create_qdrant_collection(client)
    
    # Obtener la función de embeddings de Azure
    embedding_function = get_embedding_function()
    
    # Procesar PDFs
    pdf_dir = "pdfs"
    if not os.path.exists(pdf_dir):
        print(f"Error: No se encontró el directorio {pdf_dir}")
        return
        
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            print(f"\nProcesando: {filename}")
            
            try:
                # Procesar el PDF
                chunks = process_pdf(pdf_path)
                
                # Generar embeddings y guardar en Qdrant
                for chunk in chunks:
                    # Generar embedding
                    embedding = embedding_function.embed_query(chunk['text'])
                    
                    # Preparar metadatos
                    metadata = {
                        'Fuente': filename,
                        'pagina': chunk['page'],
                        'texto': chunk['text'][:200]  # Primeros 200 caracteres como preview
                    }
                    
                    # Guardar en Qdrant
                    client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=[
                            models.PointStruct(
                                id=str(uuid.uuid4()),
                                vector=embedding,
                                payload=metadata
                            )
                        ]
                    )
                
                print(f"Documento {filename} procesado y guardado en Qdrant")
                
            except Exception as e:
                print(f"Error procesando {filename}: {str(e)}")
                continue

if __name__ == "__main__":
    main()
