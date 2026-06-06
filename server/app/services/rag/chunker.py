# pyrefly: ignore [missing-import]
from tree_sitter import Language, Parser
import os

class CodeChunker:
    def __init__(self):
        self.parsers = {}
        self.languages = {}
        
        # We will lazy-load languages to avoid import errors if a library is missing
        
        # A list of AST node types we consider as meaningful code blocks across major languages
        self.BLOCK_TYPES = {
            'function_definition', 'class_definition', # Python, TS/JS
            'method_definition', 'arrow_function', 'function_declaration', # TS/JS, C
            'method_declaration', 'class_declaration', # Java, C++, TS/JS
            'func_decl', 'method_decl', # Go
            'function_item', 'impl_item', 'struct_item', # Rust
            'interface_declaration', 'type_alias_declaration' # TS
        }

    def _get_parser(self, extension: str):
        if extension in self.parsers:
            return self.parsers[extension]

        language = None
        try:
            if extension == '.py':
                import tree_sitter_python
                language = Language(tree_sitter_python.language())
            elif extension in ['.js', '.jsx']:
                import tree_sitter_javascript
                language = Language(tree_sitter_javascript.language())
            elif extension == '.ts':
                import tree_sitter_typescript
                language = Language(tree_sitter_typescript.language_typescript())
            elif extension == '.tsx':
                import tree_sitter_typescript
                language = Language(tree_sitter_typescript.language_tsx())
            elif extension == '.java':
                import tree_sitter_java
                language = Language(tree_sitter_java.language())
            elif extension == '.go':
                import tree_sitter_go
                language = Language(tree_sitter_go.language())
            elif extension in ['.cpp', '.cc', '.cxx', '.hpp']:
                import tree_sitter_cpp
                language = Language(tree_sitter_cpp.language())
            elif extension in ['.c', '.h']:
                import tree_sitter_c
                language = Language(tree_sitter_c.language())
            elif extension == '.rs':
                import tree_sitter_rust
                language = Language(tree_sitter_rust.language())
        except ImportError:
            print(f"Warning: Tree-sitter parser for {extension} not installed.")
            return None

        if language:
            parser = Parser(language)
            self.parsers[extension] = parser
            return parser
            
        return None

    def extract_chunks(self, source_code: str, file_path: str):
        """
        Parses source code using Tree-sitter and returns meaningful chunks
        like functions and classes. Falls back to whole-file module chunking if parsing fails.
        """
        _, ext = os.path.splitext(file_path.lower())
        parser = self._get_parser(ext)
        
        chunks = []
        
        if parser:
            tree = parser.parse(bytes(source_code, "utf8"))
            root_node = tree.root_node
            
            # A simple tree traversal to find functions and classes
            def traverse(node):
                if node.type in self.BLOCK_TYPES:
                    # Extract the exact text for this block of code
                    chunk_text = source_code[node.start_byte:node.end_byte]
                    
                    # We can also grab the function/class name for metadata
                    name_node = node.child_by_field_name('name')
                    chunk_name = source_code[name_node.start_byte:name_node.end_byte] if name_node else "unknown"
                    
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "file_path": file_path,
                            "type": node.type,
                            "name": chunk_name,
                            "start_line": node.start_point[0],
                            "end_line": node.end_point[0]
                        }
                    })
                
                # Continue traversing children
                for child in node.children:
                    traverse(child)

            traverse(root_node)
            
        # If no specific functions/classes were found or parsing is unsupported, 
        # treat the whole file as a single module chunk.
        # This acts as our fallback for text files like .css, .html, .md, or unsupported langs.
        if not chunks and source_code.strip():
            chunks.append({
                "text": source_code,
                "metadata": {
                    "file_path": file_path,
                    "type": "module" if parser else "text_file",
                    "name": os.path.basename(file_path),
                    "start_line": 0,
                    "end_line": len(source_code.splitlines())
                }
            })
            
        return chunks

# Test code block (runs only if this file is executed directly)
if __name__ == "__main__":
    sample_code = """
def hello_world():
    print("Hello, world!")

class Calculator:
    def add(self, a, b):
        return a + b
"""
    chunker = CodeChunker()
    extracted = chunker.extract_chunks(sample_code, "sample.py")
    for i, chunk in enumerate(extracted):
        print(f"--- Chunk {i+1} [{chunk['metadata']['type']}: {chunk['metadata']['name']}] ---")
        print(chunk['text'])
