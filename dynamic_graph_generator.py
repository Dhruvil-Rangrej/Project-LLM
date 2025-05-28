#!/usr/bin/env python3
"""
Dynamic Graph Structure Generator - Creates graph structure prompts from agent_config.json
"""

import json
from typing import Dict, List, Set
from transition_manager import TRANSITION_PATH_SEPARATOR

class DynamicGraphStructureGenerator:
    def __init__(self, config_file: str):
        """Initialize with agent configuration file"""
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.agents = self.config.get('agents', [])
        
    def generate_graph_structure_prompt(self) -> str:
        """Generate a dynamic graph structure prompt based on the agent configuration"""
        
        # Extract agent information
        agent_names = [agent['agent_name'] for agent in self.agents]
        root_agent = next((agent['agent_name'] for agent in self.agents if agent.get('is_root', False)), None)
        
        # Build transition mapping
        transition_paths = self._build_transition_paths()
        
        # Generate the dynamic prompt
        graph_structure = f"""
GRAPH STRUCTURE:
- You are part of a network of specialized agents
- You can route requests through other agents if you don't have direct access
- Available agents (use exact names in transitions):"""

        # Add agent list dynamically
        for agent_name in sorted(agent_names):
            root_indicator = " (root)" if agent_name == root_agent else ""
            graph_structure += f"\n  * {agent_name}{root_indicator}"
        
        # Add common routing paths
        graph_structure += "\n- Common routing paths:"
        for path in sorted(transition_paths):
            graph_structure += f"\n  * {path}"
            
        # Add syntax instructions
        graph_structure += """
- Use exact syntax for transitions:
  * Single transition: TRANSITION_TO:agent_name
  * Multi-step: TRANSITION_TO:agent1{TRANSITION_PATH_SEPARATOR}agent2
- Example: TRANSITION_TO:it_agent or TRANSITION_TO:faq_agent{TRANSITION_PATH_SEPARATOR}reception_agent
"""
        
        return graph_structure
    
    def _build_transition_paths(self) -> Set[str]:
        """Build transition paths from agent configurations"""
        paths = set()
        
        # Direct transitions from each agent
        for agent in self.agents:
            agent_name = agent['agent_name']
            transition_rules = agent.get('transition_rules', {})
            for intent, target_agent in transition_rules.items():
                paths.add(f"{agent_name} {TRANSITION_PATH_SEPARATOR} {target_agent}")
        
        # Add hierarchical paths based on parent-child relationships
        parent_child_map = {}
        for agent in self.agents:
            parent = agent.get('parent_agent')
            if parent:
                if parent not in parent_child_map:
                    parent_child_map[parent] = []
                parent_child_map[parent].append(agent['agent_name'])
        
        # Generate paths from root to leaf agents
        root_agent = next((agent['agent_name'] for agent in self.agents if agent.get('is_root', False)), None)
        if root_agent:
            for child_agents in parent_child_map.values():
                for child in child_agents:
                    paths.add(f"{root_agent} {TRANSITION_PATH_SEPARATOR} Any agent")
                    break
        
        # Add feedback/return paths (all agents can go to feedback and back to reception)
        feedback_agents = [agent['agent_name'] for agent in self.agents if 'feedback' in agent['agent_name']]
        reception_agents = [agent['agent_name'] for agent in self.agents if 'reception' in agent['agent_name']]
        
        if feedback_agents and reception_agents:
            feedback_agent = feedback_agents[0]
            reception_agent = reception_agents[0]
            paths.add(f"All agents {TRANSITION_PATH_SEPARATOR} {feedback_agent} {TRANSITION_PATH_SEPARATOR} {reception_agent}")
        
        return paths
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities (tools) for each agent"""
        capabilities = {}
        for agent in self.agents:
            agent_name = agent['agent_name']
            tools = agent.get('agent_tools', [])
            tool_names = []
            for tool in tools:
                if 'function' in tool and 'name' in tool['function']:
                    tool_names.append(tool['function']['name'])
            capabilities[agent_name] = tool_names
        return capabilities
    
    def get_transition_rules_summary(self) -> Dict[str, Dict[str, str]]:
        """Get transition rules for each agent"""
        rules = {}
        for agent in self.agents:
            agent_name = agent['agent_name']
            rules[agent_name] = agent.get('transition_rules', {})
        return rules

def test_dynamic_generator():
    """Test the dynamic graph structure generator"""
    print("=== TESTING DYNAMIC GRAPH STRUCTURE GENERATOR ===\n")
    
    generator = DynamicGraphStructureGenerator("agent_config.json")
    
    print("1. DYNAMIC GRAPH STRUCTURE PROMPT:")
    dynamic_prompt = generator.generate_graph_structure_prompt()
    print(dynamic_prompt)
    print()
    
    print("2. AGENT CAPABILITIES:")
    capabilities = generator.get_agent_capabilities()
    for agent, tools in capabilities.items():
        print(f"  {agent}: {tools}")
    print()
    
    print("3. TRANSITION RULES SUMMARY:")
    rules = generator.get_transition_rules_summary()
    for agent, agent_rules in rules.items():
        if agent_rules:
            print(f"  {agent}: {agent_rules}")
    print()

if __name__ == "__main__":
    test_dynamic_generator()
