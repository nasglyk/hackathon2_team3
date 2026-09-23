from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import re
from pathlib import Path

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
)

# -----------------------------------------------
#create docs: list[Document] = []
docs = []
#read pdf file and make it into a Document object
def read_pdf(file_path: Path) -> list[Document]:
    """Read the content of a PDF file and return it as a Document object."""
    return [Document(page_content=read_pdf_content(file_path), metadata={"source": str(file_path)})]

def read_pdf_content(file_path: Path) -> str:
    """Read the content of a PDF file and return it as a string."""
    from PyPDF2 import PdfReader

    reader = PdfReader(str(file_path))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

docs = read_pdf(Path(__file__).parent / "knowledge" / "gdpr.pdf")

# -----------------------------------------------

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=40)

chunks = splitter.split_documents(docs)

print(f"Split into {len(chunks)} chunks:\n")
for i, chunk in enumerate(chunks):
    print(f"--- chunk {i} ({len(chunk.page_content)} chars) ---")
    print(chunk.page_content)
    print()

store.add_documents(chunks)