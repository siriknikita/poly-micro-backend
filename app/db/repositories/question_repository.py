"""Question repository for database operations."""
from typing import List, Dict, Any, Optional
from app.db.repositories.base_repository import BaseRepository
from app.schemas.question import QuestionInDB, Question
from bson import ObjectId


class QuestionRepository(BaseRepository):
    """Repository for managing questions in the database."""
    
    def __init__(self, db):
        super().__init__(db, "poly_micro_questions")
    
    async def create_question(self, question_data: Dict[str, Any]) -> QuestionInDB:
        """Create a new question in the database.
        
        Args:
            question_data: The question data to create
            
        Returns:
            The created question
        """
        question = await self.create(question_data)
        if "_id" in question:
            # Convert ObjectId to string and create a new dict with the string _id
            question_dict = {**question}
            question_dict["_id"] = str(question["_id"])
            question_dict["id"] = str(question["_id"])
            return QuestionInDB(**question_dict)
        return QuestionInDB(**question)
    
    async def get_question(self, question_id: str) -> Optional[Question]:
        """Get a question by ID.
        
        Args:
            question_id: The ID of the question to retrieve
            
        Returns:
            The question or None if not found
        """
        question = await self.find_one(question_id)
        if question:
            if "_id" in question:
                question["id"] = str(question["_id"])
            return Question(**question)
        return None
    
    async def get_questions(self, limit: int = 100, user_id: Optional[str] = None) -> List[Question]:
        """Get all questions with optional user filter.
        
        Args:
            limit: Maximum number of questions to return
            user_id: Optional user ID to filter questions by
            
        Returns:
            List of questions
        """
        filter_query = {}
        if user_id:
            filter_query["user_id"] = user_id
        
        questions = await self.find_all(filter_query, limit)
        return [Question(**{**q, "id": str(q["_id"]) if "_id" in q else None}) for q in questions]
    
    async def update_question_status(self, question_id: str, status: str) -> Optional[Question]:
        """Update the status of a question.
        
        Args:
            question_id: The ID of the question to update
            status: The new status
            
        Returns:
            The updated question or None if not found
        """
        question = await self.update(question_id, {"status": status})
        if question:
            if "_id" in question:
                question["id"] = str(question["_id"])
            return Question(**question)
        return None
    
    async def delete_question(self, question_id: str) -> bool:
        """Delete a question by ID.
        
        Args:
            question_id: The ID of the question to delete
            
        Returns:
            True if the question was deleted, False otherwise
        """
        return await self.delete(question_id)
