from agents.voice_agent import ConversationalAgent

class HRAgent(ConversationalAgent):
    def __init__(self):
        super().__init__(
            agent_name="hr_agent",
            agent_tools=[{
                "type": "function",
                "function": {
                    "name": "handle_hr_query",
                    "description": "Handle HR-related queries (leave, payroll, policies).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "employee_id": {"type": "string"}
                        }
                    }
                }
            }],
            agent_system_prompt="You are an HR agent.Always respnd within 50 words. Handle HR queries and redirect to FAQ, reception, or feedback as needed.",
            temperature=0.7,
            agent_tool_prompt=""
        ) 