from agents.voice_agent import ConversationalAgent

class ITAgent(ConversationalAgent):
    def __init__(self):
        super().__init__(
            agent_name="it_agent",
            agent_tools=[{
                "type": "function",
                "function": {
                    "name": "handle_it_issue",
                    "description": "Handle IT issues (password reset, device problems).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "issue": {"type": "string"},
                            "device": {"type": "string"}
                        }
                    }
                }
            }],
            agent_system_prompt="You are an IT support agent.Always respnd within 50 words. Handle IT issues and redirect to FAQ, reception, or feedback as needed.",
            temperature=0.7,
            agent_tool_prompt=""
        ) 