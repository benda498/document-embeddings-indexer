# Document Embeddings Indexer

A Python script that processes PDF and DOCX files, splits them into sentences, generates embeddings using Google's Gemini API, and stores everything in PostgreSQL.

## What it does

1. Takes a PDF or DOCX file
2. Extracts all the text
3. Splits it into sentences (each sentence becomes a chunk)
4. Creates embeddings for each sentence using Gemini
5. Saves everything to PostgreSQL

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL with pgvector extension
- Google Gemini API key

### Install PostgreSQL pgvector

First, you need to install the pgvector extension in your PostgreSQL database:

```sql
CREATE EXTENSION vector;
```

### Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

4. Edit `.env` and add your credentials:
   - `GEMINI_API_KEY` - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - `POSTGRES_URL` - Your PostgreSQL connection string

## Usage

Basic usage:

```bash
python index_documents.py path/to/your/file.pdf
```

The script uses sentence-based chunking:
- Each sentence becomes a separate chunk
- Splits on periods (.), exclamation marks (!), and question marks (?)
- Preserves complete sentences, so each chunk has full meaning

This approach is simple and ensures each chunk contains a complete thought.

## Examples

Process a PDF:
```bash
python index_documents.py research_paper.pdf
```

Process a Word document:
```bash
python index_documents.py report.docx
```

## Database Schema

The script creates a table called `document_embeddings` with this structure:

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| chunk_text | TEXT | The sentence |
| embedding | vector(768) | The embedding vector |
| filename | VARCHAR(255) | Original filename |
| split_strategy | VARCHAR(50) | Always "sentence_based" |
| created_at | TIMESTAMP | When it was added |

## Notes

- Embeddings are 768-dimensional vectors (Gemini's embedding-001 model)
- The script shows progress as it processes sentences
- Each sentence is treated as a complete semantic unit
- Works best with well-structured documents

## Troubleshooting

**"Could not connect to database"**
- Make sure PostgreSQL is running
- Check your connection string in `.env`
- Verify the database exists

**"API key not valid"**
- Double-check your Gemini API key
- Make sure there are no extra spaces in `.env`

**"Unsupported file format"**
- Only PDF and DOCX files are supported
- Check the file extension
