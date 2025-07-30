import openai

from config import AZURE_OPENAI_DEPLOYMENT_NAME
from prompts.developer_prompt import SYSTEM_PROMPT
from rag_src.rag_tool import RAGPipeline

# Initialize conversation history
conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]

def truncate_conversation(conversation, max_tokens=4200):
    """
    Truncate the conversation history to ensure it doesn't exceed the token limit.
    """
    total_tokens = 0
    truncated_history = []
    for message in reversed(conversation):  # Start from the most recent messages
        message_tokens = len(message['content'].split())  # Approximate token count
        if total_tokens + message_tokens > max_tokens:
            break
        truncated_history.insert(0, message)
        total_tokens += message_tokens
    return truncated_history

def chatbot_response(query, retrieved_context=None):
    """
    Generate a response from the chatbot using Azure OpenAI's GPT.
    """
    global conversation_history

    # Append the retrieved context to the conversation history if provided
    if retrieved_context:
        conversation_history.append({"role": "system", "content": f"Context: {retrieved_context}"})

    # Append the user's input to the conversation history
    conversation_history.append({"role": "user", "content": query})

    # Truncate conversation history to avoid exceeding token limits
    conversation_history = truncate_conversation(conversation_history)

    try:
        # Call Azure OpenAI's GPT model
        response = openai.ChatCompletion.create(
            engine=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=conversation_history,
            temperature=0.7,
            max_tokens=4200,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract the chatbot's reply
        bot_reply = response['choices'][0]['message']['content']

        # Append the chatbot's reply to the conversation history
        conversation_history.append({"role": "assistant", "content": bot_reply})

        return bot_reply
    except openai.error.OpenAIError as e:
        return f"An error occurred while generating a response: {str(e)}"

def chat():
    print("Chatbot: Hello! How can I assist you today?"
          "\nHere are few commands you need to know before start:"
          "\n - type exit, quit or bye to complete conversation")
    while True:
        # Get user input
        query = input("You: ")

        # Exit the chat loop if the user says "exit"
        if query.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Goodbye! Have a great day!")
            break

        # Instantiate RAG pipeline
        rag_pipeline = RAGPipeline()

        # Retrieve context
        retrieved_context = rag_pipeline(query)

        # Get the chatbot's response
        bot_reply = chatbot_response(query, retrieved_context)
        print(f"Chatbot: {bot_reply}")