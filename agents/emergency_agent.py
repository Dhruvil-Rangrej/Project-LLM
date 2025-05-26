from agents.voice_agent import ConversationalAgent

class EmergencyAgent(ConversationalAgent):
    def __init__(self):
        super().__init__(
            agent_name="emergency_agent",
            agent_tools=[{
                "type": "function",
                "function": {
                    "name": "handle_emergency",
                    "description": "Handle urgent or emergency situations (medical, fire, security).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "location": {"type": "string"}
                        }
                    }
                }
            }],
            agent_system_prompt="You are an emergency agent.Always respnd within 50 words. Handle urgent situations and redirect to reception after handling or escalation.",
            temperature=0.7,
            agent_tool_prompt=""
        ) 