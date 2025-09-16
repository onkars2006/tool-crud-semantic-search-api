from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from typing import Union

class ToolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the tool")
    description: str = Field(..., min_length=1, description="Description of the tool")
    tags: Optional[List[str]] = Field(default=[], description="List of tags for the tool")
    tool_metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata for the tool")

class ToolCreate(ToolBase):
    pass

class ToolUpdate(ToolBase):
    pass

class ToolResponse(ToolBase):
    id: int
    created_at: Union[datetime, str, None]
    updated_at: Union[datetime, str, None]
    
    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of results to return")

class SearchResult(BaseModel):
    id: int
    name: str
    description: str
    score: float
    tags: List[str] = []
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    
    class Config:
        from_attributes = True

class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    results: List[Dict[str, Any]]
    created_at: Union[datetime, str, None]
    
    class Config:
        from_attributes = True