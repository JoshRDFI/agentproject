from crewai import Crew, Process
from typing import List, Dict, Any, Optional, Callable, Awaitable
from agents import ResearchAgent, AnalysisAgent, WriterAgent, WebSearchAgent, ManagerAgent, PDFProcessingAgent
from tasks import ResearchTask, AnalysisTask, WritingTask, WebSearchTask, ManagerTask, PDFProcessingTask
from database.storage_factory import default_storage
import asyncio
import os

def create_crew(task_description: str, pdf_paths: List[str] = None, llm_models: Dict[str, str] = None, callback = None) -> Crew:
    """Create a crew of agents to work on a task.
    
    Args:
        task_description: A description of the task to be performed
        pdf_paths: Optional list of paths to PDF files to process
        llm_models: A dictionary mapping agent types to LLM models
        callback: Optional callback for real-time updates
        
    Returns:
        A configured Crew object ready to run
    """
    if llm_models is None:
        llm_models = {
            "research": "deepseek-r1:8b",
            "analysis": "deepseek-r1:8b",
            "writer": "llama3.2:latest",
            "web_search": "llama3.2:latest",
            "manager": "llama3.2:latest",
            "pdf_processing": "qwen2.5vl:7b"
        }
    
    # Create agents
    web_search_agent = WebSearchAgent(llm_model=llm_models.get("web_search", "llama3.2:latest"))
    research_agent = ResearchAgent(llm_model=llm_models.get("research", "deepseek-r1:8b"))
    analysis_agent = AnalysisAgent(llm_model=llm_models.get("analysis", "deepseek-r1:8b"))
    writer_agent = WriterAgent(llm_model=llm_models.get("writer", "llama3.2:latest"))
    manager_agent = ManagerAgent(llm_model=llm_models.get("manager", "llama3.2:latest"))
    
    # Create tasks
    tasks = []
    
    web_search_task = WebSearchTask(
        agent=web_search_agent,
        query=task_description,
        context="Find relevant and up-to-date information from the web about this topic."
    )
    tasks.append(web_search_task)
    
    # Add PDF processing task if PDF paths are provided
    pdf_results_placeholder = "No PDF analysis results provided."
    if pdf_paths and len(pdf_paths) > 0:
        pdf_processing_agent = PDFProcessingAgent(llm_model=llm_models.get("pdf_processing", "qwen2.5vl:7b"))
        pdf_processing_task = PDFProcessingTask(
            agent=pdf_processing_agent,
            pdf_paths=pdf_paths,
            context=f"Extract relevant information related to: {task_description}"
        )
        tasks.append(pdf_processing_task)
        pdf_results_placeholder = "{pdf_processing_task_output}"
    
    research_task = ResearchTask(
        agent=research_agent,
        topic=task_description,
        context="Use the web search results and PDF analysis (if available) to inform your research. This research will be used for analysis and writing.",
        web_search_results="{web_search_task_output}",  # This will be filled with the output of the web search task
        pdf_results=pdf_results_placeholder
    )
    tasks.append(research_task)
    
    analysis_task = AnalysisTask(
        agent=analysis_agent,
        data="{research_task_output}",  # This will be filled with the output of the research task
        question=f"What are the key insights from the research on {task_description}?"
    )
    tasks.append(analysis_task)
    
    writing_task = WritingTask(
        agent=writer_agent,
        topic=task_description,
        style="professional",
        length="comprehensive",
        research_results="{analysis_task_output}"  # This will be filled with the output of the analysis task
    )
    tasks.append(writing_task)
    
    manager_task = ManagerTask(
        agent=manager_agent,
        topic=task_description,
        web_search_results="{web_search_task_output}",
        pdf_results=pdf_results_placeholder,
        research_results="{research_task_output}",
        analysis_results="{analysis_task_output}",
        writing_results="{writing_task_output}"
    )
    tasks.append(manager_task)
    
    # Create crew
    agents = [web_search_agent, research_agent, analysis_agent, writer_agent, manager_agent]
    if pdf_paths and len(pdf_paths) > 0:
        agents.append(pdf_processing_agent)
    
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True,
        process=Process.sequential,  # Tasks will be executed in sequence
        # If we had a real callback system in CrewAI, we would register it here
        # callback=callback
    )
    
    return crew

