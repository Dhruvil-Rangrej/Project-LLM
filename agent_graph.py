from typing import Dict, Generator, List, Optional
from agents.voice_agent import ConversationalAgent
from agent_node import AgentNode

# TODO : prompt a model or agent that answer the question if agent is able to handle
# it and if there is 'yes there is a emergency' then output "TRANSITION_TO:{emergency_agent}"
# that's how we can control the transition.
TRANSITION_TEXT = "TRANSITION_TO:"
TRANSITION_CONFIRMATION = "TRANSITION_CONFIRM:"
TRANSITION_CONTEXT = "TRANSITION_CONTEXT:"


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
        # Global context that persists across all agents
        self.global_context: Dict = {
            "conversation_summary": [],
            "user_preferences": {},
            "session_data": {},
            "transition_history": []
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
        
    def transition_to(self, agent_name: str) -> bool:
        if agent_name not in self.nodes:
            return False
            
        self.active_node = self.nodes[agent_name]
        self.agent_path.append(agent_name)
        return True
        
    def process_message(self, user_message: str) -> Generator[str, None, None]:
        # Update global context with new user message
        self.global_context["conversation_summary"].append({
            "role": "user",
            "content": user_message,
            "agent": self.active_node.agent.get_name()
        })
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        active_agent = self.active_node.agent
        
        # Add system message with global context
        if len(self.conversation_history) == 1:
            system_message = active_agent.get_system_message()
            # Include relevant global context in system message
            context_str = self._format_global_context()
            system_message += f"\nGlobal Context: {context_str}"
            messages = [{"role": "system", "content": system_message}]
            messages.extend(self.conversation_history)
        else:
            messages = self.conversation_history.copy()
        
        response_chunks = []
        for chunk in active_agent.execute_with_streaming(messages):
            response_chunks.append(chunk)
            yield chunk
        
        full_response = "".join(response_chunks) if isinstance(response_chunks[0], str) else response_chunks[0]
        
        # Update global context with agent response
        self.global_context["conversation_summary"].append({
            "role": "assistant",
            "content": full_response,
            "agent": self.active_node.agent.get_name()
        })
        
        self.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        # Check for transition intent with improved detection
        transition_target = self._detect_intent_and_transition(user_message, full_response)
        if transition_target:
            # Update global context before transition
            self._update_global_context(user_message, full_response, transition_target)
            
            if self.transition_to(transition_target):
                transition_message = f"\n[Transitioning to {transition_target}]\n"
                context_str = self._format_global_context()
                transition_message += f"[Global Context: {context_str}]\n"
                yield transition_message
                
    def get_current_agent(self) -> ConversationalAgent:
        """Get the currently active agent"""
        return self.active_node.agent
        
    def get_agent_path(self) -> List[str]:
        """Get the path of agents that led to the current agent"""
        return self.agent_path.copy()
        
    def _update_global_context(self, user_message: str, response: str, next_agent: str) -> None:
        """Update the global context with the latest interaction and transition"""
        # Update transition history
        self.global_context["transition_history"].append({
            "from_agent": self.active_node.agent.get_name(),
            "to_agent": next_agent,
            "user_message": user_message,
            "agent_response": response
        })
        
        # Extract and store any user preferences or session data
        # This is a simple implementation - you can make it more sophisticated
        if "preference" in user_message.lower():
            self.global_context["user_preferences"].update({
                "last_preference": user_message
            })
            
        # Update session data
        self.global_context["session_data"].update({
            "last_interaction": {
                "user_message": user_message,
                "agent_response": response,
                "timestamp": None  # You can add timestamp if needed
            }
        })
        
    def _format_global_context(self) -> str:
        """Format the global context into a readable string"""
        context_parts = []
        
        # Add recent conversation summary
        if self.global_context["conversation_summary"]:
            recent_messages = self.global_context["conversation_summary"][-3:]  # Last 3 messages
            context_parts.append("Recent conversation: " + " | ".join([
                f"{msg['role']}: {msg['content'][:50]}..." for msg in recent_messages
            ]))
            
        # Add user preferences
        if self.global_context["user_preferences"]:
            context_parts.append("User preferences: " + str(self.global_context["user_preferences"]))
            
        # Add transition history
        if self.global_context["transition_history"]:
            last_transition = self.global_context["transition_history"][-1]
            context_parts.append(f"Last transition: {last_transition['from_agent']} -> {last_transition['to_agent']}")
            
        return " | ".join(context_parts)
        
    def _detect_intent_and_transition(self, user_message: str, agent_response: str) -> Optional[str]:
        # First check for explicit transition in agent response
        if TRANSITION_TEXT in agent_response:
            transition_path = agent_response.split(TRANSITION_TEXT)[1].split("\n")[0].strip()
            # Normalize agent names
            transition_path = transition_path.lower().replace("_department", "_agent").replace("department", "_agent")
            
            # Handle multi-step transitions
            if "->" in transition_path:
                # Get the first agent in the path
                first_agent = transition_path.split("->")[0].strip()
                # Store the full path in global context for future transitions
                self.global_context["transition_path"] = transition_path
                return first_agent
            return transition_path
            
        # Then check for transition confirmation
        if TRANSITION_CONFIRMATION in agent_response:
            target = agent_response.split(TRANSITION_CONFIRMATION)[1].split("\n")[0].strip()
            return target.lower().replace("_department", "_agent").replace("department", "_agent")
            
        # Check if we're in the middle of a multi-step transition
        if "transition_path" in self.global_context:
            path = self.global_context["transition_path"]
            current_agent = self.active_node.agent.get_name()
            if current_agent in path:
                # Get the next agent in the path
                agents = path.split("->")
                current_index = agents.index(current_agent)
                if current_index + 1 < len(agents):
                    next_agent = agents[current_index + 1].strip()
                    if current_index + 2 == len(agents):
                        # This is the last transition, clear the path
                        del self.global_context["transition_path"]
                    return next_agent
            
        # Finally check transition rules with improved detection
        transition_rules = self.active_node.transition_rules
        if not transition_rules:
            return None
            
        user_message_lower = user_message.lower()
        agent_response_lower = agent_response.lower()
        
        # Check both user message and agent response for transition intents
        for intent, target_agent in transition_rules.items():
            if intent in user_message_lower or intent in agent_response_lower:
                # Add confidence scoring
                confidence = 0
                if intent in user_message_lower:
                    confidence += 1
                if intent in agent_response_lower:
                    confidence += 1
                    
                # Only transition if we have reasonable confidence
                if confidence >= 1:
                    return target_agent
                    
        return None

