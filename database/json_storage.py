import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

class JSONStorage:
    """JSON-based storage implementation."""
    
    def __init__(self, storage_dir: str = "uploads/json"):
        """Initialize the JSON storage.
        
        Args:
            storage_dir: The directory to store JSON files in
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save(self, data: Dict[str, Any], file_id: Optional[str] = None) -> str:
        """Save data to a JSON file.
        
        Args:
            data: The data to save
            file_id: Optional file ID to use for the filename
            
        Returns:
            The ID of the saved file
        """
        # Generate a file ID if not provided
        if file_id is None:
            file_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Add metadata
        data["_metadata"] = {
            "id": file_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to file
        file_path = os.path.join(self.storage_dir, f"{file_id}.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return file_id
    
    def load(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Load data from a JSON file.
        
        Args:
            file_id: The ID of the file to load
            
        Returns:
            The loaded data, or None if the file doesn't exist
        """
        file_path = os.path.join(self.storage_dir, f"{file_id}.json")
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, "r") as f:
            return json.load(f)
    
    def list_files(self) -> List[str]:
        """List all JSON files in the storage directory.
        
        Returns:
            A list of file IDs
        """
        files = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                files.append(filename[:-5])  # Remove .json extension
        return files
    
    def delete(self, file_id: str) -> bool:
        """Delete a JSON file.
        
        Args:
            file_id: The ID of the file to delete
            
        Returns:
            True if the file was deleted, False otherwise
        """
        file_path = os.path.join(self.storage_dir, f"{file_id}.json")
        if not os.path.exists(file_path):
            return False
        
        os.remove(file_path)
        return True