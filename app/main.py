from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from contextlib import asynccontextmanager

from app import crud, schemas, models
from app.database import get_db, init_db
from app.config import settings
from app.vector_db import search_tools
from fastapi.responses import JSONResponse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully!")
    yield
    # Shutdown: Clean up resources
    logger.info("Shutting down application...")

app = FastAPI(
    title="Tool Semantic Search API",
    description="API for managing tools and performing semantic search",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Tool Semantic Search API"}

@app.get(f"{settings.API_PREFIX}/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

@app.post(f"{settings.API_PREFIX}/tools", response_model=schemas.ToolResponse, status_code=status.HTTP_201_CREATED, tags=["Tools"])
def create_tool(tool: schemas.ToolCreate, db: Session = Depends(get_db)):
    """
    Create a new tool
    """
    db_tool = crud.create_tool(db, tool)
    if not db_tool:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool with this name already exists"
        )
    return db_tool

@app.get(f"{settings.API_PREFIX}/tools", response_model=List[schemas.ToolResponse], tags=["Tools"])
def read_tools(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get a list of tools with pagination
    """
    tools = crud.get_tools(db, skip=skip, limit=limit)
    return tools

@app.get(f"{settings.API_PREFIX}/tools/{{tool_id}}", response_model=schemas.ToolResponse, tags=["Tools"])
def read_tool(tool_id: int, db: Session = Depends(get_db)):
    """
    Get a specific tool by ID
    """
    db_tool = crud.get_tool(db, tool_id)
    if not db_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return db_tool

@app.put(f"{settings.API_PREFIX}/tools/{{tool_id}}", response_model=schemas.ToolResponse, tags=["Tools"])
def update_tool(tool_id: int, tool: schemas.ToolUpdate, db: Session = Depends(get_db)):
    """
    Update an existing tool
    """
    db_tool = crud.update_tool(db, tool_id, tool)
    if not db_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found or name already exists"
        )
    return db_tool

@app.delete(f"{settings.API_PREFIX}/tools/{{tool_id}}", tags=["Tools"])
def delete_tool_endpoint(tool_id: int, db: Session = Depends(get_db)):
    """
    Delete a tool
    """
    if not crud.delete_tool_db(db, tool_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return {"message": "Tool deleted successfully"}

@app.post(f"{settings.API_PREFIX}/search", response_model=schemas.SearchResponse, tags=["Search"])
def semantic_search(query: schemas.SearchQuery, db: Session = Depends(get_db)):
    """
    Perform semantic search for tools
    """
    # Perform semantic search
    search_results = search_tools(query.query, query.limit)
    
    # Filter out tools that don't exist in the database
    valid_results = []
    for result in search_results:
        tool_id = result.get('id')
        if tool_id and crud.get_tool(db, tool_id):
            valid_results.append(result)
    
    # Save search history to database (only valid results)
    crud.create_search_history(db, query.query, valid_results)
    
    return {
        "query": query.query,
        "results": valid_results
    }

@app.get(f"{settings.API_PREFIX}/search/history", response_model=List[schemas.SearchHistoryResponse], tags=["Search"])
def get_search_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get search history with pagination
    """
    history = crud.get_search_history(db, skip=skip, limit=limit)
    return history

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )