import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'notes.db')

def init_database():
    conn = sqlite3.connect(DB_PATH)
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

if __name__ == '__main__':
    init_database()