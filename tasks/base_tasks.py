from crewai import Task
from typing import List, Optional, Callable
from crewai.agent import Agent

# These are task definitions for different types of work

def PDFProcessingTask(agent: Agent, pdf_paths: List[str], context: Optional[str] = None) -> Task:
    """Creates a PDF processing task for extracting information from PDF files."""
    pdf_paths_str = "\n".join([f"- {path}" for path in pdf_paths])
    return Task(
        description=f"Extract and analyze information from the following PDF files:\n{pdf_paths_str}\n\nContext: {context if context else 'No additional context provided.'}",
        agent=agent,
        expected_output="A comprehensive report with extracted information from the PDF files, including key content, insights, and relevant data."
    )

def WebSearchTask(agent: Agent, query: str, context: Optional[str] = None) -> Task:
    """Creates a web search task for finding information on the internet."""
    return Task(
        description=f"Search the web for information about: {query}\n\nContext: {context if context else 'No additional context provided.'}",
        agent=agent,
        expected_output="A comprehensive report with relevant information from the web, including sources, key findings, and up-to-date data."
    )

def ResearchTask(agent: Agent, topic: str, context: Optional[str] = None, web_search_results: Optional[str] = None, pdf_results: Optional[str] = None) -> Task:
    """Creates a research task for analyzing and synthesizing information."""
    return Task(
        description=f"Research and synthesize information on: {topic}\n\nContext: {context if context else 'No additional context provided.'}\n\n"
                   f"Web Search Results: {web_search_results if web_search_results else 'No web search results provided.'}\n\n"
                   f"PDF Analysis Results: {pdf_results if pdf_results else 'No PDF analysis results provided.'}",
        agent=agent,
        expected_output="A comprehensive research report with synthesized information, key findings, and insights."
    )

def AnalysisTask(agent: Agent, data: str, question: str, research_results: Optional[str] = None) -> Task:
    """Creates an analysis task for analyzing data and answering a question."""
    data_source = data
    if research_results:
        data_source = research_results
    
    return Task(
        description=f"Analyze the following information and answer the question:\n\nInformation: {data_source}\n\nQuestion: {question}",
        agent=agent,
        expected_output="A detailed analysis with insights, patterns, and a clear answer to the question."
    )

def WritingTask(agent: Agent, topic: str, style: str, length: str, research_results: Optional[str] = None) -> Task:
    """Creates a writing task for producing content on a topic."""
    return Task(
        description=f"Write content on the following topic: {topic}\n\nStyle: {style}\nLength: {length}\n\nResearch Results: {research_results if research_results else 'No research results provided.'}",
        agent=agent,
        expected_output=f"A well-written {length} piece in {style} style about {topic}."
    )

def ManagerTask(agent: Agent, topic: str, web_search_results: str, research_results: str, analysis_results: str, writing_results: str, pdf_results: Optional[str] = None) -> Task:
    """Creates a manager task for checking information accuracy and presenting a cohesive final result."""
    return Task(
        description=f"Review all the information gathered about {topic} and create a final, cohesive report.\n\n"
                   f"Web Search Results:\n{web_search_results}\n\n"
                   f"PDF Analysis Results:\n{pdf_results if pdf_results else 'No PDF analysis results provided.'}\n\n"
                   f"Research Results:\n{research_results}\n\n"
                   f"Analysis Results:\n{analysis_results}\n\n"
                   f"Writing Results:\n{writing_results}",
        agent=agent,
        expected_output="A comprehensive, accurate, and well-organized final report that integrates all the information gathered, highlights key insights, and presents a cohesive narrative."
    )