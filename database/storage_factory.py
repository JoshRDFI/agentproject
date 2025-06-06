from typing import Optional, Union
from .json_storage import JSONStorage
from .postgres_storage import PostgresStorage

class StorageFactory:
    """Factory for creating storage instances based on configuration."""
    
    @staticmethod
    def get_storage(storage_type: str = "json", **kwargs) -> Union[JSONStorage, PostgresStorage]:
        """Get a storage instance based on the specified type.
        
        Args:
            storage_type: Type of storage to use ("json" or "postgres")
            **kwargs: Additional arguments to pass to the storage constructor
            
        Returns:
            Storage instance
        """
        if storage_type.lower() == "json":
            return JSONStorage(**kwargs)
        elif storage_type.lower() == "postgres":
            return PostgresStorage(**kwargs)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")

# Default storage instance
default_storage = StorageFactory.get_storage("json")