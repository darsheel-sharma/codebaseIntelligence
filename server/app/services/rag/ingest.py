import os
from langchain_core.documents import Document
from app.services.rag.chunker import CodeChunker
from app.core.database import get_vector_store

class IngestionService:
    def __init__(self):
        self.chunker = CodeChunker()
        self.vector_store = get_vector_store()

    def process_directory(self, directory_path: str):
        SUPPORTED_EXTENSIONS = {
            '.py', '.js', '.jsx', '.ts', '.tsx', 
            '.java', '.go', '.cpp', '.cc', '.cxx', '.hpp', 
            '.c', '.h', '.rs', '.css', '.html', '.md'
        }
        
        documents = []
        # Walk through the directory to find all supported files
        for root, _, files in os.walk(directory_path):
            # Skip virtual environment and node_modules folders
            if any(skip in root for skip in ["venv", ".venv", "node_modules", ".git", "dist", "build"]):
                continue

            for file in files:
                _, ext = os.path.splitext(file.lower())
                if ext in SUPPORTED_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            source_code = f.read()
                        
                        # Extract semantic chunks using Tree-sitter
                        chunks = self.chunker.extract_chunks(source_code, file_path)
                        
                        # Convert to LangChain Document objects
                        for chunk in chunks:
                            # Prepend metadata to the raw code to dramatically improve semantic matching
                            # When the user asks "where is query.py", this text helps the vector DB find it.
                            enhanced_content = (
                                f"File Path: {file_path}\n"
                                f"Code Block Type: {chunk['metadata'].get('type', 'unknown')}\n"
                                f"Component Name: {chunk['metadata'].get('name', 'unknown')}\n"
                                f"---\n{chunk['text']}"
                            )
                            
                            doc = Document(
                                page_content=enhanced_content,
                                metadata=chunk['metadata']
                            )
                            documents.append(doc)
                    except Exception as e:
                        print(f"Failed to process {file_path}: {e}")
        
        # Insert all documents into pgvector
        if documents:
            try:
                self.vector_store.delete_collection()
            except Exception:
                pass # May fail if it doesn't exist yet
            
            # Re-initialize the PGVector object because delete_collection invalidates the current object's internal collection_id
            from app.core.database import embeddings, settings
            from langchain_postgres import PGVector
            self.vector_store = PGVector(
                embeddings=embeddings,
                collection_name="codebase_chunks",
                connection=settings.DATABASE_URL,
                use_jsonb=True,
            )
            
            self.vector_store.add_documents(documents)
            print(f"Successfully ingested {len(documents)} chunks from {directory_path}")
        else:
            print(f"No valid chunks found in {directory_path}")
        
        return len(documents)

if __name__ == "__main__":
    # Quick test to ingest the 'app' directory
    ingester = IngestionService()
    
    # Path to the server/app folder
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../app"))
    print(f"Starting ingestion for: {test_dir}")
    
    count = ingester.process_directory(test_dir)
    print(f"Done! {count} documents added to the database.")
