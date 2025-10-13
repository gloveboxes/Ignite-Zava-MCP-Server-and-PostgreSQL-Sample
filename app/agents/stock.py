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

class Writer(Executor):
    """Custom executor that owns a domain specific agent responsible for generating content.

    This class demonstrates:
    - Attaching a ChatAgent to an Executor so it participates as a node in a workflow.
    - Using a @handler method to accept a typed input and forward a typed output via ctx.send_message.
    """

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
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[list[ChatMessage], str]) -> None:
        """Generate content using the agent and forward the updated conversation.

        Contract for this handler:
        - message is the inbound user ChatMessage.
        - ctx is a WorkflowContext that expects a list[ChatMessage] to be sent downstream.

        Pattern shown here:
        1) Seed the conversation with the inbound message.
        2) Run the attached agent to produce assistant messages.
        3) Forward the cumulative messages to the next executor with ctx.send_message.
        """
        # Start the conversation with the incoming user message.
        messages: list[ChatMessage] = [message]
        # Run the agent and extend the conversation with the agent's messages.
        response = await self.agent.run(messages)
        messages.extend(response.messages)
        # Forward the accumulated messages to the next executor in the workflow.
        await ctx.send_message(messages)

class Reviewer(Executor):
    """Custom executor that owns a review agent and completes the workflow.

    This class demonstrates:
    - Consuming a typed payload produced upstream.
    - Yielding the final text outcome to complete the workflow.
    """

    agent: ChatAgent

    def __init__(self, chat_client: AzureOpenAIChatClient, id: str = "reviewer"):
        # Create a domain specific agent that evaluates and refines content.
        self.agent = chat_client.create_agent(
            instructions=(
                "You are an excellent content reviewer. You review the content and provide feedback to the writer."
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
writer = Writer(chat_client)
reviewer = Reviewer(chat_client)

# Build the workflow using the fluent builder.
# Set the start node and connect an edge from writer to reviewer.
workflow = WorkflowBuilder().set_start_executor(writer).add_edge(writer, reviewer).build()
