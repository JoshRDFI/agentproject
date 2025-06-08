from crewai import Agent, Crew, Process, Task
from typing import List, Optional, Dict, Any

# Disable OpenAI API key validation
import os
import warnings

# Set a dummy OpenAI API key to satisfy CrewAI's validation
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-validation-purposes-only"

# Suppress OpenAI API key validation warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openai")
warnings.filterwarnings("ignore", category=UserWarning, module="crewai")

from agents.base_agents import (
    PDFProcessingAgent, WebSearchAgent, ResearchAgent,
    AnalysisAgent, WriterAgent, ManagerAgent
)
from tasks.base_tasks import (
    pdf_processing_task, web_search_task, research_task,
    analysis_task, writing_task, management_task
)

from crewai import LLM
from litellm import completion

def create_crew(task_id: str, topic: str, pdf_paths: List[str] = None) -> Crew:
    """Creates a crew of agents for processing a task.
    
    Args:
        task_id: The ID of the task
        topic: The topic to research
        pdf_paths: Optional list of paths to PDF files to process
    
    Returns:
        A Crew object with the specified agents and tasks
    """
    # Test Ollama connection with LiteLLM directly
    try:
        # Test with the correct format
        test_response = completion(
            model="ollama/llama3.2", 
            messages=[{"content": "Test message. Respond briefly.", "role": "user"}], 
            api_base="http://localhost:11434"
        )
        print("LiteLLM direct test successful:", test_response.choices[0].message.content[:50])
    except Exception as e:
        print(f"LiteLLM direct test failed: {str(e)}")
    # Initialize LLMs for each agent with proper Ollama configuration
    # The key fix: use "ollama/" prefix for the model names
    try:
        # Configure LLMs with correct Ollama configuration
        llm_web = LLM(
            provider="ollama",  # Use provider instead of model prefix
            model="llama3.2",  # Model name without version tag
            api_base="http://localhost:11434"
        )
        llm_research = LLM(
            provider="ollama",
            model="deepseek-r1", 
            api_base="http://localhost:11434"
        )
        llm_analysis = LLM(
            provider="ollama",
            model="deepseek-r1",
            api_base="http://localhost:11434"
        )
        llm_writer = LLM(
            provider="ollama",
            model="llama3.2",
            api_base="http://localhost:11434"
        )
        llm_manager = LLM(
            provider="ollama",
            model="llama3.2",
            api_base="http://localhost:11434"
        )
        llm_pdf = LLM(
            provider="ollama",
            model="qwen2.5vl",
            api_base="http://localhost:11434"
        )
        
        print("Successfully initialized all LLMs")
    except Exception as e:
        print(f"Error initializing LLMs: {str(e)}")
        # Fallback to a single LLM for all agents
        print("Falling back to a single LLM for all agents")
        fallback_llm = LLM(
            provider="ollama",
            model="llama3.2",
            api_base="http://localhost:11434"
        )
        llm_web = llm_research = llm_analysis = llm_writer = llm_manager = llm_pdf = fallback_llm

    # Initialize agents with their respective LLMs
    web_agent = WebSearchAgent(llm=llm_web)
    research_agent = ResearchAgent(llm=llm_research)
    analysis_agent = AnalysisAgent(llm=llm_analysis)
    writer_agent = WriterAgent(llm=llm_writer)
    manager_agent = ManagerAgent(llm=llm_manager)
    
    # Create a list of agents for the crew
    agents = [web_agent, research_agent, analysis_agent, writer_agent, manager_agent]
    
    # Create tasks
    tasks = []
    
    # Add PDF processing task if PDF paths are provided
    if pdf_paths and len(pdf_paths) > 0:
        pdf_agent = PDFProcessingAgent(llm=llm_pdf)
        pdf_task = pdf_processing_task(pdf_paths=pdf_paths, agent=pdf_agent, query=topic)
        tasks.append(pdf_task)
        agents.append(pdf_agent)
    
    # Add web search task
    web_task = web_search_task(query=topic, agent=web_agent)
    tasks.append(web_task)
    
    # Add research task
    research_task_obj = research_task(topic=topic, agent=research_agent)
    tasks.append(research_task_obj)
    
    # Add analysis task
    analysis_task_obj = analysis_task(research_report="", agent=analysis_agent)
    tasks.append(analysis_task_obj)
    
    # Add writing task
    writing_task_obj = writing_task(analysis="", topic=topic, agent=writer_agent)
    tasks.append(writing_task_obj)
    
    # Add management task
    management_task_obj = management_task(content="", topic=topic, agent=manager_agent)
    tasks.append(management_task_obj)
    
    # Create crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,  # Enable verbosity for logs
        process=Process.sequential,  # Sequential process for predictable flow
        memory=True  # Enable memory for the crew
    )
    
    return crew

def run_crew(crew: Crew, task_id: str, connections: Dict[str, Any] = None, agent_interactions: Dict[str, List[Dict]] = None) -> str:
    """Runs a crew and returns the result.
    
    Args:
        crew: The crew to run
        task_id: The ID of the task
        connections: Optional dictionary of WebSocket connections
        agent_interactions: Optional dictionary of agent interactions
    
    Returns:
        The result of running the crew
    """
    try:
        # Add debug print statements
        print(f"Starting crew for task {task_id}")
        print(f"Crew has {len(crew.agents)} agents and {len(crew.tasks)} tasks")
        
        # Import and initialize the callback if connections are provided
        if connections and agent_interactions:
            from callbacks import AgentInteractionCallback
            callback = AgentInteractionCallback(task_id, connections, agent_interactions)
            # Register the callback with the crew
            crew.callbacks = [callback]
            result = crew.kickoff()
        else:
            result = crew.kickoff()
            
        print(f"Crew completed task {task_id} with result: {str(result)[:100]}...")
        return str(result)
    except Exception as e:
        error_message = f"Error running crew for task {task_id}: {str(e)}"
        print(error_message)
        import traceback
        print(traceback.format_exc())
        return error_message