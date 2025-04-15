# ESG AI Analysis Platform

A powerful platform for analyzing ESG (Environmental, Social, and Governance) documents using AI. Built with Next.js, FastAPI, and LLM integration.

## Features

- 📄 Document Upload & Processing
  - Support for PDF and DOCX files
  - Automatic text extraction and chunking
  - Vector storage using ChromaDB

- 💬 Question Answering System
  - Natural language queries about ESG documents
  - Context-aware responses using LLM
  - Citation support with source highlighting
  - Answer validation functionality

- 📊 ESG Metrics Dashboard
  - Automatic metrics extraction
  - Table and chart visualization
  - RAG (Red, Amber, Green) status tracking
  - Performance trend analysis

## Project Structure

```
esg-v1/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI application
│   └── requirements.txt   # Python dependencies
├── src/                   # Next.js frontend
│   ├── app/
│   │   ├── components/   # React components
│   │   └── page.tsx      # Main page
├── uploads/              # Document storage
├── chroma_db/            # Vector database
└── .env                  # Environment variables
```

## Tech Stack

- **Frontend**:
  - Next.js 14
  - React
  - TailwindCSS
  - Chart.js
  - React Dropzone

- **Backend**:
  - FastAPI
  - SQLite
  - ChromaDB
  - OpenAI GPT-4
  - PyMuPDF & python-docx

## Setup Instructions

### Prerequisites

- Node.js 18+
- Python 3.8+
- OpenAI API key

### Environment Setup

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd esg-v1
   ```

2. Create a `.env` file in the project root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Backend Setup

1. Create and activate a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:
   ```bash
   cd ..  # Return to project root
   uvicorn backend.app.main:app --reload --port 8000
   ```

   The backend API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Start the Next.js development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Usage

1. **Document Upload**:
   - Navigate to the home page
   - Drag & drop or click to upload an ESG document (PDF/DOCX)
   - The document will be processed automatically
   - Processing includes:
     - Text extraction
     - Chunking
     - Vector embedding generation
     - Storage in ChromaDB

2. **Question Answering**:
   - Select a processed document
   - Type your question in natural language
   - The system will:
     - Search relevant context using ChromaDB
     - Generate an answer using GPT-4
     - Provide source citations
   - You can validate answers as helpful/not helpful

3. **ESG Metrics**:
   - Navigate to the ESG Performance Dashboard
   - Click "Extract Metrics" to analyze the document
   - View metrics in:
     - Table format with RAG status
     - Radar chart visualization
   - Track performance trends over time

## Development

### API Endpoints

- `POST /documents/upload`: Upload and process documents
- `POST /qa/ask`: Ask questions about documents
- `POST /metrics/extract`: Extract ESG metrics
- `GET /metrics/{document_id}`: Get metrics for a document

### Database Schema

- `users`: User authentication and management
- `documents`: Document metadata and processing status
- `qa_interactions`: Question-answer history
- `esg_metrics`: Extracted metrics and performance data

### Vector Storage

- Uses ChromaDB for semantic search
- Document chunks stored with metadata
- Enables context-aware question answering

## Troubleshooting

1. **Backend Issues**:
   - Check Python virtual environment is activated
   - Verify OpenAI API key in `.env`
   - Look for errors in backend logs

2. **Frontend Issues**:
   - Clear npm cache if needed: `npm cache clean --force`
   - Check console for JavaScript errors
   - Verify API endpoint URLs

3. **Document Processing**:
   - Ensure document format is PDF or DOCX
   - Check file permissions
   - Monitor ChromaDB logs for embedding issues

## License

MIT
