import pytest
from datetime import datetime
import json
import os
import sys

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
    cursor = app.db.cursor()
    
    # Create required tables if they don't exist
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        );
        
        CREATE TABLE IF NOT EXISTS study_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        );
        
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            study_activity_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(id),
            FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
        );
        
        CREATE TABLE IF NOT EXISTS word_review_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_session_id INTEGER NOT NULL,
            FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
        );
    ''')
    app.db.commit()
    
    yield app
    
    # Clean up test database after tests
    cursor = app.db.cursor()
    cursor.executescript('''
        DELETE FROM word_review_items;
        DELETE FROM study_sessions;
        DELETE FROM groups;
        DELETE FROM study_activities;
    ''')
    app.db.commit()
    
    # Pop the application context
    ctx.pop()

@pytest.fixture
def client(app):
    """Test client fixture that provides the application context"""
    return app.test_client()

def test_create_study_session_success(client, app):
    """Test successful creation of a study session"""
    # First create test data
    cursor = app.db.cursor()
    
    # Create a test group
    cursor.execute('''
        INSERT INTO groups (name, description) 
        VALUES (?, ?)
    ''', ('Test Group', 'A test group'))
    group_id = cursor.lastrowid
    
    # Create a test study activity
    cursor.execute('''
        INSERT INTO study_activities (name, description) 
        VALUES (?, ?)
    ''', ('Test Activity', 'A test activity'))
    activity_id = cursor.lastrowid
    
    app.db.commit()

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
    cursor = app.db.cursor()
    cursor.execute('SELECT * FROM study_sessions WHERE id = ?', (data['id'],))
    session = cursor.fetchone()
    assert session is not None
    assert session['group_id'] == group_id
    assert session['study_activity_id'] == activity_id

def test_create_study_session_invalid_request(client, app):
    """Test study session creation with invalid request data"""
    # Create a valid activity first for type validation test
    cursor = app.db.cursor()
    cursor.execute('''
        INSERT INTO study_activities (name, description) 
        VALUES (?, ?)
    ''', ('Test Activity', 'A test activity'))
    valid_activity_id = cursor.lastrowid
    app.db.commit()
    
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

def test_create_study_session_nonexistent_references(client, app):
    """Test study session creation with non-existent group or activity IDs"""
    # Create a valid group and activity first
    cursor = app.db.cursor()
    
    # Create a test group
    cursor.execute('''
        INSERT INTO groups (name, description) 
        VALUES (?, ?)
    ''', ('Test Group', 'A test group'))
    valid_group_id = cursor.lastrowid
    
    # Create a test study activity
    cursor.execute('''
        INSERT INTO study_activities (name, description) 
        VALUES (?, ?)
    ''', ('Test Activity', 'A test activity'))
    valid_activity_id = cursor.lastrowid
    
    app.db.commit()
    
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
