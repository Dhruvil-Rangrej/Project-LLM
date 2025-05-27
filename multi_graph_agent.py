from json_graph_builder import JSONGraphBuilder
from agent_graph import AgentGraph
import glob
import os

class ConversationAgentGraph():
    @staticmethod
    def create_agent_graph() -> AgentGraph:
        # Get all JSON files from the agents directory
        json_files = glob.glob(os.path.join("agents", "*.json"))
        
        # Build the graph from JSON files
        return JSONGraphBuilder.build_graph_from_json_files(json_files)