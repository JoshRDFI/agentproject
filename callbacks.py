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
        super().__init__()
        self.task_id = task_id
        self.connections = connections
        self.agent_interactions = agent_interactions
    
    async def on_agent_start(self, agent: Any, task: Any, inputs: Dict[str, Any]) -> None:
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
        
    def on_agent_start_sync(self, agent: Any, task: Any, inputs: Dict[str, Any]) -> None:
        """Synchronous version of on_agent_start."""
        interaction = {
            "type": "agent_start",
            "agent": agent.role,
            "task": task.description,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
    
    async def on_agent_finish(self, agent: Any, task: Any, output: str) -> None:
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
        
    def on_agent_finish_sync(self, agent: Any, task: Any, output: str) -> None:
        """Synchronous version of on_agent_finish."""
        interaction = {
            "type": "agent_finish",
            "agent": agent.role,
            "output": output,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
    
    async def on_agent_error(self, agent: Any, task: Any, error: Exception) -> None:
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
        
    def on_agent_error_sync(self, agent: Any, task: Any, error: Exception) -> None:
        """Synchronous version of on_agent_error."""
        interaction = {
            "type": "agent_error",
            "agent": agent.role,
            "error": str(error),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
    
    async def on_crew_start(self, crew: Any, inputs: Dict[str, Any]) -> None:
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
        
    def on_crew_start_sync(self, crew: Any, inputs: Dict[str, Any]) -> None:
        """Synchronous version of on_crew_start."""
        interaction = {
            "type": "crew_start",
            "crew": crew.name if hasattr(crew, "name") else "Crew",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
    
    async def on_crew_finish(self, crew: Any, output: Any) -> None:
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
        
    def on_crew_finish_sync(self, crew: Any, output: Any) -> None:
        """Synchronous version of on_crew_finish."""
        interaction = {
            "type": "crew_finish",
            "crew": crew.name if hasattr(crew, "name") else "Crew",
            "output": str(output),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
    
    async def on_crew_error(self, crew: Any, error: Exception) -> None:
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
        
    def on_crew_error_sync(self, crew: Any, error: Exception) -> None:
        """Synchronous version of on_crew_error."""
        interaction = {
            "type": "crew_error",
            "crew": crew.name if hasattr(crew, "name") else "Crew",
            "error": str(error),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
    
    async def on_subtask_start(self, agent: Any, task: Any, inputs: Dict[str, Any]) -> None:
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
        
    def on_subtask_start_sync(self, agent: Any, task: Any, inputs: Dict[str, Any]) -> None:
        """Synchronous version of on_subtask_start."""
        interaction = {
            "type": "subtask_start",
            "agent": agent.role,
            "task": task.description,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
    
    async def on_subtask_finish(self, agent: Any, task: Any, output: str) -> None:
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
        
    def on_subtask_finish_sync(self, agent: Any, task: Any, output: str) -> None:
        """Synchronous version of on_subtask_finish."""
        interaction = {
            "type": "subtask_finish",
            "agent": agent.role,
            "output": output,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
    
    async def on_subtask_error(self, agent: Any, task: Any, error: Exception) -> None:
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
        
    def on_subtask_error_sync(self, agent: Any, task: Any, error: Exception) -> None:
        """Synchronous version of on_subtask_error."""
        interaction = {
            "type": "subtask_error",
            "agent": agent.role,
            "error": str(error),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
    
    def on_task_complete(self, output: Any) -> None:
        """Called when a task is completed.
        
        Args:
            output: The output of the task
        """
        interaction = {
            "type": "task_complete",
            "output": str(output),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
            
    def on_step(self, agent: Any, step: str) -> None:
        """Called after each step in an agent's execution process.
        
        Args:
            agent: The agent that executed the step
            step: The step that was executed
        """
        interaction = {
            "type": "agent_step",
            "agent": agent.role if hasattr(agent, "role") else "Agent",
            "step": step,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.agent_interactions[self.task_id].append(interaction)
        # Create a new event loop for the async call if needed
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._broadcast(interaction))
            else:
                loop.run_until_complete(self._broadcast(interaction))
        except RuntimeError:
            # If no event loop is available in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._broadcast(interaction))
            loop.close()
            
    async def _broadcast(self, message: Dict) -> None:
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