"""
Agent Path Finder Module

This module provides pathfinding capabilities to determine the optimal route
from one agent to another in the agent graph structure.
"""

import json
from typing import Dict, List, Optional, Set
from collections import deque


class AgentPathFinder:
    """Finds optimal paths between agents in the agent graph"""
    
    def __init__(self, config_file: str = "agent_config.json"):
        """
        Initialize the path finder with agent configuration
        
        Args:
            config_file: Path to the agent configuration JSON file
        """
        self.config_file = config_file
        self.agents_config = self._load_config()
        self.graph = self._build_graph()
        
    def _load_config(self) -> Dict:
        """Load agent configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file {self.config_file}")
    
    def _build_graph(self) -> Dict[str, Set[str]]:
        """
        Build a bidirectional graph from agent configuration
        
        Returns:
            Dictionary mapping agent names to sets of connected agents
        """
        graph = {}
        
        # Initialize all agents in graph
        for agent in self.agents_config['agents']:
            agent_name = agent['agent_name']
            graph[agent_name] = set()
        
        # Add edges based on transition rules
        for agent in self.agents_config['agents']:
            agent_name = agent['agent_name']
            transition_rules = agent.get('transition_rules', {})
            
            for target_agent in transition_rules.items():
                # Add bidirectional connections
                graph[agent_name].add(target_agent)
                if target_agent in graph:
                    graph[target_agent].add(agent_name)
        
        # Add parent-child relationships
        for agent in self.agents_config['agents']:
            agent_name = agent['agent_name']
            parent_agent = agent.get('parent_agent')
            
            if parent_agent and parent_agent in graph:
                # Add bidirectional parent-child connection
                graph[agent_name].add(parent_agent)
                graph[parent_agent].add(agent_name)
        
        return graph
    
    def find_path(self, start_agent: str, target_agent: str) -> Optional[List[str]]:
        """
        Find the shortest path between two agents using BFS
        
        Args:
            start_agent: Name of the starting agent
            target_agent: Name of the target agent
            
        Returns:
            List of agent names representing the path, or None if no path exists
        """
        if start_agent not in self.graph or target_agent not in self.graph:
            return None
            
        if start_agent == target_agent:
            return [start_agent]
        
        # BFS to find shortest path
        queue = deque([(start_agent, [start_agent])])
        visited = {start_agent}
        
        while queue:
            current_agent, path = queue.popleft()
            
            # Check all connected agents
            for neighbor in self.graph[current_agent]:
                if neighbor == target_agent:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # No path found
    
    def get_direct_connections(self, agent_name: str) -> Set[str]:
        """
        Get all agents directly connected to the given agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Set of directly connected agent names
        """
        return self.graph.get(agent_name, set()).copy()
    
    def is_reachable(self, start_agent: str, target_agent: str) -> bool:
        """
        Check if target agent is reachable from start agent
        
        Args:
            start_agent: Name of the starting agent
            target_agent: Name of the target agent
            
        Returns:
            True if target is reachable, False otherwise
        """
        return self.find_path(start_agent, target_agent) is not None
    
    def get_path_description(self, path: List[str]) -> str:
        """
        Get a human-readable description of a path
        
        Args:
            path: List of agent names representing the path
            
        Returns:
            String description of the path
        """
        if not path:
            return "No path"
        
        if len(path) == 1:
            return f"Already at {path[0]}"
        
        return " → ".join(path)
