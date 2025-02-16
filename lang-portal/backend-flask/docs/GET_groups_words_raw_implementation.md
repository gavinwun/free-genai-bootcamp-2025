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
- [x] Add the `@app.route` decorator with GET method and URL parameter
- [x] Add the `@cross_origin()` decorator for CORS support
```python
@app.route('/groups/<int:id>/words/raw', methods=['GET'])
@cross_origin()
def get_group_words_raw(id):
    # Implementation will go here
    pass
```

### 2. Request Validation
- [x] Validate if group_id is valid
- [x] Check if group exists
- [x] Return 404 Not Found if group doesn't exist

### 3. Database Operations
- [x] Create SQL query to fetch all words for the group:
  ```sql
  SELECT 
      w.id,
      w.kanji,
      w.romaji,
      w.english,
      w.parts
  FROM word_groups wg
  JOIN words w ON wg.word_id = w.id
  WHERE wg.group_id = ?
  ORDER BY w.kanji ASC
  ```
- [x] Execute the query with proper parameters
- [x] Fetch all results

### 4. Response Formatting
- [x] Format the response JSON:
  ```python
  {
      "group_id": int,
      "group_name": str,
      "words": [
          {
              "id": int,
              "kanji": str,
              "romaji": str,
              "english": str,
              "parts": object     # parsed JSON object
          },
          ...
      ],
      "total_words": int
  }
  ```
- [x] Return 200 OK status code with the response

### 5. Error Handling
- [x] Add try-except blocks for database operations
- [x] Return appropriate error messages and status codes:
  - 404 for group not found
  - 500 for server errors

### 6. Testing
- [x] Test with valid group ID
- [x] Test with non-existent group ID
- [x] Test with empty group (no words)
- [x] Test with group containing multiple words
- [x] Test error scenarios

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
            "kanji": "今日",
            "romaji": "kyou",
            "english": "today",
            "parts": {
                "type": "noun"
            }
        },
        {
            "id": 2,
            "kanji": "明日",
            "romaji": "ashita",
            "english": "tomorrow",
            "parts": {
                "type": "noun"
            }
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
- Words are sorted alphabetically by the kanji field
- For large groups, consider using appropriate database indexing
- Response includes both group metadata and the complete list of words
