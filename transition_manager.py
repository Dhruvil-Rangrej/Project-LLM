from typing import Dict, Generator, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.voice_agent import ConversationalAgent

# Transition constants
TRANSITION_TEXT = "TRANSITION_TO:"
TRANSITION_CONTEXT = "TRANSITION_CONTEXT:"
TRANSITION_PATH_SEPARATOR = "->"


class TransitionManager:
    """Manages all transition logic and processing for the agent graph"""
    
    def __init__(self):
        """Initialize the transition manager"""
        self.transitions: List[Dict] = []
    
    def detect_intent_and_transition(self, user_message: str, agent_response: str, 
                                   active_node, nodes: Dict) -> Optional[str]:
        """
        Detect if a transition should occur based on user message and agent response
        
        Args:
            user_message: The user's input message
            agent_response: The agent's response
            active_node: Current active agent node
            nodes: Dictionary of all agent nodes
            
        Returns:
            Target agent name if transition should occur, None otherwise
        """        # First check for explicit transition in agent response
        if TRANSITION_TEXT in agent_response:
            transition_path = agent_response.split(TRANSITION_TEXT)[1].split("\n")[0].strip()
            # Normalize agent names            transition_path = transition_path.lower().replace("_department", "_agent").replace("department", "_agent")
            
            # Handle multi-step transitions
            if TRANSITION_PATH_SEPARATOR in transition_path:
                # Get the first agent in the path
                first_agent = transition_path.split(TRANSITION_PATH_SEPARATOR)[0].strip()
                # Store the full path for future transitions
                self.transitions.append({
                    "type": "multi_step_path",
                    "path": transition_path,
                    "from_agent": active_node.agent.get_name(),
                    "timestamp": None
                })
                return first_agent
            return transition_path
            
        # Check if we're in the middle of a multi-step transition
        current_agent_name = active_node.agent.get_name()        # Look for multi-step path in transitions list
        for transition in reversed(self.transitions):
            if (transition.get("type") == "multi_step_path" and 
                transition.get("from_agent") == current_agent_name):
                path = transition["path"]
                if current_agent_name in path:
                    # Get the next agent in the path
                    agents = path.split(TRANSITION_PATH_SEPARATOR)
                    try:
                        current_index = agents.index(current_agent_name)
                        if current_index + 1 < len(agents):
                            next_agent = agents[current_index + 1].strip()
                            if current_index + 2 == len(agents):
                                # This is the last transition, mark as completed
                                transition["completed"] = True
                            return next_agent
                    except ValueError:
                        continue
                break
            
        # Finally check transition rules with improved detection
        transition_rules = active_node.transition_rules
        if not transition_rules:
            return None
            
        user_message_lower = user_message.lower()
        agent_response_lower = agent_response.lower()
        
        # Check both user message and agent response for transition intents
        for intent, target_agent in transition_rules.items():
            # Improved intent matching with keyword variations
            intent_keywords = self._get_intent_keywords(intent)
            
            user_matches = any(keyword in user_message_lower for keyword in intent_keywords)
            agent_matches = any(keyword in agent_response_lower for keyword in intent_keywords)
            
            if user_matches or agent_matches:
                # Add confidence scoring
                confidence = 0
                if user_matches:
                    confidence += 1
                if agent_matches:
                    confidence += 1
                    
                # Only transition if we have reasonable confidence
                if confidence >= 1:
                    return target_agent
                    
        return None
    
    def _get_intent_keywords(self, intent: str) -> List[str]:
        """Get expanded keywords for better intent matching"""
        keyword_map = {
            "booking": ["booking", "book", "reserve", "schedule", "appointment", "meeting room", "conference room"],
            "faq": ["faq", "question", "help", "info", "information", "what", "how", "why", "policy"],
            "emergency": ["emergency", "urgent", "help", "crisis", "accident", "fire", "medical"],
            "hr": ["hr", "human resources", "employee", "staff", "payroll", "leave", "vacation", "benefits"],
            "it": ["it", "computer", "technical", "tech", "software", "hardware", "network", "password", "login"],
            "visitor": ["visitor", "guest", "badge", "check-in", "visit", "entrance"],
            "feedback": ["feedback", "complaint", "suggestion", "review", "opinion", "rating"]
        }
        return keyword_map.get(intent, [intent])
    
    def process_transitioned_message(self, user_message: str, target_agent: str, 
                                   nodes: Dict, agent_contexts: Dict, 
                                   conversation_history: List[Dict],
                                   format_parent_context_func) -> Generator[str, None, None]:
        """
        Process the original message with the new target agent
        
        Args:
            user_message: Original user message
            target_agent: Name of the target agent
            nodes: Dictionary of all agent nodes
            agent_contexts: Dictionary of agent contexts
            conversation_history: Global conversation history
            format_parent_context_func: Function to format parent context
            
        Yields:
            Response chunks from the target agent
        """
        target_node = nodes[target_agent]
        target_agent_obj = target_node.agent
        
        # Add the user message to the new agent's context
        agent_contexts[target_agent]["conversation_summary"].append({
            "role": "user",
            "content": user_message,
            "agent": target_agent
        })
        
        # Get parent context for the new agent
        context_str = format_parent_context_func(target_agent)
        
        # Create a specialized system message for transitioned agents that overrides routing behavior
        base_system_message = target_agent_obj.get_system_message()
        
        # Remove the graph structure and transition instructions from the base message
        base_parts = base_system_message.split("GRAPH STRUCTURE:")
        core_prompt = base_parts[0] if base_parts else base_system_message
        
        # Create a new system message specifically for handling transitioned requests
        specialized_system_message = f"""{core_prompt}

TRANSITION OVERRIDE: You have received a transferred request that you are specifically designed to handle. 
The user's query is: '{user_message}'

IMPORTANT INSTRUCTIONS:
- You are the FINAL destination for this request - do not transfer to another agent
- Provide a direct, helpful response to address the user's specific needs
- Use your specialized knowledge and tools to fully resolve their request
- Do not use TRANSITION_TO: commands in your response
- Handle the request completely within your capabilities"""
        
        if context_str:
            specialized_system_message += f"\nParent Context: {context_str}"
            
        # Create messages for the new agent with the specialized system prompt
        messages = [
            {"role": "system", "content": specialized_system_message},
            {"role": "user", "content": f"[TRANSFERRED REQUEST] {user_message}"}
        ]
        
        # Generate response from new agent
        response_chunks = []
        for chunk in target_agent_obj.execute_with_streaming(messages):
            response_chunks.append(chunk)
            yield chunk
        
        full_response = "".join(response_chunks) if isinstance(response_chunks[0], str) else response_chunks[0]
        
        # Update the new agent's context with its response
        agent_contexts[target_agent]["conversation_summary"].append({
            "role": "assistant",
            "content": full_response,
            "agent": target_agent
        })
        
        # Update conversation history
        conversation_history.append({
            "role": "assistant", 
            "content": full_response
        })
        
        # Important: Do NOT check for transitions in the response from a transitioned agent
        # This prevents infinite transition loops
    
    def record_transition(self, current_agent: str, user_message: str, 
                         response: str, next_agent: str, agent_contexts: Dict) -> None:
        """
        Record a transition and update agent context
        
        Args:
            current_agent: Name of the current agent
            user_message: User's message that triggered transition
            response: Agent's response
            next_agent: Target agent name
            agent_contexts: Dictionary of agent contexts
        """
        # Add transition to list
        self.transitions.append({
            "from_agent": current_agent,
            "to_agent": next_agent,
            "user_message": user_message,
            "agent_response": response,
            "timestamp": None  # You can add timestamp if needed
        })
        
        # Extract and store any user preferences or session data in current agent context
        if "preference" in user_message.lower():
            agent_contexts[current_agent]["user_preferences"].update({
                "last_preference": user_message
            })
            
        # Update session data for current agent
        agent_contexts[current_agent]["session_data"].update({
            "last_interaction": {
                "user_message": user_message,
                "agent_response": response,
                "transitioned_to": next_agent
            }
        })
    
    def get_transitions(self) -> List[Dict]:
        """Get all transitions that have occurred"""
        return self.transitions.copy()
        
    def get_recent_transitions(self, count: int = 5) -> List[Dict]:
        """Get the most recent transitions"""
        return self.transitions[-count:] if self.transitions else []
    
    def get_last_transition(self) -> Optional[Dict]:
        """Get the last transition that occurred"""
        return self.transitions[-1] if self.transitions else None
