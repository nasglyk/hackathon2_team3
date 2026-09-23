from functools import lru_cache

from langchain_postgres import PGVector
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.tools.structured import StructuredTool
import os


@lru_cache(maxsize=1)
def get_vector_store() -> PGVector:
    """Create the shared NFS PGVector store lazily for MCP and agent callers."""
    load_dotenv()
    connection = os.getenv(
        "NFS_RAG_CONNECTION",
        "postgresql+psycopg://langchain:langchain@localhost:5447/vectorstore",
    )
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
        api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )
    return PGVector(
        embeddings=embeddings,
        connection=connection,
        collection_name=os.getenv("NFS_RAG_COLLECTION", "hackathon2_team3_docs"),
        use_jsonb=True,
        create_extension=False,
    )


def get_rag_tool() -> StructuredTool:
    store = get_vector_store()

    return create_retriever_tool(
        store.as_retriever(search_kwargs={"k": 10}),
        name="hackathon2_team3_docs",
        description="",
    )