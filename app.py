import os
import secrets
import io
import cv2
import base64
import numpy as np
import pickle
import threading
import shutil
from datetime import datetime
import asyncio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from deepface import DeepFace
from scipy.spatial.distance import cosine
from ultralytics import YOLO
from dotenv import load_dotenv
import mediapipe as mp

load_dotenv()

# --- Advanced Liveness (MediaPipe Face Mesh EAR via Tasks API) ---
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='face_landmarker.task'),
    running_mode=VisionRunningMode.IMAGE)
landmarker = FaceLandmarker.create_from_options(options)

def compute_ear(eye_points):
    p1, p2, p3, p4, p5, p6 = eye_points
    h_dist = np.linalg.norm(np.array(p1) - np.array(p4))
    v_dist1 = np.linalg.norm(np.array(p2) - np.array(p6))
    v_dist2 = np.linalg.norm(np.array(p3) - np.array(p5))
    if h_dist == 0: return 0
    return (v_dist1 + v_dist2) / (2.0 * h_dist)

def check_blink(rgb_image):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    detection_result = landmarker.detect(mp_image)
    if not detection_result.face_landmarks:
        return False
    
    landmarks = detection_result.face_landmarks[0]
    h, w, _ = rgb_image.shape
    
    # MediaPipe eye indices
    # Left eye
    left_eye_indices = [362, 385, 387, 263, 373, 380]
    left_eye_pts = [(landmarks[i].x * w, landmarks[i].y * h) for i in left_eye_indices]
    
    # Right eye
    right_eye_indices = [33, 160, 158, 133, 153, 144]
    right_eye_pts = [(landmarks[i].x * w, landmarks[i].y * h) for i in right_eye_indices]
    
    ear_left = compute_ear(left_eye_pts)
    ear_right = compute_ear(right_eye_pts)
    avg_ear = (ear_left + ear_right) / 2.0
    
    # Threshold for closing eyes
    return avg_ear < 0.22

# Import existing logic 
from database import DatabaseManager
from attendance import get_attendance_history, mark_attendance

app = FastAPI(title="Face Recognition Attendance Web")

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount templates (HTML)
templates = Jinja2Templates(directory="templates")

# Initialize YOLOv11 Pose model
# It will automatically download yolo11n-pose.pt on first run
print("Loading YOLOv11-Pose model. This might take a moment to download on first run...")
pose_model = YOLO("yolo11n-pose.pt")

# --- Authentication Configuration ---
_env_password = os.getenv("ADMIN_PASSWORD")
if _env_password:
    ADMIN_PASSWORD = _env_password
else:
    ADMIN_PASSWORD = secrets.token_urlsafe(16)
    print(f"[AttendX] No ADMIN_PASSWORD env var set. Generated password: {ADMIN_PASSWORD}")
SESSION_COOKIE = "attendx_session"
SESSION_MAX_AGE = 3600 * 12 # 12 hours
active_sessions: set = set()

# --- Initialize Database ---
db = DatabaseManager()
db.create_tables()

# Global State
active_session_marked = set()
training_state = {"is_training": False, "total": 0, "current": 0, "student": "", "error": None}

# Decode base64 image from WebSocket
def decode_image(data_url):
    encoded_data = data_url.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def apply_clahe(img):
    if img is None or img.size == 0:
        return img
    try:
        # 1. Fast Gaussian blur to remove grain with near-zero latency
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        # 2. CLAHE for contrast normalization under varying lighting
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        # 3. Subtle sharpening kernel to give YOLO crisper edges
        sharpen_kernel = np.array([[0, -0.5, 0],
                                   [-0.5, 3, -0.5],
                                   [0, -0.5, 0]])
        img = cv2.filter2D(img, -1, sharpen_kernel)
        
        return img
    except Exception:
        return img  # return original as fallback

# --- Old Motion-based liveness vars removed ---

# --- Authentication Routes ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        token = secrets.token_urlsafe(32)
        active_sessions.add(token)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key=SESSION_COOKIE, value=token, httponly=True, max_age=SESSION_MAX_AGE, samesite="strict", secure=True)
        return response
    return Response(status_code=401)

