import os
import requests
import json
import time

class ConversationalAgent:
    def __init__(self, agent_name, agent_tools=None, agent_system_prompt="", temperature=0.7, agent_tool_prompt=""):
        self._agent_name = agent_name
        self._agent_tools = agent_tools or []
        # Add word limit instruction to system prompt
        word_limit_instruction = "\nIMPORTANT: Your responses must be concise and limited to 50 words or less. Be direct and clear in your communication."
        
        # Add graph structure information
        graph_structure = """
GRAPH STRUCTURE:
- You are part of a network of specialized agents
- You can route requests through other agents if you don't have direct access
- Available agents (use exact names in transitions):
  * reception_agent (root)
  * booking_agent
  * scheduler_agent
  * faq_agent
  * emergency_agent
  * feedback_agent
  * hr_agent
  * it_agent
  * visitor_agent
- Common routing paths:
  * reception_agent -> Any agent
  * faq_agent -> hr_agent/it_agent -> reception_agent
  * hr_agent/it_agent -> faq_agent -> reception_agent
  * booking_agent -> scheduler_agent -> reception_agent
  * visitor_agent -> booking_agent -> reception_agent
  * emergency_agent -> reception_agent
  * All agents -> feedback_agent -> reception_agent
- Use exact syntax for transitions:
  * Single transition: TRANSITION_TO:agent_name
  * Multi-step: TRANSITION_TO:agent1->agent2
- Example: TRANSITION_TO:it_agent or TRANSITION_TO:faq_agent->reception_agent
"""
        self._agent_system_prompt = agent_system_prompt + word_limit_instruction + graph_structure
        self._temperature = temperature
        self._agent_tool_prompt = agent_tool_prompt
        self._ngrok_url = os.environ.get("NGROK_SERVER_URL", "https://c5b9-34-59-120-93.ngrok-free.app")
        self._model_name = "Qwen/Qwen2.5-7B-Instruct"  

    def get_name(self):
        """Gets the name of an agent"""
        return self._agent_name

    def get_temperature(self):
        """Gets the temperature of an agent"""
        return self._temperature

    def get_system_message(self):
        """Gets system message"""
        return self._agent_system_prompt

    def get_tools(self):
        """Gets available functions/tools to the agent"""
        return self._agent_tools

    def get_tools_with_impl(self) -> dict:
        """Gets tools with their reference to implementations"""
        
        return {tool['function']['name']: None for tool in self._agent_tools}

    def send_request(self, user_message):
        payload = {
            "model": self._model_name,
            "messages": [
                {"role": "system", "content": self._agent_system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
        url = self._ngrok_url.rstrip('/') + "/v1/chat/completions"
        start_time = time.time()
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            elapsed = time.time() - start_time
            print(f"[Request-Response Time: {elapsed:.2f} seconds]")
            # Extract the assistant's reply
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[Request-Response Time: {elapsed:.2f} seconds]")
            return f"[Error contacting backend: {e}]"

    def execute_with_streaming(self, messages):
        # Use the last user message for the request
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break
        response = self.send_request(user_message)
        yield response