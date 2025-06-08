from crewai import Task
from typing import List, Optional, Dict, Any

def pdf_processing_task(pdf_paths: List[str], agent, query: Optional[str] = None) -> Task:
    """Creates a task for processing PDF files.
    
    Args:
        pdf_paths: List of paths to PDF files to process
        agent: The agent to assign this task to
        query: Optional query to focus the extraction on specific information
    
    Returns:
        A Task object for processing PDF files
    """
    description = f"Extract and analyze information from the following PDF files: {', '.join(pdf_paths)}"
    if query:
        description += f"\nFocus on extracting information related to: {query}"
    
    return Task(
        description=description,
        expected_output="A comprehensive summary of the key information extracted from the PDF files, including text, tables, and visual elements.",
        agent=agent
    )

def web_search_task(query: str, agent) -> Task:
    """Creates a task for searching the web.
    
    Args:
    query: The search query
    agent: The agent to assign this task to
    
    Returns:
    A Task object for searching the web
    """
    return Task(
        description=f"Search the web for information about: {query}",
        expected_output="A comprehensive summary of the most relevant and reliable information found on the web, with sources cited.",
        agent=agent
    )

def research_task(topic: str, agent, web_search_results: Optional[str] = None, pdf_analysis: Optional[str] = None) -> Task:
    """Creates a task for researching a topic.
    
    Args:
    topic: The topic to research
    agent: The agent to assign this task to
    Web Search_results: Optional results from web search
    pdf_analysis: Optional results from PDF analysis
    
    Returns:
    A Task object for researching a topic
    """
    description = f"Research the following topic: {topic}"

    if web_search_results:
        description += "\nUse the following web search results as a starting point:"
        description += f"\n{web_search_results}"

    if pdf_analysis:
        description += "\nIncorporate the following PDF analysis into your research:"
        description += f"\n{pdf_analysis}"
    
    return Task(
        description=description,
        expected_output="A detailed research report on the topic, synthesizing information from all available sources.",
        agent=agent
    )

def analysis_task(research_report: str, agent) -> Task:
    """ Creates a task for analyzing a research report.
    
    Args:
    research_report: The research report to analyze
    agent: The agent to assign this task to
    
    Returns:
    A Task object for analyzing a research report
    """
    return Task(
        description="Analyze the research report and identify key insights.",
        expected_output="A list of key insights and findings from the research.",
        agent=agent
    )

def writing_task(analysis: str, topic: str, agent) -> Task:
    """Creates a task for writing content based on analysis.
    
    Args:
    analysis: The analysis to base the writing on
    topic: The topic of the writing
    agent: The agent to assign this task to
    
    Returns:
    A Task object for writing content
    """
    return Task(
        description=f"Write a detailed article on the topic: {topic} based on the provided analysis.",
        expected_output="A well-structured and informative article.",
        agent=agent
    )

def management_task(content: str, topic: str, agent) -> Task:
    """Creates a task for managing and finalizing content.
    
    Args:
    content: The content to manage and finalize
    topic: The topic of the content
    agent: The agent to assign this task to
    
    Returns:
    A Task object for managing and finalizing content
    """
    return Task(
        description=f"Review, verify, and finalize the content on the topic: {topic}. Ensure accuracy and clarity.",
        expected_output="A final, polished version of the content ready for presentation.",
        agent=agent
    )