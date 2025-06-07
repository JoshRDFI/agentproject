from crewai import Agent, Crew, Process, Task
from typing import List, Optional, Dict, Any
from agents.base_agents import (
    PDFProcessingAgent, WebSearchAgent, ResearchAgent,
    AnalysisAgent, WriterAgent, ManagerAgent
)
from tasks.base_tasks import (
    pdf_processing_task, web_search_task, research_task,
    analysis_task, writing_task, management_task
)

def create_crew(task_id: str, topic: str, pdf_paths: List[str] = None) -> Crew:
    """Creates a crew of agents for processing a task.
    
    Args:
        task_id: The ID of the task
        topic: The topic to research
        pdf_paths: Optional list of paths to PDF files to process
        
    Returns:
        A Crew object with the specified agents and tasks
    """
    # Initialize agents with specific LLMs
    web_agent = WebSearchAgent(llm_model="llama3.2:latest")
    research_agent = ResearchAgent(llm_model="deepseek-r1:8b")
    analysis_agent = AnalysisAgent(llm_model="deepseek-r1:8b")
    writer_agent = WriterAgent(llm_model="llama3.2:latest")
    manager_agent = ManagerAgent(llm_model="llama3.2:latest")
    
    # Create a list of agents for the crew
    agents = [web_agent, research_agent, analysis_agent, writer_agent, manager_agent]
    
    # Create tasks
    tasks = []
    
    # Add PDF processing task if PDF paths are provided
    if pdf_paths and len(pdf_paths) > 0:
        pdf_agent = PDFProcessingAgent(llm_model="qwen2.5-7b")
        pdf_task = pdf_processing_task(pdf_paths=pdf_paths, query=topic)
        tasks.append((pdf_agent, pdf_task))
        agents.append(pdf_agent)
    
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
    tasks.append((manager_agent, management_task_obj))
    
    # Create crew
    crew = Crew(
        agents=agents,
        tasks=[task for _, task in tasks],
        verbose=2,  # Increased verbosity for more detailed logs
        process=Process.sequential,  # Sequential process for predictable flow
        memory=True,  # Enable memory for the crew
        manager_llm="llama3"  # Use llama3 for the crew manager
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