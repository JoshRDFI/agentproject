import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:
    # Define a placeholder class if psycopg2 is not installed
    class Json:
        def __init__(self, obj):
            self.obj = obj

class PostgresStorage:
    """PostgreSQL-based storage implementation."""
    
    def __init__(self, connection_string: Optional[str] = None, table_name: str = "pdf_extractions"):
        """Initialize the PostgreSQL storage.
        
        Args:
            connection_string: The PostgreSQL connection string
            table_name: The name of the table to store data in
        """
        self.connection_string = connection_string or os.environ.get("POSTGRES_CONNECTION_STRING")
        self.table_name = table_name
        
        # Create table if it doesn't exist
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """Create the table if it doesn't exist."""
        if not self.connection_string:
            print("PostgreSQL connection string not provided. Table creation skipped.")
            return
        
        try:
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Create table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id VARCHAR(255) PRIMARY KEY,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error creating table: {str(e)}")
    
    def save(self, data: Dict[str, Any], file_id: Optional[str] = None) -> str:
        """Save data to PostgreSQL.
        
        Args:
            data: The data to save
            file_id: Optional file ID to use as the primary key
            
        Returns:
            The ID of the saved record
        """
        if not self.connection_string:
            raise ValueError("PostgreSQL connection string not provided")
        
        # Generate a file ID if not provided
        if file_id is None:
            file_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Add metadata
        data["_metadata"] = {
            "id": file_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute(f"SELECT id FROM {self.table_name} WHERE id = %s", (file_id,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update existing record
                cursor.execute(
                    f"UPDATE {self.table_name} SET data = %s, updated_at = NOW() WHERE id = %s",
                    (Json(data), file_id)
                )
            else:
                # Insert new record
                cursor.execute(
                    f"INSERT INTO {self.table_name} (id, data, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())",
                    (file_id, Json(data))
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return file_id
        except Exception as e:
            raise Exception(f"Error saving to PostgreSQL: {str(e)}")
    
    def load(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Load data from PostgreSQL.
        
        Args:
            file_id: The ID of the record to load
            
        Returns:
            The loaded data, or None if the record doesn't exist
        """
        if not self.connection_string:
            raise ValueError("PostgreSQL connection string not provided")
        
        try:
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Query record
            cursor.execute(f"SELECT data FROM {self.table_name} WHERE id = %s", (file_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result is None:
                return None
            
            return result[0]
        except Exception as e:
            raise Exception(f"Error loading from PostgreSQL: {str(e)}")
    
    def list_files(self) -> List[str]:
        """List all records in the table.
        
        Returns:
            A list of record IDs
        """
        if not self.connection_string:
            raise ValueError("PostgreSQL connection string not provided")
        
        try:
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Query all IDs
            cursor.execute(f"SELECT id FROM {self.table_name} ORDER BY created_at DESC")
            result = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [row[0] for row in result]
        except Exception as e:
            raise Exception(f"Error listing records from PostgreSQL: {str(e)}")
    
    def delete(self, file_id: str) -> bool:
        """Delete a record from PostgreSQL.
        
        Args:
            file_id: The ID of the record to delete
            
        Returns:
            True if the record was deleted, False otherwise
        """
        if not self.connection_string:
            raise ValueError("PostgreSQL connection string not provided")
        
        try:
            conn = psycopg2.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Delete record
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (file_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return deleted
        except Exception as e:
            raise Exception(f"Error deleting from PostgreSQL: {str(e)}")