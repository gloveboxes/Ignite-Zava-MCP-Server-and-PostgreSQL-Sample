# Copyright (c) Microsoft. All rights reserved.

from agent_framework import (
    ChatAgent,
    ChatMessage,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

from app.config import Config
from app.finance_postgres import FinancePostgreSQLProvider

from pydantic import BaseModel

class DepartmentRequest(BaseModel):
    department: str

class DepartmentExtractor(Executor):
    """Custom executor that extracts department information from messages."""

    agent: ChatAgent

    def __init__(self, chat_client: AzureOpenAIChatClient, id: str = "writer"):
        # Create a domain specific agent using your configured AzureOpenAIChatClient.
        self.agent = chat_client.create_agent(
            instructions=(
                "You are an excellent content writer. You create new content and edit contents based on the feedback."
            ),
        )
        # Associate the agent with this executor node. The base Executor stores it on self.agent.
        super().__init__(id=id)

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[DepartmentRequest]) -> None:
        """Extract department data"""
        response = await self.agent.run(message, response_format=DepartmentRequest)
        if response.value:
            await ctx.send_message(response.value)
        else:
            raise ValueError("Department not found")

# Initialize configuration
config = Config()

# Create database provider
finance_provider = FinancePostgreSQLProvider()


class PolicyExecutor(Executor):
    """Custom executor that finds policy violations in the workflow."""

    def __init__(self, finance_provider: FinancePostgreSQLProvider, id: str = "policy_executor"):
        self.finance_provider = finance_provider
        super().__init__(id=id)

    @handler
    async def handle(self, department: DepartmentRequest, ctx: WorkflowContext[list[ChatMessage], str]) -> None:
        """Identify and flag any policy violations in the workflow."""

        result = await self.finance_provider.get_company_order_policy(
            department=department.department
        )

        await ctx.send_message(result.messages)


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
    async def handle(self, messages: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage], str]) -> None:
        """Review the full conversation transcript and complete with a final string.

        This node consumes all messages so far. It uses its agent to produce the final text,
        then signals completion by yielding the output.
        """
        response = await self.agent.run(messages)
        await ctx.yield_output(response.text)


chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential(), deployment_name="gpt-4o-mini")

# Instantiate the two agent backed executors.
writer = DepartmentExtractor(chat_client)
policy = PolicyExecutor(finance_provider)
summarizer = Summarizer(chat_client)

# Build the workflow using the fluent builder.
# Set the start node and connect an edge from writer to summarizer.
workflow = WorkflowBuilder().set_start_executor(writer).add_edge(writer, policy).add_edge(policy, summarizer).build()
