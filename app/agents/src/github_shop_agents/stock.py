# Copyright (c) Microsoft. All rights reserved.
import os

from agent_framework import (
    ChatAgent,
    ChatMessage,
    Executor,
    MCPStreamableHTTPTool,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
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

GPT_DEPLOYMENT = os.getenv("GPT_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
if os.environ.get("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME_GPT5") is None:
    chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential(), deployment_name=GPT_DEPLOYMENT)
else:
    chat_client = AzureOpenAIChatClient(api_key=os.environ.get("AZURE_OPENAI_API_KEY_GPT5"),
                                        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT_GPT5"),
                                        deployment_name=os.environ.get("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME_GPT5"),
                                        api_version=os.environ.get("AZURE_OPENAI_ENDPOINT_VERSION_GPT5", "2024-02-15-preview"))

class StockItem(BaseModel):
    sku: str
    product_name: str
    category_name: str
    stock_level: int
    cost: float


class StockItemCollection(BaseModel):
    items: list[StockItem]


class StockExtractorResult(BaseModel):
    context: str
    messages: list[str]
    collection: StockItemCollection


class RestockResult(BaseModel):
    items: list[StockItem]
    summary: str


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
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[StockExtractorResult]) -> None:
        """Extract department data"""
        response = await self.agent.run(message, response_format=StockItemCollection)

        result = StockExtractorResult(context=message.text, messages=[message.text for message in response.messages if message.text.strip()], collection=response.value)
        await ctx.send_message(result)


class ContextExecutor(Executor):
    """Custom executor that provides context about the user request."""

    agent: ChatAgent

    def __init__(self, responses_client: AzureOpenAIChatClient, id: str = "Context Analyzer"):
        # Create a domain specific agent using your configured AzureOpenAIChatClient.
        self.agent = responses_client.create_agent(
            instructions=(
                "You look at the context to prioritize restocking items."
            ),
        )
        # Associate the agent with this executor node. The base Executor stores it on self.agent.
        super().__init__(id=id)

    @handler
    async def handle(self, stock_result: StockExtractorResult, ctx: WorkflowContext[StockExtractorResult]) -> None:
        m = "You look at the context to prioritize restocking items. Original Request:\n" + stock_result.context
        m += "\n\nCurrent Items:\n" + stock_result.collection.model_dump_json(indent=2)
        response = await self.agent.run(m, response_format=StockItemCollection)
        context_result = StockExtractorResult(context=stock_result.context, messages=[message.text for message in response.messages if message.text.strip()], collection=response.value)
        await ctx.send_message(context_result)


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
                "You are an excellent workflow summarizer. You summarize the restocking task and what the user asked for into an overview. "
                "Do not list the items one by one as the user will get these in the final output."
                "Look at the specific user instructions and context to provide a tailored summary."
            ),
        )
        super().__init__(id=id)

    @handler
    async def handle(self, stock_result: StockExtractorResult, ctx: WorkflowContext[list[ChatMessage], RestockResult]) -> None:
        """Review the full conversation transcript and complete with a final string.

        This node consumes all messages so far. It uses its agent to produce the final text,
        then signals completion by yielding the output.
        """
        response = await self.agent.run(stock_result.messages)
        await ctx.send_message(response.messages)
        await ctx.yield_output(RestockResult(items=stock_result.collection.items, summary=response.text))


# Instantiate the two agent backed executors.
stock = StockExtractor(chat_client)
context = ContextExecutor(chat_client)
summarizer = Summarizer(chat_client)

# Build the workflow using the fluent builder.
# Set the start node and connect an edge from stock to summarizer.
workflow = WorkflowBuilder().set_start_executor(stock).add_edge(stock, context).add_edge(context, summarizer).build()
