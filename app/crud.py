from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import models, schemas
from app.vector_db import upsert_tool, delete_tool
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def get_tool(db: Session, tool_id: int) -> Optional[models.Tool]:
    """
    Get tool by ID
    """
    try:
        return db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    except Exception as e:
        logger.error(f"Error getting tool {tool_id}: {e}")
        return None

def get_tool_by_name(db: Session, name: str) -> Optional[models.Tool]:
    """
    Get tool by name
    """
    try:
        return db.query(models.Tool).filter(models.Tool.name == name).first()
    except Exception as e:
        logger.error(f"Error getting tool by name {name}: {e}")
        return None

def get_tools(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tool]:
    """
    Get paginated list of tools
    """
    try:
        return db.query(models.Tool).order_by(models.Tool.id).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        return []

def create_tool(db: Session, tool: schemas.ToolCreate) -> Optional[models.Tool]:
    """
    Create a new tool
    """
    try:
        db_tool = models.Tool(
            name=tool.name,
            description=tool.description,
            tags=tool.tags,
            tool_metadata=tool.tool_metadata
        )
        db.add(db_tool)
        db.commit()
        db.refresh(db_tool)
        
        # Also add to vector database
        if not upsert_tool(
            tool_id=db_tool.id,
            name=db_tool.name,
            description=db_tool.description,
            tags=db_tool.tags
        ):
            logger.warning(f"Failed to upsert tool {db_tool.id} to vector database")
        
        logger.info(f"Created tool {db_tool.id}: {db_tool.name}")
        return db_tool
    except IntegrityError:
        db.rollback()
        logger.error(f"Tool with name {tool.name} already exists")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating tool: {e}")
        return None

def update_tool(db: Session, tool_id: int, tool: schemas.ToolUpdate) -> Optional[models.Tool]:
    """
    Update an existing tool
    """
    try:
        db_tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
        if not db_tool:
            logger.error(f"Tool {tool_id} not found for update")
            return None
        
        db_tool.name = tool.name
        db_tool.description = tool.description
        db_tool.tags = tool.tags
        db_tool.tool_metadata = tool.tool_metadata
        
        db.commit()
        db.refresh(db_tool)
        
        # Update vector database
        if not upsert_tool(
            tool_id=db_tool.id,
            name=db_tool.name,
            description=db_tool.description,
            tags=db_tool.tags
        ):
            logger.warning(f"Failed to upsert tool {db_tool.id} to vector database during update")
        
        logger.info(f"Updated tool {db_tool.id}: {db_tool.name}")
        return db_tool
    except IntegrityError:
        db.rollback()
        logger.error(f"Tool with name {tool.name} already exists")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating tool {tool_id}: {e}")
        return None

def delete_tool_db(db: Session, tool_id: int) -> bool:
    """
    Delete a tool
    """
    try:
        db_tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
        if not db_tool:
            logger.error(f"Tool {tool_id} not found for deletion")
            return False
        
        db.delete(db_tool)
        db.commit()
        
        # Also delete from vector database
        if not delete_tool(tool_id):
            logger.warning(f"Failed to delete tool {tool_id} from vector database")
        
        logger.info(f"Deleted tool {tool_id}: {db_tool.name}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting tool {tool_id}: {e}")
        return False

def create_search_history(db: Session, query: str, results: list) -> Optional[models.SearchHistory]:
    """
    Create search history record with only valid tools
    """
    try:
        # Filter out results for tools that no longer exist
        valid_results = []
        for result in results:
            tool_id = result.get('id')
            if tool_id and get_tool(db, tool_id):
                valid_results.append(result)
        
        db_history = models.SearchHistory(query=query, results=valid_results)
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        
        logger.info(f"Created search history record {db_history.id} for query: {query}")
        return db_history
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating search history: {e}")
        return None

def get_search_history(db: Session, skip: int = 0, limit: int = 10) -> List[models.SearchHistory]:
    """
    Get paginated search history with only valid tools
    """
    try:
        history_items = db.query(models.SearchHistory).order_by(
            models.SearchHistory.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        # Filter out deleted tools from search history results
        for history_item in history_items:
            valid_results = []
            for result in history_item.results:
                tool_id = result.get('id')
                if tool_id and get_tool(db, tool_id):
                    valid_results.append(result)
            history_item.results = valid_results
        
        return history_items
    except Exception as e:
        logger.error(f"Error getting search history: {e}")
        return []