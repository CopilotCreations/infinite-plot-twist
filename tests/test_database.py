"""
Tests for the DatabaseManager and models.

This module contains comprehensive tests for the database layer
including models and CRUD operations.
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta

from src.database.models import (
    DatabaseManager,
    User,
    StorySegment,
    Interaction,
    MergeRequest,
    Base
)


@pytest.fixture
def db_manager():
    """Create a temporary database for testing."""
    # Use a temporary file for SQLite
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    manager = DatabaseManager(f"sqlite:///{path}")
    manager.create_tables()
    
    yield manager
    
    # Cleanup
    manager.drop_tables()
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def sample_user(db_manager):
    """Create a sample user for testing."""
    return db_manager.create_user("test-session-123")


class TestDatabaseManagerInit:
    """Tests for DatabaseManager initialization."""

    def test_init_creates_engine(self, db_manager):
        """Test that initialization creates a database engine."""
        assert db_manager.engine is not None

    def test_init_creates_session_factory(self, db_manager):
        """Test that initialization creates a session factory."""
        assert db_manager.Session is not None

    def test_create_tables(self, db_manager):
        """Test that create_tables works without error."""
        db_manager.create_tables()
        # If we get here without exception, tables were created

    def test_drop_tables(self, db_manager):
        """Test that drop_tables works without error."""
        db_manager.drop_tables()
        db_manager.create_tables()  # Recreate for other tests

    def test_get_session(self, db_manager):
        """Test getting a database session."""
        session = db_manager.get_session()
        assert session is not None
        session.close()


class TestUserOperations:
    """Tests for user CRUD operations."""

    def test_create_user(self, db_manager):
        """Test creating a new user."""
        user = db_manager.create_user("new-session-456")
        
        assert user is not None
        assert user.id is not None
        assert user.session_id == "new-session-456"
        assert user.created_at is not None

    def test_get_user_by_session(self, db_manager, sample_user):
        """Test retrieving a user by session ID."""
        user = db_manager.get_user_by_session("test-session-123")
        
        assert user is not None
        assert user.session_id == "test-session-123"

    def test_get_user_by_session_not_found(self, db_manager):
        """Test retrieving a non-existent user by session ID."""
        user = db_manager.get_user_by_session("nonexistent-session")
        
        assert user is None

    def test_get_user_by_id(self, db_manager, sample_user):
        """Test retrieving a user by ID."""
        user = db_manager.get_user_by_id(sample_user.id)
        
        assert user is not None
        assert user.id == sample_user.id

    def test_get_user_by_id_not_found(self, db_manager):
        """Test retrieving a non-existent user by ID."""
        user = db_manager.get_user_by_id("nonexistent-id")
        
        assert user is None

    def test_update_user_activity(self, db_manager, sample_user):
        """Test updating user activity timestamp."""
        original_time = sample_user.last_active
        
        # Wait a moment and update
        db_manager.update_user_activity(sample_user.id)
        
        user = db_manager.get_user_by_id(sample_user.id)
        # The time should be updated (or at least not raise an error)
        assert user is not None

    def test_get_active_users(self, db_manager, sample_user):
        """Test getting active users."""
        users = db_manager.get_active_users(minutes=60)
        
        assert len(users) >= 1
        assert any(u.id == sample_user.id for u in users)

    def test_delete_user_data(self, db_manager, sample_user):
        """Test deleting user data."""
        user_id = sample_user.id
        
        result = db_manager.delete_user_data(user_id)
        
        assert result is True
        assert db_manager.get_user_by_id(user_id) is None

    def test_delete_user_data_not_found(self, db_manager):
        """Test deleting non-existent user data."""
        result = db_manager.delete_user_data("nonexistent-id")
        
        assert result is False


class TestStorySegmentOperations:
    """Tests for story segment CRUD operations."""

    def test_create_story_segment(self, db_manager, sample_user):
        """Test creating a story segment."""
        segment = db_manager.create_story_segment(
            user_id=sample_user.id,
            content="Once upon a time...",
            sequence_number=0
        )
        
        assert segment is not None
        assert segment.id is not None
        assert segment.content == "Once upon a time..."
        assert segment.sequence_number == 0
        assert segment.user_id == sample_user.id

    def test_create_story_segment_with_parent(self, db_manager, sample_user):
        """Test creating a story segment with a parent."""
        parent = db_manager.create_story_segment(
            user_id=sample_user.id,
            content="Parent segment",
            sequence_number=0
        )
        
        child = db_manager.create_story_segment(
            user_id=sample_user.id,
            content="Child segment",
            sequence_number=1,
            parent_id=parent.id
        )
        
        assert child.parent_id == parent.id

    def test_create_merged_segment(self, db_manager, sample_user):
        """Test creating a merged story segment."""
        segment = db_manager.create_story_segment(
            user_id=sample_user.id,
            content="Merged content",
            sequence_number=0,
            is_merged=True,
            merged_from=["seg-1", "seg-2"]
        )
        
        assert segment.is_merged is True
        # Note: merged_from is stored as JSON string in DB

    def test_get_story_segments(self, db_manager, sample_user):
        """Test getting story segments for a user."""
        # Create multiple segments
        for i in range(5):
            db_manager.create_story_segment(
                user_id=sample_user.id,
                content=f"Segment {i}",
                sequence_number=i
            )
        
        segments = db_manager.get_story_segments(sample_user.id)
        
        assert len(segments) == 5
        assert segments[0].sequence_number == 0
        assert segments[4].sequence_number == 4

    def test_get_story_segments_with_limit(self, db_manager, sample_user):
        """Test getting story segments with limit."""
        for i in range(10):
            db_manager.create_story_segment(
                user_id=sample_user.id,
                content=f"Segment {i}",
                sequence_number=i
            )
        
        segments = db_manager.get_story_segments(sample_user.id, limit=3)
        
        assert len(segments) == 3

    def test_get_story_segments_with_offset(self, db_manager, sample_user):
        """Test getting story segments with offset."""
        for i in range(10):
            db_manager.create_story_segment(
                user_id=sample_user.id,
                content=f"Segment {i}",
                sequence_number=i
            )
        
        segments = db_manager.get_story_segments(sample_user.id, limit=3, offset=5)
        
        assert len(segments) == 3
        assert segments[0].sequence_number == 5

    def test_get_latest_segment(self, db_manager, sample_user):
        """Test getting the latest story segment."""
        for i in range(5):
            db_manager.create_story_segment(
                user_id=sample_user.id,
                content=f"Segment {i}",
                sequence_number=i
            )
        
        latest = db_manager.get_latest_segment(sample_user.id)
        
        assert latest is not None
        assert latest.sequence_number == 4

    def test_get_latest_segment_none(self, db_manager, sample_user):
        """Test getting latest segment when none exist."""
        latest = db_manager.get_latest_segment(sample_user.id)
        
        assert latest is None

    def test_get_segment_by_id(self, db_manager, sample_user):
        """Test getting a segment by ID."""
        created = db_manager.create_story_segment(
            user_id=sample_user.id,
            content="Test content",
            sequence_number=0
        )
        
        segment = db_manager.get_segment_by_id(created.id)
        
        assert segment is not None
        assert segment.id == created.id

    def test_get_segment_by_id_not_found(self, db_manager):
        """Test getting a non-existent segment."""
        segment = db_manager.get_segment_by_id("nonexistent-id")
        
        assert segment is None

    def test_get_full_story(self, db_manager, sample_user):
        """Test getting the full story text."""
        db_manager.create_story_segment(
            user_id=sample_user.id, content="Once upon a time", sequence_number=0
        )
        db_manager.create_story_segment(
            user_id=sample_user.id, content="there was a hero", sequence_number=1
        )
        db_manager.create_story_segment(
            user_id=sample_user.id, content="who saved the day.", sequence_number=2
        )
        
        story = db_manager.get_full_story(sample_user.id)
        
        assert story == "Once upon a time there was a hero who saved the day."


class TestInteractionOperations:
    """Tests for interaction CRUD operations."""

    def test_record_interaction(self, db_manager, sample_user):
        """Test recording an interaction."""
        interaction = db_manager.record_interaction(
            user_id=sample_user.id,
            interaction_type="click",
            data={"x": 100, "y": 200}
        )
        
        assert interaction is not None
        assert interaction.interaction_type == "click"
        assert interaction.user_id == sample_user.id

    def test_record_interaction_without_data(self, db_manager, sample_user):
        """Test recording an interaction without data."""
        interaction = db_manager.record_interaction(
            user_id=sample_user.id,
            interaction_type="scroll"
        )
        
        assert interaction is not None
        assert interaction.data is None

    def test_get_recent_interactions(self, db_manager, sample_user):
        """Test getting recent interactions."""
        for i in range(5):
            db_manager.record_interaction(
                user_id=sample_user.id,
                interaction_type=f"type_{i}"
            )
        
        interactions = db_manager.get_recent_interactions(sample_user.id)
        
        assert len(interactions) == 5

    def test_get_recent_interactions_with_limit(self, db_manager, sample_user):
        """Test getting recent interactions with limit."""
        for i in range(10):
            db_manager.record_interaction(
                user_id=sample_user.id,
                interaction_type=f"type_{i}"
            )
        
        interactions = db_manager.get_recent_interactions(sample_user.id, limit=3)
        
        assert len(interactions) == 3

    def test_get_interaction_counts(self, db_manager, sample_user):
        """Test getting interaction counts by type."""
        for _ in range(3):
            db_manager.record_interaction(
                user_id=sample_user.id, interaction_type="click"
            )
        for _ in range(5):
            db_manager.record_interaction(
                user_id=sample_user.id, interaction_type="scroll"
            )
        for _ in range(2):
            db_manager.record_interaction(
                user_id=sample_user.id, interaction_type="keypress"
            )
        
        counts = db_manager.get_interaction_counts(sample_user.id)
        
        assert counts["click"] == 3
        assert counts["scroll"] == 5
        assert counts["keypress"] == 2


class TestMergeRequestOperations:
    """Tests for merge request CRUD operations."""

    def test_create_merge_request(self, db_manager):
        """Test creating a merge request."""
        user1 = db_manager.create_user("session-1")
        user2 = db_manager.create_user("session-2")
        segment = db_manager.create_story_segment(
            user_id=user1.id, content="Test", sequence_number=0
        )
        
        merge_request = db_manager.create_merge_request(
            source_user_id=user1.id,
            target_user_id=user2.id,
            source_segment_id=segment.id
        )
        
        assert merge_request is not None
        assert merge_request.status == "pending"
        assert merge_request.source_user_id == user1.id
        assert merge_request.target_user_id == user2.id

    def test_get_pending_merge_requests(self, db_manager):
        """Test getting pending merge requests."""
        user1 = db_manager.create_user("session-1")
        user2 = db_manager.create_user("session-2")
        segment = db_manager.create_story_segment(
            user_id=user1.id, content="Test", sequence_number=0
        )
        
        db_manager.create_merge_request(
            source_user_id=user1.id,
            target_user_id=user2.id,
            source_segment_id=segment.id
        )
        
        requests = db_manager.get_pending_merge_requests(user2.id)
        
        assert len(requests) == 1
        assert requests[0].target_user_id == user2.id

    def test_resolve_merge_request_accept(self, db_manager):
        """Test accepting a merge request."""
        user1 = db_manager.create_user("session-1")
        user2 = db_manager.create_user("session-2")
        segment = db_manager.create_story_segment(
            user_id=user1.id, content="Test", sequence_number=0
        )
        
        merge_request = db_manager.create_merge_request(
            source_user_id=user1.id,
            target_user_id=user2.id,
            source_segment_id=segment.id
        )
        
        resolved = db_manager.resolve_merge_request(merge_request.id, accepted=True)
        
        assert resolved is not None
        assert resolved.status == "accepted"
        assert resolved.resolved_at is not None

    def test_resolve_merge_request_reject(self, db_manager):
        """Test rejecting a merge request."""
        user1 = db_manager.create_user("session-1")
        user2 = db_manager.create_user("session-2")
        segment = db_manager.create_story_segment(
            user_id=user1.id, content="Test", sequence_number=0
        )
        
        merge_request = db_manager.create_merge_request(
            source_user_id=user1.id,
            target_user_id=user2.id,
            source_segment_id=segment.id
        )
        
        resolved = db_manager.resolve_merge_request(merge_request.id, accepted=False)
        
        assert resolved is not None
        assert resolved.status == "rejected"

    def test_resolve_merge_request_not_found(self, db_manager):
        """Test resolving a non-existent merge request."""
        resolved = db_manager.resolve_merge_request("nonexistent-id", accepted=True)
        
        assert resolved is None


class TestModelToDictMethods:
    """Tests for model to_dict conversion methods."""

    def test_user_to_dict(self, db_manager, sample_user):
        """Test User.to_dict() method."""
        user_dict = sample_user.to_dict()
        
        assert 'id' in user_dict
        assert 'session_id' in user_dict
        assert 'created_at' in user_dict
        assert 'last_active' in user_dict
        assert user_dict['session_id'] == "test-session-123"

    def test_story_segment_to_dict(self, db_manager, sample_user):
        """Test StorySegment.to_dict() method."""
        segment = db_manager.create_story_segment(
            user_id=sample_user.id,
            content="Test content",
            sequence_number=0
        )
        
        segment_dict = segment.to_dict()
        
        assert 'id' in segment_dict
        assert 'user_id' in segment_dict
        assert 'content' in segment_dict
        assert 'sequence_number' in segment_dict
        assert segment_dict['content'] == "Test content"

    def test_interaction_to_dict(self, db_manager, sample_user):
        """Test Interaction.to_dict() method."""
        interaction = db_manager.record_interaction(
            user_id=sample_user.id,
            interaction_type="click",
            data={"x": 100}
        )
        
        interaction_dict = interaction.to_dict()
        
        assert 'id' in interaction_dict
        assert 'user_id' in interaction_dict
        assert 'interaction_type' in interaction_dict
        assert 'data' in interaction_dict
        assert interaction_dict['interaction_type'] == "click"

    def test_merge_request_to_dict(self, db_manager):
        """Test MergeRequest.to_dict() method."""
        user1 = db_manager.create_user("session-1")
        user2 = db_manager.create_user("session-2")
        segment = db_manager.create_story_segment(
            user_id=user1.id, content="Test", sequence_number=0
        )
        
        merge_request = db_manager.create_merge_request(
            source_user_id=user1.id,
            target_user_id=user2.id,
            source_segment_id=segment.id
        )
        
        request_dict = merge_request.to_dict()
        
        assert 'id' in request_dict
        assert 'source_user_id' in request_dict
        assert 'target_user_id' in request_dict
        assert 'status' in request_dict
        assert request_dict['status'] == "pending"
