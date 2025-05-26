import json
from agents.voice_agent import ConversationalAgent

def agent_from_json(json_data):
    """
    Create a ConversationalAgent from a JSON object.
    JSON should have keys: agent_name, agent_tools, agent_system_prompt, temperature, agent_tool_prompt
    """
    return ConversationalAgent(
        agent_name=json_data.get("agent_name", "custom_agent"),
        agent_tools=json_data.get("agent_tools", []),
        agent_system_prompt=json_data.get("agent_system_prompt", ""),
        temperature=json_data.get("temperature", 0.7),
        agent_tool_prompt=json_data.get("agent_tool_prompt", "")
    )

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python from_json_agent.py <agent_json_file>")
        exit(1)
    json_file = sys.argv[1]
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    agent = agent_from_json(json_data)
    print(f"Agent created: {agent.get_name()}")
    print(f"System prompt: {agent.get_system_message()}")
    print(f"Tools: {agent.get_tools()}") 