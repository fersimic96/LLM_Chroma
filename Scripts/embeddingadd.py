import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
from get_embedding_function import get_embedding_function
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid

# Cargar variables de entorno
load_dotenv()

# Configuración de Qdrant
QDRANT_PATH = "qdrant_db"
COLLECTION_NAME = "documentos_nace"

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

def add_documents():
    """Agregar nuevos documentos a la colección existente de Qdrant"""
    # Crear cliente de Qdrant
    client = QdrantClient(path=QDRANT_PATH)
    
    # Verificar que la colección existe
    collections = client.get_collections().collections
    if not any(col.name == COLLECTION_NAME for col in collections):
        print(f"Error: La colección '{COLLECTION_NAME}' no existe.")
        print("Primero debes crear la colección usando embedding2.py")
        return
    
    # Obtener la función de embeddings de Azure
    embedding_function = get_embedding_function()
    
    # Procesar PDFs de la carpeta pdfsADD
    pdf_dir = "pdfsADD"
    if not os.path.exists(pdf_dir):
        print(f"Error: No se encontró el directorio {pdf_dir}")
        return
    
    # Verificar si hay PDFs en el directorio
    pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    if not pdfs:
        print(f"No se encontraron archivos PDF en {pdf_dir}")
        return
    
    print(f"Se encontraron {len(pdfs)} archivos PDF para procesar")
    
    # Procesar cada PDF
    for filename in pdfs:
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
            
            print(f"Documento {filename} procesado y agregado a Qdrant")
            
            # Mover el archivo procesado a un subdirectorio 'processed'
            processed_dir = os.path.join(pdf_dir, "processed")
            if not os.path.exists(processed_dir):
                os.makedirs(processed_dir)
            
            os.rename(
                pdf_path,
                os.path.join(processed_dir, filename)
            )
            print(f"Archivo movido a {processed_dir}")
            
        except Exception as e:
            print(f"Error procesando {filename}: {str(e)}")
            continue

if __name__ == "__main__":
    add_documents()