@app.get("/logout")
async def logout(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        active_sessions.discard(token)
    response = RedirectResponse(url="/login")
    response.delete_cookie(SESSION_COOKIE)
    return response

# --- Middleware-like check for protected routes ---
def is_authenticated(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    return token is not None and token in active_sessions

# --- Middleware for global protection ---
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if path in ["/login", "/logout"] or path.startswith("/static"):
        return await call_next(request)
    
    token = request.cookies.get(SESSION_COOKIE)
    if not token or token not in active_sessions:
        if path.startswith("/api") or path.startswith("/ws"):
            return Response("Unauthorized", status_code=401)
        return RedirectResponse(url="/login")
    
    return await call_next(request)

# --- REST Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/attendance", response_class=HTMLResponse)
async def attendance_page(request: Request):
    return templates.TemplateResponse("attendance.html", {"request": request})

@app.get("/api/students")
async def get_students():
    db = DatabaseManager()
    rows = db.get_students()
    return {"students": [{"id": r[0], "name": r[1], "registered_at": r[2]} for r in rows]}

@app.get("/api/stats")
async def get_stats():
    db = DatabaseManager()
    students_count = len(db.get_students())
    
    # Get today's attendance count
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    today_attendance = len([row for row in db.get_attendance(date=date_str)])
    
    # Check model status
    model_trained = os.path.exists("encodings.pkl")
    
    return {
        "total_students": students_count,
        "today_attendance": today_attendance,
        "model_trained": model_trained
    }

@app.get("/api/attendance")
async def get_attendance():
    df = get_attendance_history()
    if df.empty:
        return {"records": []}
    
    df = df.sort_values(by=["Date", "Time"], ascending=False)
    records = df.to_dict('records')
    return {"records": records}

@app.get("/api/sessions")
async def list_sessions():
    db = DatabaseManager()
    rows = db.get_sessions()
    return {"sessions": [{"id": r[0], "name": r[1], "started_at": r[2], "ended_at": r[3]} for r in rows]}

@app.put("/api/sessions/{session_id}/rename")
async def rename_session(session_id: int, request: Request):
    data = await request.json()
    new_name = data.get("name")
    if not new_name:
        return {"success": False, "message": "Name is required"}
    
    db = DatabaseManager()
    if db.rename_session(session_id, new_name):
        return {"success": True, "message": "Session renamed successfully"}
    return {"success": False, "message": "Failed to rename session"}

@app.get("/api/sessions/{session_id}/attendance")
async def get_session_attendance(session_id: int):
    db = DatabaseManager()
    rows = db.get_attendance_by_session(session_id)
    return {"records": [{"id": r[0], "student_id": r[1], "name": r[2], "date": r[3], "time": r[4]} for r in rows]}

@app.get("/api/sessions/{session_id}/export")
async def export_session_attendance(session_id: int):
    db = DatabaseManager()
    rows = db.get_attendance_by_session(session_id)
    csv_content = "ID,Student ID,Name,Date,Time\n"
    for r in rows:
        csv_content += f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=session_{session_id}_attendance.csv"}
    )

@app.post("/api/clear/{type}")
async def clear_data(type: str):
    db = DatabaseManager()
    if type == 'attendance':
        db.clear_attendance()
        if os.path.exists("attendance.csv"):
            os.remove("attendance.csv")
        return {"message": "Attendance cleared"}
    elif type == 'students':
        db.clear_all_students()
        if os.path.exists("dataset"):
            shutil.rmtree("dataset")
            os.makedirs("dataset")
        if os.path.exists("encodings.pkl"):
            os.remove("encodings.pkl")
        return {"message": "Students dataset deleted"}
    elif type == 'model':
        if os.path.exists("encodings.pkl"):
            os.remove("encodings.pkl")
            return {"message": "Model cleared"}
        return {"message": "No model found"}
    return JSONResponse(status_code=400, content={"message": "Invalid type"})

@app.delete("/api/students/{student_id}")
async def delete_student(student_id: str):
    db = DatabaseManager()
    success = db.delete_student(student_id)
    if success:
        # Also remove their dataset folder if it exists
        dataset_path = os.path.join("dataset", student_id)
        if os.path.exists(dataset_path):
            shutil.rmtree(dataset_path)
        return {"message": f"Student {student_id} successfully deleted."}
    return JSONResponse(status_code=400, content={"message": "Failed to delete student."})

@app.delete("/api/attendance/{log_id}")
async def delete_attendance(log_id: int):
    db = DatabaseManager()
    success = db.delete_attendance(log_id)
    if success:
        return {"message": "Attendance record deleted."}
    return JSONResponse(status_code=400, content={"message": "Failed to delete attendance record."})

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: int):
    db = DatabaseManager()
    success = db.delete_session(session_id)
    if success:
        return {"message": "Session and associated attendance deleted."}
    return JSONResponse(status_code=400, content={"message": "Failed to delete session."})


