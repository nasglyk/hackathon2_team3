from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from pathlib import Path
import re

load_dotenv()

CONNECTION = "postgresql+psycopg://langchain:langchain@localhost:5447/vectorstore"

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

store = PGVector(
    embeddings=embeddings,
    connection=CONNECTION,
    collection_name="hackathon2_team3_docs",
    pre_delete_collection=True,  # This empties the collection on initialization
)

def read_pdf(file_path: Path) -> list[Document]:
    """Read the content of a PDF file and return it as a Document object."""
    knowledge_root = Path(__file__).parent / "knowledge"
    return [
        Document(
            page_content=read_pdf_content(file_path),
            metadata={
                "source": str(file_path),
                "source_name": file_path.name,
                "relative_source": str(file_path.relative_to(knowledge_root)),
            },
        )
    ]



def read_pdf_content(file_path: Path) -> str:
    """Read the content of a PDF file and normalize broken whitespace."""
    from PyPDF2 import PdfReader

    reader = PdfReader(str(file_path))
    raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    
    # Replace any sequence of whitespace characters (spaces, tabs, newlines) with a single space
    cleaned_text = re.sub(r'\s+', ' ', raw_text)
    
    # Optional: Restore paragraph breaks if you want cleaner visual chunks
    # (assuming the original PDF used double newlines for paragraphs)
    # cleaned_text = cleaned_text.replace(" . ", ".\n\n") 
    
    return cleaned_text.strip()


knowledge_root = Path(__file__).parent / "knowledge"
pdf_files = sorted(knowledge_root.rglob("*.pdf"))
docs = [document for pdf_file in pdf_files for document in read_pdf(pdf_file)]

print(f"Found {len(pdf_files)} PDF files under {knowledge_root}")

# -----------------------------------------------

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=40)

chunks = splitter.split_documents(docs)

print(f"Split into {len(chunks)} chunks:\n")
for i, chunk in enumerate(chunks):
    print(f"--- chunk {i} ({len(chunk.page_content)} chars) ---")
    print(chunk.page_content)
    print()

store.add_documents(chunks)