import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), 'notes.db')

def init_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA encoding = "UTF-8"')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#1E90FF',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                category_id INTEGER,
                is_favorite INTEGER DEFAULT 0,
                is_archived INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (note_id, tag_id),
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anonymous_users (
                token TEXT PRIMARY KEY,
                ip_address TEXT,
                ip_location TEXT DEFAULT '未知',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                parent_id INTEGER,
                token TEXT,
                ip_location TEXT DEFAULT '未知',
                content TEXT NOT NULL,
                like_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES comments (id) ON DELETE CASCADE,
                FOREIGN KEY (token) REFERENCES anonymous_users (token)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_likes (
                note_id INTEGER,
                token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (note_id, token),
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                FOREIGN KEY (token) REFERENCES anonymous_users (token)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comment_likes (
                comment_id INTEGER,
                token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (comment_id, token),
                FOREIGN KEY (comment_id) REFERENCES comments (id) ON DELETE CASCADE,
                FOREIGN KEY (token) REFERENCES anonymous_users (token)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notes_category ON notes(category_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notes_favorite ON notes(is_favorite)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notes_archived ON notes(is_archived)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_comments_note_id ON comments(note_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON comments(parent_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_comments_token ON comments(token)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_note_likes_token ON note_likes(token)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_comment_likes_token ON comment_likes(token)
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            default_categories = [
                ('默认', '#1E90FF'),
                ('工作', '#FF6347'),
                ('生活', '#32CD32'),
                ('学习', '#9370DB'),
                ('灵感', '#FFD700')
            ]
            cursor.executemany('INSERT INTO categories (name, color) VALUES (?, ?)', default_categories)
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
        return True
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        sys.stderr.write(f"Database initialization error: {e}\n")
        if 'conn' in locals():
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False
    except Exception as e:
        print(f"Unexpected error during database initialization: {e}")
        sys.stderr.write(f"Unexpected error during database initialization: {e}\n")
        if 'conn' in locals():
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)