from typing import Dict, Generator, List, Optional, TYPE_CHECKING
from agent_path_finder import AgentPathFinder

if TYPE_CHECKING:
    from agents.voice_agent import ConversationalAgent

# Transition constants
TRANSITION_TEXT = "TRANSITION_TO:"
TRANSITION_PATH_SEPARATOR = "->"


class TransitionManager:
    """Manages all transition logic and processing for the agent graph"""
    
    def __init__(self):
        """Initialize the transition manager"""
        self.transitions: List[Dict] = []
        self.path_finder = AgentPathFinder("agent_config.json")
        self._transition_history: List[str] = []  # Track recent transitions to prevent loops
    
    def detect_transition(self, response_text: str) -> Optional[Dict]:
        """
        Simple helper method to detect transition from response text
        
        Args:
            response_text: The response text to analyze
            
        Returns:
            Dictionary with transition info if found, None otherwise
        """
        if TRANSITION_TEXT in response_text:
            transition_target = response_text.split(TRANSITION_TEXT)[1].split("\n")[0].strip()
            # Normalize agent names
            transition_target = transition_target.lower().replace("_department", "_agent").replace("department", "_agent")
            
            return {
                "next_agent": transition_target,
                "context": "Transition detected in response"
            }
        return None

    def detect_intent_and_transition(self, user_message: str, agent_response: str, 
                                   active_node, nodes: Dict) -> Optional[str]:
        """
        Detect if a transition should occur based on LLM decision in agent response
        
        Args:
            user_message: The user's input message
            agent_response: The agent's response
            active_node: Current active agent node
            nodes: Dictionary of all agent nodes
            
        Returns:
            Target agent name if transition should occur, None otherwise
        """        # First check for explicit transition in agent response
        if TRANSITION_TEXT in agent_response:
            transition_target = agent_response.split(TRANSITION_TEXT)[1].split("\n")[0].strip()
            # Normalize agent names
            transition_target = transition_target.lower().replace("_department", "_agent").replace("department", "_agent")
            
            # Prevent self-transitions (agent transitioning to itself)
            current_agent = active_node.agent.get_name()
            if transition_target == current_agent:
                print(f"[DEBUG] Prevented self-transition: {current_agent} -> {transition_target}")
                return None
            
            # Handle multi-step transitions using path finder
            if TRANSITION_PATH_SEPARATOR in transition_target:
                # Parse the requested path
                requested_path = [agent.strip() for agent in transition_target.split(TRANSITION_PATH_SEPARATOR)]
                
                # Store the full path for execution
                self.transitions.append({
                    "type": "multi_step_path",
                    "path": transition_target,
                    "from_agent": active_node.agent.get_name(),
                    "requested_path": requested_path,
                    "current_step": 0,
                    "timestamp": None
                })
                return requested_path[0] if requested_path else None
            
            # For single transitions, use path finder to validate and find route
            current_agent = active_node.agent.get_name()
            if transition_target in nodes:
                # Check if direct transition is possible or find a path
                path = self.path_finder.find_path(current_agent, transition_target)
                if path and len(path) > 1:
                    if len(path) == 2:  # Direct transition
                        return transition_target
                    else:  # Multi-step path needed
                        path_str = TRANSITION_PATH_SEPARATOR.join(path[1:])  # Exclude current agent
                        self.transitions.append({
                            "type": "auto_generated_path",
                            "path": path_str,
                            "from_agent": current_agent,
                            "target_agent": transition_target,
                            "full_path": path,
                            "current_step": 0,
                            "timestamp": None
                        })
                        return path[1]  # Return next agent in path
                        
            return transition_target
            
        # Check if we're in the middle of a multi-step transition
        current_agent_name = active_node.agent.get_name()
        
        # Look for active multi-step transitions
        for transition in reversed(self.transitions):
            if (transition.get("type") in ["multi_step_path", "auto_generated_path"] and 
                not transition.get("completed", False)):
                
                if transition.get("type") == "multi_step_path":
                    # Handle user-requested multi-step paths
                    requested_path = transition.get("requested_path", [])
                    current_step = transition.get("current_step", 0)
                    
                    if current_step < len(requested_path) and requested_path[current_step] == current_agent_name:
                        # Move to next step
                        next_step = current_step + 1
                        if next_step < len(requested_path):
                            transition["current_step"] = next_step
                            return requested_path[next_step]
                        else:
                            # Path completed
                            transition["completed"] = True
                            
                elif transition.get("type") == "auto_generated_path":
                    # Handle auto-generated paths
                    full_path = transition.get("full_path", [])
                    current_step = transition.get("current_step", 0)
                    
                    # Find current position in path
                    if current_agent_name in full_path:
                        current_index = full_path.index(current_agent_name)
                        next_index = current_index + 1
                        
                        if next_index < len(full_path):
                            transition["current_step"] = next_index
                            return full_path[next_index]
                        else:
                            # Path completed
                            transition["completed"] = True
                break
                    
        return None
    
    def find_path_to_agent(self, current_agent: str, target_agent: str) -> Optional[List[str]]:
        """
        Find the optimal path from current agent to target agent
        
        Args:
            current_agent: Name of the current agent
            target_agent: Name of the target agent
            
        Returns:
            List of agent names representing the path, or None if no path exists
        """
        return self.path_finder.find_path(current_agent, target_agent)
    
    def execute_path_transition(self, current_agent: str, target_agent: str) -> Optional[str]:
        """
        Execute a path-based transition to reach the target agent
        
        Args:
            current_agent: Name of the current agent
            target_agent: Name of the target agent
              Returns:
            Next agent in the path, or None if no path exists
        """
        path = self.find_path_to_agent(current_agent, target_agent)
        if path and len(path) > 1:
            # Store the path for multi-step execution
            if len(path) > 2:  # Multi-step path
                path_str = TRANSITION_PATH_SEPARATOR.join(path[1:])
                self.transitions.append({
                    "type": "auto_generated_path",
                    "path": path_str,
                    "from_agent": current_agent,
                    "target_agent": target_agent,
                    "full_path": path,
                    "current_step": 1,
                    "timestamp": None
                })
                
            return path[1]  # Return next agent in path
                        
        return None
        
    def process_transitioned_message(self, user_message: str, target_agent: str, 
                                   nodes: Dict, agent_contexts: Dict, 
                                   conversation_history: List[Dict],
                                   format_parent_context_func, context_str: str = "") -> Generator[str, None, None]:
        """
        Process the original message with the new target agent
        
        Args:
            user_message: Original user message
            target_agent: Name of the target agent
            nodes: Dictionary of all agent nodes
            agent_contexts: Dictionary of agent contexts
            conversation_history: Global conversation history
            format_parent_context_func: Function to format parent context
            context_str: Optional context string to override default context
            
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
        if not context_str:
            context_str = format_parent_context_func(target_agent)
        
        # Create a specialized system message for transitioned agents that overrides routing behavior
        base_system_message = target_agent_obj.get_system_message()
        
        # Remove the graph structure and transition instructions from the base message
        base_parts = base_system_message.split("GRAPH STRUCTURE:")
        core_prompt = base_parts[0] if base_parts else base_system_message
          # Create a new system message specifically for handling transitioned requests
        specialized_system_message = f"""{core_prompt}

