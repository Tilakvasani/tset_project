import asyncio, sys, os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.claude import Claude
from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# ── Azure OpenAI ──────────────────────────────────────────────────────────────
azure_deployment  = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
azure_api_key     = os.getenv("AZURE_OPENAI_API_KEY", "")
azure_endpoint    = os.getenv("AZURE_OPENAI_ENDPOINT", "")
azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

assert azure_deployment, "AZURE_OPENAI_DEPLOYMENT_NAME missing in .env"
assert azure_api_key,    "AZURE_OPENAI_API_KEY missing in .env"
assert azure_endpoint,   "AZURE_OPENAI_ENDPOINT missing in .env"

if not os.getenv("HUBSPOT_TOKEN"):
    print("⚠️  HUBSPOT_TOKEN not set — HubSpot tools will be unavailable\n")


async def main():
    use_uv = os.getenv("USE_UV", "0") == "1"
    cmd    = "uv"    if use_uv else "python"
    prefix = ["run"] if use_uv else []

    claude_service = Claude(model=azure_deployment)

    async with AsyncExitStack() as stack:

        # ── Document MCP server ───────────────────────────────────────────────
        doc_client = await stack.enter_async_context(
            MCPClient(command=cmd, args=prefix + ["mcp_server.py"])
        )
        clients: dict[str, MCPClient] = {"doc_client": doc_client}

        # ── HubSpot MCP server ────────────────────────────────────────────────
        try:
            hs_client = await stack.enter_async_context(
                MCPClient(command=cmd, args=prefix + ["hubspot_mcp_server.py"])
            )
            clients["hubspot_client"] = hs_client
        except Exception as e:
            print(f"⚠️  HubSpot MCP server failed to start: {e}\n")

        # ── Extra servers from CLI args ───────────────────────────────────────
        for i, script in enumerate(sys.argv[1:]):
            try:
                extra = await stack.enter_async_context(
                    MCPClient(command=cmd, args=prefix + [script])
                )
                clients[f"extra_{i}"] = extra
            except Exception as e:
                print(f"⚠️  Could not start {script}: {e}")

        chat = CliChat(doc_client=doc_client, clients=clients, claude_service=claude_service)
        cli  = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
