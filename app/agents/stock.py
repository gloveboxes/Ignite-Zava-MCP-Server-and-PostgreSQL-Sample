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
from pydantic import BaseModel

finance_mcp_tools = MCPStreamableHTTPTool(
    name="FinanceMCP",
    url="http://localhost:8002/mcp",
    headers=None,
    load_tools=True,
    load_prompts=False,
    request_timeout=30,
)


class StockItem(BaseModel):
    sku: str
    product_name: str
    category_name: str
    stock_level: int
    cost: float


class StockItemCollection(BaseModel):
    items: list[StockItem]


class StockExtractor(Executor):
    """Custom executor that extracts stock information from messages."""

    agent: ChatAgent

    def __init__(self, responses_client: AzureOpenAIChatClient, id: str = "Stock Analyzer"):
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
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[StockItemCollection]) -> None:
        """Extract department data"""
        response = await self.agent.run(message, response_format=StockItemCollection)
        # TODO: Change to yield_output if you want to pass to another node
        await ctx.send_message(response.value)


class Summarizer(Executor):
    """Custom executor that owns a summarization agent and completes the workflow.

    This class demonstrates:
    - Consuming a typed payload produced upstream.
    - Yielding the final text outcome to complete the workflow.
    """

    agent: ChatAgent

    def __init__(self, chat_client: AzureOpenAIChatClient, id: str = "Summarizer"):
        # Create a domain specific agent that summarizes content.
        self.agent = chat_client.create_agent(
            instructions=(
                "You are an excellent workflow summarizer. You summarize the workflow and its key points into actionable tasks for the user."
            ),
        )
        super().__init__(id=id)

    @handler
    async def handle(self, messages: StockItemCollection, ctx: WorkflowContext[list[ChatMessage], StockItemCollection]) -> None:
        """Review the full conversation transcript and complete with a final string.

        This node consumes all messages so far. It uses its agent to produce the final text,
        then signals completion by yielding the output.
        """
        response = await self.agent.run(messages.model_dump_json())
        await ctx.send_message(response.messages)
        await ctx.yield_output(messages)

chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential(), deployment_name="gpt-4o-mini")
responses_client = AzureOpenAIResponsesClient(credential=DefaultAzureCredential(), deployment_name="gpt-4o-mini")

# Instantiate the two agent backed executors.
writer = StockExtractor(chat_client)
summarizer = Summarizer(chat_client)

# Build the workflow using the fluent builder.
# Set the start node and connect an edge from writer to summarizer.
workflow = WorkflowBuilder().set_start_executor(writer).add_edge(writer, summarizer).build()
