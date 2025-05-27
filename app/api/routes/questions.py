"""API routes for questions."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db.database import get_database
from app.db.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionCreate, Question
from app.core.auth import get_current_active_user
from app.schemas.user import User

router = APIRouter()


@router.post("/", response_model=Question, status_code=status.HTTP_201_CREATED)
async def create_question(
    question: QuestionCreate,
    db=Depends(get_database),
    current_user: Optional[User] = Depends(get_current_active_user),
):
    """Create a new question.
    
    Args:
        question: The question data
        db: Database connection
        current_user: Current authenticated user (optional)
        
    Returns:
        The created question
    """
    question_data = question.dict()
    
    # If user is authenticated, add user info to the question
    if current_user:
        question_data["user_id"] = current_user.id
        question_data["user_email"] = current_user.email
    
    question_repo = QuestionRepository(db)
    return await question_repo.create_question(question_data)


@router.get("/", response_model=List[Question])
async def get_questions(
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user),
    all: bool = False,
):
    """Get all questions.
    
    Args:
        db: Database connection
        current_user: Current authenticated user
        all: If True, return all questions (admin only)
        
    Returns:
        List of questions
    """
    question_repo = QuestionRepository(db)
    
    # If admin and requested all questions
    if all and getattr(current_user, "is_admin", False):
        return await question_repo.get_questions()
    
    # Otherwise, only return the user's questions
    return await question_repo.get_questions(user_id=current_user.id)


@router.get("/{question_id}", response_model=Question)
async def get_question(
    question_id: str,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user),
):
    """Get a question by ID.
    
    Args:
        question_id: Question ID
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        The question
    """
    question_repo = QuestionRepository(db)
    question = await question_repo.get_question(question_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user has permission to view this question
    if question.user_id != current_user.id and not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this question"
        )
    
    return question


@router.patch("/{question_id}/status", response_model=Question)
async def update_question_status(
    question_id: str,
    status: str,
    db=Depends(get_database),
    current_user: User = Depends(get_current_active_user),
):
    """Update the status of a question.
    
    Args:
        question_id: Question ID
        status: New status
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        The updated question
    """
    # Only admin can update question status
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update question status"
        )
    
    question_repo = QuestionRepository(db)
    question = await question_repo.update_question_status(question_id, status)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question
