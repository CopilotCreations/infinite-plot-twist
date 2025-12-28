"""
Backend package for Infinite Story Web.

This package provides the Flask server, story generation engine,
and WebSocket handlers for real-time collaborative features.
"""

from .story_generator import StoryGenerator, Mood, Genre, StoryContext
from .server import create_app, create_socketio, app, socketio

__all__ = [
    'StoryGenerator',
    'Mood',
    'Genre',
    'StoryContext',
    'create_app',
    'create_socketio',
    'app',
    'socketio'
]
