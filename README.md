# CrewAI Multi-Agent Project

This project uses CrewAI to create a crew of AI agents that can perform various tasks. It includes a web interface for submitting tasks, receiving responses, and viewing real-time agent interactions.

## Features

- **Multiple Specialized Agents**: Web Search Agent, Research Agent, Analysis Agent, Writer Agent, Manager Agent, and PDF Processing Agent
- **Web Interface**: Submit tasks, view results, add clarifications, and upload PDF files
- **Real-time Agent Interactions**: Watch agents work in real-time through a collapsible interface
- **Multiple LLM Support**: Configure different LLMs for different agents
- **Task Management**: Track task status and history
- **PDF Processing**: Extract and analyze information from PDF files using vision-language models
- **Data Storage**: Store PDF extraction results in JSON or PostgreSQL

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure Ollama is running with your desired models. The project is configured to use the following models by default:
   - Web Search Agent: llama3.2:latest
   - Research Agent: deepseek-r1:8b
   - Analysis Agent: deepseek-r1:8b
   - Writer Agent: llama3.2:latest
   - Manager Agent: llama3.2:latest
   - PDF Processing Agent: qwen2.5vl:7b

   You can change these in the `crew_setup.py` file.

3. Start the web interface:
   ```bash
   python main.py
   ```

   Or use the CLI interface:
   ```bash
   python main.py --cli
   ```

4. Open your browser and navigate to `http://localhost:8000`.

## Project Structure

- `agents/`: Contains the agent definitions
  - `base_agents.py`: Defines the specialized agents with different roles and capabilities

- `tasks/`: Contains the task definitions
  - `base_tasks.py`: Defines the specialized tasks for each agent

- `web_interface/`: Contains the web interface code
  - `main.py`: FastAPI web server with WebSocket support for real-time updates
  - `templates/`: HTML templates for the web interface

- `database/`: Contains the database modules for storing PDF extraction results
  - `json_storage.py`: JSON-based storage implementation
  - `postgres_storage.py`: PostgreSQL-based storage implementation
  - `storage_factory.py`: Factory for creating storage instances

- `uploads/`: Directory for storing uploaded files
  - `pdfs/`: Directory for storing uploaded PDF files
  - `json/`: Directory for storing JSON extraction results

- `crew_setup.py`: Core logic for creating and running crews
- `main.py`: Entry point for running the web interface or CLI

## How It Works

1. **Task Submission**: Users submit tasks through the web interface or CLI, optionally uploading PDF files
2. **PDF Processing**: If PDF files are provided, the PDF Processing Agent extracts and analyzes information from them
3. **Web Search**: The Web Search Agent searches the internet for relevant information
4. **Research**: The Research Agent analyzes and synthesizes the web search results and PDF analysis
5. **Analysis**: The Analysis Agent identifies patterns and insights from the research
6. **Writing**: The Writer Agent creates well-written content based on the analysis
7. **Management**: The Manager Agent reviews all information for accuracy and presents a cohesive final result

## PDF Processing

The PDF Processing Agent uses the qwen2.5vl:7b model to extract and analyze information from PDF files. The extracted information is stored in either JSON files or a PostgreSQL database, depending on the configuration.

### Storage Options

- **JSON Storage**: By default, the project uses JSON storage for PDF extraction results. The results are stored in the `uploads/json` directory.
- **PostgreSQL Storage**: To use PostgreSQL storage, modify the `database/storage_factory.py` file to use the PostgreSQL storage implementation. You'll need to provide a connection string for your PostgreSQL database.

## Customization

You can customize the agents, tasks, and LLMs used in the project by modifying the following files:

- `agents/base_agents.py`: Modify agent roles, goals, and capabilities
- `tasks/base_tasks.py`: Modify task descriptions and expected outputs
- `crew_setup.py`: Change the LLMs used for each agent and the crew workflow
- `database/storage_factory.py`: Change the storage implementation (JSON or PostgreSQL)

## Troubleshooting

- If you encounter issues with the web interface, check the console for error messages
- Make sure Ollama is running and the specified models are available
- If WebSockets aren't working, try refreshing the page or restarting the server
- If PDF processing fails, check that the qwen2.5vl:7b model is available in Ollama