from crewai.callbacks import CrewCallbackHandler
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
import asyncio

class AgentInteractionCallback(CrewCallbackHandler):
    """Custom callback handler for tracking agent interactions.
    
    This callback handler captures agent start, finish, and error events,
    and broadcasts them to connected WebSocket clients.
    """
    
    def __init__(self, task_id: str, connections: Dict[str, Set], agent_interactions: Dict[str, List[Dict]]):
        """Initialize the callback handler.
        
        Args:
            task_id: The ID of the task being processed
            connections: Dictionary mapping task IDs to sets of WebSocket connections
            agent_interactions: Dictionary mapping task IDs to lists of agent interactions
        """
        self.task_id = task_id
        self.connections = connections
        self.agent_interactions = agent_interactions
    
    async def on_agent_start(self, agent: Any, task: Any, inputs: Dict[str, Any]):
        """Called when an agent starts processing a task.
        
        Args:
            agent: The agent that started processing
            task: The task being processed
            inputs: The inputs to the task
        """
        interaction = {
            "type": "agent_start",
            "agent": agent.role,
            "task": task.description,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_agent_finish(self, agent: Any, task: Any, output: str):
        """Called when an agent finishes processing a task.
        
        Args:
            agent: The agent that finished processing
            task: The task that was processed
            output: The output of the task
        """
        interaction = {
            "type": "agent_finish",
            "agent": agent.role,
            "output": output,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_agent_error(self, agent: Any, task: Any, error: Exception):
        """Called when an agent encounters an error while processing a task.
        
        Args:
            agent: The agent that encountered the error
            task: The task being processed
            error: The error that occurred
        """
        interaction = {
            "type": "agent_error",
            "agent": agent.role,
            "error": str(error),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_crew_start(self, crew: Any, inputs: Dict[str, Any]):
        """Called when a crew starts processing.
        
        Args:
            crew: The crew that started processing
            inputs: The inputs to the crew
        """
        interaction = {
            "type": "crew_start",
            "crew": crew.name if hasattr(crew, "name") else "Crew",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_crew_finish(self, crew: Any, output: Any):
        """Called when a crew finishes processing.
        
        Args:
            crew: The crew that finished processing
            output: The output of the crew
        """
        interaction = {
            "type": "crew_finish",
            "crew": crew.name if hasattr(crew, "name") else "Crew",
            "output": str(output),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_crew_error(self, crew: Any, error: Exception):
        """Called when a crew encounters an error.
        
        Args:
            crew: The crew that encountered the error
            error: The error that occurred
        """
        interaction = {
            "type": "crew_error",
            "crew": crew.name if hasattr(crew, "name") else "Crew",
            "error": str(error),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_subtask_start(self, agent: Any, task: Any, inputs: Dict[str, Any]):
        """Called when an agent starts processing a subtask.
        
        Args:
            agent: The agent that started processing
            task: The subtask being processed
            inputs: The inputs to the subtask
        """
        interaction = {
            "type": "subtask_start",
            "agent": agent.role,
            "task": task.description,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_subtask_finish(self, agent: Any, task: Any, output: str):
        """Called when an agent finishes processing a subtask.
        
        Args:
            agent: The agent that finished processing
            task: The subtask that was processed
            output: The output of the subtask
        """
        interaction = {
            "type": "subtask_finish",
            "agent": agent.role,
            "output": output,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def on_subtask_error(self, agent: Any, task: Any, error: Exception):
        """Called when an agent encounters an error while processing a subtask.
        
        Args:
            agent: The agent that encountered the error
            task: The subtask being processed
            error: The error that occurred
        """
        interaction = {
            "type": "subtask_error",
            "agent": agent.role,
            "error": str(error),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        await self._broadcast(interaction)
    
    async def _broadcast(self, message: Dict):
        """Broadcast a message to all connected WebSocket clients for this task.
        
        Args:
            message: The message to broadcast
        """
        if self.task_id in self.connections:
            for connection in self.connections[self.task_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # If sending fails, we'll just continue with the other connections
                    pass