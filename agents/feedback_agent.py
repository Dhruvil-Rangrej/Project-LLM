from agents.voice_agent import ConversationalAgent

class FeedbackAgent(ConversationalAgent):
    def __init__(self):
        super().__init__(
            agent_name="feedback_agent",
            agent_tools=[{
                "type": "function",
                "function": {
                    "name": "collect_feedback",
                    "description": "Collect user feedback after interactions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "feedback": {"type": "string"}
                        }
                    }
                }
            }],
            agent_system_prompt="You are a feedback agent.Always respnd within 50 words. Collect user feedback and redirect to reception.",
            temperature=0.7,
            agent_tool_prompt=""
        ) 