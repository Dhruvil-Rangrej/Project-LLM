from json_graph_builder import JSONGraphBuilder
from agent_graph import AgentGraph

class ConversationAgentGraph():
    @staticmethod
    def create_agent_graph() -> AgentGraph:
        # Build the graph from the single JSON configuration file
        return JSONGraphBuilder.build_graph_from_json_file("agent_config.json")