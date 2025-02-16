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
        DELETE FROM word_groups;
        DELETE FROM words;
        DELETE FROM groups;
        DELETE FROM study_activities;
    ''')
    db.commit()
    
    # Pop the application context
    ctx.pop()

@pytest.fixture
def client(app):
    """Test client fixture"""
    return app.test_client()

def test_get_group_words_raw_success(client, app):
    """Test successful retrieval of raw words for a group"""
    # Create test group
    cursor = app.db.cursor()
    cursor.execute('INSERT INTO groups (name) VALUES (?)', ('Test Group',))
    group_id = cursor.lastrowid
    
    # Create test words
    test_words = [
        ('今日', 'kyou', 'today', '{"type": "noun"}'),
        ('明日', 'ashita', 'tomorrow', '{"type": "noun"}'),
        ('昨日', 'kinou', 'yesterday', '{"type": "noun"}')
    ]
    
    for kanji, romaji, english, parts in test_words:
        cursor.execute('''
            INSERT INTO words (kanji, romaji, english, parts)
            VALUES (?, ?, ?, ?)
        ''', (kanji, romaji, english, parts))
        word_id = cursor.lastrowid
        
        # Associate word with group
        cursor.execute('''
            INSERT INTO word_groups (word_id, group_id)
            VALUES (?, ?)
        ''', (word_id, group_id))
    
    app.db.commit()
    
    # Test the endpoint
    response = client.get(f'/groups/{group_id}/words/raw')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify response structure
    assert data['group_id'] == group_id
    assert data['group_name'] == 'Test Group'
    assert 'words' in data
    assert 'total_words' in data
    assert data['total_words'] == len(test_words)
    
    # Verify word data
    words = data['words']
    assert len(words) == len(test_words)
    for word in words:
        assert all(key in word for key in ['id', 'kanji', 'romaji', 'english', 'parts'])

def test_get_group_words_raw_empty_group(client, app):
    """Test retrieval of words from an empty group"""
    # Create test group
    cursor = app.db.cursor()
    cursor.execute('INSERT INTO groups (name) VALUES (?)', ('Empty Group',))
    group_id = cursor.lastrowid
    app.db.commit()
    
    # Test the endpoint
    response = client.get(f'/groups/{group_id}/words/raw')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify empty response
    assert data['group_id'] == group_id
    assert data['group_name'] == 'Empty Group'
    assert data['words'] == []
    assert data['total_words'] == 0

def test_get_group_words_raw_nonexistent_group(client, app):
    """Test retrieval of words from a non-existent group"""
    response = client.get('/groups/999/words/raw')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'not found' in data['error'].lower()

def test_get_group_words_raw_multiple_words(client, app):
    """Test retrieval of multiple words with sorting"""
    # Create test group
    cursor = app.db.cursor()
    cursor.execute('INSERT INTO groups (name) VALUES (?)', ('Test Group',))
    group_id = cursor.lastrowid
    
    # Create test words in non-alphabetical order
    test_words = [
        ('食べる', 'taberu', 'to eat', '{"type": "verb"}'),
        ('あれ', 'are', 'that', '{"type": "pronoun"}'),
        ('いつ', 'itsu', 'when', '{"type": "adverb"}')
    ]
    
    for kanji, romaji, english, parts in test_words:
        cursor.execute('''
            INSERT INTO words (kanji, romaji, english, parts)
            VALUES (?, ?, ?, ?)
        ''', (kanji, romaji, english, parts))
        word_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO word_groups (word_id, group_id)
            VALUES (?, ?)
        ''', (word_id, group_id))
    
    app.db.commit()
    
    # Test the endpoint
    response = client.get(f'/groups/{group_id}/words/raw')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify words are sorted alphabetically
    words = data['words']
    assert len(words) == len(test_words)
    assert words[0]['kanji'] == 'あれ'  # Should come first alphabetically
    assert words[1]['kanji'] == 'いつ'
    assert words[2]['kanji'] == '食べる'
