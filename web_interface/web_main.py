from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
import asyncio
import requests
from typing import Dict, List, Set, Any, Optional
import json
from datetime import datetime

# Import crew setup
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crew_setup import create_crew, run_crew
from check_crewai_version import check_crewai_version

# Check crewai version
if not check_crewai_version():
    print("Please upgrade crewai and try again.")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(title="CrewAI Multi-Agent System")

# Check if Ollama server is running
try:
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        print("Ollama server is running. Available models:")
        models = response.json().get("models", [])
        model_names = [model['name'] for model in models]
        for model in models:
            print(f"- {model['name']}")
            
        # Check if required models are available
        required_models = ["llama3.2", "deepseek-r1", "qwen2.5vl"]
        missing_models = [model for model in required_models if not any(model in m for m in model_names)]
        if missing_models:
            print("\nWarning: The following required models are not available in Ollama:")
            for model in missing_models:
                print(f"- {model}")
            print("\nYou can pull these models using the following commands:")
            for model in missing_models:
                print(f"ollama pull {model}")
    else:
        print("Ollama server is running but returned an unexpected response.")
except requests.exceptions.ConnectionError:
    print("Warning: Could not connect to Ollama server at http://localhost:11434.")
    print("Make sure Ollama is running for the agents to work properly.")

# Mount static files
app.mount("/static", StaticFiles(directory="web_interface/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="web_interface/templates")

# Store WebSocket connections and task information
connections: Dict[str, Set[WebSocket]] = {}
tasks: Dict[str, Dict] = {}
agent_interactions: Dict[str, List[Dict]] = {}

# Create uploads directories if they don't exist
os.makedirs("uploads/pdfs", exist_ok=True)
os.makedirs("uploads/json", exist_ok=True)

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Render the index page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit-task")
async def submit_task(topic: str = Form(...), files: List[UploadFile] = File([])):
    """Submit a task for processing.
    
    Args:
        topic: The topic to research
        files: Optional list of PDF files to process
        
    Returns:
        JSON response with task ID and status
    """
    # Generate a task ID
    task_id = str(uuid.uuid4())
    
    # Save uploaded files
    pdf_paths = []
    for file in files:
        if file.filename.lower().endswith(".pdf"):
            file_path = os.path.join("uploads/pdfs", f"{task_id}_{file.filename}")
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            pdf_paths.append(file_path)
    
    # Store task information
    tasks[task_id] = {
        "id": task_id,
        "topic": topic,
        "pdf_paths": pdf_paths,
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "result": None
    }
    
    # Start task processing in the background
    asyncio.create_task(process_task(task_id, topic, pdf_paths))
    
    return {"task_id": task_id, "status": "pending"}

@app.get("/task/{task_id}")
async def get_task(task_id: str):
    """Get task information.
    
    Args:
        task_id: The ID of the task
        
    Returns:
        JSON response with task information
    """
    if task_id in tasks:
        return tasks[task_id]
    return JSONResponse(status_code=404, content={"message": "Task not found"})

@app.get("/tasks")
async def get_tasks():
    """Get all tasks.
    
    Returns:
        JSON response with all tasks
    """
    return list(tasks.values())

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time updates.
    
    Args:
        websocket: The WebSocket connection
        task_id: The ID of the task
    """
    await websocket.accept()
    
    # Add connection to the task's connections
    if task_id not in connections:
        connections[task_id] = set()
    connections[task_id].add(websocket)
    
    # Send task information if available
    if task_id in tasks:
        await websocket.send_json({"type": "task_info", "task": tasks[task_id]})
    
    try:
        # Keep the connection open
        while True:
            # Wait for messages (not used for now, but required to keep the connection open)
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Remove connection when disconnected
        if task_id in connections and websocket in connections[task_id]:
            connections[task_id].remove(websocket)

async def process_task(task_id: str, topic: str, pdf_paths: List[str]):
    """Process a task in the background.
    
    Args:
        task_id: The ID of the task
        topic: The topic to research
        pdf_paths: List of paths to PDF files to process
    """
    # Update task status
    tasks[task_id]["status"] = "processing"
    
    try:
        # Initialize agent_interactions for this task
        if task_id not in agent_interactions:
            agent_interactions[task_id] = []
        
        # Create the crew
        print(f"Creating crew for task {task_id} on topic: {topic}")
        crew = create_crew(task_id, topic, pdf_paths)
        print(f"Crew created with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
        
        # Run the crew in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: run_crew(crew, task_id, connections, agent_interactions))
        
        # Update task status and result
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = result
        tasks[task_id]["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Notify connected clients
        if task_id in connections:
            for connection in connections[task_id]:
                try:
                    await connection.send_json({
                        "type": "task_completed",
                        "task_id": task_id,
                        "result": result
                    })
                except Exception as e:
                    print(f"Error sending completion notification: {str(e)}")
    except Exception as e:
        error_message = f"Error processing task {task_id}: {str(e)}"
        print(error_message)
        import traceback
        print(traceback.format_exc())
        
        # Update task status to error
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = error_message
        
        # Notify connected clients of the error
        if task_id in connections:
            for connection in connections[task_id]:
                try:
                    await connection.send_json({
                        "type": "task_error",
                        "task_id": task_id,
                        "error": error_message
                    })
                except Exception:
                    pass