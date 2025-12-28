"""
Infinite Story Web - Flask Server

This module provides the main Flask server that handles
user sessions, story generation, and collaborative features.
"""

import os
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

from .story_generator import StoryGenerator
from ..database.models import DatabaseManager


def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """Create and configure the Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, 
                static_folder='../frontend',
                static_url_path='')
    
    # Apply configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///stories.db')
    
    if config:
        app.config.update(config)
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db = DatabaseManager(app.config['DATABASE_URL'])
    db.create_tables()
    app.db = db
    
    # Store active story generators per session
    app.generators: Dict[str, StoryGenerator] = {}
    
    # Register routes
    register_routes(app)
    
    return app


def create_socketio(app: Flask) -> SocketIO:
    """Create and configure SocketIO for real-time features.
    
    Args:
        app: Flask application instance
        
    Returns:
        Configured SocketIO instance
    """
    socketio = SocketIO(app, cors_allowed_origins="*")
    register_socket_events(socketio, app)
    return socketio


def register_routes(app: Flask) -> None:
    """Register all HTTP routes.
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/')
    def index():
        """Serve the main page."""
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/api/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    
    @app.route('/api/session', methods=['POST'])
    def create_session():
        """Create a new user session."""
        session_id = str(uuid.uuid4())
        user = app.db.create_user(session_id)
        
        # Create a story generator for this session
        app.generators[session_id] = StoryGenerator()
        
        return jsonify({
            'session_id': session_id,
            'user_id': user.id
        })
    
    @app.route('/api/session/<session_id>')
    def get_session(session_id: str):
        """Get session information."""
        user = app.db.get_user_by_session(session_id)
        if not user:
            return jsonify({'error': 'Session not found'}), 404
        
        generator = app.generators.get(session_id)
        context = generator.get_context_summary() if generator else None
        
        return jsonify({
            'user': user.to_dict(),
            'context': context
        })
    
    @app.route('/api/story/start', methods=['POST'])
    def start_story():
        """Start a new story."""
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        user = app.db.get_user_by_session(session_id)
        if not user:
            return jsonify({'error': 'Invalid session'}), 404
        
        # Get or create generator
        if session_id not in app.generators:
            app.generators[session_id] = StoryGenerator()
        
        generator = app.generators[session_id]
        generator.reset()
        
        # Generate opening
        opening = generator.generate_opening()
        
        # Save to database
        segment = app.db.create_story_segment(
            user_id=user.id,
            content=opening,
            sequence_number=0
        )
        
        return jsonify({
            'segment': segment.to_dict(),
            'context': generator.get_context_summary()
        })
    
    @app.route('/api/story/continue', methods=['POST'])
    def continue_story():
        """Continue the story with a new segment."""
        data = request.get_json() or {}
        session_id = data.get('session_id')
        interaction = data.get('interaction')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        user = app.db.get_user_by_session(session_id)
        if not user:
            return jsonify({'error': 'Invalid session'}), 404
        
        # Get generator
        generator = app.generators.get(session_id)
        if not generator:
            generator = StoryGenerator()
            app.generators[session_id] = generator
        
        # Record interaction if provided
        if interaction:
            app.db.record_interaction(
                user_id=user.id,
                interaction_type=interaction.get('type', 'unknown'),
                data=interaction
            )
        
        # Get latest segment for sequence number
        latest = app.db.get_latest_segment(user.id)
        sequence_number = (latest.sequence_number + 1) if latest else 0
        
        # Generate new segment
        content = generator.generate_segment(interaction)
        
        # Save to database
        segment = app.db.create_story_segment(
            user_id=user.id,
            content=content,
            sequence_number=sequence_number,
            parent_id=latest.id if latest else None
        )
        
        # Update user activity
        app.db.update_user_activity(user.id)
        
        return jsonify({
            'segment': segment.to_dict(),
            'context': generator.get_context_summary()
        })
    
    @app.route('/api/story/<session_id>')
    def get_story(session_id: str):
        """Get the full story for a session."""
        user = app.db.get_user_by_session(session_id)
        if not user:
            return jsonify({'error': 'Invalid session'}), 404
        
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        segments = app.db.get_story_segments(user.id, limit=limit, offset=offset)
        
        generator = app.generators.get(session_id)
        context = generator.get_context_summary() if generator else None
        
        return jsonify({
            'segments': [s.to_dict() for s in segments],
            'context': context
        })
    
    @app.route('/api/story/mood', methods=['POST'])
    def set_mood():
        """Set the story mood."""
        data = request.get_json() or {}
        session_id = data.get('session_id')
        mood = data.get('mood')
        
        if not session_id or not mood:
            return jsonify({'error': 'Session ID and mood required'}), 400
        
        generator = app.generators.get(session_id)
        if not generator:
            return jsonify({'error': 'No active story'}), 404
        
        if generator.set_mood(mood):
            return jsonify({'success': True, 'context': generator.get_context_summary()})
        else:
            return jsonify({'error': 'Invalid mood'}), 400
    
    @app.route('/api/story/genre', methods=['POST'])
    def set_genre():
        """Set the story genre."""
        data = request.get_json() or {}
        session_id = data.get('session_id')
        genre = data.get('genre')
        
        if not session_id or not genre:
            return jsonify({'error': 'Session ID and genre required'}), 400
        
        generator = app.generators.get(session_id)
        if not generator:
            return jsonify({'error': 'No active story'}), 404
        
        if generator.set_genre(genre):
            return jsonify({'success': True, 'context': generator.get_context_summary()})
        else:
            return jsonify({'error': 'Invalid genre'}), 400
    
    @app.route('/api/users/active')
    def get_active_users():
        """Get list of active users for potential merging."""
        minutes = request.args.get('minutes', 5, type=int)
        users = app.db.get_active_users(minutes=minutes)
        return jsonify({
            'users': [u.to_dict() for u in users],
            'count': len(users)
        })
    
    @app.route('/api/merge/request', methods=['POST'])
    def request_merge():
        """Request to merge storylines with another user."""
        data = request.get_json() or {}
        session_id = data.get('session_id')
        target_session_id = data.get('target_session_id')
        
        if not session_id or not target_session_id:
            return jsonify({'error': 'Both session IDs required'}), 400
        
        source_user = app.db.get_user_by_session(session_id)
        target_user = app.db.get_user_by_session(target_session_id)
        
        if not source_user or not target_user:
            return jsonify({'error': 'Invalid session(s)'}), 404
        
        latest = app.db.get_latest_segment(source_user.id)
        if not latest:
            return jsonify({'error': 'No story to merge'}), 400
        
        merge_request = app.db.create_merge_request(
            source_user_id=source_user.id,
            target_user_id=target_user.id,
            source_segment_id=latest.id
        )
        
        return jsonify({'merge_request': merge_request.to_dict()})
    
    @app.route('/api/merge/pending/<session_id>')
    def get_pending_merges(session_id: str):
        """Get pending merge requests for a user."""
        user = app.db.get_user_by_session(session_id)
        if not user:
            return jsonify({'error': 'Invalid session'}), 404
        
        requests = app.db.get_pending_merge_requests(user.id)
        return jsonify({
            'requests': [r.to_dict() for r in requests]
        })
    
    @app.route('/api/merge/accept', methods=['POST'])
    def accept_merge():
        """Accept a merge request and combine storylines."""
        data = request.get_json() or {}
        session_id = data.get('session_id')
        request_id = data.get('request_id')
        
        if not session_id or not request_id:
            return jsonify({'error': 'Session ID and request ID required'}), 400
        
        user = app.db.get_user_by_session(session_id)
        if not user:
            return jsonify({'error': 'Invalid session'}), 404
        
        # Resolve the merge request
        merge_request = app.db.resolve_merge_request(request_id, accepted=True)
        if not merge_request:
            return jsonify({'error': 'Merge request not found'}), 404
        
        # Get the source segment
        source_segment = app.db.get_segment_by_id(merge_request.source_segment_id)
        if not source_segment:
            return jsonify({'error': 'Source segment not found'}), 404
        
        # Generate merged content
        generator = app.generators.get(session_id)
        if not generator:
            generator = StoryGenerator()
            app.generators[session_id] = generator
        
        merged_content = generator.merge_storylines([source_segment.content])
        
        # Get latest segment for sequence number
        latest = app.db.get_latest_segment(user.id)
        sequence_number = (latest.sequence_number + 1) if latest else 0
        
        # Create merged segment
        segment = app.db.create_story_segment(
            user_id=user.id,
            content=merged_content,
            sequence_number=sequence_number,
            parent_id=latest.id if latest else None,
            is_merged=True,
            merged_from=[source_segment.id]
        )
        
        return jsonify({
            'segment': segment.to_dict(),
            'context': generator.get_context_summary()
        })
    
    @app.route('/api/interactions/<session_id>')
    def get_interactions(session_id: str):
        """Get interaction history for a session."""
        user = app.db.get_user_by_session(session_id)
        if not user:
            return jsonify({'error': 'Invalid session'}), 404
        
        limit = request.args.get('limit', 10, type=int)
        interactions = app.db.get_recent_interactions(user.id, limit=limit)
        counts = app.db.get_interaction_counts(user.id)
        
        return jsonify({
            'interactions': [i.to_dict() for i in interactions],
            'counts': counts
        })


