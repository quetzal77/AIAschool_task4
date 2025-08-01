import os

from langchain import hub
from langchain.agents import Tool, initialize_agent, AgentType, create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

from agentic_chatbot_src.rag_tool_faiss import query_vector_store
from config import llm_azure
from prompts.developer_prompt import SYSTEM_PROMPT

# Wrap tools as LangChain tool
tools = [
    Tool(
        name="QueryVectorStore",
        func= query_vector_store,
        description="Use this tool to query the vector store for relevant information. Input should be a dictionary with keys 'vector_store' and 'query'.",
    ),
]


# Add System Prompt to Conversation History
def initialize_memory_with_system_prompt():
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # Add the system prompt to memory as the first message
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    memory.chat_memory.add_message(system_message)
    return memory

# Initialize the LangChain Agent
def create_agent_with_tools_and_prompt():
    # Initialize memory with the system prompt
    memory = initialize_memory_with_system_prompt()

    # Initialize the agent
    agent = initialize_agent(
        tools=tools,
        llm=llm_azure,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,  # Set to True to see detailed logs
    )

    return agent
