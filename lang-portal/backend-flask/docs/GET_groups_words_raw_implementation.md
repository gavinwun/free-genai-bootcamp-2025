# Implementation Plan: GET /groups/:id/words/raw Endpoint

This document outlines the step-by-step process to implement the GET `/groups/:id/words/raw` endpoint in the Language Portal backend.

## Overview
The endpoint will retrieve all words associated with a specific group in a raw format, without pagination. This is useful for data export or bulk operations.

## Prerequisites
- [ ] Review the existing groups code in `routes/groups.py`
- [ ] Understand the database schema for `groups` and `words` tables
- [ ] Familiarize yourself with Flask route decorators and request handling

## Implementation Steps

### 1. Add the Route
- [ ] Add the `@app.route` decorator with GET method and URL parameter
- [ ] Add the `@cross_origin()` decorator for CORS support
```python
@app.route('/groups/<int:id>/words/raw', methods=['GET'])
@cross_origin()
def get_group_words_raw(id):
    # Implementation will go here
    pass
```

### 2. Request Validation
- [ ] Validate if group_id is valid
- [ ] Check if group exists
- [ ] Return 404 Not Found if group doesn't exist

### 3. Database Operations
- [ ] Create SQL query to fetch all words for the group:
  ```sql
  SELECT 
      w.id,
      w.word,
      w.reading,
      w.meaning,
      w.part_of_speech,
      w.level,
      w.created_at
  FROM words w
  JOIN group_words gw ON gw.word_id = w.id
  WHERE gw.group_id = ?
  ORDER BY w.word ASC
  ```
- [ ] Execute the query with proper parameters
- [ ] Fetch all results

### 4. Response Formatting
- [ ] Format the response JSON:
  ```python
  {
      "group_id": int,
      "group_name": str,
      "words": [
          {
              "id": int,
              "word": str,
              "reading": str,
              "meaning": str,
              "part_of_speech": str,
              "level": str,
              "created_at": datetime
          },
          ...
      ],
      "total_words": int
  }
  ```
- [ ] Return 200 OK status code with the response

### 5. Error Handling
- [ ] Add try-except blocks for database operations
- [ ] Return appropriate error messages and status codes:
  - 404 for group not found
  - 500 for server errors

### 6. Testing
- [ ] Test with valid group ID
- [ ] Test with non-existent group ID
- [ ] Test with empty group (no words)
- [ ] Test with group containing multiple words
- [ ] Test error scenarios

### 7. Documentation
- [ ] Add API documentation with request/response examples
- [ ] Document error scenarios and responses
- [ ] Update API schema if using OpenAPI/Swagger

## API Documentation

### GET /groups/:id/words/raw

Retrieve all words associated with a specific group in raw format (no pagination).

#### Request

```http
GET /groups/123/words/raw
```

#### Parameters
None required in request body. Group ID is specified in the URL.

#### Successful Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "group_id": 123,
    "group_name": "JLPT N5 Vocabulary",
    "words": [
        {
            "id": 1,
            "word": "今日",
            "reading": "きょう",
            "meaning": "today",
            "part_of_speech": "noun",
            "level": "N5",
            "created_at": "2025-02-16T19:39:50+13:00"
        },
        {
            "id": 2,
            "word": "明日",
            "reading": "あした",
            "meaning": "tomorrow",
            "part_of_speech": "noun",
            "level": "N5",
            "created_at": "2025-02-16T19:39:50+13:00"
        }
    ],
    "total_words": 2
}
```

#### Error Responses

##### Non-existent Group
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
    "error": "Group with id 123 not found"
}
```

##### Server Error
```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
    "error": "Failed to fetch group words"
}
```

#### Notes

- This endpoint returns all words without pagination
- Words are sorted alphabetically by the word field
- For large groups, consider using appropriate database indexing
- Response includes both group metadata and the complete list of words
