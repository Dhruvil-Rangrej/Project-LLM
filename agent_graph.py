from typing import Dict, Generator, List, Optional
from agents.voice_agent import ConversationalAgent
from agent_node import AgentNode
from transition_manager import TransitionManager, TRANSITION_PATH_SEPARATOR


class AgentGraph:
    def __init__(self, root_agent: ConversationalAgent, transition_rules: Dict[str, str] = None, intent_patterns: Dict[str, List[str]] = None):
        """
        Initialize the agent graph with a root agent.
        
        Args:
            root_agent: The root agent of the graph
            intent_patterns: Dictionary mapping intent names to regex patterns or keywords
        """
        self.root = AgentNode(root_agent, transition_rules)
        self.nodes: Dict[str, AgentNode] = {root_agent.get_name(): self.root}
        self.active_node = self.root
        self.agent_path: List[str] = [root_agent.get_name()]
        self.conversation_history: List[Dict] = []
        self.intent_patterns = intent_patterns or {}
        
        # Initialize transition manager
        self.transition_manager = TransitionManager()
        
        # Per-agent context (simplified)
        self.agent_contexts: Dict[str, Dict] = {
            root_agent.get_name(): {
                "conversation_summary": [],
                "user_preferences": {},
                "session_data": {}
            }
        }
        
    def add_agent(self, parent_agent_name: str, agent: ConversationalAgent, 
                  transition_rules: Dict[str, str] = None) -> None:
        """
        Add an agent to the graph under a parent agent.
        
        Args:
            parent_agent_name: Name of the parent agent
            agent: The agent to add
            transition_rules: Rules for transitioning from this agent to others
        """
        if parent_agent_name not in self.nodes:
            raise ValueError(f"Parent agent '{parent_agent_name}' not found in graph")
            
        agent_node = AgentNode(agent, transition_rules)
        self.nodes[agent.get_name()] = agent_node
        self.nodes[parent_agent_name].add_child(agent_node)
        
        # Initialize context for the new agent
        self.agent_contexts[agent.get_name()] = {
            "conversation_summary": [],
            "user_preferences": {},
            "session_data": {}
        }
        
    def transition_to(self, agent_name: str) -> bool:
        if agent_name not in self.nodes:
            return False
            
        self.active_node = self.nodes[agent_name]
        self.agent_path.append(agent_name)
        return True
        
    def process_message(self, user_message: str) -> Generator[str, None, None]:
        # Update current agent's context with new user message
        current_agent_name = self.active_node.agent.get_name()
        self.agent_contexts[current_agent_name]["conversation_summary"].append({
            "role": "user",
            "content": user_message,
            "agent": current_agent_name
        })
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        active_agent = self.active_node.agent
        
        # Add system message with parent context (not global)
        if len(self.conversation_history) == 1:
            system_message = active_agent.get_system_message()
            # Include relevant parent context in system message
            context_str = self._format_parent_context(current_agent_name)
            if context_str:
                system_message += f"\nParent Context: {context_str}"
            messages = [{"role": "system", "content": system_message}]
            messages.extend(self.conversation_history)
        else:
            messages = self.conversation_history.copy()
        
        response_chunks = []
        for chunk in active_agent.execute_with_streaming(messages):
            response_chunks.append(chunk)
            yield chunk
        
        full_response = "".join(response_chunks) if isinstance(response_chunks[0], str) else response_chunks[0]
        
        # Update current agent's context with agent response
        self.agent_contexts[current_agent_name]["conversation_summary"].append({
            "role": "assistant",
            "content": full_response,
            "agent": current_agent_name
        })
        
        self.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        # Check for transition intent with improved detection
        transition_target = self.transition_manager.detect_intent_and_transition(
            user_message, full_response, self.active_node, self.nodes)
        if transition_target:
            # Record the transition
            self.transition_manager.record_transition(
                current_agent_name, user_message, full_response, transition_target, self.agent_contexts)
            
            if self.transition_to(transition_target):
                # Pass the original query to the new agent for processing
                yield f"\n[Transferring to {transition_target} to handle your request...]\n"
                
                # Process the query with the new agent
                yield from self.transition_manager.process_transitioned_message(
                    user_message, transition_target, self.nodes, self.agent_contexts, 
                    self.conversation_history, self._format_parent_context)
                
    def get_current_agent(self) -> ConversationalAgent:
        """Get the currently active agent"""
        return self.active_node.agent
        
    def get_agent_path(self) -> List[str]:
        """Get the path of agents that led to the current agent"""
        return self.agent_path.copy()
        
    def get_transitions(self) -> List[Dict]:
        """Get all transitions that have occurred"""
        return self.transition_manager.get_transitions()
        
    def get_recent_transitions(self, count: int = 5) -> List[Dict]:
        """Get the most recent transitions"""
        return self.transition_manager.get_recent_transitions(count)
        

        
    def _format_parent_context(self, current_agent: str) -> str:
        """Format the parent agent's context into a readable string"""
        parent_agent = self._find_parent_agent(current_agent)
        if not parent_agent or parent_agent not in self.agent_contexts:
            return ""
            
        parent_context = self.agent_contexts[parent_agent]
        context_parts = []
        
        # Add recent conversation summary from parent
        if parent_context["conversation_summary"]:
            recent_messages = parent_context["conversation_summary"][-2:]  # Last 2 messages from parent
            context_parts.append("Parent conversation: " + " | ".join([
                f"{msg['role']}: {msg['content'][:30]}..." for msg in recent_messages
            ]))
            
        # Add user preferences from parent
        if parent_context["user_preferences"]:
            context_parts.append("User preferences: " + str(parent_context["user_preferences"]))
            
        # Add recent transitions from transition manager
        last_transition = self.transition_manager.get_last_transition()
        if last_transition:
            context_parts.append(f"Previous transition: {last_transition['from_agent']} {TRANSITION_PATH_SEPARATOR} {last_transition['to_agent']}")
            
        return " | ".join(context_parts)
        
    def _find_parent_agent(self, agent_name: str) -> Optional[str]:
        """Find the parent agent for a given agent"""
        if agent_name == self.root.agent.get_name():
            return None
            
        # Search through all nodes to find the parent
        for parent_name, parent_node in self.nodes.items():
            for child in parent_node.get_children():
                if child.agent.get_name() == agent_name:
                    return parent_name
        return None
        



