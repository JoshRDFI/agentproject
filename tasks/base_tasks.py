from crewai import Task
from typing import List, Optional, Dict, Any

def pdf_processing_task(pdf_paths: List[str], query: Optional[str] = None) -> Task:
    """Creates a task for processing PDF files.
    
    Args:
        pdf_paths: List of paths to PDF files to process
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
        context={
            "pdf_paths": pdf_paths,
            "query": query
        }
    )

def web_search_task(query: str) -> Task:
    """Creates a task for searching the web.
    
    Args:
        query: The search query
        
    Returns:
        A Task object for searching the web
    """
    return Task(
        description=f"Search the web for information about: {query}",
        expected_output="A comprehensive summary of the most relevant and reliable information found on the web, with sources cited.",
        context=[query]
    )

def research_task(topic: str, web_search_results: Optional[str] = None, pdf_analysis: Optional[str] = None) -> Task:
    """Creates a task for researching a topic.
    
    Args:
        topic: The topic to research
        web_search_results: Optional results from web search
        pdf_analysis: Optional results from PDF analysis
        
    Returns:
        A Task object for researching a topic
    """
    description = f"Research the following topic: {topic}"
    context = {"topic": topic}
    
    if web_search_results:
        description += "\nUse the following web search results as a starting point:"
        description += f"\n{web_search_results}"
        context["web_search_results"] = web_search_results
    
    if pdf_analysis:
        description += "\nIncorporate the following PDF analysis into your research:"
        description += f"\n{pdf_analysis}"
        context["pdf_analysis"] = pdf_analysis
    
    return Task(
        description=description,
        expected_output="A comprehensive research report that synthesizes information from all available sources and identifies key insights.",
        context=context
    )

def analysis_task(research_report: str) -> Task:
    """Creates a task for analyzing a research report.
    
    Args:
        research_report: The research report to analyze
        
    Returns:
        A Task object for analyzing a research report
    """
    return Task(
        description="Analyze the following research report and identify key patterns, insights, and implications:",
        expected_output="A detailed analysis that identifies patterns, insights, and implications from the research report.",
        context={
            "research_report": research_report
        }
    )

def writing_task(analysis: str, topic: str) -> Task:
    """Creates a task for writing content based on analysis.
    
    Args:
        analysis: The analysis to base the writing on
        topic: The topic of the writing
        
    Returns:
        A Task object for writing content
    """
    return Task(
        description=f"Create clear, engaging, and informative content on the topic of {topic} based on the following analysis:",
        expected_output="Well-written, engaging, and informative content that effectively communicates the key insights from the analysis.",
        context={
            "analysis": analysis,
            "topic": topic
        }
    )

def management_task(content: str, topic: str) -> Task:
    """Creates a task for managing and finalizing content.
    
    Args:
        content: The content to manage and finalize
        topic: The topic of the content
        
    Returns:
        A Task object for managing and finalizing content
    """
    return Task(
        description=f"Review, verify, and finalize the following content on the topic of {topic}:",
        expected_output="A final, polished version of the content that is accurate, well-organized, and meets high standards of quality.",
        context={
            "content": content,
            "topic": topic
        }
    )