# --- Training ---
def background_train():
    global training_state
    training_state = {"is_training": True, "total": 0, "current": 0, "student": "", "error": None}
    
    dataset_dir = "dataset"
    if not os.path.exists(dataset_dir):
        training_state["is_training"] = False
        training_state["error"] = "No dataset found"
        return

    known_encodings = []
    known_names = []
    known_ids = []
    model_name = "VGG-Face"

    student_folders = [f for f in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, f))]
    
    for folder in student_folders:
        path = os.path.join(dataset_dir, folder)
        training_state["total"] += len([f for f in os.listdir(path) if f.endswith(('.jpg', '.jpeg', '.png'))])

    if training_state["total"] == 0:
        training_state["is_training"] = False
        training_state["error"] = "Dataset is empty"
        return

    for folder in student_folders:
        path = os.path.join(dataset_dir, folder)
        try:
            student_id, student_name = folder.split('_', 1)
        except ValueError:
            continue

        training_state["student"] = student_name

        for filename in os.listdir(path):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(path, filename)
                try:
                    objs = DeepFace.represent(img_path=img_path, model_name=model_name, enforce_detection=False)
                    if len(objs) > 0:
                        known_encodings.append(objs[0]["embedding"])
                        known_names.append(student_name)
                        known_ids.append(student_id)
                except Exception:
                    pass
                training_state["current"] += 1

    if len(known_encodings) > 0:
        data = {"encodings": known_encodings, "names": known_names, "ids": known_ids, "model_name": model_name}
        with open("encodings.pkl", "wb") as f:
            pickle.dump(data, f)
            
    training_state["is_training"] = False

@app.post("/api/train")
async def start_training():
    if training_state["is_training"]:
        return {"success": False, "message": "Already training"}
    
    t = threading.Thread(target=background_train)
    t.start()
    return {"success": True}

@app.get("/api/train/status")
async def get_train_status():
    return training_state


# --- WebSockets ---

