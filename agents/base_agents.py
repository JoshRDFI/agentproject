import os
import traceback
from typing import List, Optional, Type

from crewai import Agent
from crewai.tools import BaseTool

# Set custom storage location for CrewAI memory
os.environ["CREWAI_STORAGE_DIR"] = "./storage"

# Custom DuckDuckGo search tool implementation
from langchain_community.tools import DuckDuckGoSearchRun

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for information using DuckDuckGo"

    def _run(self, query: str) -> str:
        duckduckgo_tool = DuckDuckGoSearchRun()
        response = duckduckgo_tool.invoke(query)
        return response


# Custom tool for PDF processing
class PDFProcessingTool(BaseTool):
    name: str = "pdf_processor"
    description: str = "Extracts and analyzes text and visual content from PDF files"
    
    def __init__(self):
        super().__init__()
        self._pdf_storage_path = "uploads/pdfs"
        # Check if required libraries are available
        try:
            import PyPDF2
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.available = True
        except ImportError as e:
            self.available = False
            print(f"PDF processing dependencies not available: {e}")
            print("Install with: pip install transformers accelerate PyPDF2")
    
    def _run(self, pdf_path: str, query: Optional[str] = None) -> str:
        """
        Process a PDF file and extract information using the qwen2.5vl model.
        
        Args:
            pdf_path: Path to the PDF file
            query: Optional query to focus the extraction on specific information
            
        Returns:
            Extracted information from the PDF
        """
        if not self.available:
            return ("PDF processing functionality is not available. \n"
                    "Install required dependencies first.")
        
        try:
            import os
            import PyPDF2
            from PIL import Image
            import io
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Check if the PDF exists
            full_path = pdf_path
            if not os.path.isabs(pdf_path):
                full_path = os.path.join(self._pdf_storage_path, pdf_path)
                
            if not os.path.exists(full_path):
                return f"Error: PDF file not found at {full_path}"
            
            # Extract text from PDF
            with open(full_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                # For simplicity, we'll process just the first few pages
                max_pages = min(5, num_pages)  # Limit to first 5 pages for demo
                
                # Load the model and tokenizer
                model_name = "Qwen/Qwen2.5-VL-7B"
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    trust_remote_code=True
                )
                
                # Process the PDF with the model
                results = []
                
                for i in range(max_pages):
                    # Extract text from page
                    page = reader.pages[i]
                    text = page.extract_text()
                    
                    # Prepare prompt based on whether a query was provided
                    if query:
                        prompt = f"This is page {i+1} of a PDF document. Please answer the following question based on this page: {query}\n\nPage content: {text}"
                    else:
                        prompt = f"This is page {i+1} of a PDF document. Please extract and summarize the key information from this page.\n\nPage content: {text}"
                    
                    # Generate response
                    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
                    generated_ids = model.generate(
                        inputs.input_ids,
                        max_new_tokens=500,
                        do_sample=True,
                        temperature=0.7
                    )
                    response = tokenizer.decode(generated_ids[0][inputs.input_ids.shape[1]:])
                    results.append(f"Page {i+1} analysis:\n{response}\n")
                
                # Combine results
                combined_result = f"Analysis of PDF: {os.path.basename(full_path)}\n\n"
                combined_result += "\n".join(results)
                
                # Add a summary if there was a specific query
                if query:
                    summary_prompt = f"Based on the PDF document, please provide a concise answer to: {query}"
                    inputs = tokenizer(summary_prompt, return_tensors="pt").to(model.device)
                    generated_ids = model.generate(
                        inputs.input_ids,
                        max_new_tokens=300,
                        do_sample=True,
                        temperature=0.7
                    )
                    summary = tokenizer.decode(generated_ids[0][inputs.input_ids.shape[1]:])
                    combined_result += f"\n\nSummary answer to query '{query}':\n{summary}"
                
                return combined_result
                
        except Exception as e:
            return f"Error processing PDF: {str(e)}\n{traceback.format_exc()}"

# These are agent definitions with specific roles and capabilities

def PDFProcessingAgent(llm) -> Agent:
    """Creates a PDF processing agent that can extract and analyze information from PDF files."""
    return Agent(
        role="PDF Document Specialist",
        goal="Extract and analyze information from PDF documents accurately and comprehensively",
        backstory="You are an expert in document analysis with a specialty in PDF processing. You can extract text, understand tables, and interpret visual elements in documents.",
        verbose=True,
        llm=llm,
        tools=[PDFProcessingTool()],
        allow_delegation=False,
        memory=True  # Enable memory for context retention
    )

def WebSearchAgent(llm) -> Agent:
    """Creates a web search agent that can find information on the internet."""
    return Agent(
        role="Web Search Specialist",
        goal="Find accurate and up-to-date information on the web about the given topic",
        backstory="You are an expert web researcher with a talent for finding the most relevant and reliable information online.",
        verbose=True,
        llm=llm,
        tools=[WebSearchTool()],
        allow_delegation=False,
        memory=True  # Enable memory for context retention
    )

def ResearchAgent(llm) -> Agent:
    """Creates a research agent that can analyze and synthesize information."""
    return Agent(
        role="Research Specialist",
        goal="Analyze and synthesize information to create a comprehensive research report",
        backstory="You are an expert researcher with a talent for organizing information and identifying key insights.",
        verbose=True,
        llm=llm,
        allow_delegation=True,
        memory=True  # Enable memory for context retention
    )

def AnalysisAgent(llm) -> Agent:
    """Creates an analysis agent that can analyze information and draw insights."""
    return Agent(
        role="Data Analyst",
        goal="Analyze information and extract meaningful insights and patterns",
        backstory="You are a skilled analyst with a background in data science and critical thinking. You excel at identifying patterns and drawing conclusions from complex information.",
        verbose=True,
        llm=llm,
        allow_delegation=True,
        memory=True  # Enable memory for context retention
    )

def WriterAgent(llm) -> Agent:
    """Creates a writer agent that can produce well-written content."""
    return Agent(
        role="Content Writer",
        goal="Create clear, engaging, and informative content based on research and analysis",
        backstory="You are a talented writer with experience in various styles and formats. You can transform complex information into accessible and engaging content.",
        verbose=True,
        llm=llm,
        allow_delegation=True,
        memory=True  # Enable memory for context retention
    )

def ManagerAgent(llm) -> Agent:
    """Creates a manager agent that checks information for accuracy and presents a cohesive final result."""
    return Agent(
        role="Project Manager",
        goal="Verify the accuracy of information and present a cohesive, well-organized final result",
        backstory="You are an experienced project manager with a keen eye for detail and a talent for organizing information. You excel at identifying inconsistencies and ensuring the final product meets high standards of quality and accuracy.",
        verbose=True,
        llm=llm,
        allow_delegation=False,
        memory=True  # Enable memory for context retention
    )