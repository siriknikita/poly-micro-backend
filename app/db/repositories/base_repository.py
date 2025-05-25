from bson import ObjectId
from typing import List, Dict, Any, Optional, TypeVar, Generic, Type
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseRepository:
    """Base repository with common database operations"""
    
    def __init__(self, db, collection_name: str):
        self.db = db
        self.collection = db[collection_name]
    
    async def find_all(self, filter_query: Dict = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all documents with optional filter"""
        filter_query = filter_query or {}
        cursor = self.collection.find(filter_query)
        return await cursor.to_list(length=limit)
    
    async def find_one(self, id_value: str) -> Optional[Dict[str, Any]]:
        """Find one document by ID or Object ID"""
        try:
            # Try to find by ObjectId
            return await self.collection.find_one({"_id": ObjectId(id_value)})
        except:
            # If not a valid ObjectId, try with id as a string
            return await self.collection.find_one({"id": id_value})
    
    async def find_by_filter(self, filter_query: Dict) -> Optional[Dict[str, Any]]:
        """Find one document by custom filter"""
        return await self.collection.find_one(filter_query)
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        result = await self.collection.insert_one(data)
        if "_id" in data:
            data["id"] = str(data["_id"])
        return data
    
    async def update(self, id_value: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a document by ID"""
        try:
            # Try to update by ObjectId
            result = await self.collection.update_one(
                {"_id": ObjectId(id_value)}, {"$set": data}
            )
            if result.modified_count:
                return await self.collection.find_one({"_id": ObjectId(id_value)})
        except:
            # If not a valid ObjectId, try with id as a string
            result = await self.collection.update_one(
                {"id": id_value}, {"$set": data}
            )
            if result.modified_count:
                return await self.collection.find_one({"id": id_value})
        return None
    
    async def delete(self, id_value: str) -> bool:
        """Delete a document by ID"""
        try:
            # Try to delete by ObjectId
            result = await self.collection.delete_one({"_id": ObjectId(id_value)})
            if result.deleted_count:
                return True
        except:
            # If not a valid ObjectId, try with id as a string
            result = await self.collection.delete_one({"id": id_value})
            if result.deleted_count:
                return True
        return False
    
    async def count(self, filter_query: Dict = None) -> int:
        """Count documents with optional filter"""
        filter_query = filter_query or {}
        return await self.collection.count_documents(filter_query)
    
    async def find_one_by_field(self, field_name: str, field_value: Any) -> Optional[Dict[str, Any]]:
        """Find one document by a specific field value
        
        Args:
            field_name: The name of the field to search by
            field_value: The value to search for
            
        Returns:
            The matching document or None if not found
        """
        return await self.collection.find_one({field_name: field_value})