@app.websocket("/ws/register/{student_id}/{student_name}")
async def ws_register(websocket: WebSocket, student_id: str, student_name: str):
    await websocket.accept()
    
    db = DatabaseManager()
    db.add_student(student_id, student_name)
    
    dataset_path = os.path.join("dataset", f"{student_id}_{student_name}")
    os.makedirs(dataset_path, exist_ok=True)
    
    max_images = 20
    count = 0
    confirmed = False
    
    try:
        # --- Phase 1: Preview (detect face, draw box, but don't save) ---
        while not confirmed:
            data_url = await websocket.receive_text()
            
            # Check if the client sent a confirmation signal
            if data_url == "CONFIRM":
                confirmed = True
                await websocket.send_json({"status": "confirmed"})
                break
            
            frame = decode_image(data_url)
            
            # Run YOLOv11 pose detection
            results = await asyncio.to_thread(pose_model, frame, classes=[0], verbose=False)
            
            face_list = []
            if len(results) > 0 and results[0].keypoints is not None:
                try:
                    kp_data = results[0].keypoints.xy.cpu().numpy()
                    for kp in kp_data:
                        if len(kp) < 5: continue
                        face_pts = kp[0:5]
                        valid_pts = [p for p in face_pts if p[0] > 0 and p[1] > 0]
                        if len(valid_pts) < 3: continue
                        
                        valid_pts = np.array(valid_pts)
                        xs, ys = valid_pts[:, 0], valid_pts[:, 1]
                        x_min, y_min = np.min(xs), np.min(ys)
                        x_max, y_max = np.max(xs), np.max(ys)
                        
                        head_width = max(30, x_max - x_min)
                        head_height = head_width * 1.5
                        
                        center_x = np.mean(xs)
                        center_y = np.mean(ys) + (head_height * 0.1)
                        
                        x = int(max(0, center_x - head_width * 0.7))
                        y = int(max(0, center_y - head_height * 0.5))
                        w = int(min(frame.shape[1], center_x + head_width * 0.7)) - x
                        h = int(min(frame.shape[0], center_y + head_height * 0.6)) - y
                        
                        if w >= 30 and h >= 30:
                            face_list.append({"x": x, "y": y, "w": w, "h": h})
                except Exception:
                    pass
            
            if len(face_list) > 0:
                await websocket.send_json({"status": "preview", "faces": face_list})
            else:
                await websocket.send_json({"status": "no_face", "faces": []})
        
        # --- Phase 2: Capture (save images after user confirmed) ---
        while count < max_images:
            data_url = await websocket.receive_text()
            frame = decode_image(data_url)
            
            # Run YOLOv11 pose detection
            results = await asyncio.to_thread(pose_model, frame, classes=[0], verbose=False)
            
            face_list = []
            if len(results) > 0 and results[0].keypoints is not None:
                try:
                    kp_data = results[0].keypoints.xy.cpu().numpy()
                    for kp in kp_data:
                        if len(kp) < 5: continue
                        face_pts = kp[0:5]
                        valid_pts = [p for p in face_pts if p[0] > 0 and p[1] > 0]
                        if len(valid_pts) < 3: continue
                        
                        valid_pts = np.array(valid_pts)
                        xs, ys = valid_pts[:, 0], valid_pts[:, 1]
                        x_min, y_min = np.min(xs), np.min(ys)
                        x_max, y_max = np.max(xs), np.max(ys)
                        
                        head_width = max(30, x_max - x_min)
                        head_height = head_width * 1.5
                        
                        center_x = np.mean(xs)
                        center_y = np.mean(ys) + (head_height * 0.1)
                        
                        x = int(max(0, center_x - head_width * 0.7))
                        y = int(max(0, center_y - head_height * 0.5))
                        w = int(min(frame.shape[1], center_x + head_width * 0.7)) - x
                        h = int(min(frame.shape[0], center_y + head_height * 0.6)) - y
                        
                        if w >= 30 and h >= 30:
                            face_list.append({"x": x, "y": y, "w": w, "h": h})
                except Exception:
                    pass
            
            if len(face_list) > 0:
                img_name = f"{dataset_path}/image_{count}.jpg"
                enhanced_frame = apply_clahe(frame)
                cv2.imwrite(img_name, enhanced_frame)
                count += 1
                await websocket.send_json({"status": "progress", "count": count, "faces": face_list})
            else:
                await websocket.send_json({"status": "no_face", "faces": []})
                
        await websocket.send_json({"status": "completed"})
    except WebSocketDisconnect:
        print("Registration client disconnected")
        # If registration was cancelled or interrupted before capturing all required images
        if count < max_images:
            print(f"Rolling back incomplete registration for {student_name} ({student_id})")
            db.delete_student(student_id)
            if os.path.exists(dataset_path):
                shutil.rmtree(dataset_path)


