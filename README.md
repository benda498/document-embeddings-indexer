# Document Embeddings Indexer

Python script that takes PDF/DOCX files, splits them into sentences, generates embeddings via Google Gemini API, and stores everything in PostgreSQL.

## Setup

**Requirements:**
- Python 3.8+
- PostgreSQL with pgvector extension
- Google Gemini API key

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure environment:**

Create a `.env` file in the project directory with the following structure:

```
GEMINI_API_KEY=your_gemini_api_key_here
POSTGRES_URL=postgresql://user:password@host:5432/database
```

- Get your Gemini API key from https://makersuite.google.com/app/apikey
- PostgreSQL connection string format: `postgresql://username:password@host:port/database_name`
- Make sure pgvector extension is enabled in your database:

```sql
CREATE EXTENSION vector;
```

## Usage

```bash
python index_documents.py document.pdf
```

The script will:
1. Extract text from the file
2. Split into sentences
3. Generate 768-dimensional embeddings for each sentence
4. Save to PostgreSQL

## Database Schema

```sql
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    filename VARCHAR(255),
    split_strategy VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Notes

Works with PDF and DOCX files only. Each sentence is treated as a separate chunk using sentence-based splitting strategy.

