from fastapi import FastAPI, Request, Form, BackgroundTasks, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import sys
import uuid
import json
import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime

# Add the parent directory to the path so we can import the crew_setup module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crew_setup import run_crew_async
from database.storage_factory import default_storage

app = FastAPI(title="CrewAI Web Interface")

# Create templates directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), "templates"), exist_ok=True)

# Create static directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), "static"), exist_ok=True)

# Create uploads directory if it doesn't exist
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(os.path.join(uploads_dir, "pdfs"), exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Set up templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Store tasks and their results
tasks: Dict[str, Dict] = {}

# Store WebSocket connections for each task
connections: Dict[str, Set[WebSocket]] = {}

# Store agent interactions for each task
agent_interactions: Dict[str, List[Dict]] = {}

# Store uploaded files for each task
uploaded_files: Dict[str, List[Dict]] = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

@app.post("/submit_task", response_class=HTMLResponse)
async def submit_task(
    request: Request, 
    background_tasks: BackgroundTasks, 
    task_description: str = Form(...),
    files: List[UploadFile] = File(None)
):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "description": task_description,
        "status": "running",
        "result": None,
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Initialize connections and agent interactions for this task
    connections[task_id] = set()
    agent_interactions[task_id] = []
    uploaded_files[task_id] = []
    
    # Process uploaded files
    pdf_paths = []
    if files:
        for file in files:
            if file.filename:
                # Save the file
                file_path = os.path.join(uploads_dir, "pdfs", f"{task_id}_{file.filename}")
                with open(file_path, "wb") as f:
                    f.write(await file.read())
                
                # Store file info
                file_info = {
                    "filename": file.filename,
                    "path": file_path,
                    "content_type": file.content_type,
                    "size": os.path.getsize(file_path)
                }
                uploaded_files[task_id].append(file_info)
                
                # Add to PDF paths if it's a PDF
                if file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
                    pdf_paths.append(file_path)
    
    background_tasks.add_task(process_task, task_id, task_description, pdf_paths)
    
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks, "message": "Task submitted successfully!"})

@app.get("/task/{task_id}", response_class=HTMLResponse)
async def get_task(request: Request, task_id: str):
    if task_id not in tasks:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Task not found"})
    
    return templates.TemplateResponse("task.html", {
        "request": request, 
        "task": tasks[task_id], 
        "task_id": task_id,
        "agent_interactions": agent_interactions.get(task_id, []),
        "uploaded_files": uploaded_files.get(task_id, [])
    })

@app.post("/clarify/{task_id}", response_class=HTMLResponse)
async def clarify_task(
    request: Request, 
    task_id: str, 
    clarification: str = Form(...),
    files: List[UploadFile] = File(None)
):
    if task_id not in tasks:
        return templates.TemplateResponse("error.html", {"request": request, "error": "Task not found"})
    
    # Add the clarification to the task
    if "clarifications" not in tasks[task_id]:
        tasks[task_id]["clarifications"] = []
    
    tasks[task_id]["clarifications"].append(clarification)
    
    # Update the task description with the clarification
    updated_description = f"{tasks[task_id]['description']}\n\nClarification: {clarification}"
    
    # Process additional uploaded files
    pdf_paths = []
    if files:
        for file in files:
            if file.filename:
                # Save the file
                file_path = os.path.join(uploads_dir, "pdfs", f"{task_id}_clarification_{file.filename}")
                with open(file_path, "wb") as f:
                    f.write(await file.read())
                
                # Store file info
                file_info = {
                    "filename": file.filename,
                    "path": file_path,
                    "content_type": file.content_type,
                    "size": os.path.getsize(file_path),
                    "clarification": True
                }
                uploaded_files[task_id].append(file_info)
                
                # Add to PDF paths if it's a PDF
                if file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
                    pdf_paths.append(file_path)
    
    # Get existing PDF paths
    existing_pdf_paths = [file_info["path"] for file_info in uploaded_files[task_id] 
                         if file_info["path"].endswith(".pdf") and "clarification" not in file_info]
    
    # Combine existing and new PDF paths
    all_pdf_paths = existing_pdf_paths + pdf_paths
    
    # Reset the task status and result
    tasks[task_id]["status"] = "running"
    tasks[task_id]["result"] = None
    
    # Clear previous agent interactions
    agent_interactions[task_id] = []
    
    # Run the task again with the updated description
    background_tasks = BackgroundTasks()
    background_tasks.add_task(process_task, task_id, updated_description, all_pdf_paths)
    
    return templates.TemplateResponse("task.html", {
        "request": request, 
        "task": tasks[task_id], 
        "task_id": task_id, 
        "message": "Clarification submitted!",
        "agent_interactions": agent_interactions.get(task_id, []),
        "uploaded_files": uploaded_files.get(task_id, [])
    })

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    
    if task_id not in connections:
        connections[task_id] = set()
    
    connections[task_id].add(websocket)
    
    try:
        # Send existing agent interactions to the new connection
        if task_id in agent_interactions:
            for interaction in agent_interactions[task_id]:
                await websocket.send_json(interaction)
        
        # Keep the connection open
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        connections[task_id].remove(websocket)

# Custom CrewAI callback to capture agent interactions
class AgentInteractionCallback:
    def __init__(self, task_id: str):
        self.task_id = task_id
    
    async def on_agent_start(self, agent_name: str, task_description: str):
        interaction = {
            "type": "agent_start",
            "agent": agent_name,
            "task": task_description,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_agent_finish(self, agent_name: str, output: str):
        interaction = {
            "type": "agent_finish",
            "agent": agent_name,
            "output": output,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_agent_error(self, agent_name: str, error: str):
        interaction = {
            "type": "agent_error",
            "agent": agent_name,
            "error": error,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def _broadcast(self, message: Dict):
        if self.task_id in connections:
            for connection in connections[self.task_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

async def process_task(task_id: str, task_description: str, pdf_paths: List[str] = None):
    try:
        # Create a callback for this task
        callback = AgentInteractionCallback(task_id)
        
        # Run the crew on the task with the callback
        # Note: In a real implementation, you would need to modify run_crew to accept and use the callback
        result = await run_crew_async(task_description, pdf_paths, callback)
        
        # Update the task with the result
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = result
        tasks[task_id]["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Notify all connections that the task is complete
        if task_id in connections:
            completion_message = {
                "type": "task_complete",
                "task_id": task_id,
                "result": result
            }
            for connection in connections[task_id]:
                await connection.send_json(completion_message)
    except Exception as e:
        # Update the task with the error
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = f"Error: {str(e)}"
        tasks[task_id]["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Notify all connections that the task failed
        if task_id in connections:
            error_message = {
                "type": "task_error",
                "task_id": task_id,
                "error": str(e)
            }
            for connection in connections[task_id]:
                await connection.send_json(error_message)