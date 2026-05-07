import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from core.cli_chat import CliChat

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║         HubSpot CRM Agent  ·  Powered by Azure OpenAI       ║
╠══════════════════════════════════════════════════════════════╣
║  MCP Connections:                                            ║
║    📄  Document Server    {doc_status}                       ║
║    🟠  HubSpot Server     {hs_status}                        ║
╠══════════════════════════════════════════════════════════════╣
║  8 Universal Tools:                                          ║
║    crm_object_action  · engagement_action  · automation_action ║
║    marketing_action   · conversation_action · analytics_action ║
║    cms_action         · settings_action                      ║
╠══════════════════════════════════════════════════════════════╣
║  Slash Commands:                                             ║
║    /find_contact <name or email>                             ║
║    /deal_report [stage]                                      ║
║    /create_contact_flow <email>                              ║
║    /contact_summary <contact_id>                             ║
║    /pipeline_overview                                        ║
║    /log_call_flow <name or email>                            ║
║    /ticket_triage [priority]                                 ║
╠══════════════════════════════════════════════════════════════╣
║  Reference docs: @filename  ·  Type 'exit' to quit          ║
╚══════════════════════════════════════════════════════════════╝
"""

STYLE = Style.from_dict({"prompt": "ansicyan bold", "": "ansiwhite"})


class CliApp:
    def __init__(self, chat: CliChat):
        self.chat = chat
        self.session = PromptSession(history=InMemoryHistory())

    async def initialize(self):
        doc_ok = False
        hs_ok  = False

        try:
            tools = await self.chat.doc_client.list_tools()
            doc_ok = len(tools) >= 0
        except Exception:
            doc_ok = False

        try:
            hs_client = self.chat.clients.get("hubspot_client")
            if hs_client:
                tools = await hs_client.list_tools()
                hs_ok = len(tools) > 0
        except Exception:
            hs_ok = False

        doc_status = "✅ connected" if doc_ok else "❌ failed   "
        hs_status  = "✅ connected" if hs_ok  else "❌ check HUBSPOT_TOKEN"
        print(BANNER.format(doc_status=doc_status, hs_status=hs_status))

        if not hs_ok:
            print("⚠️  HubSpot tools unavailable — set HUBSPOT_TOKEN in .env\n")

    async def run(self):
        while True:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.session.prompt("You ▶ ", style=STYLE)
                )
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye! 👋")
                break

            user_input = user_input.strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Goodbye! 👋")
                break

            try:
                print("\nAssistant ▶ ", end="", flush=True)
                response = await self.chat.run(user_input)
                print(response)
                print()
            except Exception as e:
                print(f"\n[Error] {e}\n")
