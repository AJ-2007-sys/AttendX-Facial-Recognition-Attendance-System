import pandas as pd
from datetime import datetime
import os
from database import DatabaseManager

def mark_attendance(student_id, name, session_id=None):
    """
    Marks attendance for a student in a specific session:
    1. Checks if already marked in this session in CSV
    2. Appends to attendance.csv if not present
    3. Calls DatabaseManager to log in SQLite
    """
    
    # Ensure CSV file exists
    if not os.path.isfile("attendance.csv"):
        df = pd.DataFrame(columns=["Student_ID", "Name", "Date", "Time", "Session_ID"])
        df.to_csv("attendance.csv", index=False)

    # Load existing attendance
    df = pd.read_csv("attendance.csv")
    
    # Add Session_ID column if missing (migration)
    if "Session_ID" not in df.columns:
        df["Session_ID"] = None
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Check if student already marked in THIS session (not just today)
    if session_id is not None:
        session_records = df[(df["Student_ID"] == student_id) & (df["Session_ID"] == session_id)]
        if not session_records.empty:
            return False
    else:
        # Fallback: check by date if no session
        student_records = df[df["Student_ID"] == student_id]
        if not student_records.empty:
            today_records = student_records[student_records["Date"] == date_str]
            if not today_records.empty:
                return False

    # Log to CSV
    new_record = pd.DataFrame([{
        "Student_ID": student_id, 
        "Name": name, 
        "Date": date_str, 
        "Time": time_str,
        "Session_ID": session_id
    }])
    df = pd.concat([df, new_record], ignore_index=True)
    df.to_csv("attendance.csv", index=False)
    
    # Log to Database
    db = DatabaseManager()
    db.mark_attendance(student_id, name, session_id)
    
    return True

def get_attendance_history():
    """Reads the CSV file and returns the dataframe"""
    if os.path.isfile("attendance.csv"):
        df = pd.read_csv("attendance.csv")
        # Add Session_ID column if missing (migration)
        if "Session_ID" not in df.columns:
            df["Session_ID"] = None
        return df
    else:
        return pd.DataFrame(columns=["Student_ID", "Name", "Date", "Time", "Session_ID"])
