# RAG Pipeline PDF & Website Processor

Simple RAG system that extracts content from PDFs and websites, creates embeddings with chunk overlap, and generates AI responses.

## Quick Start

### 1. Setup & Run
```bash
# Setup PostgreSQL with PGVector
docker run -d --name pgvector-db -p 5433:5432 -e POSTGRES_PASSWORD=3485 ankane/pgvector

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "GOOGLE_API_KEY=your_google_api_key" > .env

# Run application
cd src
python app.py
```

## Features

- **PDF/TXT Processing**: Extract text with 500-char chunks (50-char overlap)
- **Website Crawling**: Extract content from web pages
- **Vector Storage**: Store embeddings in PGVector database
- **AI Responses**: Generate answers using Google Generative AI
- **Auto Cleanup**: Clear database after each session

## Requirements

- Docker (for PostgreSQL + PGVector)
- Python 3.8+
- Google API key

## Usage

1. **Start**: Run `python app.py`
2. **Choose**: Select PDF (1) or Website (2)
3. **Input**: Enter file path or URL
4. **Process**: System creates embeddings and stores in database
5. **Query**: Ask questions about the content
6. **Exit**: Type 'quit' - database auto-cleans

## Configuration

- **Chunk Size**: 500 characters
- **Overlap**: 50 characters
- **Database**: PostgreSQL (port 5433)
- **Embedding Model**: models/embedding-001 (Google)
- **LLM Model**: Google Generative AI

## Files

- `app.py` - Main application entry point
- `pipeline.py` - Main orchestrator
- `database_setup.py` - PostgreSQL + PGVector connection
- `text_processor.py` - PDF/TXT processing with chunk overlap
- `website.py` - Website content extraction
- `embedding_generator.py` - Google API embeddings generation
- `vector_store.py` - Store embeddings in PGVector database
- `retriever.py` - Vector similarity search and retrieval
- `generator.py` - LLM response generation