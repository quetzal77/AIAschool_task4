from agentic_chatbot_src.agent_tools import create_agent_with_tools_and_prompt

def main():
    agent = create_agent_with_tools_and_prompt()
    print("Chatbot: Hello! How can I assist you today?"
          "\nHere are few commands you need to know before start:"
          "\n - type exit, quit or bye to complete conversation")

    # Example usage
    while True:
        query = input("\nYou: ")
        if query.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Goodbye! Have a great day!")
            break

        # Pass the query to the agent
        response = agent.invoke(query)
        # print(f"Bot: {response}")

if __name__ == "__main__":
    main()