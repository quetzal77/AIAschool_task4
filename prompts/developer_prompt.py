# System prompt that sets the behavior of the chatbot
from langchain_core.prompts import PromptTemplate

SYSTEM_PROMPT = """
    You are a helpful assistant.
    """

# # Define the input variables for the prompt
# SYSTEM_PROMPT = PromptTemplate(
#     input_variables=["tool_name", "user_query", "agent_scratchpad"],
#     template=prompt_string
# )

# SYSTEM_PROMPT = [
#     ("system", "You are a helpful assistant"),
#     ("placeholder", "{chat_history}"),
#     ("human", "{input}"),
#     ("placeholder", "{agent_scratchpad}"),
#     ]
