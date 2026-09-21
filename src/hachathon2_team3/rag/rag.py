from langchain_postgres import PGVector
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.tools.structured import StructuredTool
import os


def get_rag_tool() -> StructuredTool:
    load_dotenv()

    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
        api_key=os.getenv("AZURE_EMBEDDING_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )

    store = PGVector(
        embeddings=embeddings,
        connection="postgresql+psycopg_async://langchain:langchain@localhost:5447/vectorstore", #TODO: change the url
        collection_name="hackathon2_team3_docs",
        use_jsonb=True,
        create_extension=False,
        async_mode=True, # maybe not needed if we don't use async methods.
    )

    return create_retriever_tool(
        store.as_retriever(search_kwargs={"k": 10}),
        name="hackathon2_team3_docs",
        description="",
    )