TRANSITION CONTEXT: You have received a transferred request that you are specifically designed to handle. 
The user's query is: '{user_message}'

IMPORTANT INSTRUCTIONS:
- Handle this request using your specialized knowledge and tools
- Provide a direct, helpful response to address the user's specific needs
- Once you have completed your task (e.g., confirmed a booking, answered a question), you may redirect the user back to reception or feedback for additional assistance
- If your task is complete and the user needs general assistance, use: TRANSITION_TO: reception_agent
- If your task is complete and the user wants to provide feedback, use: TRANSITION_TO: feedback_agent
- Only transition after you have fully completed your assigned task"""
        if context_str:
            specialized_system_message += f"\nParent Context: {context_str}"
        
        # Add scheduler-specific context if transitioning to scheduler agent
        if target_agent == "scheduler_agent":
            scheduling_context = agent_contexts[target_agent]["session_data"].get("scheduling_context")
            if scheduling_context:
                specialized_system_message += f"""

SCHEDULING CONTEXT:
- Original request: {scheduling_context.get('original_request', '')}
- Transferred from: {scheduling_context.get('from_agent', '')}
- This is a scheduling-focused request - prioritize gathering time, date, duration, and location details
- Use your manage_schedule tool once you have all required information"""
            
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
        
        # Check for completion transitions (e.g., back to reception after task completion)
        # Allow transitions to root/reception agent or feedback agent (completion flows)
        # But prevent transitions back to parent agent or infinite loops
        completion_transition = self.detect_transition(full_response)
        if completion_transition:
            next_agent = completion_transition["next_agent"]
            
            # Allow completion transitions to specific agents
            allowed_completion_agents = ["reception_agent", "feedback_agent"]
            
            # Prevent infinite loops: don't transition back to the agent that initiated this transfer
            # or to the same agent we're currently in
            transition_history = getattr(self, '_transition_history', [])
            if len(transition_history) > 0:
                initiating_agent = transition_history[-1] if transition_history else None
            else:
                initiating_agent = None
                
            should_allow_transition = (
                next_agent in allowed_completion_agents and
                next_agent != target_agent and  # Don't transition to self
                next_agent != initiating_agent  # Don't go back to the agent that sent us here
            )
            
            if should_allow_transition:
                print(f" Completion transition: {target_agent} → {next_agent}")
                
                # Record this as a completion transition
                self.record_transition(
                    current_agent=target_agent,
                    user_message=user_message,
                    response=full_response,
                    next_agent=next_agent,
                    agent_contexts=agent_contexts
                )                # Process the completion transition
                context_info = f"Completed task in {target_agent}, transitioning to {next_agent}"
                yield from self.process_transitioned_message(
                    user_message=f"Task completed. {completion_transition.get('context', '')}",
                    target_agent=next_agent,
                    nodes=nodes,
                    agent_contexts=agent_contexts,
                    conversation_history=conversation_history,
                    format_parent_context_func=format_parent_context_func,
                    context_str=context_info
                )
                return
        
        # No completion transition detected or allowed
    
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
        
        # Update transition history for loop prevention
        self._transition_history.append(current_agent)
        # Keep only the last 5 transitions to prevent memory buildup
        if len(self._transition_history) > 5:
            self._transition_history.pop(0)
          # Extract and store any user preferences or session data in current agent context
        if "preference" in user_message.lower():
            agent_contexts[current_agent]["user_preferences"].update({
                "last_preference": user_message
            })
            
        # Enhanced context preservation for scheduler agent
        if current_agent == "scheduler_agent" or next_agent == "scheduler_agent":
            # Preserve scheduling context
            scheduling_keywords = ["meeting", "appointment", "schedule", "book", "calendar", "time", "date"]
            if any(keyword in user_message.lower() for keyword in scheduling_keywords):
                agent_contexts[next_agent]["session_data"].update({
                    "scheduling_context": {
                        "original_request": user_message,
                        "from_agent": current_agent,
                        "scheduling_intent": True
                    }
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
    
    def get_available_agents(self, current_agent: str) -> List[str]:
        """Get list of agents reachable from current agent"""
        return list(self.path_finder.get_direct_connections(current_agent))
    
    def get_path_description(self, current_agent: str, target_agent: str) -> str:
        """Get human-readable description of path to target agent"""
        path = self.find_path_to_agent(current_agent, target_agent)
        return self.path_finder.get_path_description(path) if path else "No path available"
    
    def is_agent_reachable(self, current_agent: str, target_agent: str) -> bool:
        """Check if target agent is reachable from current agent"""
        return self.path_finder.is_reachable(current_agent, target_agent)
