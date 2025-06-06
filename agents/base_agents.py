from crewai import Agent
from typing import List, Optional
from crewai.tools import WebSearchTool

# Custom tool for PDF processing
class PDFProcessingTool:
    def __init__(self, pdf_storage_path: str = "uploads/pdfs"):
        self.pdf_storage_path = pdf_storage_path
        
    def name(self) -> str:
        return "pdf_processor"
        
    def description(self) -> str:
        return "Extracts and analyzes text and visual content from PDF files"
    
    def run(self, pdf_path: str, query: Optional[str] = None) -> str:
        """Process a PDF file and extract information.
        
        Args:
            pdf_path: Path to the PDF file
            query: Optional query to focus the extraction on specific information
            
        Returns:
            Extracted information from the PDF
        """
        # In a real implementation, this would use a PDF processing library
        # and the qwen2.5vl:7b model to extract information from the PDF
        # For now, we'll return a placeholder message
        return f"Extracted information from {pdf_path}: [PDF content would be processed here using qwen2.5vl:7b model]"

# These are agent definitions with specific roles and capabilities

def PDFProcessingAgent(llm_model: str = "qwen2.5vl:7b") -> Agent:
    """Creates a PDF processing agent that can extract and analyze information from PDF files."""
    return Agent(
        role="PDF Document Specialist",
        goal="Extract and analyze information from PDF documents accurately and comprehensively",
        backstory="You are an expert in document analysis with a specialty in PDF processing. You can extract text, understand tables, and interpret visual elements in documents.",
        verbose=True,
        llm=llm_model,
        tools=[PDFProcessingTool()],
        allow_delegation=False
    )

def WebSearchAgent(llm_model: str = "llama3") -> Agent:
    """Creates a web search agent that can find information on the internet."""
    return Agent(
        role="Web Search Specialist",
        goal="Find accurate and up-to-date information on the web about the given topic",
        backstory="You are an expert web researcher with a talent for finding the most relevant and reliable information online.",
        verbose=True,
        llm=llm_model,
        tools=[WebSearchTool()],
        allow_delegation=False
    )

def ResearchAgent(llm_model: str = "llama3") -> Agent:
    """Creates a research agent that can analyze and synthesize information."""
    return Agent(
        role="Research Specialist",
        goal="Analyze and synthesize information to create a comprehensive research report",
        backstory="You are an expert researcher with a talent for organizing information and identifying key insights.",
        verbose=True,
        llm=llm_model,
        allow_delegation=True
    )

def AnalysisAgent(llm_model: str = "llama3") -> Agent:
    """Creates an analysis agent that can analyze information and draw insights."""
    return Agent(
        role="Data Analyst",
        goal="Analyze information and extract meaningful insights and patterns",
        backstory="You are a skilled analyst with a background in data science and critical thinking. You excel at identifying patterns and drawing conclusions from complex information.",
        verbose=True,
        llm=llm_model,
        allow_delegation=True
    )

def WriterAgent(llm_model: str = "llama3") -> Agent:
    """Creates a writer agent that can produce well-written content."""
    return Agent(
        role="Content Writer",
        goal="Create clear, engaging, and informative content based on research and analysis",
        backstory="You are a talented writer with experience in various styles and formats. You can transform complex information into accessible and engaging content.",
        verbose=True,
        llm=llm_model,
        allow_delegation=True
    )

def ManagerAgent(llm_model: str = "llama3") -> Agent:
    """Creates a manager agent that checks information for accuracy and presents a cohesive final result."""
    return Agent(
        role="Project Manager",
        goal="Verify the accuracy of information and present a cohesive, well-organized final result",
        backstory="You are an experienced project manager with a keen eye for detail and a talent for organizing information. You excel at identifying inconsistencies and ensuring the final product meets high standards of quality and accuracy.",
        verbose=True,
        llm=llm_model,
        allow_delegation=False
    )