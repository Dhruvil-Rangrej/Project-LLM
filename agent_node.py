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
        self.transition_history: List[Dict] = []

    def get_agent(self):
        return self.agent    
        
    def add_child(self, child_node: 'AgentNode') -> None:
        """Add a child node to this agent node"""
        self.children.append(child_node)
        
    def get_children(self) -> List['AgentNode']:
        """Get all child nodes"""
        return self.children.copy()
        
    def record_transition(self, from_agent: str, to_agent: str, context: Dict = None) -> None:
        """Record a transition between agents with context"""
        self.transition_history.append({
            "from": from_agent,
            "to": to_agent,
            "context": context or {},
            "timestamp": None  # You can add timestamp if needed
        })
        
    def get_transition_history(self) -> List[Dict]:
        """Get the history of transitions"""
        return self.transition_history.copy()
        
    def can_transition_to(self, target_agent: str) -> bool:
        """Check if transition to target agent is allowed"""
        return target_agent in self.transition_rules.values()
        
    def get_transition_confidence(self, user_message: str, agent_response: str) -> float:
        """Calculate confidence score for transition based on message content"""
        confidence = 0.0
        user_message_lower = user_message.lower()
        agent_response_lower = agent_response.lower()
        
        # Check for explicit transition markers
        if "TRANSITION_TO:" in agent_response:
            confidence += 0.8
        if "TRANSITION_CONFIRM:" in agent_response:
            confidence += 0.6
            
        # Check for intent keywords in both messages
        for intent in self.transition_rules.keys():
            if intent in user_message_lower:
                confidence += 0.3
            if intent in agent_response_lower:
                confidence += 0.2
                
        return min(confidence, 1.0)  # Cap at 1.0
