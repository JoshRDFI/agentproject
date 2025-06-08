import argparse
import os
import uuid
import requests
from typing import Dict, List, Set, Any
from crew_setup import create_crew, run_crew
from check_crewai_version import check_crewai_version

# For CLI mode
def run_cli():
    """Run the application in CLI mode."""
    print("CrewAI Multi-Agent System - CLI Mode")
    print("==================================")
    
    # Check if Ollama server is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("Ollama server is running. Available models:")
            models = response.json().get("models", [])
            for model in models:
                print(f"- {model['name']}")
        else:
            print("Ollama server is running but returned an unexpected response.")
    except requests.exceptions.ConnectionError:
        print("Warning: Could not connect to Ollama server at http://localhost:11434.")
        print("Make sure Ollama is running before proceeding.")
        proceed = input("Do you want to proceed anyway? (y/n): ").lower()
        if proceed != 'y':
            return
    
    # Get topic from user
    topic = input("Enter a topic to research: ")
    
    # Ask if user wants to process PDF files
    process_pdfs = input("Do you want to process PDF files? (y/n): ").lower() == 'y'
    pdf_paths = []
    
    if process_pdfs:
        # Create uploads/pdfs directory if it doesn't exist
        os.makedirs("uploads/pdfs", exist_ok=True)
        
        # Get PDF file paths from user
        print("Enter the paths to the PDF files (one per line, empty line to finish):")
        while True:
            pdf_path = input("PDF path: ")
            if not pdf_path:
                break
            if os.path.exists(pdf_path):
                # Copy the file to uploads/pdfs
                filename = os.path.basename(pdf_path)
                destination = os.path.join("uploads/pdfs", filename)
                with open(pdf_path, "rb") as src, open(destination, "wb") as dst:
                    dst.write(src.read())
                pdf_paths.append(destination)
            else:
                print(f"File not found: {pdf_path}")
    
    # Generate a task ID
    task_id = str(uuid.uuid4())
    
    # Create and run the crew
    print(f"\nCreating crew for task {task_id}...")
    crew = create_crew(task_id, topic, pdf_paths)
    
    print("\nRunning crew...")
    result = run_crew(crew, task_id)
    
    print("\nResult:")
    print("=======\n")
    print(result)

# For web mode (import and run the FastAPI app)
def run_web():
    """Run the application in web mode."""
    try:
        from web_interface.web_main import app
        import uvicorn
        print("Starting web interface...")
        uvicorn.run(app, host="localhost", port=8088)
    except ImportError:
        print("Error: FastAPI or uvicorn not installed. Please install them with:")
        print("pip install fastapi uvicorn")

# Main entry point
if __name__ == "__main__":
    # Check crewai version
    if not check_crewai_version():
        print("Please upgrade crewai and try again.")
        exit(1)
        
    parser = argparse.ArgumentParser(description="CrewAI Multi-Agent System")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    else:
        run_web()