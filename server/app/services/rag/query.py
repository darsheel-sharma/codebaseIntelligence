from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.database import get_vector_store
from app.core.config import settings
import asyncio
import re

class QueryService:
    def __init__(self):
        self.vector_store = get_vector_store()
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="llama-3.1-8b-instant", 
            temperature=0.2
        )
        
        # Base vector retriever (fetch top 5 per generated query)
        self.base_retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

    def ask_question(self, question: str):
        # 1. Retrieve the relevant code chunks (Manual Multi-Query Expansion)
        # Generate query variations to improve recall
        variation_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI language model assistant. Your task is to generate 2 different variations of the given user question to retrieve relevant documents from a vector database. Provide these alternative questions separated by newlines, with no numbering or extra text."),
            ("human", "Original question: {question}")
        ])
        
        chain = variation_prompt | self.llm
        response = chain.invoke({"question": question})
        variations = [q.strip() for q in response.content.split('\n') if q.strip()][:2]
        all_queries = [question] + variations
        
        print(f"Generated queries for retrieval: {all_queries}")
        
        # Gather documents for all queries
        source_documents = []
        seen_doc_ids = set()
        
        for q in all_queries:
            docs = self.base_retriever.invoke(q)
            for doc in docs:
                # Use file path + start line + end line as unique identifier
                metadata = doc.metadata
                doc_id = f"{metadata.get('file_path')}:{metadata.get('start_line')}-{metadata.get('end_line')}"
                if doc_id not in seen_doc_ids:
                    seen_doc_ids.add(doc_id)
                    source_documents.append(doc)
        
        # 2. Format them for the prompt & Context Window Optimization
        # Llama 3.1 8b has an 8k context window. Let's limit the total chars to ~15,000 to be safe.
        MAX_CONTEXT_CHARS = 15000
        context_chunks = []
        current_chars = 0
        
        for doc in source_documents:
            if current_chars + len(doc.page_content) > MAX_CONTEXT_CHARS:
                break
            context_chunks.append(doc.page_content)
            current_chars += len(doc.page_content)
            
        context_text = "\n\n".join(context_chunks)
        
        # 3. Create the tuned prompt (Phase 4: Prompt Tuning)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert developer assistant analyzing a codebase.\n"
                       "Use the provided retrieved code snippets to answer the user's question accurately.\n\n"
                       "CRITICAL INSTRUCTIONS:\n"
                       "1. First, think step-by-step in a <thought> block about how the code flows or works.\n"
                       "2. Then, provide your final comprehensive answer outside of the thought block.\n"
                       "3. If you don't know the answer or the context doesn't contain it, say so clearly.\n"
                       "4. Do NOT append a 'Sources' list at the end of your answer. The system will handle citations automatically.\n"
                       "5. If the user's input is just a greeting (like 'hi') or a general conversation completely unrelated to the codebase, politely respond without referencing the context. If you do this, you MUST include the exact string [NO_SOURCES_USED] anywhere in your response.\n\n"
                       "Context:\n{context}"),
            ("human", "{input}")
        ])
        
        # 4. Invoke LLM via standard LCEL
        chain = prompt | self.llm
        response = chain.invoke({"context": context_text, "input": question})
        answer = response.content
        
        # Strip out the <thought> block so it's not shown to the user
        answer = re.sub(r'<thought>.*?</thought>', '', answer, flags=re.DOTALL).strip()
        
        # Check if the LLM flagged that it didn't need the context
        used_sources = True
        if "[NO_SOURCES_USED]" in answer:
            used_sources = False
            answer = answer.replace("[NO_SOURCES_USED]", "").strip()
        
        # 5. Extract sources while removing duplicates
        sources = []
        if used_sources:
            seen = set()
            
            # Only include sources that were actually passed in the context window
            valid_docs = source_documents[:len(context_chunks)]
            
            for doc in valid_docs:
                file_path = doc.metadata.get("file_path", "unknown")
                name = doc.metadata.get("name", "unknown")
                identifier = f"{file_path}:{name}"
                
                if identifier not in seen:
                    seen.add(identifier)
                    sources.append({
                        "file_path": file_path,
                        "name": name,
                        "type": doc.metadata.get("type", "unknown"),
                        "content": doc.page_content
                    })
            
        return {
            "answer": answer,
            "sources": sources
        }

if __name__ == "__main__":
    # Quick test
    query_service = QueryService()
    result = query_service.ask_question("What does the chunker do?")
    print("\n--- Answer ---")
    print(result["answer"])
    print("\n--- Sources ---")
    for s in result["sources"]:
        print(f"- {s['file_path']} ({s['name']})")
