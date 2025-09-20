import sqlite3
import json
from datetime import datetime, timedelta
import os

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create cache table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            expires_at DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def get_cached_data(key: str):
    """Get data from cache if it exists and isn't expired"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT value, expires_at FROM cache 
        WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
    ''', (key, datetime.now().isoformat()))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

def cache_data(key: str, value, expiry_minutes: int = 5):
    """Cache data with expiration"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    expires_at = (datetime.now() + timedelta(minutes=expiry_minutes)).isoformat()
    value_json = json.dumps(value, default=str)
    
    c.execute('''
        INSERT OR REPLACE INTO cache (key, value, expires_at)
        VALUES (?, ?, ?)
    ''', (key, value_json, expires_at))
    
    conn.commit()
    conn.close()

def clear_expired_cache():
    """Clear expired cache entries"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM cache WHERE expires_at < ?', (datetime.now().isoformat(),))
    
    conn.commit()
    conn.close()