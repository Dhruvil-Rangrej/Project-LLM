import os
import requests
import json
import time
from dynamic_graph_generator import DynamicGraphStructureGenerator

class ConversationalAgent:
    def __init__(self, agent_name, agent_tools=None, agent_system_prompt="", temperature=0.7, agent_tool_prompt=""):
        self._agent_name = agent_name
        self._agent_tools = agent_tools or []
        
        # Generate dynamic graph structure from config
        generator = DynamicGraphStructureGenerator("agent_config.json")
        graph_structure = generator.generate_graph_structure_prompt()
        
        self._agent_system_prompt = agent_system_prompt + graph_structure
        self._temperature = temperature
        self._agent_tool_prompt = agent_tool_prompt
        self._ngrok_url = os.environ.get("NGROK_SERVER_URL", "https://919c-34-125-210-249.ngrok-free.app")
        self._model_name = "Qwen/Qwen3-1.7B"

    def get_name(self):
        return self._agent_name

    def get_temperature(self):
        return self._temperature

    def get_system_message(self):
        return self._agent_system_prompt

    def get_tools(self):
        return self._agent_tools

    def get_tools_with_impl(self):
        return {tool['function']['name']: None for tool in self._agent_tools}

    def send_request(self, user_message, custom_system_message=None):
        system_message = custom_system_message if custom_system_message else self._agent_system_prompt
        
        payload = {
            "model": self._model_name,
            "messages": [
                {"role": "system", "content": system_message},
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
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[Request-Response Time: {elapsed:.2f} seconds]")
            return f"[Error contacting backend: {e}]"

    def execute_with_streaming(self, messages):
        system_message = None
        user_message = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] == "user":
                user_message = msg["content"]
        
        response = self.send_request(user_message, system_message)
        yield response
