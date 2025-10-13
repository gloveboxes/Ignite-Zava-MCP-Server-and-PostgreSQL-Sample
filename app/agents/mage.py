import logging

from agent_framework import (
    ChatAgent,
    MCPStreamableHTTPTool,
    MagenticBuilder,
)
from agent_framework.azure import AzureOpenAIChatClient, AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

# from .finance_tools import get_company_order_policy, get_supplier_contract, get_historical_sales_data, get_current_inventory_status

import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

"""
Sample: Magentic Orchestration (multi-agent)

What it does:
- Orchestrates multiple agents using `MagenticBuilder` with streaming callbacks.

- ResearcherAgent (ChatAgent backed by an OpenAI chat client) for
    finding information.
- CoderAgent (ChatAgent backed by OpenAI Assistants with the hosted
    code interpreter tool) for analysis and computation.

The workflow is configured with:
- A Standard Magentic manager (uses a chat client for planning and progress).
- Callbacks for final results, per-message agent responses, and streaming
    token updates.

When run, the script builds the workflow, submits a task about estimating the
energy efficiency and CO2 emissions of several ML models, streams intermediate
events, and prints the final answer. The workflow completes when idle.

Prerequisites:
- OpenAI credentials configured for `OpenAIChatClient` and `OpenAIResponsesClient`.
"""

chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential(), deployment_name="gpt-4o-mini")


researcher_agent = ChatAgent(
    name="ResearcherAgent",
    description="Specialist in research and information gathering",
    instructions=(
        "You are a Researcher. You find information without additional computation or quantitative analysis."
    ),
    chat_client=chat_client,
)

sales_mcp_tools = MCPStreamableHTTPTool(
    name="SalesMCP",
    url="http://localhost:8000/",
    headers=None,
    load_tools=True,
    load_prompts=False,
    request_timeout=30,
)

supplier_mcp_tools = MCPStreamableHTTPTool(
    name="SupplierMCP",
    url="http://localhost:8001/",
    headers=None,
    load_tools=True,
    load_prompts=False,
    request_timeout=30,
)

finance_mcp_tools = MCPStreamableHTTPTool(
    name="FinanceMCP",
    url="http://localhost:8002/",
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


workflow = (
    MagenticBuilder()
    .participants(researcher=researcher_agent, financier=finance_agent)
    # .on_event(on_event, mode=MagenticCallbackMode.STREAMING)
    .with_standard_manager(
        chat_client=chat_client,
        max_round_count=10,
        max_stall_count=3,
        max_reset_count=2,
    )
    .build()
)
