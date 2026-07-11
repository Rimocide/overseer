import os
import io
import tarfile
import hashlib
import requests
import time
import pathspec
from pathlib import Path
from dotenv import load_dotenv

from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
import tree_sitter_go as tsgo

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

class UniversalCodeRAGPipeline:
    def __init__(self, github_token: str, pinecone_index_name: str, pinecone_api_key: str):
        self.github_token = github_token
        self.embed_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", task_type="retrieval_document", output_dimensionality=768)
        self.summary_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        existing_indexes = [idx.name for idx in pc.list_indexes()]

        if pinecone_index_name not in existing_indexes:
            print(f"Index '{pinecone_index_name}' not found. Initializing serverless instance...")
            pc.create_index(
            name=pinecone_index_name,
            dimension=768,  
            metric="cosine",
            spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
                    )
            )

        while not pc.describe_index(pinecone_index_name).status['ready']:
            print(f"Waiting for index '{pinecone_index_name}' to become active...")
            time.sleep(2)
                        
        print(f"Index '{pinecone_index_name}' is fully ready.")
        
        self.index = pc.Index(pinecone_index_name)

        # registers languages and maps extension types to their specific tree-sitter node targets
        self.LANGUAGE_REGISTRY = {
                    ".py": {
                        "language": Language(tspython.language()), # Wraps PyCapsule cleanly
                        "target_nodes": ["function_definition", "class_definition"]
                    },
                    ".js": {
                        "language": Language(tsjavascript.language()),
                        "target_nodes": ["function_declaration", "method_definition", "arrow_function", "class_declaration"]
                    },
                    ".jsx": {
                        "language": Language(tsjavascript.language()),
                        "target_nodes": ["function_declaration", "method_definition", "arrow_function", "class_declaration"]
                    },
                    ".ts": {
                        "language": Language(tstypescript.language_typescript()),
                        "target_nodes": ["function_declaration", "method_definition", "arrow_function", "class_declaration"]
                    },
                    ".tsx": {
                        "language": Language(tstypescript.language_tsx()),
                        "target_nodes": ["function_declaration", "method_definition", "arrow_function", "class_declaration"]
                    },
                    ".go": {
                        "language": Language(tsgo.language()),
                        "target_nodes": ["function_declaration", "method_declaration", "type_declaration"]
                    }
                }

        self.parser = Parser()

    def fetch_repo_tarball(self, owner: str, repo: str) -> list[dict]:
        url = f"https://api.github.com/repos/{owner}/{repo}/tarball"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()

        tar = tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz")
        extracted_files = []
        gitignore_patterns = [".git/", "node_modules/", "venv/", "dist/", "build/", "*.pyc"]

        for member in tar.getmembers():
            if member.name.endswith(".gitignore"):
                f = tar.extractfile(member)
                if f:
                    gitignore_patterns.extend(f.read().decode('utf-8').splitlines())

        spec = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_patterns)
        supported_extensions = tuple(self.LANGUAGE_REGISTRY.keys())

        for member in tar.getmembers():
            if member.isfile():
                relative_path = "/".join(member.name.split("/")[1:])

                if not spec.match_file(relative_path) and relative_path.endswith(supported_extensions):
                    file_obj = tar.extractfile(member)
                    if file_obj:
                        extracted_files.append({
                            "path": relative_path,
                            "extension": Path(relative_path).suffix,
                            "content": file_obj.read().decode("utf-8", errors="ignore")
                        })
        return extracted_files

    def chunk_code_ast(self, source_code: str, extension: str) -> list[str]:
        config = self.LANGUAGE_REGISTRY.get(extension)
        if not config:
            return [source_code]

        parser = Parser(config["language"])
        tree = parser.parse(bytes(source_code, "utf8"))
        root_node = tree.root_node
        chunks = []
        
        def traverse(node):
            if node.type in config["target_nodes"]:
                chunk = source_code[node.start_byte:node.end_byte]
                chunks.append(chunk)
                return
        
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return chunks if chunks else [source_code]

    def generate_deterministic_id(self, repo_name: str, file_path: str, content: str) -> str:
        unique_string = f"{repo_name}::{file_path}::{content}"
        return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

    def generate_file_summary(self, file_path: str, source_code: str) -> str:
        prompt = f"""
        Analyze the codebase file located at `{file_path}`.
        Provide a highly concise architectural summary (2-3 sentences max) detailing its primary responsibility, structural classes/exports, and system dependencies.

        Source Code:
        {source_code[:4000]}
        """
        response = self.summary_model.invoke(prompt)
       
        content = response.content
                

        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                elif isinstance(part, str):
                    text_parts.append(part)
            return "".join(text_parts).strip()
                    
        # Fallback to standard string cast if it's already a single string
        return str(content).strip()

    def process_repository(self, owner: str, repo: str):
        """
        processes the full ingestion lifecycle.
        yields logging status strings designed for seamless streaming in frontends like streamlit.
        """
        repo_name = f"{owner}/{repo}"
        yield f"Connecting to GitHub and streaming tarball for {repo_name}..."

        try:
            files = self.fetch_repo_tarball(owner, repo)
        except Exception as e:
            yield f"Error fetching repository: {str(e)}"
            return

        code_vectors = []
        summary_vectors = []

        yield f"Parsing AST structural blocks for {len(files)} targeted files..."
        for file in files:
            file_path = file["path"]
            ext = file["extension"]
            source_code = file["content"]

            summary_text = self.generate_file_summary(file_path, source_code)
            summary_id = self.generate_deterministic_id(repo_name, file_path, "SUMMARY")
            summary_embed = self.embed_model.embed_query(summary_text)

            summary_vectors.append({
                "id": summary_id,
                "values": summary_embed,
                "metadata": {
                    "repo": repo_name,
                    "path": file_path,
                    "extension": ext,
                    "type": "file_summary",
                    "text": summary_text
                }
            })

            code_chunks = self.chunk_code_ast(source_code, ext)
            for chunk in code_chunks:
                contextual_string = f"Repo: {repo_name}\nFile: {file_path}\nCode:\n{chunk}"
                chunk_id = self.generate_deterministic_id(repo_name, file_path, chunk)
                chunk_embed = self.embed_model.embed_query(contextual_string)

                code_vectors.append({
                    "id": chunk_id,
                    "values": chunk_embed,
                    "metadata": {
                        "repo": repo_name,
                        "path": file_path,
                        "extension": ext,
                        "type": "code_chunk",
                        "text": chunk
                    }
                })

        yield f"Uploading {len(code_vectors)} code nodes and {len(summary_vectors)} file summaries to Pinecone..."

        batch_size = 100
        for i in range(0, len(code_vectors), batch_size):
            self.index.upsert(vectors=code_vectors[i:i+batch_size], namespace="code-chunks")

        for i in range(0, len(summary_vectors), batch_size):
            self.index.upsert(vectors=summary_vectors[i:i+batch_size], namespace="repo-summaries")

        yield f"Ingestion complete for {repo_name}. Index updated."