def run_crew(task_description: str, pdf_paths: List[str] = None, llm_models: Optional[Dict[str, str]] = None) -> str:
    """Run a crew on a task and return the result.
    
    Args:
        task_description: A description of the task to be performed
        pdf_paths: Optional list of paths to PDF files to process
        llm_models: A dictionary mapping agent types to LLM models
        
    Returns:
        The result of the crew's work
    """
    crew = create_crew(task_description, pdf_paths, llm_models)
    result = crew.kickoff()
    return result

async def run_crew_async(task_description: str, pdf_paths: List[str] = None, callback = None, llm_models: Optional[Dict[str, str]] = None) -> str:
    """Run a crew on a task asynchronously and return the result.
    
    Args:
        task_description: A description of the task to be performed
        pdf_paths: Optional list of paths to PDF files to process
        callback: Optional callback for real-time updates
        llm_models: A dictionary mapping agent types to LLM models
        
    Returns:
        The result of the crew's work
    """
    # In a real implementation, we would pass the callback to create_crew
    # and CrewAI would use it to provide real-time updates
    # For now, we'll simulate the process with our own implementation
    
    # Simulate PDF Processing Agent if PDF paths are provided
    pdf_results = None
    if pdf_paths and len(pdf_paths) > 0:
        if callback:
            await callback.on_agent_start("PDF Processing Agent", f"Processing PDF files for information related to: {task_description}")
        await asyncio.sleep(3)  # Simulate work
        
        # Store simulated extraction results in the database
        pdf_extraction_results = []
        for pdf_path in pdf_paths:
            extraction_data = {
                "text": f"Extracted text from {os.path.basename(pdf_path)}: [PDF content would be processed here using qwen2.5vl:7b model]",
                "metadata": {
                    "filename": os.path.basename(pdf_path),
                    "pages": 10,  # Simulated page count
                    "extracted_at": asyncio.get_event_loop().time()
                }
            }
            extraction_id = default_storage.store_pdf_extraction(pdf_path, extraction_data)
            pdf_extraction_results.append(extraction_data)
        
        pdf_results = f"PDF analysis results for {task_description}:\n\n" + "\n\n".join([result["text"] for result in pdf_extraction_results])
        if callback:
            await callback.on_agent_finish("PDF Processing Agent", pdf_results)
    
    # Simulate Web Search Agent
    if callback:
        await callback.on_agent_start("Web Search Agent", f"Searching the web for information about: {task_description}")
    await asyncio.sleep(2)  # Simulate work
    web_search_result = f"Web search results for {task_description}:\n\n1. Found information from source A\n2. Found information from source B\n3. Found information from source C"
    if callback:
        await callback.on_agent_finish("Web Search Agent", web_search_result)
    
    # Simulate Research Agent
    if callback:
        await callback.on_agent_start("Research Agent", f"Researching: {task_description}")
    await asyncio.sleep(3)  # Simulate work
    research_context = "Based on the web search results"
    if pdf_results:
        research_context += " and PDF analysis"
    research_result = f"Research findings on {task_description}:\n\n{research_context}, the key information includes...\n\n[Detailed research would be here in a real implementation]"
    if callback:
        await callback.on_agent_finish("Research Agent", research_result)
    
    # Simulate Analysis Agent
    if callback:
        await callback.on_agent_start("Analysis Agent", f"Analyzing research on: {task_description}")
    await asyncio.sleep(2)  # Simulate work
    analysis_result = f"Analysis of {task_description}:\n\nThe research reveals several important patterns and insights...\n\n[Detailed analysis would be here in a real implementation]"
    if callback:
        await callback.on_agent_finish("Analysis Agent", analysis_result)
    
    # Simulate Writer Agent
    if callback:
        await callback.on_agent_start("Writer Agent", f"Writing content about: {task_description}")
    await asyncio.sleep(3)  # Simulate work
    writing_result = f"Written content on {task_description}:\n\n[Professional, comprehensive content would be here in a real implementation]"
    if callback:
        await callback.on_agent_finish("Writer Agent", writing_result)
    
    # Simulate Manager Agent
    if callback:
        await callback.on_agent_start("Manager Agent", f"Reviewing all information about: {task_description}")
    await asyncio.sleep(2)  # Simulate work
    final_result = f"Final report on {task_description}:\n\nThis is a comprehensive analysis based on web research, detailed investigation, and expert analysis. The key findings include...\n\n[Detailed report would be here in a real implementation]"
    if callback:
        await callback.on_agent_finish("Manager Agent", final_result)
    
    return final_result