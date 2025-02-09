import pytest
from datetime import datetime
import json

def test_create_study_session_success(client, app):
    """Test successful creation of a study session"""
    # First create test data
    with app.db.cursor() as cursor:
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
    with app.db.cursor() as cursor:
        cursor.execute('SELECT * FROM study_sessions WHERE id = ?', (data['id'],))
        session = cursor.fetchone()
        assert session is not None
        assert session['group_id'] == group_id
        assert session['study_activity_id'] == activity_id

def test_create_study_session_invalid_request(client):
    """Test study session creation with invalid request data"""
    # Test missing required field
    response = client.post('/api/study-sessions', json={
        'group_id': 1
        # Missing study_activity_id
    })
    assert response.status_code == 400
    assert b'Missing required field' in response.data
    
    # Test invalid field type
    response = client.post('/api/study-sessions', json={
        'group_id': 'not an integer',
        'study_activity_id': 1
    })
    assert response.status_code == 400
    assert b'Invalid type for field' in response.data
    
    # Test empty request
    response = client.post('/api/study-sessions', json={})
    assert response.status_code == 400
    assert b'Missing required field' in response.data
    
    # Test no JSON data
    response = client.post('/api/study-sessions')
    assert response.status_code == 400
    assert b'No data provided' in response.data

def test_create_study_session_nonexistent_references(client):
    """Test study session creation with non-existent group or activity IDs"""
    # Test non-existent group
    response = client.post('/api/study-sessions', json={
        'group_id': 99999,  # Non-existent group ID
        'study_activity_id': 1
    })
    assert response.status_code == 404
    assert b'Group with id' in response.data
    
    # Test non-existent activity
    response = client.post('/api/study-sessions', json={
        'group_id': 1,
        'study_activity_id': 99999  # Non-existent activity ID
    })
    assert response.status_code == 404
    assert b'Study activity with id' in response.data

@pytest.fixture
def client(app):
    """Test client fixture"""
    return app.test_client()

@pytest.fixture
def app():
    """Test app fixture with test database"""
    from app import create_app
    app = create_app()
    
    # Configure app for testing
    app.config['TESTING'] = True
    
    # Set up test database
    with app.db.cursor() as cursor:
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
    with app.db.cursor() as cursor:
        cursor.executescript('''
            DELETE FROM word_review_items;
            DELETE FROM study_sessions;
            DELETE FROM groups;
            DELETE FROM study_activities;
        ''')
        app.db.commit()
