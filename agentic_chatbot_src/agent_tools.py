from langchain.agents import Tool, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

from agentic_chatbot_src.content_scrapper import scrape_web_pages
from agentic_chatbot_src.html_parser import extract_content_from_html
from agentic_chatbot_src.rag_tool_faiss import combine_text_to_chunks, create_vector_store, generate_embeddings, \
    query_vector_store
from config import llm_azure
from prompts.developer_prompt import SYSTEM_PROMPT

# Wrap tools as LangChain tool
tools = [
    Tool(
        name="LoadHTML",
        func=extract_content_from_html(),
        description="Use this tool to load HTML content from a local file.",
    ),
    Tool(
        name="ScratText",
        func=lambda html: combine_text_to_chunks(html),
        description="Use this tool to scrap text from html. Input should be the loaded documents.",
    ),
    Tool(
        name="GenerateEmbeddings",
        func=lambda all_chunks: generate_embeddings(all_chunks),
        description="Use this tool to generate embeddings.",
    ),
    Tool(
        name="CreateVectorStore",
        func=lambda embeddings: create_vector_store(embeddings),
        description="Use this tool to create a FAISS vector store from text chunks. Input should be the split documents.",
    ),
    Tool(
        name="QueryVectorStore",
        func=lambda all_chunks, index, input_dict: query_vector_store(all_chunks, index, input_dict["query"]),
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
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        verbose=True,  # Set to True to see detailed logs
    )
    return agent
