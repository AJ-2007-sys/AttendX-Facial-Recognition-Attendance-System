import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_file="database.db"):
        self.db_file = db_file
        self.create_tables()

    def create_connection(self):
        """Create a database connection to the SQLite database specified by db_file"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
        return conn

    def create_tables(self):
        """Create students, sessions, and attendance tables"""
        sql_create_students_table = """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        sql_create_sessions_table = """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP
            );
        """

        sql_create_attendance_table = """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                session_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students (student_id),
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            );
        """

        conn = self.create_connection()
        if conn is not None:
            try:
                c = conn.cursor()
                c.execute(sql_create_students_table)
                c.execute(sql_create_sessions_table)
                c.execute(sql_create_attendance_table)
                
                # Migration: add session_id column if it doesn't exist yet
                try:
                    c.execute("ALTER TABLE attendance ADD COLUMN session_id INTEGER")
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                conn.commit()
                print("Database tables created successfully.")
            except sqlite3.Error as e:
                print(f"Error creating tables: {e}")
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")

    # --- Session Management ---
    def create_session(self):
        """Create a new attendance session and return its ID"""
        now = datetime.now()
        session_name = f"Session {now.strftime('%Y-%m-%d %H:%M')}"
        
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO sessions(session_name, started_at) VALUES(?,?)", 
                           (session_name, now.strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                session_id = cur.lastrowid
                print(f"Created session #{session_id}: {session_name}")
                return session_id
            except sqlite3.Error as e:
                print(f"Error creating session: {e}")
                return None
            finally:
                conn.close()

    def end_session(self, session_id):
        """Mark a session as ended"""
        now = datetime.now()
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("UPDATE sessions SET ended_at=? WHERE id=?", 
                           (now.strftime("%Y-%m-%d %H:%M:%S"), session_id))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error ending session: {e}")
                conn.close()

    def rename_session(self, session_id, new_name):
        """Rename an existing session"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("UPDATE sessions SET session_name=? WHERE id=?", (new_name, session_id))
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error renaming session: {e}")
                return False
            finally:
                conn.close()

    def get_sessions(self):
        """Retrieve all sessions, most recent first"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, session_name, started_at, ended_at FROM sessions ORDER BY id DESC")
                return cur.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching sessions: {e}")
                return []
            finally:
                conn.close()

    # --- Student Management ---
    def add_student(self, student_id, name):
        """Add a new student to the database"""
        sql = ''' INSERT INTO students(student_id, name)
                  VALUES(?,?) '''
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, (student_id, name))
                conn.commit()
                print(f"Student {name} added successfully.")
                return cur.lastrowid
            except sqlite3.IntegrityError:
                print(f"Student ID {student_id} already exists.")
                return None
            except sqlite3.Error as e:
                print(f"Error adding student: {e}")
                return None
            finally:
                conn.close()

    # --- Attendance ---
    def mark_attendance(self, student_id, name, session_id=None):
        """Mark attendance for a student in a specific session"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                
                # Check if already marked in THIS session (not just today)
                if session_id:
                    cur.execute("SELECT * FROM attendance WHERE student_id=? AND session_id=?", 
                               (student_id, session_id))
                else:
                    cur.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", 
                               (student_id, date_str))
                rows = cur.fetchall()
                
                if len(rows) > 0:
                    return False
                
                sql = ''' INSERT INTO attendance(student_id, name, date, time, session_id)
                          VALUES(?,?,?,?,?) '''
                cur.execute(sql, (student_id, name, date_str, time_str, session_id))
                conn.commit()
                print(f"Attendance marked for {name} at {time_str} (Session #{session_id}).")
                return True
            except sqlite3.Error as e:
                print(f"Error marking attendance: {e}")
                return False
            finally:
                conn.close()

    def get_attendance_by_session(self, session_id):
        """Retrieve attendance records for a specific session"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, student_id, name, date, time FROM attendance WHERE session_id=?", 
                           (session_id,))
                return cur.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching session attendance: {e}")
                return []
            finally:
                conn.close()

    def get_attendance(self, date=None):
        """Retrieve attendance records, optionally filtered by date"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                if date:
                    cur.execute("SELECT * FROM attendance WHERE date=?", (date,))
                else:
                    cur.execute("SELECT * FROM attendance")
                rows = cur.fetchall()
                return rows
            except sqlite3.Error as e:
                print(f"Error fetching attendance: {e}")
                return []
            finally:
                conn.close()

    def get_students(self):
        """Retrieve all currently registered students"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT student_id, name, created_at FROM students")
                rows = cur.fetchall()
                return rows
            except sqlite3.Error as e:
                print(f"Error fetching students: {e}")
                return []
            finally:
                conn.close()

    def clear_attendance(self):
        """Clears all attendance records and sessions from the database"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM attendance")
                cur.execute("DELETE FROM sessions")
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error clearing attendance: {e}")
                return False
            finally:
                conn.close()

    def clear_all_students(self):
        """Clears all student records and their attendance"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM attendance")
                cur.execute("DELETE FROM sessions")
                cur.execute("DELETE FROM students")
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error clearing students: {e}")
                return False
            finally:
                conn.close()

    def delete_student(self, student_id):
        """Delete a single student and their associated attendance records"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM attendance WHERE student_id=?", (student_id,))
                cur.execute("DELETE FROM students WHERE student_id=?", (student_id,))
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error deleting student: {e}")
                return False
            finally:
                conn.close()

    def delete_attendance(self, log_id):
        """Delete a single attendance log entry"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM attendance WHERE id=?", (log_id,))
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error deleting attendance record: {e}")
                return False
            finally:
                conn.close()

    def delete_session(self, session_id):
        """Delete an entire session and all its associated attendance records"""
        conn = self.create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM attendance WHERE session_id=?", (session_id,))
                cur.execute("DELETE FROM sessions WHERE id=?", (session_id,))
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error deleting session: {e}")
                return False
            finally:
                conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
