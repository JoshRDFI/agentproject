import argparse
import os
import uuid
from typing import Dict, List, Set, Any
from crew_setup import create_crew, run_crew

# For CLI mode
def run_cli():
    """Run the application in CLI mode."""
    print("CrewAI Multi-Agent System - CLI Mode")
    print("==================================")
    
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
    crew = create_crew(task_id, topic, pdf_paths, callback_enabled=False)
    
    print("\nRunning crew...")
    result = run_crew(crew, task_id)
    
    print("\nResult:")
    print("=======\n")
    print(result)

# For web mode (import and run the FastAPI app)
def run_web():
    """Run the application in web mode."""
    try:
        from web_interface.main import app
        import uvicorn
        print("Starting web interface...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        print("Error: FastAPI or uvicorn not installed. Please install them with:")
        print("pip install fastapi uvicorn")

# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CrewAI Multi-Agent System")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    else:
        run_web()