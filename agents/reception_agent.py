from agents.voice_agent import ConversationalAgent

class ReceptionAgent(ConversationalAgent):
    def __init__(self):
        super().__init__(
            agent_name="reception_agent",
            agent_tools=[{
                "type": "function",
                "function": {
                    "name": "transfer_call",
                    "description": "Transfer a call to the right department.",
                    "parameters": {"type": "object", "properties": {}}
                }
            }],
            agent_system_prompt="You are an office reception agent.Always respnd within 50 words. Greet visitors, understand their needs, and redirect them to booking, scheduler, FAQ, emergency, HR, IT support, or visitor management as appropriate.",
            temperature=0.7,
            agent_tool_prompt=""
        ) 