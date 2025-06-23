# Create and manage database of users

import sqlite3
from config import DB_PATH
import bcrypt
from typing import Optional, Dict, Any
from datetime import datetime

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            sex TEXT,
            activity_level TEXT,
            goal TEXT
        )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT DEFAULT CURRENT_DATE,
            weight REAL,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)

    conn.commit()
    conn.close()
        
def insert_user(email: str, password: str, age: Optional[int] = None, 
                height: Optional[float] = None, weight: Optional[float] = None,
                sex: Optional[str] = None, activity_level: Optional[str] = None,
                goal: Optional[str] = None) -> int:
    """
    Insert a new user into the database.
    Returns the user_id if successful, raises exception if not.
    """
    try:
        # Validate email
        if not email or '@' not in email:
            raise ValueError("Invalid email format")
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (email, password, age, height, weight, sex, activity_level, goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, hashed_password, age, height, weight, sex, activity_level, goal))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
        
    except sqlite3.IntegrityError:
        raise ValueError("Email already exists")
    except Exception as e:
        raise Exception(f"Error inserting user: {str(e)}")

def insert_log(user_id: int, weight: Optional[float] = None,
              calories: Optional[float] = None, protein: Optional[float] = None,
              carbs: Optional[float] = None, fat: Optional[float] = None,
              date: Optional[str] = None) -> int:
    """
    Insert a new daily log entry for a user.
    Returns the log_id if successful, raises exception if not.
    """
    try:
        # Validate user exists
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            raise ValueError("User does not exist")
        
        # Use current date if none provided
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        cursor.execute("""
            INSERT INTO daily_logs (user_id, date, weight, calories, protein, carbs, fat)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date, weight, calories, protein, carbs, fat))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id
        
    except Exception as e:
        raise Exception(f"Error inserting log: {str(e)}")

def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by their ID.
    Returns a dictionary of user data or None if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, email, age, height, weight, sex, activity_level, goal
            FROM users WHERE user_id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'email': user[1],
                'age': user[2],
                'height': user[3],
                'weight': user[4],
                'sex': user[5],
                'activity_level': user[6],
                'goal': user[7]
            }
        return None
        
    except Exception as e:
        raise Exception(f"Error retrieving user: {str(e)}")

def get_logs(user_id: int, start_date: Optional[str] = None, 
            end_date: Optional[str] = None) -> list:
    """
    Retrieve logs for a user within a date range.
    Returns a list of log entries.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT log_id, date, weight, calories, protein, carbs, fat
            FROM daily_logs WHERE user_id = ?
        """
        params = [user_id]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
            
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        conn.close()
        
        return [{
            'log_id': log[0],
            'date': log[1],
            'weight': log[2],
            'calories': log[3],
            'protein': log[4],
            'carbs': log[5],
            'fat': log[6]
        } for log in logs]
        
    except Exception as e:
        raise Exception(f"Error retrieving logs: {str(e)}")

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by their email.
    Returns a dictionary of user data or None if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, email, password, age, height, weight, sex, activity_level, goal
            FROM users WHERE email = ?
        """, (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'email': user[1],
                'password': user[2],  # Hashed password
                'age': user[3],
                'height': user[4],
                'weight': user[5],
                'sex': user[6],
                'activity_level': user[7],
                'goal': user[8]
            }
        return None
        
    except Exception as e:
        raise Exception(f"Error retrieving user: {str(e)}")

def verify_password(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify a user's email and password.
    Returns user data without password if successful, None if not.
    """
    try:
        user = get_user_by_email(email)
        if not user:
            return None
            
        # Verify password - handle both string and bytes formats
        stored_password = user['password']
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            # Remove password from user data before returning
            user.pop('password')
            return user
        return None
        
    except Exception as e:
        raise Exception(f"Error verifying password: {str(e)}")