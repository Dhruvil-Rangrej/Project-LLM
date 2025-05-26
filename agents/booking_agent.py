from agents.voice_agent import ConversationalAgent

class BookingAgent(ConversationalAgent):
    def __init__(self):
        super().__init__(
            agent_name="booking_agent",
            agent_tools=[{
                "type": "function",
                "function": {
                    "name": "book_appointment",
                    "description": "Book an appointment for the user.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "time": {"type": "string"},
                            "person": {"type": "string"}
                        }
                    }
                }
            }],
            agent_system_prompt="You are a booking agent. Always respnd within 50 words. Help users book appointments and collect necessary details. Redirect to scheduler, FAQ, feedback, or reception as needed.",
            temperature=0.7,
            agent_tool_prompt=""
        ) 