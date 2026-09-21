from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
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
)

# -----------------------------------------------
#create docs: list[Document] = []
docs = []

# -----------------------------------------------

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=40)

chunks = splitter.split_documents(docs)

print(f"Split into {len(chunks)} chunks:\n")
for i, chunk in enumerate(chunks):
    print(f"--- chunk {i} ({len(chunk.page_content)} chars) ---")
    print(chunk.page_content)
    print()

store.add_documents(chunks)