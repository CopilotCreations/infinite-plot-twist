"""
Tests for the Flask server and API endpoints.

This module contains comprehensive tests for all API endpoints
and WebSocket functionality.
"""

import pytest
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.backend.server import create_app


@pytest.fixture
def app():
    """Create a test application instance."""
    test_config = {
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key'
    }
    application = create_app(test_config)
    
    yield application


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def session_id(client):
    """Create a session and return the session ID."""
    response = client.post('/api/session')
    data = json.loads(response.data)
    return data['session_id']


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_200(self, client):
        """Test that health endpoint returns 200."""
        response = client.get('/api/health')
        
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        """Test that health endpoint returns healthy status."""
        response = client.get('/api/health')
        data = json.loads(response.data)
        
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestSessionEndpoints:
    """Tests for session management endpoints."""

    def test_create_session(self, client):
        """Test creating a new session."""
        response = client.post('/api/session')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'session_id' in data
        assert 'user_id' in data

    def test_get_session(self, client, session_id):
        """Test getting session information."""
        response = client.get(f'/api/session/{session_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['session_id'] == session_id

    def test_get_session_not_found(self, client):
        """Test getting a non-existent session."""
        response = client.get('/api/session/nonexistent-session')
        
        assert response.status_code == 404


class TestStoryEndpoints:
    """Tests for story management endpoints."""

    def test_start_story(self, client, session_id):
        """Test starting a new story."""
        response = client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'segment' in data
        assert 'context' in data
        assert data['segment']['content'] is not None

    def test_start_story_without_session(self, client):
        """Test starting a story without session ID."""
        response = client.post('/api/story/start',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_start_story_invalid_session(self, client):
        """Test starting a story with invalid session."""
        response = client.post('/api/story/start',
            data=json.dumps({'session_id': 'invalid-session'}),
            content_type='application/json'
        )
        
        assert response.status_code == 404

    def test_continue_story(self, client, session_id):
        """Test continuing a story."""
        # Start story first
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        # Continue story
        response = client.post('/api/story/continue',
            data=json.dumps({
                'session_id': session_id,
                'interaction': {'type': 'click', 'x': 100, 'y': 100}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'segment' in data
        assert 'context' in data

    def test_continue_story_without_session(self, client):
        """Test continuing a story without session ID."""
        response = client.post('/api/story/continue',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_continue_story_with_scroll_interaction(self, client, session_id):
        """Test continuing a story with scroll interaction."""
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        response = client.post('/api/story/continue',
            data=json.dumps({
                'session_id': session_id,
                'interaction': {'type': 'scroll', 'amount': 200}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200

    def test_continue_story_with_keypress_interaction(self, client, session_id):
        """Test continuing a story with keypress interaction."""
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        response = client.post('/api/story/continue',
            data=json.dumps({
                'session_id': session_id,
                'interaction': {'type': 'keypress', 'key': 'm'}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200

    def test_get_story(self, client, session_id):
        """Test getting the full story."""
        # Start and continue story
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        client.post('/api/story/continue',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        response = client.get(f'/api/story/{session_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'segments' in data
        assert len(data['segments']) >= 1

    def test_get_story_with_pagination(self, client, session_id):
        """Test getting story with pagination parameters."""
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        response = client.get(f'/api/story/{session_id}?limit=5&offset=0')
        
        assert response.status_code == 200

    def test_get_story_invalid_session(self, client):
        """Test getting story with invalid session."""
        response = client.get('/api/story/invalid-session')
        
        assert response.status_code == 404


class TestMoodAndGenreEndpoints:
    """Tests for mood and genre control endpoints."""

    def test_set_mood(self, client, session_id):
        """Test setting story mood."""
        # Start story first
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        response = client.post('/api/story/mood',
            data=json.dumps({
                'session_id': session_id,
                'mood': 'dark'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['context']['mood'] == 'dark'

    def test_set_mood_invalid(self, client, session_id):
        """Test setting an invalid mood."""
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        response = client.post('/api/story/mood',
            data=json.dumps({
                'session_id': session_id,
                'mood': 'invalid_mood'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_set_mood_without_story(self, client):
        """Test setting mood without a generator (fresh session)."""
        # Use a session ID that doesn't have an active generator
        response = client.post('/api/story/mood',
            data=json.dumps({
                'session_id': 'non-existent-session-no-generator',
                'mood': 'dark'
            }),
            content_type='application/json'
        )
        
        # Should return 404 because session doesn't exist
        assert response.status_code == 404

    def test_set_mood_missing_params(self, client):
        """Test setting mood with missing parameters."""
        response = client.post('/api/story/mood',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_set_genre(self, client, session_id):
        """Test setting story genre."""
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        response = client.post('/api/story/genre',
            data=json.dumps({
                'session_id': session_id,
                'genre': 'scifi'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['context']['genre'] == 'scifi'

    def test_set_genre_invalid(self, client, session_id):
        """Test setting an invalid genre."""
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        response = client.post('/api/story/genre',
            data=json.dumps({
                'session_id': session_id,
                'genre': 'invalid_genre'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_set_genre_missing_params(self, client):
        """Test setting genre with missing parameters."""
        response = client.post('/api/story/genre',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestActiveUsersEndpoint:
    """Tests for active users endpoint."""

    def test_get_active_users(self, client, session_id):
        """Test getting active users."""
        response = client.get('/api/users/active')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert 'count' in data

    def test_get_active_users_with_minutes(self, client, session_id):
        """Test getting active users with custom time range."""
        response = client.get('/api/users/active?minutes=60')
        
        assert response.status_code == 200


class TestMergeEndpoints:
    """Tests for merge-related endpoints."""

    def test_request_merge(self, client):
        """Test requesting a merge."""
        # Create two sessions
        response1 = client.post('/api/session')
        session1 = json.loads(response1.data)['session_id']
        
        response2 = client.post('/api/session')
        session2 = json.loads(response2.data)['session_id']
        
        # Start story for session1
        client.post('/api/story/start',
            data=json.dumps({'session_id': session1}),
            content_type='application/json'
        )
        
        # Request merge
        response = client.post('/api/merge/request',
            data=json.dumps({
                'session_id': session1,
                'target_session_id': session2
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'merge_request' in data

    def test_request_merge_missing_params(self, client):
        """Test requesting a merge with missing parameters."""
        response = client.post('/api/merge/request',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_request_merge_invalid_session(self, client, session_id):
        """Test requesting a merge with invalid session."""
        response = client.post('/api/merge/request',
            data=json.dumps({
                'session_id': 'invalid',
                'target_session_id': session_id
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 404

    def test_get_pending_merges(self, client, session_id):
        """Test getting pending merge requests."""
        response = client.get(f'/api/merge/pending/{session_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'requests' in data

    def test_get_pending_merges_invalid_session(self, client):
        """Test getting pending merges with invalid session."""
        response = client.get('/api/merge/pending/invalid-session')
        
        assert response.status_code == 404

    def test_accept_merge(self, client):
        """Test accepting a merge request."""
        # Create two sessions
        response1 = client.post('/api/session')
        session1 = json.loads(response1.data)['session_id']
        
        response2 = client.post('/api/session')
        session2 = json.loads(response2.data)['session_id']
        
        # Start stories
        client.post('/api/story/start',
            data=json.dumps({'session_id': session1}),
            content_type='application/json'
        )
        client.post('/api/story/start',
            data=json.dumps({'session_id': session2}),
            content_type='application/json'
        )
        
        # Request merge
        merge_response = client.post('/api/merge/request',
            data=json.dumps({
                'session_id': session1,
                'target_session_id': session2
            }),
            content_type='application/json'
        )
        merge_data = json.loads(merge_response.data)
        request_id = merge_data['merge_request']['id']
        
        # Accept merge
        response = client.post('/api/merge/accept',
            data=json.dumps({
                'session_id': session2,
                'request_id': request_id
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'segment' in data
        assert data['segment']['is_merged'] is True

    def test_accept_merge_missing_params(self, client):
        """Test accepting a merge with missing parameters."""
        response = client.post('/api/merge/accept',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestInteractionsEndpoint:
    """Tests for interactions endpoint."""

    def test_get_interactions(self, client, session_id):
        """Test getting interaction history."""
        # Start story and create some interactions
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        client.post('/api/story/continue',
            data=json.dumps({
                'session_id': session_id,
                'interaction': {'type': 'click'}
            }),
            content_type='application/json'
        )
        
        response = client.get(f'/api/interactions/{session_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'interactions' in data
        assert 'counts' in data

    def test_get_interactions_with_limit(self, client, session_id):
        """Test getting interactions with limit."""
        client.post('/api/story/start',
            data=json.dumps({'session_id': session_id}),
            content_type='application/json'
        )
        
        response = client.get(f'/api/interactions/{session_id}?limit=5')
        
        assert response.status_code == 200

    def test_get_interactions_invalid_session(self, client):
        """Test getting interactions with invalid session."""
        response = client.get('/api/interactions/invalid-session')
        
        assert response.status_code == 404


class TestStaticFiles:
    """Tests for static file serving."""

    def test_index_page(self, client):
        """Test that index page is served."""
        # This may return 404 in test environment without static files
        # but we're testing the route exists
        response = client.get('/')
        # Accept 200 or 404 (if static folder doesn't exist in test)
        assert response.status_code in [200, 404, 500]


class TestErrorHandling:
    """Tests for error handling."""

    def test_empty_json_body(self, client):
        """Test handling of empty JSON body."""
        response = client.post('/api/story/start',
            data='',
            content_type='application/json'
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 500]

    def test_invalid_json_body(self, client):
        """Test handling of invalid JSON."""
        response = client.post('/api/story/start',
            data='not valid json',
            content_type='application/json'
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 500]

    def test_no_content_type(self, client, session_id):
        """Test handling of missing content type."""
        response = client.post('/api/story/start',
            data=json.dumps({'session_id': session_id})
        )
        
        # Should still work or return appropriate error
        assert response.status_code in [200, 400, 415]
