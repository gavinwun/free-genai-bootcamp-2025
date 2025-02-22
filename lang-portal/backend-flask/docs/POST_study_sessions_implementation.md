# Implementation Plan: POST /study_sessions Endpoint

This document outlines the step-by-step process to implement the POST `/study_sessions` endpoint in the Language Portal backend.

## Overview
The endpoint will create a new study session for a specific group and study activity. It will be accessible at `/api/study-sessions` with the POST method.

## Prerequisites
- [ ] Review the existing study sessions code in `routes/study_sessions.py`
- [ ] Understand the database schema for `study_sessions` table
- [ ] Familiarize yourself with Flask route decorators and request handling

## Implementation Steps

### 1. Add the Route
- [x] Add the `@app.route` decorator with POST method
- [x] Add the `@cross_origin()` decorator for CORS support
```python
@app.route('/api/study-sessions', methods=['POST'])
@cross_origin()
def create_study_session():
    # Implementation will go here
    pass
```

### 2. Request Validation
- [x] Add validation for required fields in request body:
  ```python
  required_fields = {
      'group_id': int,
      'study_activity_id': int
  }
  ```
- [x] Check if all required fields are present
- [x] Validate field types
- [x] Return 400 Bad Request if validation fails

### 3. Database Operations
- [x] Create SQL insert statement for study_sessions table:
  ```sql
  INSERT INTO study_sessions (group_id, study_activity_id)
  VALUES (?, ?)
  ```
- [x] Execute the insert with proper parameters
- [x] Get the ID of the newly created session
- [x] Fetch the complete session details using the new ID

### 4. Response Formatting
- [x] Format the response JSON to match the GET endpoint format:
  ```python
  {
    'id': session['id'],
    'group_id': session['group_id'],
    'group_name': session['group_name'],
    'activity_id': session['activity_id'],
    'activity_name': session['activity_name'],
    'created_at': session['created_at'],
    'review_items_count': session['review_items_count']
  }
  ```

### 5. Error Handling
- [x] Add try-except block for database operations
- [x] Handle foreign key constraint violations (invalid group_id or study_activity_id)
- [x] Return appropriate error messages and status codes

## Testing

### Manual Testing
- [ ] Test with valid request body:
```bash
curl -X POST http://localhost:5000/api/study-sessions \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1,
    "study_activity_id": 1
  }'
```

### Unit Test Code
Create a new test file `tests/test_study_sessions.py`:

```python
def test_create_study_session(client):
    # Test valid creation
    response = client.post('/api/study-sessions', json={
        'group_id': 1,
        'study_activity_id': 1
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'id' in data
    assert data['group_id'] == 1
    assert data['study_activity_id'] == 1
    assert 'created_at' in data
    
    # Test missing required field
    response = client.post('/api/study-sessions', json={
        'group_id': 1
    })
    assert response.status_code == 400
    
    # Test invalid group_id
    response = client.post('/api/study-sessions', json={
        'group_id': 999999,
        'study_activity_id': 1
    })
    assert response.status_code == 404
```

## Verification Checklist
- [ ] All required fields are validated
- [ ] Database insert works correctly
- [ ] Response format matches GET endpoint
- [ ] Error cases are handled appropriately
- [ ] CORS is working
- [ ] Unit tests pass
- [ ] Manual testing successful

## Notes
- The endpoint should return 200 OK for successful creation
- The endpoint should return 400 Bad Request for validation errors
- The endpoint should return 404 Not Found for invalid group_id or study_activity_id
- The endpoint should return 500 Internal Server Error for database errors
