# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from app.core.config import settings
from app.services.rag.ingest import IngestionService
from app.services.rag.query import QueryService

app = FastAPI(
    title="Codebase Intelligence API",
    description="Backend API for the RAG-based Codebase Assistant",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Codebase Intelligence API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/config-test")
async def config_test():
    return {
        "database_url_configured": bool(settings.DATABASE_URL),
        "openai_api_key_configured": bool(settings.OPENAI_API_KEY)
    }

class IngestRequest(BaseModel):
    directory_path: str

@app.post("/ingest")
async def ingest_codebase(request: IngestRequest):
    try:
        ingester = IngestionService()
        chunks_count = ingester.process_directory(request.directory_path)
        return {"status": "success", "chunks_ingested": chunks_count, "directory": request.directory_path}
    except Exception as e:
        # pyrefly: ignore [missing-import]
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query_codebase(request: QueryRequest):
    try:
        query_service = QueryService()
        result = query_service.ask_question(request.question)
        return result
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))
