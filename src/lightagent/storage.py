# storage.py
from typing import List, Optional, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON, create_engine, Session, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import json
from uuid import UUID, uuid4
from .utils.logging import get_logger

logger = get_logger(__name__)

class StoredStep(SQLModel, table=True):
    """Database model for steps."""
    __tablename__ = "steps"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tape_id: UUID = Field(index=True)
    type: str
    content: dict = Field(sa_type=JSON)
    agent: str = Field(index=True)
    node: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    prompt_id: Optional[str] = Field(default=None, index=True)
    sequence: int = Field(index=True)  # Order within tape

class StoredTape(SQLModel, table=True):
    """Database model for tapes."""
    __tablename__ = "tapes"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    parent_id: Optional[UUID] = Field(default=None, index=True)
    author: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default=list(), sa_type=JSON)  # For filtering/organization
    title: Optional[str] = Field(default=None)  # Human readable title
    description: Optional[str] = Field(default=None)  # Optional description

class TapeStore:
    """Handles tape storage and retrieval."""
    
    def __init__(self, database_url: str = "sqlite:///tapes.db"):
        logger.debug(f"Initializing TapeStore with database: {database_url}")
        self.engine = create_engine(database_url)
        # Create tables
        SQLModel.metadata.create_all(self.engine)
        logger.debug("Database tables created successfully")

    def save_tape(self, tape: 'Tape') -> UUID:
        """Save a tape and its steps."""
        logger.debug(f"Saving tape {tape.metadata.tape_id} with {len(tape.steps)} steps")
        
        with Session(self.engine) as session:
            try:
                # Create StoredTape
                stored_tape = StoredTape(
                    id=UUID(tape.metadata.tape_id),
                    parent_id=UUID(tape.metadata.parent_id) if tape.metadata.parent_id else None,
                    author=tape.metadata.author,
                    created_at=datetime.fromisoformat(tape.metadata.created_at),
                )
                session.add(stored_tape)
                logger.debug(f"Created StoredTape record for tape {stored_tape.id}")

                # Save each step
                for i, step in enumerate(tape.steps):
                    stored_step = StoredStep(
                        tape_id=stored_tape.id,
                        type=step.type.value,
                        content=json.loads(step.model_dump_json())['content'],
                        agent=step.metadata.agent,
                        node=step.metadata.node,
                        timestamp=datetime.fromisoformat(step.metadata.timestamp),
                        prompt_id=step.metadata.prompt_id,
                        sequence=i
                    )
                    session.add(stored_step)
                    logger.debug(f"Added step {i+1}/{len(tape.steps)} to tape {stored_tape.id}")

                session.commit()
                logger.debug(f"Successfully committed tape {stored_tape.id} to database")
                return stored_tape.id
            except Exception as e:
                logger.error(f"Error saving tape: {str(e)}")
                session.rollback()
                raise

    def load_tape(self, tape_id: UUID) -> 'Tape':
        """Load a tape and its steps from storage."""
        logger.debug(f"Loading tape {tape_id} from storage")
        
        with Session(self.engine) as session:
            try:
                # Load tape metadata
                stored_tape = session.get(StoredTape, tape_id)
                if not stored_tape:
                    logger.error(f"Tape {tape_id} not found in storage")
                    raise ValueError(f"No tape found with id {tape_id}")

                logger.debug(f"Found tape {tape_id} in storage")
                
                # Load steps
                stmt = select(StoredStep).where(StoredStep.tape_id == tape_id).order_by(StoredStep.sequence)
                stored_steps = session.exec(stmt).all()
                logger.debug(f"Loaded {len(stored_steps)} steps for tape {tape_id}")

                # Convert back to Tape format
                from .tape import Tape, Step, StepMetadata, TapeMetadata, StepType
                
                metadata = TapeMetadata(
                    author=stored_tape.author,
                    parent_id=str(stored_tape.parent_id) if stored_tape.parent_id else None,
                    created_at=stored_tape.created_at.isoformat(),
                    tape_id=str(stored_tape.id)
                )
                
                tape_steps = []
                for stored_step in stored_steps:
                    step = Step(
                        type=StepType(stored_step.type),
                        content=stored_step.content,
                        metadata=StepMetadata(
                            agent=stored_step.agent,
                            node=stored_step.node,
                            timestamp=stored_step.timestamp.isoformat(),
                            prompt_id=stored_step.prompt_id
                        )
                    )
                    tape_steps.append(step)
                    logger.debug(f"Processed step {stored_step.sequence} of type {stored_step.type}")

                tape = Tape(steps=tape_steps, metadata=metadata)
                logger.debug(f"Successfully reconstructed tape {tape_id}")
                return tape
            except Exception as e:
                logger.error(f"Error loading tape {tape_id}: {str(e)}")
                raise

    def get_tape_history(self, tape_id: UUID) -> List[UUID]:
        """Get the history of tapes leading to this one."""
        history = []
        with Session(self.engine) as session:
            current_id = tape_id
            while current_id:
                history.append(current_id)
                stored_tape = session.get(StoredTape, current_id)
                if not stored_tape or not stored_tape.parent_id:
                    break
                current_id = stored_tape.parent_id
        return history

    def search_tapes(self, 
                    agent: Optional[str] = None, 
                    node: Optional[str] = None,
                    tags: Optional[List[str]] = None,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> List[StoredTape]:
        """Search tapes based on various criteria."""
        with Session(self.engine) as session:
            query = select(StoredTape)
            
            if start_date:
                query = query.where(StoredTape.created_at >= start_date)
            if end_date:
                query = query.where(StoredTape.created_at <= end_date)
            if tags:
                # Note: This is a simple implementation. For production, 
                # you might want a more sophisticated tag matching system
                query = query.where(StoredTape.tags.contains(tags))
            
            # If agent or node specified, need to join with steps
            if agent or node:
                stmt = select(StoredStep.tape_id).distinct()
                if agent:
                    stmt = stmt.where(StoredStep.agent == agent)
                if node:
                    stmt = stmt.where(StoredStep.node == node)
                step_tape_ids = session.exec(stmt).all()
                query = query.where(StoredTape.id.in_(step_tape_ids))
            
            return session.exec(query).all()

    def add_tag(self, tape_id: UUID, tag: str):
        """Add a tag to a tape."""
        with Session(self.engine) as session:
            tape = session.get(StoredTape, tape_id)
            if not tape:
                raise ValueError(f"Tape {tape_id} not found")
            if tag not in tape.tags:
                tape.tags.append(tag)
            session.add(tape)
            session.commit()

# Example usage
def example_usage():
    # Initialize storage
    store = TapeStore()
    
    # Create and save a tape
    from .tape import Tape, Step, StepMetadata, TapeMetadata, StepType
    
    tape = Tape(
        steps=[
            Step(
                type=StepType.THOUGHT,
                content="Initial thought",
                metadata=StepMetadata(agent="test_agent", node="test_node")
            )
        ],
        metadata=TapeMetadata(author="test")
    )
    
    # Save the tape
    tape_id = store.save_tape(tape)
    
    # Load the tape
    loaded_tape = store.load_tape(tape_id)
    
    # Add a tag
    store.add_tag(tape_id, "example")
    
    # Search tapes
    results = store.search_tapes(agent="test_agent", tags=["example"])
    
    return results