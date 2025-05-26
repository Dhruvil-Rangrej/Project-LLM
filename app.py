from multi_graph_agent import ConversationAgentGraph

def chat():
    print("🤖 Multi-Agent Office Assistant is ready! Type 'exit' to quit.")
    agent_graph = ConversationAgentGraph.create_agent_graph()
    print(f"[Active Agent: {agent_graph.get_current_agent().get_name()}]")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        try:
            # Process the message through the agent graph (generator)
            response_stream = agent_graph.process_message(user_input)
            full_response = ""
            for chunk in response_stream:
                print(chunk, end="", flush=True)
                full_response += chunk
            print()  # Newline after streaming

            # Show the current active agent after possible transition
            print(f"[Active Agent: {agent_graph.get_current_agent().get_name()}]")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    chat()
