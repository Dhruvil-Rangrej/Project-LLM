from typing import Dict, List, Optional
from agents.voice_agent import ConversationalAgent


class AgentNode:
    def __init__(self, agent: ConversationalAgent, transition_rules: Dict[str, str] = None):
        """
        Initialize an agent node in the graph.
        
        Args:
            agent: The agent implementation
            transition_rules: Mapping from intent/tool name to target agent name
        """
        self.agent = agent
        self.transition_rules = transition_rules or {}
        self.children: List['AgentNode'] = []

    def get_agent(self):
        return self.agent    
        
    def add_child(self, child_node: 'AgentNode') -> None:
        """Add a child node to this agent node"""
        self.children.append(child_node)
        
    def get_children(self) -> List['AgentNode']:
        """Get all child nodes"""
        return self.children.copy()
        
    def can_transition_to(self, target_agent: str) -> bool:
        """Check if transition to target agent is allowed"""
        return target_agent in self.transition_rules.values()
