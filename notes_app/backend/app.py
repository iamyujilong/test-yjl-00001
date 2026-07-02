import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import time

FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
DB_PATH = os.path.join(BASE_DIR, 'database', 'notes.db')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def dict_from_row(row):
    return dict(row)

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        search = request.args.get('search', '')
        category_id = request.args.get('category_id')
        tag_id = request.args.get('tag_id')
        is_favorite = request.args.get('is_favorite')
        is_archived = request.args.get('is_archived')
        
        query = '''
            SELECT n.*, c.name as category_name, c.color as category_color
            FROM notes n
            LEFT JOIN categories c ON n.category_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if search:
            query += ' AND (n.title LIKE ? OR n.content LIKE ?)'
            params.append(f'%{search}%')
            params.append(f'%{search}%')
        
        if category_id:
            query += ' AND n.category_id = ?'
            params.append(category_id)
        
        if is_favorite is not None:
            query += ' AND n.is_favorite = ?'
            params.append(is_favorite)
        
        if is_archived is not None:
            query += ' AND n.is_archived = ?'
            params.append(is_archived)
        
        if tag_id:
            query = '''
                SELECT DISTINCT n.*, c.name as category_name, c.color as category_color
                FROM notes n
                LEFT JOIN categories c ON n.category_id = c.id
                JOIN note_tags nt ON n.id = nt.note_id
                WHERE nt.tag_id = ?
            ''' + query[query.find('WHERE')+6:]
            params.insert(0, tag_id)
        
        query += ' ORDER BY n.updated_at DESC'
        
        cursor.execute(query, params)
        notes = [dict_from_row(row) for row in cursor.fetchall()]
        
        for note in notes:
            cursor.execute('SELECT t.id, t.name FROM tags t JOIN note_tags nt ON t.id = nt.tag_id WHERE nt.note_id = ?', (note['id'],))
            note['tags'] = [dict_from_row(row) for row in cursor.fetchall()]
        
        return jsonify({'notes': notes})
    except sqlite3.Error as e:
        logger.error(f"Database error in get_notes: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_notes: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.*, c.name as category_name, c.color as category_color
            FROM notes n
            LEFT JOIN categories c ON n.category_id = c.id
            WHERE n.id = ?
        ''', (note_id,))
        note = cursor.fetchone()
        
        if not note:
            return jsonify({'error': 'Note not found'}), 404
        
        note_dict = dict_from_row(note)
        
        cursor.execute('SELECT t.id, t.name FROM tags t JOIN note_tags nt ON t.id = nt.tag_id WHERE nt.note_id = ?', (note_id,))
        note_dict['tags'] = [dict_from_row(row) for row in cursor.fetchall()]
        
        return jsonify(note_dict)
    except sqlite3.Error as e:
        logger.error(f"Database error in get_note: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_note: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/notes', methods=['POST'])
def create_note():
    conn = None
    try:
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notes (title, content, category_id, is_favorite, is_archived, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data.get('content', ''),
            data.get('category_id'),
            data.get('is_favorite', 0),
            data.get('is_archived', 0),
            time.strftime('%Y-%m-%d %H:%M:%S'),
            time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        note_id = cursor.lastrowid
        
        if 'tags' in data:
            for tag_name in data['tags']:
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                tag = cursor.fetchone()
                if tag:
                    tag_id = tag['id']
                else:
                    cursor.execute('INSERT INTO tags (name, created_at) VALUES (?, ?)', (tag_name, time.strftime('%Y-%m-%d %H:%M:%S')))
                    tag_id = cursor.lastrowid
                
                cursor.execute('INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)', (note_id, tag_id))
        
        conn.commit()
        return jsonify({'message': 'Note created', 'id': note_id}), 201
    except sqlite3.IntegrityError:
        if conn:
            conn.rollback()
        logger.error("Integrity error in create_note")
        return jsonify({'error': 'Duplicate entry'}), 409
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error in create_note: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in create_note: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    conn = None
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM notes WHERE id = ?', (note_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Note not found'}), 404
        
        update_fields = []
        params = []
        
        if 'title' in data:
            update_fields.append('title = ?')
            params.append(data['title'])
        if 'content' in data:
            update_fields.append('content = ?')
            params.append(data['content'])
        if 'category_id' in data:
            update_fields.append('category_id = ?')
            params.append(data['category_id'])
        if 'is_favorite' in data:
            update_fields.append('is_favorite = ?')
            params.append(data['is_favorite'])
        if 'is_archived' in data:
            update_fields.append('is_archived = ?')
            params.append(data['is_archived'])
        
        update_fields.append('updated_at = ?')
        params.append(time.strftime('%Y-%m-%d %H:%M:%S'))
        
        params.append(note_id)
        
        cursor.execute(f'UPDATE notes SET {", ".join(update_fields)} WHERE id = ?', params)
        
        if 'tags' in data:
            cursor.execute('DELETE FROM note_tags WHERE note_id = ?', (note_id,))
            for tag_name in data['tags']:
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                tag = cursor.fetchone()
                if tag:
                    tag_id = tag['id']
                else:
                    cursor.execute('INSERT INTO tags (name, created_at) VALUES (?, ?)', (tag_name, time.strftime('%Y-%m-%d %H:%M:%S')))
                    tag_id = cursor.lastrowid
                
                cursor.execute('INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)', (note_id, tag_id))
        
        conn.commit()
        return jsonify({'message': 'Note updated'})
    except sqlite3.IntegrityError:
        if conn:
            conn.rollback()
        logger.error("Integrity error in update_note")
        return jsonify({'error': 'Duplicate entry'}), 409
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error in update_note: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in update_note: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM notes WHERE id = ?', (note_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Note not found'}), 404
        
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
        return jsonify({'message': 'Note deleted'})
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error in delete_note: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in delete_note: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories ORDER BY name')
        categories = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify({'categories': categories})
    except sqlite3.Error as e:
        logger.error(f"Database error in get_categories: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_categories: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/categories', methods=['POST'])
def create_category():
    conn = None
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO categories (name, color, created_at) VALUES (?, ?, ?)', 
                      (data['name'], data.get('color', '#1E90FF'), time.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        category_id = cursor.lastrowid
        return jsonify({'message': 'Category created', 'id': category_id}), 201
    except sqlite3.IntegrityError:
        if conn:
            conn.rollback()
        logger.error("Integrity error in create_category")
        return jsonify({'error': 'Category already exists'}), 409
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error in create_category: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in create_category: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    conn = None
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM categories WHERE id = ?', (category_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Category not found'}), 404
        
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append('name = ?')
            params.append(data['name'])
        if 'color' in data:
            update_fields.append('color = ?')
            params.append(data['color'])
        
        params.append(category_id)
        
        cursor.execute(f'UPDATE categories SET {", ".join(update_fields)} WHERE id = ?', params)
        conn.commit()
        return jsonify({'message': 'Category updated'})
    except sqlite3.IntegrityError:
        if conn:
            conn.rollback()
        logger.error("Integrity error in update_category")
        return jsonify({'error': 'Category name already exists'}), 409
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error in update_category: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in update_category: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM categories WHERE id = ?', (category_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Category not found'}), 404
        
        cursor.execute('UPDATE notes SET category_id = NULL WHERE category_id = ?', (category_id,))
        cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        conn.commit()
        return jsonify({'message': 'Category deleted'})
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error in delete_category: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in delete_category: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/tags', methods=['GET'])
def get_tags():
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tags ORDER BY name')
        tags = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify({'tags': tags})
    except sqlite3.Error as e:
        logger.error(f"Database error in get_tags: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_tags: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/tags', methods=['POST'])
def create_tag():
    conn = None
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO tags (name, created_at) VALUES (?, ?)', 
                      (data['name'], time.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        tag_id = cursor.lastrowid
        return jsonify({'message': 'Tag created', 'id': tag_id}), 201
    except sqlite3.IntegrityError:
        if conn:
            conn.rollback()
        logger.error("Integrity error in create_tag")
        return jsonify({'error': 'Tag already exists'}), 409
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error in create_tag: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in create_tag: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM tags WHERE id = ?', (tag_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Tag not found'}), 404
        
        cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
        conn.commit()
        return jsonify({'message': 'Tag deleted'})
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error in delete_tag: {e}")
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in delete_tag: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if conn:
            conn.close()

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    from database.init_db import init_database
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)