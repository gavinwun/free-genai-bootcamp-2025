from flask import request, jsonify, g
from flask_cors import cross_origin
from datetime import datetime
import math
import sqlite3

def load(app):
  @app.route('/api/study-sessions', methods=['POST'])
  @cross_origin()
  def create_study_session():
    try:
      # Get request data
      if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
      
      try:
        data = request.get_json()
      except:
        return jsonify({'error': 'Invalid JSON data'}), 400
        
      if data is None:
        return jsonify({'error': 'No data provided'}), 400
      
      if not data:  # Empty JSON object
        return jsonify({'error': 'Missing required field: group_id'}), 400

      # Define required fields and their types
      required_fields = {
          'group_id': int,
          'study_activity_id': int
      }

      # Validate presence and types of required fields
      for field, field_type in required_fields.items():
          if field not in data:
              return jsonify({'error': f'Missing required field: {field}'}), 400
          
          try:
              data[field] = field_type(data[field])
          except (ValueError, TypeError):
              return jsonify({'error': f'Invalid type for field {field}. Expected {field_type.__name__}'}), 400

      cursor = app.db.cursor()
      
      # Verify that group_id exists
      cursor.execute('SELECT id FROM groups WHERE id = ?', (data['group_id'],))
      if not cursor.fetchone():
          return jsonify({'error': f'Group with id {data["group_id"]} does not exist'}), 404

      # Verify that study_activity_id exists
      cursor.execute('SELECT id FROM study_activities WHERE id = ?', (data['study_activity_id'],))
      if not cursor.fetchone():
          return jsonify({'error': f'Study activity with id {data["study_activity_id"]} does not exist'}), 404
      
      try:
          # Insert new study session
          cursor.execute('''
            INSERT INTO study_sessions (group_id, study_activity_id)
            VALUES (?, ?)
          ''', (data['group_id'], data['study_activity_id']))
          
          # Get the ID of the newly created session
          new_session_id = cursor.lastrowid
          
          # Fetch the complete session details
          cursor.execute('''
            SELECT 
              ss.id,
              ss.group_id,
              g.name as group_name,
              sa.id as activity_id,
              sa.name as activity_name,
              ss.created_at,
              COUNT(wri.id) as review_items_count
            FROM study_sessions ss
            JOIN groups g ON g.id = ss.group_id
            JOIN study_activities sa ON sa.id = ss.study_activity_id
            LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
            WHERE ss.id = ?
            GROUP BY ss.id
          ''', (new_session_id,))
          
          session = cursor.fetchone()
          app.db.commit()

          if not session:
            app.db.rollback()
            return jsonify({'error': 'Failed to create study session'}), 500

          # Return the newly created session in the same format as GET endpoint
          return jsonify({
            'id': session['id'],
            'group_id': session['group_id'],
            'group_name': session['group_name'],
            'activity_id': session['activity_id'],
            'activity_name': session['activity_name'],
            'created_at': session['created_at'],
            'review_items_count': session['review_items_count']
          })

      except sqlite3.IntegrityError as e:
          app.db.rollback()
          return jsonify({'error': 'Database integrity error. Please check if the provided IDs are valid.'}), 400
      except sqlite3.Error as e:
          app.db.rollback()
          return jsonify({'error': f'Database error: {str(e)}'}), 500

    except Exception as e:
      if 'app.db' in locals():
          app.db.rollback()
      return jsonify({'error': f'Server error: {str(e)}'}), 500

  @app.route('/api/study-sessions', methods=['GET'])
  @cross_origin()
  def get_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      # Get total count
      cursor.execute('''
        SELECT COUNT(*) as count 
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
      ''')
      total_count = cursor.fetchone()['count']

      # Get paginated sessions
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        GROUP BY ss.id
        ORDER BY ss.created_at DESC
        LIMIT ? OFFSET ?
      ''', (per_page, offset))
      sessions = cursor.fetchall()

      return jsonify({
        'items': [{
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time since we don't track end time
          'review_items_count': session['review_items_count']
        } for session in sessions],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      })
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions/<id>', methods=['GET'])
  @cross_origin()
  def get_study_session(id):
    try:
      cursor = app.db.cursor()
      
      # Get session details
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        WHERE ss.id = ?
        GROUP BY ss.id
      ''', (id,))
      
      session = cursor.fetchone()
      if not session:
        return jsonify({"error": "Study session not found"}), 404

      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      # Get the words reviewed in this session with their review status
      cursor.execute('''
        SELECT 
          w.*,
          COALESCE(SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END), 0) as session_correct_count,
          COALESCE(SUM(CASE WHEN wri.correct = 0 THEN 1 ELSE 0 END), 0) as session_wrong_count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
        GROUP BY w.id
        ORDER BY w.kanji
        LIMIT ? OFFSET ?
      ''', (id, per_page, offset))
      
      words = cursor.fetchall()

      # Get total count of words
      cursor.execute('''
        SELECT COUNT(DISTINCT w.id) as count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
      ''', (id,))
      
      total_count = cursor.fetchone()['count']

      return jsonify({
        'session': {
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time
          'review_items_count': session['review_items_count']
        },
        'words': [{
          'id': word['id'],
          'kanji': word['kanji'],
          'romaji': word['romaji'],
          'english': word['english'],
          'correct_count': word['session_correct_count'],
          'wrong_count': word['session_wrong_count']
        } for word in words],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      })
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions/<int:session_id>/review', methods=['POST'])
  @cross_origin()
  def create_study_session_review(session_id):
    try:
      # Validate request format
      if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
      
      try:
        data = request.get_json()
      except:
        return jsonify({'error': 'Invalid JSON data'}), 400
        
      if data is None:
        return jsonify({'error': 'No data provided'}), 400

      # Define required fields and their types
      required_fields = {
          'rating': int,
          'completion_status': str
      }
      
      # Check if session exists
      cursor = app.db.cursor()
      cursor.execute('SELECT id FROM study_sessions WHERE id = ?', (session_id,))
      session = cursor.fetchone()
      if not session:
        return jsonify({'error': f'Study session with id {session_id} not found'}), 404

      # Validate required fields
      for field, field_type in required_fields.items():
        if field not in data:
          return jsonify({'error': f'Missing required field: {field}'}), 400
        if not isinstance(data[field], field_type):
          return jsonify({'error': f'Invalid type for field {field}. Expected {field_type.__name__}'}), 400

      # Validate field values
      if not 1 <= data['rating'] <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

      valid_statuses = ['completed', 'abandoned']
      if data['completion_status'] not in valid_statuses:
        return jsonify({'error': f'Completion status must be one of: {", ".join(valid_statuses)}'}), 400

      # Check if session already has a review
      cursor.execute('SELECT id FROM study_session_reviews WHERE session_id = ?', (session_id,))
      existing_review = cursor.fetchone()
      if existing_review:
        return jsonify({'error': 'Study session already has a review'}), 409

      # Insert the review
      try:
          # First update the study session status
          cursor.execute('''
            UPDATE study_sessions 
            SET status = ?
            WHERE id = ?
          ''', (data['completion_status'], session_id))

          # Then insert the review
          cursor.execute('''
            INSERT INTO study_session_reviews (
                session_id,
                rating,
                feedback,
                completion_status,
                created_at
            ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
          ''', (
              session_id,
              data['rating'],
              data.get('feedback'),  # Optional field
              data['completion_status']
          ))
          
          # Get the ID of the newly created review
          new_review_id = cursor.lastrowid
          
          # Fetch the complete review details
          cursor.execute('''
            SELECT 
                id,
                session_id,
                rating,
                feedback,
                completion_status,
                created_at
            FROM study_session_reviews
            WHERE id = ?
          ''', (new_review_id,))
          
          review = cursor.fetchone()
          app.db.commit()

          if not review:
              app.db.rollback()
              return jsonify({'error': 'Failed to create study session review'}), 500

          # Return the newly created review
          return jsonify({
              'id': review['id'],
              'session_id': review['session_id'],
              'rating': review['rating'],
              'feedback': review['feedback'],
              'completion_status': review['completion_status'],
              'created_at': review['created_at']
          }), 201

      except sqlite3.IntegrityError as e:
          app.db.rollback()
          return jsonify({'error': str(e)}), 400

    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study-sessions/reset', methods=['POST'])
  @cross_origin()
  def reset_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # First delete all word review items since they have foreign key constraints
      cursor.execute('DELETE FROM word_review_items')
      
      # Then delete all study sessions
      cursor.execute('DELETE FROM study_sessions')
      
      app.db.commit()
      
      return jsonify({"message": "Study history cleared successfully"}), 200
    except Exception as e:
      return jsonify({"error": str(e)}), 500