def register_socket_events(socketio: SocketIO, app: Flask) -> None:
    """Register WebSocket event handlers.
    
    Args:
        socketio: SocketIO instance
        app: Flask application instance
    """
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        emit('connected', {'status': 'connected'})
    
    @socketio.on('join_story')
    def handle_join(data):
        """Join a story room for real-time updates."""
        session_id = data.get('session_id')
        if session_id:
            join_room(session_id)
            emit('joined', {'room': session_id})
    
    @socketio.on('leave_story')
    def handle_leave(data):
        """Leave a story room."""
        session_id = data.get('session_id')
        if session_id:
            leave_room(session_id)
            emit('left', {'room': session_id})
    
    @socketio.on('interaction')
    def handle_interaction(data):
        """Handle real-time interaction and generate story update."""
        session_id = data.get('session_id')
        interaction = data.get('interaction')
        
        if not session_id:
            emit('error', {'message': 'Session ID required'})
            return
        
        user = app.db.get_user_by_session(session_id)
        if not user:
            emit('error', {'message': 'Invalid session'})
            return
        
        # Record interaction
        if interaction:
            app.db.record_interaction(
                user_id=user.id,
                interaction_type=interaction.get('type', 'unknown'),
                data=interaction
            )
        
        # Get generator
        generator = app.generators.get(session_id)
        if not generator:
            generator = StoryGenerator()
            app.generators[session_id] = generator
        
        # Generate new segment
        latest = app.db.get_latest_segment(user.id)
        sequence_number = (latest.sequence_number + 1) if latest else 0
        
        content = generator.generate_segment(interaction)
        
        segment = app.db.create_story_segment(
            user_id=user.id,
            content=content,
            sequence_number=sequence_number,
            parent_id=latest.id if latest else None
        )
        
        # Emit to room
        emit('story_update', {
            'segment': segment.to_dict(),
            'context': generator.get_context_summary()
        }, room=session_id)
    
    @socketio.on('merge_notification')
    def handle_merge_notification(data):
        """Notify a user about a merge request."""
        target_session_id = data.get('target_session_id')
        if target_session_id:
            emit('merge_request', data, room=target_session_id)


# Create default app instance
app = create_app()
socketio = create_socketio(app)
