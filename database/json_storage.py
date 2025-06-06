import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class JSONStorage:
    """A simple JSON-based storage system for PDF extraction results."""
    
    def __init__(self, storage_dir: str = "uploads/json"):
        """Initialize the JSON storage.
        
        Args:
            storage_dir: Directory to store JSON files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        # Create an index file if it doesn't exist
        self.index_path = os.path.join(storage_dir, "index.json")
        if not os.path.exists(self.index_path):
            with open(self.index_path, "w") as f:
                json.dump({"pdf_extractions": []}, f)
    
    def store_pdf_extraction(self, pdf_path: str, extraction_data: Dict[str, Any], task_id: Optional[str] = None) -> str:
        """Store PDF extraction data in a JSON file.
        
        Args:
            pdf_path: Path to the original PDF file
            extraction_data: Extracted data from the PDF
            task_id: Optional task ID to associate with the extraction
            
        Returns:
            ID of the stored extraction
        """
        # Generate a unique ID for the extraction
        extraction_id = f"pdf_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(pdf_path)}"
        
        # Create the extraction record
        extraction_record = {
            "id": extraction_id,
            "pdf_path": pdf_path,
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "data": extraction_data
        }
        
        # Save the extraction to a JSON file
        extraction_path = os.path.join(self.storage_dir, f"{extraction_id}.json")
        with open(extraction_path, "w") as f:
            json.dump(extraction_record, f, indent=2)
        
        # Update the index
        with open(self.index_path, "r") as f:
            index = json.load(f)
        
        index["pdf_extractions"].append({
            "id": extraction_id,
            "pdf_path": pdf_path,
            "task_id": task_id,
            "timestamp": extraction_record["timestamp"]
        })
        
        with open(self.index_path, "w") as f:
            json.dump(index, f, indent=2)
        
        return extraction_id
    
    def get_pdf_extraction(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        """Get PDF extraction data by ID.
        
        Args:
            extraction_id: ID of the extraction to retrieve
            
        Returns:
            Extraction record or None if not found
        """
        extraction_path = os.path.join(self.storage_dir, f"{extraction_id}.json")
        if not os.path.exists(extraction_path):
            return None
        
        with open(extraction_path, "r") as f:
            return json.load(f)
    
    def get_pdf_extractions_by_task(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all PDF extractions for a specific task.
        
        Args:
            task_id: Task ID to filter by
            
        Returns:
            List of extraction records
        """
        with open(self.index_path, "r") as f:
            index = json.load(f)
        
        extraction_ids = [extraction["id"] for extraction in index["pdf_extractions"] 
                         if extraction["task_id"] == task_id]
        
        extractions = []
        for extraction_id in extraction_ids:
            extraction = self.get_pdf_extraction(extraction_id)
            if extraction:
                extractions.append(extraction)
        
        return extractions
    
    def get_all_pdf_extractions(self) -> List[Dict[str, Any]]:
        """Get all PDF extractions.
        
        Returns:
            List of all extraction records
        """
        with open(self.index_path, "r") as f:
            index = json.load(f)
        
        extractions = []
        for extraction_info in index["pdf_extractions"]:
            extraction = self.get_pdf_extraction(extraction_info["id"])
            if extraction:
                extractions.append(extraction)
        
        return extractions