import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Database connection
def get_db_connection():
    """Create and return a database connection"""
    return psycopg2.connect(os.getenv('POSTGRES_URL'))

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text.strip()

def extract_text(file_path: str) -> str:
    """Extract text based on file extension"""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

def split_text_into_chunks(text: str) -> List[str]:
    """Split text into sentences"""
    # Split by periods, exclamation marks, and question marks
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Return only non-empty sentences
    return [s.strip() for s in sentences if s.strip()]

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using Gemini API"""
    model = 'models/text-embedding-004'
    result = genai.embed_content(
        model=model,
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']

def create_table_if_not_exists(conn):
    """Create the embeddings table if it doesn't exist"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_embeddings (
            id SERIAL PRIMARY KEY,
            chunk_text TEXT NOT NULL,
            embedding vector(768),
            filename VARCHAR(255) NOT NULL,
            split_strategy VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()

def save_to_db(conn, chunks: List[str], embeddings: List[List[float]], filename: str):
    """Save chunks and embeddings to PostgreSQL"""
    cursor = conn.cursor()
    
    for chunk, embedding in zip(chunks, embeddings):
        cursor.execute("""
            INSERT INTO document_embeddings 
            (chunk_text, embedding, filename, split_strategy)
            VALUES (%s, %s, %s, %s)
        """, (chunk, embedding, filename, 'sentence_based'))
    
    conn.commit()
    cursor.close()

def process_document(file_path: str):
    """Main function to process a document"""
    print(f"Processing file: {file_path}")
    
    # Extract text
    print("Extracting text...")
    text = extract_text(file_path)
    
    # Split into chunks
    print("Splitting text into chunks...")
    chunks = split_text_into_chunks(text)
    print(f"Created {len(chunks)} chunks")
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = []
    for i, chunk in enumerate(chunks):
        if i % 10 == 0:
            print(f"Processing chunk {i+1}/{len(chunks)}")
        embedding = generate_embedding(chunk)
        embeddings.append(embedding)
    
    # Save to database
    print("Saving to database...")
    conn = get_db_connection()
    create_table_if_not_exists(conn)
    filename = Path(file_path).name
    save_to_db(conn, chunks, embeddings, filename)
    conn.close()
    
    print("Done!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Index documents with embeddings')
    parser.add_argument('file', type=str, help='Path to PDF or DOCX file')
    
    args = parser.parse_args()
    
    process_document(args.file)
