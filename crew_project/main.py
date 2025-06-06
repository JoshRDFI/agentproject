import os
import sys
import asyncio

def run_web_interface():
    """Run the web interface."""
    # Add the web_interface directory to the path
    web_interface_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_interface")
    sys.path.append(web_interface_dir)
    
    # Import and run the web interface
    from web_interface.main import app
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

async def run_cli_async():
    """Run the CLI interface asynchronously."""
    from crew_setup import run_crew_async
    
    print("Welcome to the CrewAI Task Manager CLI!")
    print("Enter your task description below:")
    
    task_description = input("> ")
    
    print("\nProcessing your task...\n")
    
    result = await run_crew_async(task_description)
    
    print("\nTask Result:")
    print(result)

def run_cli():
    """Run the CLI interface."""
    asyncio.run(run_cli_async())

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the CrewAI Task Manager")
    parser.add_argument("--cli", action="store_true", help="Run the CLI interface instead of the web interface")
    
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    else:
        run_web_interface()