import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient


SERVER = Path(__file__).parents[1] / "src" / "hachathon2_team3" / "mcp" / "server.py"


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "nfs_vendor_assessment_tools": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(SERVER)],
            }
        }
    )
    tools = await client.get_tools()
    print("discovered:", [tool.name for tool in tools])

    retrieve_document = next(tool for tool in tools if tool.name == "retrieve_document")
    try:
        result = await asyncio.wait_for(
            retrieve_document.ainvoke(
                {
                    "document_name": "gdpr.pdf",
                    "query": "security risks and GDPR compliance",
                    "max_chars": 500,
                }
            ),
            timeout=60,
        )
    except TimeoutError:
        print("retrieve_document timed out after 60 seconds")
        return
    print("found:", result)


if __name__ == "__main__":
    asyncio.run(main())
