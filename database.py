import sqlite3
import json
import os
from datetime import datetime

class Database:
    """Database handler for student progress tracking"""
    
    def __init__(self, db_path='student_progress.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                session_number INTEGER NOT NULL,
                session_date DATE,
                fluency REAL,
                lexical REAL,
                grammatical REAL,
                pronunciation REAL,
                band_score REAL,
                teacher_notes TEXT,
                student_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id),
                UNIQUE(student_id, session_number)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_student(self, name, email=""):
        """Create a new student"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO students (name, email) VALUES (?, ?)',
                (name, email)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_students(self):
        """Get list of all students"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM students ORDER BY name')
        students = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return students
    
    def get_student_id(self, name):
        """Get student ID by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM students WHERE name = ?', (name,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def get_student_email(self, name):
        """Get student email by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT email FROM students WHERE name = ?', (name,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def save_session(self, student_name, session_data):
        """Save or update a session"""
        student_id = self.get_student_id(student_name)
        if not student_id:
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO sessions (
                    student_id, session_number, session_date,
                    fluency, lexical, grammatical, pronunciation,
                    band_score, teacher_notes, student_feedback,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, session_number) 
                DO UPDATE SET
                    session_date = excluded.session_date,
                    fluency = excluded.fluency,
                    lexical = excluded.lexical,
                    grammatical = excluded.grammatical,
                    pronunciation = excluded.pronunciation,
                    band_score = excluded.band_score,
                    teacher_notes = excluded.teacher_notes,
                    student_feedback = excluded.student_feedback,
                    updated_at = excluded.updated_at
            ''', (
                student_id,
                session_data['session_number'],
                session_data['date'],
                session_data['fluency'],
                session_data['lexical'],
                session_data['grammatical'],
                session_data['pronunciation'],
                session_data['band_score'],
                session_data['teacher_notes'],
                session_data['student_feedback'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
        finally:
            conn.close()
    
    def get_student_sessions(self, student_name):
        """Get all sessions for a student"""
        student_id = self.get_student_id(student_name)
        if not student_id:
            return {}
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_number, session_date, fluency, lexical,
                   grammatical, pronunciation, band_score,
                   teacher_notes, student_feedback
            FROM sessions
            WHERE student_id = ?
            ORDER BY session_number
        ''', (student_id,))
        
        sessions = {}
        for row in cursor.fetchall():
            sessions[str(row[0])] = {
                'session_number': row[0],
                'date': row[1],
                'fluency': row[2],
                'lexical': row[3],
                'grammatical': row[4],
                'pronunciation': row[5],
                'band_score': row[6],
                'teacher_notes': row[7],
                'student_feedback': row[8]
            }
        
        conn.close()
        return sessions
    
    def delete_session(self, student_name, session_number):
        """Delete a session"""
        student_id = self.get_student_id(student_name)
        if not student_id:
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM sessions WHERE student_id = ? AND session_number = ?',
            (student_id, session_number)
        )
        
        conn.commit()
        conn.close()
        return True
    
    def get_session_stats(self, student_name):
        """Get statistics for a student"""
        sessions = self.get_student_sessions(student_name)
        
        if not sessions:
            return {
                'total_sessions': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'progress_percentage': 0
            }
        
        scores = [s['band_score'] for s in sessions.values() if s.get('band_score')]
        
        return {
            'total_sessions': len(sessions),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0,
            'progress_percentage': (len(sessions) / 30) * 100
        }
