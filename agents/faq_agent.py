from agents.voice_agent import ConversationalAgent

class FAQAgent(ConversationalAgent):
    def __init__(self):
        super().__init__(
            agent_name="faq_agent",
            agent_tools=[{
                "type": "function",
                "function": {
                    "name": "answer_faq",
                    "description": "Answer frequently asked questions about the office.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"}
                        }
                    }
                }
            }],
            agent_system_prompt="You are an FAQ agent.Always respnd within 50 words. Answer common questions about the office. Redirect to reception, feedback, HR, or IT support if you cannot answer.",
            temperature=0.7,
            agent_tool_prompt=""
        ) 