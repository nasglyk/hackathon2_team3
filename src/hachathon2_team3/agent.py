"""
Main deep agent


"""
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
import asyncio
from datetime import datetime
from pathlib import Path
import sys
from hachathon2_team3.subagents import get_subagents
from hachathon2_team3.prompts import deep_agent_prompt
from hachathon2_team3.model import VendorAssessmentRequest

load_dotenv()

checkpointer = MemorySaver()

SERVER_PATH = Path(__file__).parent / "mcp" / "server.py"
_APPROVE_EDIT_REJECT = {"allowed_decisions": ["approve", "edit", "reject"]}

load_dotenv()

print(Path(__file__))
print(SERVER_PATH)

llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))


def _trace(label, value):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] {label}")
    if value is not None:
        print(value)


def _trace_messages(messages):
    for message in messages or []:
        tool_calls = getattr(message, "tool_calls", None) or (
            message.get("tool_calls", []) if isinstance(message, dict) else []
        )
        if tool_calls:
            for call in tool_calls:
                name = call.get("name", "unknown") if isinstance(call, dict) else getattr(call, "name", "unknown")
                arguments = call.get("args", {}) if isinstance(call, dict) else getattr(call, "args", {})
                if name in {"task", "delegate_to_subagent"} or (
                    isinstance(arguments, dict) and "subagent_type" in arguments
                ):
                    subagent = arguments.get("subagent_type", arguments.get("name", "unknown"))
                    _trace("SUBAGENT DELEGATION", f"{subagent} via {name}: {arguments}")
                else:
                    _trace("MODEL TOOL CALL", f"{name}({arguments})")

        message_type = getattr(message, "type", type(message).__name__)
        if message_type == "tool":
            content = getattr(message, "content", message)
            _trace("TOOL RESULT", content)

async def main():
    client = MultiServerMCPClient(
        {
            "nfs_vendor_assessment_tools": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(SERVER_PATH)],
            }
        }
    )

    _trace("CONNECTING TO MCP", str(SERVER_PATH))
    tools = await client.get_tools()
    _trace("MCP TOOLS DISCOVERED", [t.name for t in tools])

    agent = create_deep_agent(
        llm,
        subagents= get_subagents(tools),
        tools = [t for t in tools if t.name in {"record_assessment"}],
        system_prompt=deep_agent_prompt,
        checkpointer=checkpointer,
        #interrupt_on= {"record_assessment": _APPROVE_EDIT_REJECT },
    )

    structured_request = VendorAssessmentRequest(
            vendor_name="Asteria AI Systems",
            platform_type="Enterprise Generative AI platform",
            user_count=2000,
            data_classification="confidential corporate documents"
        )

    # 2. Pass the JSON-serialized model to the Deep Agent
    request = {
        "messages": [
            {
                "role": "user",
                "content": structured_request.model_dump_json(indent=2),
            }
        ]
    }


    config = {"configurable": {"thread_id": "thread-60"}}
    final_state = {}

    _trace("STARTING AGENT WORKFLOW", request["messages"][0]["content"])
    try:
        async with asyncio.timeout(int(os.getenv("AGENT_TIMEOUT_SECONDS", "90"))):
            async for update in agent.astream(request, config=config, stream_mode="updates"):
                for node_name, node_update in update.items():
                    _trace("GRAPH STEP", node_name)
                    if isinstance(node_update, dict):
                        final_state.update(node_update)
                        _trace_messages(node_update.get("messages", []))
                    else:
                        _trace("STEP OUTPUT", node_update)
    except TimeoutError:
        _trace(
            "WORKFLOW TIMEOUT",
            "The delegated workflow did not finish. Check whether the MCP retrieve_document log appeared.",
        )
        return

    messages = final_state.get("messages", [])
    if messages:
        final_message = messages[-1]
        final_content = getattr(final_message, "content", final_message)
        _trace("FINAL RESPONSE", final_content)
    else:
        _trace("WORKFLOW COMPLETE", final_state)


asyncio.run(main())

