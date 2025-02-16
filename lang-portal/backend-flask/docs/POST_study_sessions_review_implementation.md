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
- [x] Add the `@app.route` decorator with POST method and URL parameter
- [x] Add the `@cross_origin()` decorator for CORS support
```python
@app.route('/api/study-sessions/<int:session_id>/review', methods=['POST'])
@cross_origin()
def create_study_session_review(session_id):
    # Implementation will go here
    pass
```

### 2. Request Validation
- [x] Add validation for required fields in request body:
  ```python
  required_fields = {
      'rating': int,  # Rating score for the session
      'feedback': str,  # Optional feedback text
      'completion_status': str  # Status of the study session (completed/abandoned)
  }
  ```
- [x] Check if study session exists
- [x] Validate if session_id is valid
- [x] Check if all required fields are present
- [x] Validate field types and value ranges
  - Rating should be between 1-5
  - Completion status should be one of the valid values
- [x] Return 400 Bad Request if validation fails
- [x] Return 404 Not Found if session doesn't exist

### 3. Database Operations
- [x] Create SQL insert statement for study_session_reviews table:
  ```sql
  INSERT INTO study_session_reviews (
      session_id,
      rating,
      feedback,
      completion_status,
      created_at
  ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
  ```
- [x] Execute the insert with proper parameters
- [x] Get the ID of the newly created review
- [x] Fetch the complete review details using the new ID
- [x] Update the study session status in study_sessions table

### 4. Response Formatting
- [x] Format the response JSON:
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
- [x] Return 201 Created status code with the response

### 5. Error Handling
- [x] Add try-except blocks for database operations
- [x] Handle case where session is already reviewed
- [x] Return appropriate error messages and status codes:
  - 400 for invalid input
  - 404 for session not found
  - 409 for already reviewed
  - 500 for server errors

### 6. Testing
- [x] Test with valid input
- [x] Test with invalid session ID
- [x] Test with missing required fields
- [x] Test with invalid rating values
- [x] Test with invalid completion status
- [x] Test reviewing same session multiple times
- [x] Test with very long feedback text

### 7. Documentation
- [x] Add API documentation with request/response examples
- [x] Document error scenarios and responses
- [x] Update API schema if using OpenAPI/Swagger

## API Documentation

### POST /api/study-sessions/:id/review

Create a review for a specific study session.

#### Request

```http
POST /api/study-sessions/123/review
Content-Type: application/json

{
    "rating": 4,
    "feedback": "Great study session! Learned a lot about kanji.",
    "completion_status": "completed"
}
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| rating | integer | Yes | Rating score between 1-5 |
| feedback | string | No | Optional feedback text |
| completion_status | string | Yes | Must be either 'completed' or 'abandoned' |

#### Successful Response

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": 456,
    "session_id": 123,
    "rating": 4,
    "feedback": "Great study session! Learned a lot about kanji.",
    "completion_status": "completed",
    "created_at": "2025-02-16T19:39:50+13:00"
}
```

#### Error Responses

##### Invalid Request Format
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "error": "Content-Type must be application/json"
}
```

##### Missing Required Fields
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "error": "Missing required field: rating"
}
```

##### Invalid Field Values
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "error": "Rating must be between 1 and 5"
}
```

##### Non-existent Session
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "error": "Study session with id 123 not found"
}
```

##### Duplicate Review
```http
HTTP/1.1 409 Conflict
Content-Type: application/json

{
    "error": "Study session already has a review"
}
```

#### Notes

- The study session's status will be updated to match the review's completion_status
- Once a review is created for a session, no additional reviews can be added
- The rating must be an integer between 1 and 5
- The completion_status must be either 'completed' or 'abandoned'
- Feedback is optional and can be any text

## Notes
- Ensure proper error messages are returned for all validation failures
- Consider adding a check to prevent multiple reviews for the same session
- Consider adding user authentication check if required
- Consider adding rate limiting for the endpoint
