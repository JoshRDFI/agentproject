from crewai import Crew, Process
from typing import List, Optional, Dict, Any
from agents.base_agents import (
    PDFProcessingAgent, WebSearchAgent, ResearchAgent,
    AnalysisAgent, WriterAgent, ManagerAgent
)
from tasks.base_tasks import (
    pdf_processing_task, web_search_task, research_task,
    analysis_task, writing_task, management_task
)
from callbacks import AgentInteractionCallback

def create_crew(task_id: str, topic: str, pdf_paths: List[str] = None, 
               connections: Dict[str, Any] = None, agent_interactions: Dict[str, List[Dict]] = None,
               callback_enabled: bool = True) -> Crew:
    """Creates a crew of agents for processing a task.
    
    Args:
        task_id: The ID of the task
        topic: The topic to research
        pdf_paths: Optional list of paths to PDF files to process
        connections: Optional dictionary of WebSocket connections for real-time updates
        agent_interactions: Optional dictionary to store agent interactions
        callback_enabled: Whether to enable callbacks for real-time updates
        
    Returns:
        A Crew object with the specified agents and tasks
    """
    # Initialize agents with specific LLMs
    pdf_agent = PDFProcessingAgent(llm_model="qwen2.5vl:7b")
    web_agent = WebSearchAgent(llm_model="llama3")
    research_agent = ResearchAgent(llm_model="llama3")
    analysis_agent = AnalysisAgent(llm_model="llama3")
    writer_agent = WriterAgent(llm_model="llama3")
    manager_agent = ManagerAgent(llm_model="llama3")
    
    # Create tasks
    tasks = []
    
    # Add PDF processing task if PDF paths are provided
    pdf_analysis = None
    if pdf_paths and len(pdf_paths) > 0:
        pdf_task = pdf_processing_task(pdf_paths=pdf_paths, query=topic)
        tasks.append((pdf_agent, pdf_task))
    
    # Add web search task
    web_task = web_search_task(query=topic)
    tasks.append((web_agent, web_task))
    
    # Add research task
    research_task_obj = research_task(topic=topic)
    tasks.append((research_agent, research_task_obj))
    
    # Add analysis task
    analysis_task_obj = analysis_task(research_report="")
    tasks.append((analysis_agent, analysis_task_obj))
    
    # Add writing task
    writing_task_obj = writing_task(analysis="", topic=topic)
    tasks.append((writer_agent, writing_task_obj))
    
    # Add management task
    management_task_obj = management_task(content="", topic=topic)
    tasks.append((manager_agent, management_task_obj))
    
    # Create callback if enabled
    callback = None
    if callback_enabled and connections is not None and agent_interactions is not None:
        if task_id not in agent_interactions:
            agent_interactions[task_id] = []
        callback = AgentInteractionCallback(task_id, connections, agent_interactions)
    
    # Create crew
    crew = Crew(
        agents=[pdf_agent, web_agent, research_agent, analysis_agent, writer_agent, manager_agent],
        tasks=[task for _, task in tasks],
        verbose=2,  # Increased verbosity for more detailed logs
        process=Process.sequential,  # Sequential process for predictable flow
        memory=True,  # Enable memory for the crew
        manager_llm="llama3",  # Use llama3 for the crew manager
        callback=callback  # Add callback for real-time updates
    )
    
    return crew

def run_crew(crew: Crew, task_id: str) -> str:
    """Runs a crew and returns the result.
    
    Args:
        crew: The crew to run
        task_id: The ID of the task
        
    Returns:
        The result of running the crew
    """
    try:
        result = crew.kickoff()
        return result
    except Exception as e:
        error_message = f"Error running crew for task {task_id}: {str(e)}"
        print(error_message)
        return error_message