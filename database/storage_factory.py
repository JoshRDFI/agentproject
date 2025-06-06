from typing import Dict, Any, Optional, Union
import os
import json
from datetime import datetime

# Import storage implementations
try:
    from .json_storage import JSONStorage
    from .postgres_storage import PostgresStorage
except ImportError:
    # For testing or when imported from a different directory
    try:
        from json_storage import JSONStorage
        from postgres_storage import PostgresStorage
    except ImportError:
        # Define placeholder classes if imports fail
        class JSONStorage:
            def __init__(self, *args, **kwargs):
                pass
            
            def save(self, *args, **kwargs):
                pass
            
            def load(self, *args, **kwargs):
                pass
        
        class PostgresStorage:
            def __init__(self, *args, **kwargs):
                pass
            
            def save(self, *args, **kwargs):
                pass
            
            def load(self, *args, **kwargs):
                pass

class StorageFactory:
    """Factory for creating storage instances."""
    
    @staticmethod
    def create_storage(storage_type: str = "json", **kwargs) -> Union[JSONStorage, PostgresStorage]:
        """Create a storage instance of the specified type.
        
        Args:
            storage_type: The type of storage to create ("json" or "postgres")
            **kwargs: Additional arguments to pass to the storage constructor
            
        Returns:
            A storage instance of the specified type
        """
        if storage_type.lower() == "json":
            return JSONStorage(**kwargs)
        elif storage_type.lower() == "postgres":
            return PostgresStorage(**kwargs)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")

# Default storage instance
default_storage = StorageFactory.create_storage("json", storage_dir="uploads/json")