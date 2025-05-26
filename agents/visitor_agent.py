from agents.voice_agent import ConversationalAgent

class VisitorAgent(ConversationalAgent):
    def __init__(self):
        super().__init__(
            agent_name="visitor_agent",
            agent_tools=[{
                "type": "function",
                "function": {
                    "name": "manage_visitor",
                    "description": "Manage visitor check-ins, badges, and notifications.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "visitor_name": {"type": "string"},
                            "purpose": {"type": "string"}
                        }
                    }
                }
            }],
            agent_system_prompt="You are a visitor management agent.Always respnd within 50 words. Manage visitor check-ins and redirect to booking, reception, or feedback as needed.",
            temperature=0.7,
            agent_tool_prompt=""
        ) 