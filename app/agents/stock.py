# Copyright (c) Microsoft. All rights reserved.

from agent_framework import (
    ChatAgent,
    ChatMessage,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient, AzureOpenAIResponsesClient
from agent_framework.openai import OpenAIChatClient, OpenAIResponsesClient
from azure.identity import DefaultAzureCredential

from app.config import Config
from app.finance_postgres import FinancePostgreSQLProvider

from pydantic import BaseModel
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


class DepartmentRequest(BaseModel):
    department: str

class DepartmentExtractorResponses(Executor):
    """Custom executor that extracts department information from messages."""

    agent: ChatAgent

    def __init__(self, responses_client: AzureOpenAIResponsesClient, id: str = "writer"):
        # Create a domain specific agent using your configured AzureOpenAIChatClient.
        self.agent = responses_client.create_agent(
            instructions=(
                "You determine which department the user question is about."
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

class DepartmentExtractor(Executor):
    """Custom executor that extracts department information from messages."""

    agent: ChatAgent

    def __init__(self, responses_client: AzureOpenAIChatClient, id: str = "writer"):
        # Create a domain specific agent using your configured AzureOpenAIChatClient.
        self.agent = responses_client.create_agent(
            instructions=(
                "You determine which department the user question is about. Reply only with the department name. Nothing else."
            ),
        )
        # Associate the agent with this executor node. The base Executor stores it on self.agent.
        super().__init__(id=id)

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[DepartmentRequest]) -> None:
        """Extract department data"""
        response = await self.agent.run(message)
        department_request = DepartmentRequest(department=response.text)
        await ctx.send_message(department_request)


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
    async def handle(self, department: DepartmentRequest, ctx: WorkflowContext[str]) -> None:
        """Identify and flag any policy violations in the workflow."""

        await self.finance_provider.create_pool()
        result = await self.finance_provider.get_company_order_policy(
            department=department.department
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


if GITHUB_TOKEN:
    chat_client = OpenAIChatClient(base_url="https://models.github.ai/inference", model_id="openai/gpt-4.1-mini", api_key=GITHUB_TOKEN)
    responses_client = OpenAIResponsesClient(base_url="https://models.github.ai/inference", model_id="openai/gpt-4.1-mini", api_key=GITHUB_TOKEN)
else:
    chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential(), deployment_name="gpt-4o-mini")
    responses_client = AzureOpenAIResponsesClient(credential=DefaultAzureCredential(), deployment_name="gpt-4o-mini")

# Instantiate the two agent backed executors.
writer = DepartmentExtractor(chat_client)
policy = PolicyExecutor(finance_provider)
summarizer = Summarizer(chat_client)

# Build the workflow using the fluent builder.
# Set the start node and connect an edge from writer to summarizer.
workflow = WorkflowBuilder().set_start_executor(writer).add_edge(writer, policy).add_edge(policy, summarizer).build()
