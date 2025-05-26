from agents.voice_agent import ConversationalAgent

class SchedulerAgent(ConversationalAgent):
    def __init__(self):
        super().__init__(
            agent_name="scheduler_agent",
            agent_tools=[{
                "type": "function",
                "function": {
                    "name": "manage_schedule",
                    "description": "Manage the office schedule, find available slots, reschedule, or cancel appointments.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"},
                            "date": {"type": "string"},
                            "time": {"type": "string"}
                        }
                    }
                }
            }],
            agent_system_prompt="You are a scheduler agent.Always respnd within 50 words. Manage the office calendar and appointments. Redirect to reception or feedback when done.",
            temperature=0.7,
            agent_tool_prompt=""
        ) 