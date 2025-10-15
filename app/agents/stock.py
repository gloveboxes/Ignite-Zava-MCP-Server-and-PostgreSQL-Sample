# Copyright (c) Microsoft. All rights reserved.

from agent_framework import (
    ChatAgent,
    ChatMessage,
    Executor,
    MCPStreamableHTTPTool,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient, AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

from app.config import Config
from app.finance_postgres import FinancePostgreSQLProvider


finance_mcp_tools = MCPStreamableHTTPTool(
    name="FinanceMCP",
    url="http://localhost:8002/mcp",
    headers=None,
    load_tools=True,
    load_prompts=False,
    request_timeout=30,
)

class StockExtractor(Executor):
    """Custom executor that extracts stock information from messages."""

    agent: ChatAgent

    def __init__(self, responses_client: AzureOpenAIChatClient, id: str = "writer"):
        # Create a domain specific agent using your configured AzureOpenAIChatClient.
        self.agent = responses_client.create_agent(
            instructions=(
                "You determine strategies for restocking items. Consult the tools for stock levels and prioritise which items to restock first."
            ),
            tools=finance_mcp_tools,
        )
        # Associate the agent with this executor node. The base Executor stores it on self.agent.
        super().__init__(id=id)

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[str]) -> None:
        """Extract department data"""
        response = await self.agent.run(message)
        # TODO: Change to yield_output if you want to pass to another node
        await ctx.send_message(response.text)


# Initialize configuration
config = Config()

# Create database provider
finance_provider = FinancePostgreSQLProvider()


class FinanceExecutor(Executor):
    """Custom executor that finds policy violations in the workflow."""

    def __init__(self, finance_provider: FinancePostgreSQLProvider, id: str = "finance_executor"):
        self.finance_provider = finance_provider
        super().__init__(id=id)

    @handler
    async def handle(self, stock: str, ctx: WorkflowContext[str]) -> None:
        """Identify and flag any policy violations in the workflow."""

        await self.finance_provider.create_pool()
        result = await self.finance_provider.get_company_order_policy(
            department=stock
        )

        await ctx.send_message(result)


class Summarizer(Executor):
    """Custom executor that owns a summarization agent and completes the workflow.

    This class demonstrates:
    - Consuming a typed payload produced upstream.
    - Yielding the final text outcome to complete the workflow.
    """

    agent: ChatAgent

    def __init__(self, chat_client: AzureOpenAIChatClient, id: str = "summarizer"):
        # Create a domain specific agent that summarizes content.
        self.agent = chat_client.create_agent(
            instructions=(
                "You are an excellent workflow summarizer. You summarize the workflow and its key points into actionable tasks for the user."
            ),
        )
        super().__init__(id=id)

    @handler
    async def handle(self, messages: str, ctx: WorkflowContext[list[ChatMessage], str]) -> None:
        """Review the full conversation transcript and complete with a final string.

        This node consumes all messages so far. It uses its agent to produce the final text,
        then signals completion by yielding the output.
        """
        response = await self.agent.run(messages)
        await ctx.yield_output(response.text)

chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential(), deployment_name="gpt-4o-mini")
responses_client = AzureOpenAIResponsesClient(credential=DefaultAzureCredential(), deployment_name="gpt-4o-mini")

# Instantiate the two agent backed executors.
writer = StockExtractor(chat_client)
# policy = PolicyExecutor(finance_provider)
summarizer = Summarizer(chat_client)

# Build the workflow using the fluent builder.
# Set the start node and connect an edge from writer to summarizer.
workflow = WorkflowBuilder().set_start_executor(writer).add_edge(writer, summarizer).build()
