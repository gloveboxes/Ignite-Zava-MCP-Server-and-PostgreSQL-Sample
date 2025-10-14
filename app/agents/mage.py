import logging

from agent_framework import (
    ChatAgent,
    MCPStreamableHTTPTool,
    MagenticBuilder,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

from agent_framework import (
    MagenticCallbackEvent,
    MagenticFinalResultEvent,
    MagenticOrchestratorMessageEvent,
    MagenticCallbackMode,
)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential(), deployment_name="gpt-4o-mini")


sales_mcp_tools = MCPStreamableHTTPTool(
    name="SalesMCP",
    url="http://localhost:8000/mcp",
    headers=None,
    load_tools=True,
    load_prompts=False,
    request_timeout=30,
)

sales_agent = ChatAgent(
    name="SalesAgent",
    description="A helpful assistant that integrates with the backend sales data.",
    instructions="You solve questions using sales data and the tools provided.",
    chat_client=chat_client,
    tools=sales_mcp_tools,
)


supplier_mcp_tools = MCPStreamableHTTPTool(
    name="SupplierMCP",
    url="http://localhost:8001/mcp",
    headers=None,
    load_tools=True,
    load_prompts=False,
    request_timeout=30,
)

supplier_agent = ChatAgent(
    name="SupplierAgent",
    description="A helpful assistant that integrates with the backend supplier data.",
    instructions="You solve questions using supplier data and the tools provided.",
    chat_client=chat_client,
    tools=supplier_mcp_tools,
)


finance_mcp_tools = MCPStreamableHTTPTool(
    name="FinanceMCP",
    url="http://localhost:8002/mcp",
    headers=None,
    load_tools=True,
    load_prompts=False,
    request_timeout=30,
)

finance_agent = ChatAgent(
    name="FinanceAgent",
    description="A helpful assistant that integrates with the backend finance data.",
    instructions="You solve questions using financial data and the tools provided.",
    chat_client=chat_client,
    tools=finance_mcp_tools,
)


async def on_event(event: MagenticCallbackEvent) -> None:
        """
        The `on_event` callback processes events emitted by the workflow.
        Events include: orchestrator messages, agent delta updates, agent messages, and final result events.
        """
        if isinstance(event, MagenticOrchestratorMessageEvent):
            print(f"\n[ORCH:{event.kind}]\n\n{getattr(event.message, 'text', '')}\n{'-' * 26}")
        elif isinstance(event, MagenticFinalResultEvent):
            print("\n" + "=" * 50)
            print("FINAL RESULT:")
            print("=" * 50)
            if event.message is not None:
                print(event.message.text)
            print("=" * 50)

workflow = (
    MagenticBuilder()
    .participants(sales=sales_agent, supplier=supplier_agent, financier=finance_agent)
    .on_event(on_event, mode=MagenticCallbackMode.STREAMING)
    .with_standard_manager(
        chat_client=chat_client,
        max_round_count=10,
        max_stall_count=3,
        max_reset_count=2,
        final_answer_prompt="Sing this in soprano"
    )
    .build()
)
