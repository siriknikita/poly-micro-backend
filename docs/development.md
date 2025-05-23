# Development Guide

This guide provides instructions for developers who want to contribute to the Poly Micro Manager backend.

## Prerequisites

- Python 3.10 or later
- MongoDB
- Redis (optional, for caching)
- Docker and Docker Compose (optional, for containerized development)

## Setting Up the Development Environment

### Without Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/siriknikita/university-3-course.git
   cd poly-micro-manager/poly-micro-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the development server:
   ```bash
   python run.py
   ```

### With Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/siriknikita/university-3-course.git
   cd poly-micro-manager/poly-micro-backend
   ```

2. Start the development environment:
   ```bash
   docker-compose up -d
   ```

## Project Structure

```
poly-micro-backend/
├── app/                    # Application code
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   │   ├── cache.py        # Redis caching utilities
│   │   ├── config.py       # Application configuration
│   │   └── enum_compat.py  # Enum compatibility layer
│   ├── db/                 # Database layer
│   │   ├── repositories/   # Data access repositories
│   │   └── mongodb.py      # MongoDB connection
│   ├── schemas/            # Pydantic models
│   └── services/           # Business logic
├── docs/                   # Documentation
├── tests/                  # Test suite
├── .env.example            # Example environment variables
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

## Adding a New Feature

When adding a new feature:

1. Create Pydantic models in `app/schemas/`
2. Add repository methods in `app/db/repositories/`
3. Implement business logic in `app/services/`
4. Add API endpoints in `app/api/endpoints/`
5. Update documentation as needed

### Example: Adding a New Resource

1. Create a schema:
   ```python
   # app/schemas/example.py
   from pydantic import BaseModel, Field
   from datetime import datetime
   from typing import Optional

   class ExampleCreate(BaseModel):
       name: str = Field(..., description="Resource name")
       description: Optional[str] = None

   class ExampleUpdate(BaseModel):
       name: Optional[str] = None
       description: Optional[str] = None

   class ExampleInDB(ExampleCreate):
       id: str
       created_at: datetime
       updated_at: Optional[datetime] = None
   ```

2. Create a repository:
   ```python
   # app/db/repositories/example_repository.py
   from app.db.repositories.base_repository import BaseRepository
   from app.core.cache import cached, invalidate_cache

   class ExampleRepository(BaseRepository):
       def __init__(self, db):
           super().__init__(db, "examples")

       @cached(ttl=300, prefix="examples:all")
       async def get_all_examples(self):
           examples = await self.find_all()
           return examples

       # Add other methods...
   ```

3. Add an API endpoint:
   ```python
   # app/api/endpoints/examples.py
   from fastapi import APIRouter, Depends, HTTPException
   from app.db.repositories.example_repository import ExampleRepository
   from app.db.mongodb import get_database

   router = APIRouter()

   @router.get("/")
   async def get_examples(db=Depends(get_database)):
       repository = ExampleRepository(db)
       return await repository.get_all_examples()
   ```

4. Include the router in the API:
   ```python
   # app/api/api.py
   from app.api.endpoints import examples

   api_router = APIRouter()
   api_router.include_router(examples.router, prefix="/examples", tags=["examples"])
   ```

## Testing

Run tests with pytest:

```bash
pytest
```

## Commit Guidelines

When committing changes:

1. Use appropriate commit type prefixes:
   - `Feat:` for new features
   - `Fix:` for bug fixes
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring
   - `Test:` for adding/updating tests
   - `Chore:` for maintenance tasks

2. Include ticket numbers from the branch name in parentheses at the end.

Example: `Feat: Add Redis caching to metrics repository (INT-123, CL-4567)`

## Documentation

Update documentation for any significant changes:

1. Update or add Markdown files in the `docs/` directory
2. Update the API endpoints in the Swagger documentation by adding proper docstrings
3. Run the documentation locally with Docsify:
   ```bash
   npm install -g docsify-cli
   docsify serve docs
   ```
