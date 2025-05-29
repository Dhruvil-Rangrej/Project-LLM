import json
from typing import Dict, List
from agent_graph import AgentGraph
from agents.voice_agent import ConversationalAgent

class JSONGraphBuilder:
    @staticmethod
    def create_agent_from_json(json_data: Dict) -> ConversationalAgent:
        """Create a ConversationalAgent from a JSON object."""
        return ConversationalAgent(
            agent_name=json_data.get("agent_name", "custom_agent"),
            agent_tools=json_data.get("agent_tools", []),
            agent_system_prompt=json_data.get("agent_system_prompt", ""),
            temperature=json_data.get("temperature", 0.3),
            agent_tool_prompt=json_data.get("agent_tool_prompt", "")
        )

    @staticmethod
    def build_graph_from_json_file(json_file: str) -> AgentGraph:
        """
        Build an agent graph from a single JSON file containing all agent configurations.
        
        The JSON file should have the following structure:
        {
            "agents": [
                {
                    "agent_name": "string",
                    "agent_tools": ["tool1", "tool2"],
                    "agent_system_prompt": "string",
                    "temperature": float,
                    "agent_tool_prompt": "string",
                    "is_root": boolean,
                    "parent_agent": "string",
                    "transition_rules": {
                        "intent1": "target_agent1",
                        "intent2": "target_agent2"
                    }
                },
                ...
            ]
        }
        
        Args:
            json_file: Path to the JSON file containing all agent configurations
            
        Returns:
            AgentGraph: The constructed agent graph
        """
        with open(json_file, 'r') as f:
            config = json.load(f)
            
        agents = {}
        root_agent = None
        
        # First pass: Create all agents
        for agent_data in config["agents"]:
            agent = JSONGraphBuilder.create_agent_from_json(agent_data)
            agents[agent.get_name()] = {
                "agent": agent,
                "is_root": agent_data.get("is_root", False),
                "parent_agent": agent_data.get("parent_agent"),
                "transition_rules": agent_data.get("transition_rules", {})
            }
            
            if agent_data.get("is_root", False):
                if root_agent is not None:
                    raise ValueError("Multiple root agents found in JSON file")
                root_agent = agent
        
        if root_agent is None:
            raise ValueError("No root agent found in JSON file")
            
        # Create the graph with the root agent
        agent_graph = AgentGraph(
            root_agent,
            transition_rules=agents[root_agent.get_name()]["transition_rules"],
            intent_patterns={}
        )
        
        # Second pass: Add all agents to the graph
        for agent_name, agent_info in agents.items():
            if agent_name == root_agent.get_name():
                continue
                
            if not agent_info["parent_agent"]:
                raise ValueError(f"Agent {agent_name} has no parent agent specified")
                
            if agent_info["parent_agent"] not in agents:
                raise ValueError(f"Parent agent {agent_info['parent_agent']} not found for {agent_name}")
                
            agent_graph.add_agent(
                parent_agent_name=agent_info["parent_agent"],
                agent=agent_info["agent"],
                transition_rules=agent_info["transition_rules"]
            )
            
        return agent_graph

if __name__ == "__main__":
    # Example usage
    json_file = "agent_config.json"
    
    try:
        agent_graph = JSONGraphBuilder.build_graph_from_json_file(json_file)
        print(f"Successfully built agent graph with root agent: {agent_graph.get_current_agent().get_name()}")
    except Exception as e:
        print(f"Error building agent graph: {str(e)}") 