"""
Infinite Story Web - Database Models and Manager

This module provides the database layer for storing story segments,
user sessions, and collaborative story merges.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
import json

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()


class User(Base):
    """Represents a user session in the system."""
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    stories = relationship("StorySegment", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary representation."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }


class StorySegment(Base):
    """Represents a segment of the evolving story."""
    __tablename__ = 'story_segments'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    parent_id = Column(String(36), ForeignKey('story_segments.id'), nullable=True)
    is_merged = Column(Boolean, default=False)
    merged_from = Column(Text, nullable=True)  # JSON array of segment IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="stories")
    parent = relationship("StorySegment", remote_side=[id], backref="children")

    def to_dict(self) -> Dict[str, Any]:
        """Convert story segment to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'sequence_number': self.sequence_number,
            'parent_id': self.parent_id,
            'is_merged': self.is_merged,
            'merged_from': json.loads(self.merged_from) if self.merged_from else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Interaction(Base):
    """Tracks user interactions that influence story generation."""
    __tablename__ = 'interactions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # scroll, click, keypress
    data = Column(Text, nullable=True)  # JSON data for interaction details
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="interactions")

    def to_dict(self) -> Dict[str, Any]:
        """Convert interaction to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'interaction_type': self.interaction_type,
            'data': json.loads(self.data) if self.data else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class MergeRequest(Base):
    """Tracks story merge requests between users."""
    __tablename__ = 'merge_requests'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    target_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    source_segment_id = Column(String(36), ForeignKey('story_segments.id'), nullable=False)
    status = Column(String(20), default='pending')  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert merge request to dictionary representation."""
        return {
            'id': self.id,
            'source_user_id': self.source_user_id,
            'target_user_id': self.target_user_id,
            'source_segment_id': self.source_segment_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, database_url: str = "sqlite:///stories.db"):
        """Initialize the database manager.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(self.engine)

    def drop_tables(self) -> None:
        """Drop all database tables."""
        Base.metadata.drop_all(self.engine)

    def get_session(self):
        """Get a new database session."""
        return self.Session()

    # User operations
    def create_user(self, session_id: str) -> User:
        """Create a new user with the given session ID."""
        session = self.get_session()
        try:
            user = User(session_id=session_id)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()

    def get_user_by_session(self, session_id: str) -> Optional[User]:
        """Get a user by their session ID."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.session_id == session_id).first()
        finally:
            session.close()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()

    def update_user_activity(self, user_id: str) -> None:
        """Update the last active timestamp for a user."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.last_active = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def get_active_users(self, minutes: int = 5) -> List[User]:
        """Get users active within the last N minutes."""
        session = self.get_session()
        try:
            cutoff = datetime.utcnow() - __import__('datetime').timedelta(minutes=minutes)
            return session.query(User).filter(User.last_active >= cutoff).all()
        finally:
            session.close()

    # Story segment operations
    def create_story_segment(self, user_id: str, content: str, 
                            sequence_number: int, parent_id: Optional[str] = None,
                            is_merged: bool = False, merged_from: Optional[List[str]] = None) -> StorySegment:
        """Create a new story segment."""
        session = self.get_session()
        try:
            segment = StorySegment(
                user_id=user_id,
                content=content,
                sequence_number=sequence_number,
                parent_id=parent_id,
                is_merged=is_merged,
                merged_from=json.dumps(merged_from) if merged_from else None
            )
            session.add(segment)
            session.commit()
            session.refresh(segment)
            return segment
        finally:
            session.close()

    def get_story_segments(self, user_id: str, limit: int = 50, offset: int = 0) -> List[StorySegment]:
        """Get story segments for a user."""
        session = self.get_session()
        try:
            return session.query(StorySegment)\
                .filter(StorySegment.user_id == user_id)\
                .order_by(StorySegment.sequence_number)\
                .offset(offset)\
                .limit(limit)\
                .all()
        finally:
            session.close()

    def get_latest_segment(self, user_id: str) -> Optional[StorySegment]:
        """Get the latest story segment for a user."""
        session = self.get_session()
        try:
            return session.query(StorySegment)\
                .filter(StorySegment.user_id == user_id)\
                .order_by(StorySegment.sequence_number.desc())\
                .first()
        finally:
            session.close()

    def get_segment_by_id(self, segment_id: str) -> Optional[StorySegment]:
        """Get a story segment by ID."""
        session = self.get_session()
        try:
            return session.query(StorySegment).filter(StorySegment.id == segment_id).first()
        finally:
            session.close()

    def get_full_story(self, user_id: str) -> str:
        """Get the full story text for a user."""
        segments = self.get_story_segments(user_id, limit=1000)
        return ' '.join(segment.content for segment in segments)

    # Interaction operations
    def record_interaction(self, user_id: str, interaction_type: str, 
                          data: Optional[Dict[str, Any]] = None) -> Interaction:
        """Record a user interaction."""
        session = self.get_session()
        try:
            interaction = Interaction(
                user_id=user_id,
                interaction_type=interaction_type,
                data=json.dumps(data) if data else None
            )
            session.add(interaction)
            session.commit()
            session.refresh(interaction)
            return interaction
        finally:
            session.close()

    def get_recent_interactions(self, user_id: str, limit: int = 10) -> List[Interaction]:
        """Get recent interactions for a user."""
        session = self.get_session()
        try:
            return session.query(Interaction)\
                .filter(Interaction.user_id == user_id)\
                .order_by(Interaction.timestamp.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()

    def get_interaction_counts(self, user_id: str) -> Dict[str, int]:
        """Get interaction counts by type for a user."""
        session = self.get_session()
        try:
            interactions = session.query(Interaction)\
                .filter(Interaction.user_id == user_id)\
                .all()
            counts = {}
            for interaction in interactions:
                counts[interaction.interaction_type] = counts.get(interaction.interaction_type, 0) + 1
            return counts
        finally:
            session.close()

    # Merge request operations
    def create_merge_request(self, source_user_id: str, target_user_id: str, 
                            source_segment_id: str) -> MergeRequest:
        """Create a new merge request."""
        session = self.get_session()
        try:
            merge_request = MergeRequest(
                source_user_id=source_user_id,
                target_user_id=target_user_id,
                source_segment_id=source_segment_id
            )
            session.add(merge_request)
            session.commit()
            session.refresh(merge_request)
            return merge_request
        finally:
            session.close()

    def get_pending_merge_requests(self, user_id: str) -> List[MergeRequest]:
        """Get pending merge requests for a user."""
        session = self.get_session()
        try:
            return session.query(MergeRequest)\
                .filter(MergeRequest.target_user_id == user_id)\
                .filter(MergeRequest.status == 'pending')\
                .all()
        finally:
            session.close()

    def resolve_merge_request(self, request_id: str, accepted: bool) -> Optional[MergeRequest]:
        """Resolve a merge request."""
        session = self.get_session()
        try:
            merge_request = session.query(MergeRequest)\
                .filter(MergeRequest.id == request_id)\
                .first()
            if merge_request:
                merge_request.status = 'accepted' if accepted else 'rejected'
                merge_request.resolved_at = datetime.utcnow()
                session.commit()
                session.refresh(merge_request)
            return merge_request
        finally:
            session.close()

    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a user."""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        finally:
            session.close()
