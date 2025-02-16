# Implementation Plan: POST /study_sessions/:id/review Endpoint

This document outlines the step-by-step process to implement the POST `/study_sessions/:id/review` endpoint in the Language Portal backend.

## Overview
The endpoint will create a review for a specific study session. It will be accessible at `/api/study-sessions/:id/review` with the POST method.

## Prerequisites
- [ ] Review the existing study sessions code in `routes/study_sessions.py`
- [ ] Understand the database schema for `study_session_reviews` table
- [ ] Familiarize yourself with Flask route parameter handling and request processing

## Implementation Steps

### 1. Add the Route
- [ ] Add the `@app.route` decorator with POST method and URL parameter
- [ ] Add the `@cross_origin()` decorator for CORS support
```python
@app.route('/api/study-sessions/<int:session_id>/review', methods=['POST'])
@cross_origin()
def create_study_session_review(session_id):
    # Implementation will go here
    pass
```

### 2. Request Validation
- [ ] Add validation for required fields in request body:
  ```python
  required_fields = {
      'rating': int,  # Rating score for the session
      'feedback': str,  # Optional feedback text
      'completion_status': str  # Status of the study session (completed/abandoned)
  }
  ```
- [ ] Check if study session exists
- [ ] Validate if session_id is valid
- [ ] Check if all required fields are present
- [ ] Validate field types and value ranges
  - Rating should be between 1-5
  - Completion status should be one of the valid values
- [ ] Return 400 Bad Request if validation fails
- [ ] Return 404 Not Found if session doesn't exist

### 3. Database Operations
- [ ] Create SQL insert statement for study_session_reviews table:
  ```sql
  INSERT INTO study_session_reviews (
      session_id,
      rating,
      feedback,
      completion_status,
      created_at
  ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
  ```
- [ ] Execute the insert with proper parameters
- [ ] Update the study session status in study_sessions table
- [ ] Get the ID of the newly created review
- [ ] Fetch the complete review details using the new ID

### 4. Response Formatting
- [ ] Format the response JSON:
  ```python
  {
      "id": int,
      "session_id": int,
      "rating": int,
      "feedback": str,
      "completion_status": str,
      "created_at": datetime
  }
  ```
- [ ] Return 201 Created status code with the response

### 5. Error Handling
- [ ] Add try-except blocks for database operations
- [ ] Handle case where session is already reviewed
- [ ] Return appropriate error messages and status codes:
  - 400 for invalid input
  - 404 for session not found
  - 409 for already reviewed
  - 500 for server errors

### 6. Testing
- [ ] Test with valid input
- [ ] Test with invalid session ID
- [ ] Test with missing required fields
- [ ] Test with invalid rating values
- [ ] Test with invalid completion status
- [ ] Test reviewing same session multiple times
- [ ] Test with very long feedback text

### 7. Documentation
- [ ] Add API documentation with request/response examples
- [ ] Document error scenarios and responses
- [ ] Update API schema if using OpenAPI/Swagger

## Notes
- Ensure proper error messages are returned for all validation failures
- Consider adding a check to prevent multiple reviews for the same session
- Consider adding user authentication check if required
- Consider adding rate limiting for the endpoint
