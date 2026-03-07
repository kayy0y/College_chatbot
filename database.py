import sqlite3
import pandas as pd

def init_database():
    """Initialize the database with FAQ data"""
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    
    # Create FAQs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT,
            keywords TEXT
        )
    ''')
    
    # Create chat logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_query TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create unmatched queries table (for admin review)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS unmatched_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Load data from CSV
    try:
        df = pd.read_csv('college_data.csv')
        df.to_sql('faqs', conn, if_exists='replace', index=False)
        print(f"✅ Loaded {len(df)} FAQs into database")
    except FileNotFoundError:
        print("⚠️  college_data.csv not found. Please create it first.")
    
    conn.close()

def get_all_faqs():
    """Retrieve all FAQs from database"""
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT question, answer, category FROM faqs')
    faqs = cursor.fetchall()
    conn.close()
    return faqs

def log_chat(user_query, bot_response, confidence):
    """Log chat interaction"""
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_logs (user_query, bot_response, confidence)
        VALUES (?, ?, ?)
    ''', (user_query, bot_response, confidence))
    conn.commit()
    conn.close()

def log_unmatched_query(query):
    """Log queries that couldn't be answered"""
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO unmatched_queries (query)
        VALUES (?)
    ''', (query,))
    conn.commit()
    conn.close()

def get_chat_stats():
    """Get statistics for admin panel"""
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    
    # Total queries
    cursor.execute('SELECT COUNT(*) FROM chat_logs')
    total_queries = cursor.fetchone()[0]
    
    # Average confidence
    cursor.execute('SELECT AVG(confidence) FROM chat_logs')
    avg_confidence = cursor.fetchone()[0] or 0
    
    # Top 10 questions
    cursor.execute('''
        SELECT user_query, COUNT(*) as count 
        FROM chat_logs 
        GROUP BY user_query 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    top_questions = cursor.fetchall()
    
    # Recent unmatched queries
    cursor.execute('''
        SELECT query, timestamp 
        FROM unmatched_queries 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    unmatched = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_queries': total_queries,
        'avg_confidence': round(avg_confidence * 100, 2),
        'top_questions': top_questions,
        'unmatched': unmatched
    }

def add_faq(question, answer, category, keywords):
    """Add new FAQ to database"""
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO faqs (question, answer, category, keywords)
        VALUES (?, ?, ?, ?)
    ''', (question, answer, category, keywords))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()