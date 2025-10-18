import sqlite3
file="product.db"

def init_db():
    conn = sqlite3.connect(file)
    c=conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            color TEXT,
            size TEXT,
            mrp REAL NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
def get_connection():
    conn=sqlite3.connect(file)
    return conn
    