import pytest
from uuid import UUID
from lightagent.storage import TapeStore
from lightagent.tape import Tape, Step, StepMetadata, StepType

def test_save_and_load_tape(test_db, sample_tape):
    """Test saving and loading a tape."""
    # Save tape
    tape_id = test_db.save_tape(sample_tape)
    assert isinstance(tape_id, UUID)
    
    # Load tape
    loaded_tape = test_db.load_tape(tape_id)
    assert len(loaded_tape.steps) == len(sample_tape.steps)
    assert loaded_tape.steps[0].content == sample_tape.steps[0].content

def test_get_tape_history(test_db, sample_tape):
    """Test getting tape history."""
    # Save original tape
    original_id = test_db.save_tape(sample_tape)
    
    # Create and save child tape
    child_tape = sample_tape.clone()
    child_id = test_db.save_tape(child_tape)
    
    # Get history
    history = test_db.get_tape_history(child_id)
    assert len(history) == 2
    assert history[0] == child_id
    assert history[1] == original_id

def test_search_tapes(test_db, sample_tape):
    """Test searching tapes."""
    test_db.save_tape(sample_tape)
    
    # Search by agent
    results = test_db.search_tapes(agent="test_agent")
    assert len(results) == 1
    
    # Search by node
    results = test_db.search_tapes(node="test_node")
    assert len(results) == 1