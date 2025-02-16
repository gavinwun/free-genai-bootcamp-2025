import pytest
from datetime import datetime
import json
import os
import sys
from lib.db import Db

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    """Test app fixture with test database"""
    from app import create_app
    
    # Use an in-memory SQLite database for testing
    test_config = {
        'TESTING': True,
        'DATABASE': ':memory:'
    }
    
    app = create_app(test_config)
    
    # Create an application context
    ctx = app.app_context()
    ctx.push()
    
    # Set up test database
    db = app.db
    cursor = db.cursor()
    
    # Create all tables using the setup_tables method
    db.setup_tables(cursor)
    
    yield app
    
    # Clean up test database after tests
    cursor = db.cursor()
    cursor.executescript('''
        DELETE FROM word_review_items;
        DELETE FROM study_sessions;
        DELETE FROM groups;
        DELETE FROM study_activities;
    ''')
    db.commit()
    
    # Pop the application context
    ctx.pop()

@pytest.fixture
def client(app):
    """Test client fixture that provides the application context"""
    return app.test_client()

def test_create_study_session_success(client, app):
    """Test successful creation of a study session"""
    # First create test data
    db = app.db
    cursor = db.cursor()
    
    # Create a test group
    cursor.execute('''
        INSERT INTO groups (name) 
        VALUES (?)
    ''', ('Test Group',))
    group_id = cursor.lastrowid
    
    # Create a test study activity
    cursor.execute('''
        INSERT INTO study_activities (name, url) 
        VALUES (?, ?)
    ''', ('Test Activity', 'https://example.com/activity'))
    activity_id = cursor.lastrowid
    
    db.commit()

    # Test creating a study session
    response = client.post('/api/study-sessions', json={
        'group_id': group_id,
        'study_activity_id': activity_id
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify response structure
    assert 'id' in data
    assert data['group_id'] == group_id
    assert data['group_name'] == 'Test Group'
    assert data['activity_id'] == activity_id
    assert data['activity_name'] == 'Test Activity'
    assert 'created_at' in data
    assert data['review_items_count'] == 0
    
    # Verify data was actually saved
    cursor = db.cursor()
    cursor.execute('SELECT * FROM study_sessions WHERE id = ?', (data['id'],))
    session = cursor.fetchone()
    assert session is not None
    assert session['group_id'] == group_id
    assert session['study_activity_id'] == activity_id

def test_create_study_session_invalid_request(client, app):
    """Test study session creation with invalid request data"""
    # Create a valid activity first for type validation test
    db = app.db
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO study_activities (name, url) 
        VALUES (?, ?)
    ''', ('Test Activity', 'https://example.com/activity'))
    valid_activity_id = cursor.lastrowid
    db.commit()
    
    # Test missing required field
    response = client.post('/api/study-sessions', json={
        'group_id': 1
        # Missing study_activity_id
    })
    assert response.status_code == 400
    assert b'Missing required field: study_activity_id' in response.data
    
    # Test invalid field type
    response = client.post('/api/study-sessions', json={
        'group_id': 'not an integer',
        'study_activity_id': valid_activity_id
    })
    assert response.status_code == 400
    assert b'Invalid type for field group_id' in response.data
    
    # Test empty request
    response = client.post('/api/study-sessions', json={})
    assert response.status_code == 400
    assert b'Missing required field: group_id' in response.data

def test_create_study_session_nonexistent_references(client, app):
    """Test study session creation with non-existent group or activity IDs"""
    # Create a valid group and activity first
    db = app.db
    cursor = db.cursor()
    
    # Create a test group
    cursor.execute('''
        INSERT INTO groups (name) 
        VALUES (?)
    ''', ('Test Group',))
    valid_group_id = cursor.lastrowid
    
    # Create a test study activity
    cursor.execute('''
        INSERT INTO study_activities (name, url) 
        VALUES (?, ?)
    ''', ('Test Activity', 'https://example.com/activity'))
    valid_activity_id = cursor.lastrowid
    
    db.commit()
    
    # Test non-existent group
    response = client.post('/api/study-sessions', json={
        'group_id': 99999,  # Non-existent group ID
        'study_activity_id': valid_activity_id
    })
    assert response.status_code == 404
    assert b'Group with id' in response.data
    
    # Test non-existent activity
    response = client.post('/api/study-sessions', json={
        'group_id': valid_group_id,
        'study_activity_id': 99999  # Non-existent activity ID
    })
    assert response.status_code == 404
    assert b'Study activity with id' in response.data

def test_create_study_session_invalid_json(client, app):
    """Test study session creation with invalid JSON data"""
    # Test wrong content type
    response = client.post('/api/study-sessions', 
                         data='not json',
                         content_type='text/plain')
    assert response.status_code == 400
    assert b'Content-Type must be application/json' in response.data
    
    # Test invalid JSON
    response = client.post('/api/study-sessions', 
                         data='not json',
                         content_type='application/json')
    assert response.status_code == 400
    assert b'Invalid JSON data' in response.data
    
    # Test empty data
    response = client.post('/api/study-sessions', 
                         data='null',
                         content_type='application/json')
    assert response.status_code == 400
    assert b'No data provided' in response.data

def test_create_study_session_review_success(client, app):
    """Test successful creation of a study session review"""
    # First create a test group and study activity
    cursor = app.db.cursor()
    cursor.execute('INSERT INTO groups (name) VALUES (?)', ('Test Group',))
    group_id = cursor.lastrowid
    
    cursor.execute('INSERT INTO study_activities (name, url) VALUES (?, ?)', ('Test Activity', 'http://example.com/test'))
    activity_id = cursor.lastrowid
    
    # Create a study session
    cursor.execute('''
        INSERT INTO study_sessions (group_id, study_activity_id)
        VALUES (?, ?)
    ''', (group_id, activity_id))
    session_id = cursor.lastrowid
    app.db.commit()
    
    # Test data for review
    review_data = {
        'rating': 4,
        'feedback': 'Great study session!',
        'completion_status': 'completed'
    }
    
    # Create review
    response = client.post(
        f'/api/study-sessions/{session_id}/review',
        json=review_data,
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    # Verify response data
    assert data['session_id'] == session_id
    assert data['rating'] == review_data['rating']
    assert data['feedback'] == review_data['feedback']
    assert data['completion_status'] == review_data['completion_status']
    assert 'created_at' in data
    
    # Verify database state
    cursor.execute('SELECT status FROM study_sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()
    assert session['status'] == review_data['completion_status']

def test_create_study_session_review_nonexistent_session(client, app):
    """Test review creation for non-existent study session"""
    review_data = {
        'rating': 4,
        'feedback': 'Great session!',
        'completion_status': 'completed'
    }
    
    response = client.post(
        '/api/study-sessions/999/review',
        json=review_data,
        content_type='application/json'
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'not found' in data['error'].lower()

def test_create_study_session_review_invalid_data(client, app):
    """Test review creation with invalid data"""
    # First create a test session
    cursor = app.db.cursor()
    cursor.execute('INSERT INTO groups (name) VALUES (?)', ('Test Group',))
    group_id = cursor.lastrowid
    cursor.execute('INSERT INTO study_activities (name, url) VALUES (?, ?)', ('Test Activity', 'http://example.com/test'))
    activity_id = cursor.lastrowid
    cursor.execute('''
        INSERT INTO study_sessions (group_id, study_activity_id)
        VALUES (?, ?)
    ''', (group_id, activity_id))
    session_id = cursor.lastrowid
    app.db.commit()
    
    # Test cases with invalid data
    invalid_test_cases = [
        (
            {'rating': 'invalid', 'completion_status': 'completed'},
            'Invalid type for field rating'
        ),
        (
            {'rating': 6, 'completion_status': 'completed'},
            'Rating must be between 1 and 5'
        ),
        (
            {'rating': 4, 'completion_status': 'invalid_status'},
            'Completion status must be one of'
        ),
        (
            {'completion_status': 'completed'},
            'Missing required field: rating'
        )
    ]
    
    for test_data, expected_error in invalid_test_cases:
        response = client.post(
            f'/api/study-sessions/{session_id}/review',
            json=test_data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert expected_error in data['error']

def test_create_study_session_review_duplicate(client, app):
    """Test attempting to create duplicate review for a session"""
    # First create a test session
    cursor = app.db.cursor()
    cursor.execute('INSERT INTO groups (name) VALUES (?)', ('Test Group',))
    group_id = cursor.lastrowid
    cursor.execute('INSERT INTO study_activities (name, url) VALUES (?, ?)', ('Test Activity', 'http://example.com/test'))
    activity_id = cursor.lastrowid
    cursor.execute('''
        INSERT INTO study_sessions (group_id, study_activity_id)
        VALUES (?, ?)
    ''', (group_id, activity_id))
    session_id = cursor.lastrowid
    app.db.commit()
    
    review_data = {
        'rating': 4,
        'feedback': 'Great session!',
        'completion_status': 'completed'
    }
    
    # Create first review
    response = client.post(
        f'/api/study-sessions/{session_id}/review',
        json=review_data,
        content_type='application/json'
    )
    assert response.status_code == 201
    
    # Attempt to create second review
    response = client.post(
        f'/api/study-sessions/{session_id}/review',
        json=review_data,
        content_type='application/json'
    )
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data
    assert 'already has a review' in data['error']
