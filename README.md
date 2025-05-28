# Multi-Agent Office Assistant

A sophisticated office management system that uses multiple specialized AI agents to handle various office tasks and inquiries. The system features a dynamic graph-based architecture that allows agents to intelligently route requests and collaborate to provide comprehensive office support.

## Recent Updates

- **Dynamic Configuration**: Graph structure now dynamically generated from agent_config.json
- **Standardized Response Limits**: Unified word limits across all agents (100 words from config)
- **Improved Maintainability**: Eliminated duplicate code and hardcoded values

## Features

- **Multiple Specialized Agents**:
  - Reception Agent: Main entry point for all inquiries
  - Booking Agent: Handles appointment scheduling
  - Scheduler Agent: Manages office calendar and availability
  - FAQ Agent: Answers common office-related questions
  - Emergency Agent: Handles urgent situations
  - Feedback Agent: Collects user feedback
  - HR Agent: Manages HR-related queries
  - IT Agent: Provides technical support
  - Visitor Agent: Manages visitor check-ins and badges

- **Intelligent Routing**:
  - Dynamic graph-based architecture for efficient request routing
  - Multi-step transitions between agents
  - Context-aware responses
  - Configurable response limits (100 words from agent_config.json)
  - Automatic agent discovery and routing path generation

- **REST API**:
  - FastAPI-based backend
  - CORS support
  - Comprehensive error handling
  - Detailed logging
  - Support for both GET and POST requests
  - Dynamic agent endpoint generation

## Configuration

The system uses `agent_config.json` for centralized configuration:
- Agent definitions and capabilities
- Transition rules between agents
- Response word limits
- Tool configurations
- Parent-child agent relationships

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export NGROK_SERVER_URL="your_ngrok_url"
```

4. Run the server:
```bash
python api.py
```

The server will start on `http://localhost:8000`

## API Endpoints

- `POST /chat` - Send a message to the assistant
  - Request body: `{"content": "your message", "session_id": "optional_session_id"}`
  - Response: `{"content": "response", "agent_name": "current_agent", "transition_path": ["path"]}`

- `GET /chat?message=your_message` - Alternative way to send a message

- `GET /agents` - List all available agents

- `GET /current-agent` - Get the currently active agent

## Usage Example

```python
import requests

# Send a message
response = requests.post("http://localhost:8000/chat", 
    json={"content": "I need to book a meeting room"})
print(response.json())
```

## Architecture

The system uses a dynamic graph-based architecture where:
- Each agent is a node in the graph
- Graph structure is generated dynamically from agent_config.json
- Agents can transition to other agents based on context and configuration
- The reception agent serves as the root node
- All agents can route through multiple steps to reach the appropriate handler
- Transition paths are automatically calculated and optimized

## Development

The project is structured as follows:
- `api.py`: FastAPI server implementation with dynamic agent discovery
- `agent_graph.py`: Graph structure for agent routing
- `agent_node.py`: Node implementation for the graph
- `multi_graph_agent.py`: Main agent graph implementation
- `dynamic_graph_generator.py`: Dynamic graph structure generation from config
- `transition_manager.py`: Handles complex agent transitions
- `agent_config.json`: Centralized configuration for all agents
- `agents/`: Directory containing all specialized agents
- `app.py`: Simple CLI interface for testing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Code Quality

The project maintains high code quality standards:

### Recent Improvements
- **Dynamic Configuration**: Replaced hardcoded values with configuration-driven approach
- **Standardization**: Unified response limits and error handling patterns
- **Maintainability**: Reduced code duplication and improved single source of truth


### Fixed Issues
1. **Hardcoded Agent Lists**: Replaced static lists with dynamic generation from config
2. **Word Limit Inconsistencies**: Standardized to single source in agent_config.json
3. **Duplicate Maintenance**: Eliminated redundant agent name management
4. **Dead Code**: Removed outdated TODO comments and unused code
