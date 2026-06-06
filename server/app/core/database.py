# pyrefly: ignore [missing-import]
from langchain_huggingface import HuggingFaceEmbeddings
# pyrefly: ignore [missing-import]
from langchain_postgres import PGVector
from app.core.config import settings

# Initialize local HuggingFace Embeddings model (converts code to vectors)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize PGVector VectorStore
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="codebase_chunks",
    connection=settings.DATABASE_URL,
    use_jsonb=True,
)

def get_vector_store():
    return vector_store