@app.websocket("/ws/recognize")
async def ws_recognize(websocket: WebSocket):
    await websocket.accept()
    
    if not os.path.exists("encodings.pkl"):
        await websocket.send_json({"error": "No trained model found. Please train first."})
        await websocket.close(code=1000)
        return
        
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)
        
    known_embeddings = data["encodings"]
    known_names = data["names"]
    known_ids = data["ids"]
    model_name = data.get("model_name", "VGG-Face")
    
    # Create a new session for this camera launch
    db = DatabaseManager()
    current_session_id = db.create_session()
    session_marked = set()  # Track who has been marked in THIS session
    
    # Liveness tracking per student: {student_id: {"live": bool}}
    liveness_tracker = {}
    
    try:
        while True:
            try:
                payload = await asyncio.wait_for(websocket.receive_json(), timeout=2.0)
            except asyncio.TimeoutError:
                continue
            data_url = payload.get("image")
            threshold = float(payload.get("threshold", 0.40))
            
            frame = decode_image(data_url)
            
            # Run YOLOv11 pose detection in a thread (lowered conf for multi-person)
            results = await asyncio.to_thread(
                pose_model, frame, classes=[0], conf=0.25, verbose=False
            )
            
            response_faces = []
            marked_just_now = False
            
            # Extract keypoints and build bounding boxes
            if len(results) > 0 and results[0].keypoints is not None:
                try:
                    keypoints_data = results[0].keypoints.xy.cpu().numpy()
                except Exception:
                    keypoints_data = []

                # --- Step 1: Extract all face bounding boxes & ROIs ---
                face_infos = []
                for kp in keypoints_data:
                    # YOLO Pose COCO 17 keypoints
                    # 0: Nose, 1: Left Eye, 2: Right Eye, 3: Left Ear, 4: Right Ear
                    if len(kp) < 5:
                        continue
                        
                    face_pts = kp[0:5]
                    valid_pts = [p for p in face_pts if p[0] > 0 and p[1] > 0]
                    if len(valid_pts) < 3:
                        continue
                        
                    valid_pts = np.array(valid_pts)
                    xs = valid_pts[:, 0]
                    ys = valid_pts[:, 1]
                    
                    x_min, y_min = np.min(xs), np.min(ys)
                    x_max, y_max = np.max(xs), np.max(ys)
                    
                    head_width = max(30, x_max - x_min)
                    head_height = head_width * 1.5
                    center_x = np.mean(xs)
                    center_y = np.mean(ys) + (head_height * 0.1)
                    
                    x1 = int(max(0, center_x - head_width * 0.7))
                    x2 = int(min(frame.shape[1], center_x + head_width * 0.7))
                    y1 = int(max(0, center_y - head_height * 0.5))
                    y2 = int(min(frame.shape[0], center_y + head_height * 0.6))
                    
                    w = x2 - x1
                    h = y2 - y1
                    
                    if w < 30 or h < 30:
                        continue
                    
                    face_roi = frame[y1:y2, x1:x2]
                    face_roi_clahe = apply_clahe(face_roi)
                    
                    face_infos.append({
                        "x": x1, "y": y1, "w": w, "h": h,
                        "face_roi": face_roi,
                        "face_roi_clahe": face_roi_clahe
                    })
                
                # --- Step 2: Compute DeepFace embeddings for ALL faces CONCURRENTLY ---
                async def _get_embedding(roi_clahe):
                    try:
                        objs = await asyncio.to_thread(
                            DeepFace.represent, img_path=roi_clahe,
                            model_name=model_name, enforce_detection=False
                        )
                        if len(objs) > 0:
                            return objs[0]["embedding"]
                    except Exception:
                        pass
                    return None
                
                embeddings = list(await asyncio.gather(
                    *[_get_embedding(fi["face_roi_clahe"]) for fi in face_infos]
                )) if face_infos else []
                
                # --- Step 3: Match embeddings & handle liveness (sequential) ---
                for fi, embedding in zip(face_infos, embeddings):
                    name = "Unknown"
                    distance = 1.0
                    blink_status = "none"
                    
                    if embedding is not None:
                        dist_list = [cosine(known_emb, embedding) for known_emb in known_embeddings]
                        min_dist_idx = np.argmin(dist_list)
                        min_dist = dist_list[min_dist_idx]
                        
                        if min_dist <= threshold:
                            name = known_names[min_dist_idx]
                            s_id = known_ids[min_dist_idx]
                            distance = float(min_dist)
                            
                            if s_id not in session_marked:
                                if s_id not in liveness_tracker:
                                    liveness_tracker[s_id] = {"live": False}
                                
                                tracker = liveness_tracker[s_id]
                                
                                if not tracker["live"]:
                                    face_rgb = cv2.cvtColor(fi["face_roi"], cv2.COLOR_BGR2RGB)
                                    is_blinking = check_blink(face_rgb)
                                    if is_blinking:
                                        tracker["live"] = True
                                
                                if tracker["live"]:
                                    if mark_attendance(s_id, name, current_session_id):
                                        marked_just_now = True
                                    session_marked.add(s_id)
                                    blink_status = "verified"
                                else:
                                    blink_status = "waiting"
                            else:
                                blink_status = "verified"
                    
                    response_faces.append({
                        "x": int(fi["x"]), "y": int(fi["y"]),
                        "w": int(fi["w"]), "h": int(fi["h"]),
                        "name": name, "distance": distance, "blink": blink_status
                    })
                
            await websocket.send_json({
                "faces": response_faces,
                "marked": marked_just_now
            })
            
    except WebSocketDisconnect:
        # End the session when camera disconnects
        db.end_session(current_session_id)
        print(f"Recognition client disconnected. Session #{current_session_id} closed.")


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
