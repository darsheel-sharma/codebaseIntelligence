# Codebase Intelligence Assistant

An AI-powered developer tool designed to help you understand and navigate your codebase using natural language. It utilizes a Retrieval-Augmented Generation (RAG) pipeline to ingest code, store embeddings, and accurately answer architectural and implementation questions.

## Features

- **Semantic Code Ingestion**: Parses your project files into logical code chunks using advanced parsing to preserve semantic meaning.
- **Vector Database**: Uses PostgreSQL + `pgvector` for scalable, efficient storage and retrieval of code embeddings.
- **Interactive Chat UI**: A sleek React-based frontend to chat with your codebase, view typing indicators, and render markdown/code snippets accurately.
- **AI-Powered Insights**: Get contextual answers to complex queries like "Where is the authentication handled?" or "Explain how the RAG ingestion works in this project".

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, Vanilla CSS.
- **Backend:** Python, FastAPI, PostgreSQL (`pgvector`), LangChain/LlamaIndex (for RAG), OpenAI.

## Project Structure

```text
Project1/
├── client/           # React frontend
│   ├── src/          # Components, Services, and Styles
│   ├── package.json  # Frontend dependencies
│   └── vite.config.ts
├── server/           # FastAPI backend
│   ├── app/          # Core API logic, config, and services
│   ├── requirements.txt # Python dependencies
│   └── venv/         # Virtual environment
├── plan.md           # Original architecture and project planning
└── project_details.md # In-depth details about architecture and flows
```

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL with `pgvector` extension enabled
- OpenAI API Key (or alternative LLM provider configured)

### 1. Backend Setup

1. Navigate to the server directory:
   ```bash
   cd server
   ```
2. Activate the virtual environment (if not already active):
   ```bash
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in `server/.env` (Database URL, API Keys).
5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### 2. Frontend Setup

1. Navigate to the client directory:
   ```bash
   cd client
   ```
2. Install Node modules:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

## Usage

1. Open `http://localhost:5173` in your browser.
2. Use the left sidebar to provide the absolute path to a local directory.
3. Click **Ingest Codebase** to parse and embed the code.
4. Once ingestion is complete, use the chat interface to ask questions about the ingested code!
