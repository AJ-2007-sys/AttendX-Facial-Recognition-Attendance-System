# AttendX - Intelligent Face Recognition Attendance System

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![CUDA](https://img.shields.io/badge/NVIDIA-CUDA%20Accelerated-76B900.svg?logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-zone)
[![ByteTrack](https://img.shields.io/badge/Tracking-ByteTrack-blueviolet.svg)](https://github.com/ifzhang/ByteTrack)
[![DeepFace](https://img.shields.io/badge/AI-DeepFace%20%2B%20YOLOv11%2F26-orange.svg)](https://github.com/serengil/deepface)

AttendX is a high-performance, web-based Face Recognition Attendance System built with Python, FastAPI, DeepFace, and Ultralytics YOLO. It seamlessly registers users via a browser webcam interface, trains facial recognition embeddings, and executes real-time continuous attendance logging through a sleek, glassmorphic dashboard powered by **NVIDIA GPU acceleration** and **ByteTrack multi-object tracking**.

![AttendX Dashboard Concept](https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=2000) *(Illustration of data visualization)*

## 🌟 Key Features

### 1. Modern Web Dashboard
- **Glassmorphism UI:** A premium dark-mode interface featuring blurred frosted-glass cards, animated gradient background blobs, and floating interactive particles.
- **Real-Time Data Polling:** Dashboard stats and tables automatically refresh to show the latest attendance logs without needing a page reload.
- **Animated Data Feedback:** Smooth toast notifications, skeleton loading states, and continuous background indicators give the app a polished, sci-fi feel.

### 2. GPU Accelerated Face Detection & Tracking
- **Hardware Acceleration:** Automatic hardware routing to NVIDIA GPUs via PyTorch CUDA (tested on RTX 4050 Laptop GPU), dropping inference latency to **~17 ms (56+ FPS)**.
- **ByteTrack Multi-Object Tracking:** Every person is assigned a persistent `track_id` across frames.
- **Track-Aware Recognition Caching:** DeepFace only runs once per newly tracked individual. Subsequent frames reuse recognition state instantly (0 ms), completely eliminating video stutter and frame lag.
- **Configurable Models:** Default `yolo11n-pose.pt` with native support for the new `yolo26n-pose.pt` (toggled via `POSE_MODEL_PATH`).

### 3. Intelligent Registration
- **Dedicated Camera UI:** Navigate to a dedicated full-screen page to enroll new students.
- **Live Face Overlays:** The webcam feed draws a real-time targeting box around detected faces during enrollment.
- **Automated Capture:** Automatically captures 20 face frames (at a controlled frame rate) once a face is consistently detected in the frame.

### 4. Session-Based Attendance Tracking
- **Continuous Monitoring:** Launch the attendance camera in a dedicated view. It continuously streams frames to the backend for inference.
- **Visual Confidence Metrics:** The video feed overlays color-coded bounding boxes (Green for known, Red for unknown) and displays the recognized name alongside the cosine confidence distance.
- **Anti-Spoofing:** Blink-based liveness detection using MediaPipe prevents photo/video spoofing. Attendance is only marked after a live blink is confirmed.
- **Smart Session Grouping:** Unlike flat databases, AttendX groups attendance logs by "Sessions." Every time you lock/unlock the camera, it creates a new session timestamp. Expanding a session in the dashboard reveals all students marked during that specific window.

### 5. Granular Data Management (The Danger Zone)
- **Targeted Deletion:** Individually delete specific students, entirely wipe out a specific attendance session, or single out a specific attendance log entry for deletion.
- **Bulk Wipes:** Options to securely wipe all models, all registered faces, or all global attendance history.

## 🏗️ Architecture

AttendX features a high-throughput, decoupled client-server architecture:

### Backend (Python / FastAPI)
- **Framework:** `FastAPI` + `Uvicorn` asynchronous server.
- **Hardware Acceleration:** Auto-selects `cuda:0` when an NVIDIA GPU with CUDA is present, with automatic fallback to CPU.
- **Face & Pose Localization:** `YOLOv11-Pose` (or `YOLO26-Pose`) extracts head keypoints to tightly crop faces.
- **Multi-Object Tracking:** `ByteTrack` (`tracker="bytetrack.yaml"`) maintains spatial identity continuity across video frames.
- **Recognition Cache:** In-memory `track_cache` evicts redundant DeepFace representations, executing at ~0 ms for tracked faces.
- **Face Recognition:** `DeepFace` (VGG-Face model) generates 4096-dimensional embeddings with cosine distance matching.
- **Liveness Detection:** `MediaPipe Face Landmarker` computes Eye Aspect Ratio (EAR < 0.22) to verify blinks.
- **Image Enhancement:** CLAHE (Contrast Limited Adaptive Histogram Equalization) normalizes lighting before recognition.
- **Database:** `SQLite` handles `students`, `sessions`, and `attendance` tables.
- **Real-Time Comm:** Low-overhead `WebSockets` (`/ws/register` and `/ws/recognize`) stream JPEG frames from client to server.

### Frontend (HTML5 / Vanilla JS / CSS3)
- **Zero Client Overhead:** Pure HTML, CSS, and vanilla JavaScript ensure ultra-fast load times.
- **Browser APIs:** Utilizes `navigator.mediaDevices.getUserMedia` for client-side webcam access.
- **Canvas Overlays:** Video feeds are drawn onto HTML5 `<canvas>` elements, rendering real-time bounding boxes and confidence metrics.


---

## 🚀 Setup & Installation

### Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | 3.9 or higher (3.12 recommended). [Download here](https://www.python.org/downloads/) |
| **Git** | Any recent version. [Download here](https://git-scm.com/downloads) |
| **Webcam** | Built-in or USB webcam connected to your device |
| **Browser** | Chrome, Edge, or Firefox (modern version) |
| **OS** | Windows 10/11, macOS, or Linux |
| **Internet** | Required on first run only (to download AI models ~200MB) |

> **Windows Users:** You may need [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installed for some Python dependencies (dlib, TensorFlow). If `pip install` fails, install these first.

### Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/AJ-2007-sys/AttendX-Facial-Recognition-Attendance-System.git
cd AttendX-Facial-Recognition-Attendance-System
```

#### 2. Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> You should see `(.venv)` appear at the beginning of your terminal prompt.

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs all required packages including FastAPI, DeepFace, OpenCV, MediaPipe, Ultralytics (YOLO), and ByteTrack dependencies (`lap`).

##### ⚡ (Optional) Enable NVIDIA GPU Acceleration (CUDA 12.4)
If you have an NVIDIA GPU (e.g., RTX 3050/4050/4060+), install the official PyTorch CUDA build:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```
> When launched, AttendX will automatically detect and announce:
> `[AttendX] Hardware Acceleration: GPU (NVIDIA GeForce RTX ...) with CUDA 12.4`

<details>
<summary><b>⚠️ Troubleshooting: pip install fails</b></summary>

- **TensorFlow errors on Windows:** Ensure you have Python 3.9-3.12 (not 3.13+). TensorFlow doesn't support all Python versions.
- **`mediapipe` fails to build:** Upgrade pip first: `pip install --upgrade pip setuptools wheel`
- **Permission errors:** Run your terminal as Administrator (Windows) or use `pip install --user -r requirements.txt`
- **Slow download:** Use a mirror: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

</details>

#### 4. Configure Environment Variables (Optional)

Create a `.env` file in the project root:
```env
ADMIN_PASSWORD=your_secure_password_here
SESSION_SECRET=any_random_secret_string
```

##### 🎯 Selecting Pose Detection Model (YOLO11 vs YOLO26)
AttendX defaults to `yolo11n-pose.pt`. You can toggle to the new `yolo26n-pose.pt` anytime:
```powershell
# Windows PowerShell
$env:POSE_MODEL_PATH = "yolo26n-pose.pt"
```
```bash
# Linux / macOS
export POSE_MODEL_PATH="yolo26n-pose.pt"
```

#### 5. Launch the Server
```bash
python app.py
```

On first launch, the following AI models will be automatically downloaded:
| Model | Size | Purpose |
|-------|------|---------|
| `yolo11n-pose.pt` / `yolo26n-pose.pt` | ~6–7.5 MB | Body/head pose detection & tracking |
| VGG-Face weights | ~580 MB | Facial embedding generation |
| `face_landmarker.task` | ~4 MB | Blink detection (bundled in repo) |

> **Startup takes 15-30 seconds** as TensorFlow, YOLO, and MediaPipe all initialize. This is normal.

#### 6. Open in Browser

Navigate to **[http://localhost:8000](http://localhost:8000)** and log in with your admin password.

---

## ⚡ Performance Benchmarks

Inference latency measured on an **AMD Ryzen CPU** vs **NVIDIA GeForce RTX 4050 Laptop GPU**:

| Component / Pipeline | Runtime Device | Latency | Frame Rate (FPS) |
| :--- | :--- | :--- | :--- |
| **YOLO11n-Pose Detection** | CPU | 52.80 ms | 18.9 FPS |
| **YOLO26n-Pose Detection** | CPU | 63.50 ms | 15.7 FPS |
| **YOLO11n-Pose + ByteTrack** | **NVIDIA RTX 4050 GPU** | **17.64 ms** | **56.6 FPS** |
| **YOLO26n-Pose + ByteTrack** | **NVIDIA RTX 4050 GPU** | **17.20 ms** | **58.1 FPS** |
| **Track-Cached Identity Lookup** | In-Memory Cache | **< 0.1 ms** | **Instant (Zero Lag)** |


---

## 📖 Usage Workflow

### Quick Start (5 minutes)

1. **Login** → Enter your admin password at the login screen.
2. **Register a Student** → Click "Start Camera Enrollment", enter a Student ID and Name, then look at the camera. The system captures 20 face images automatically.
3. **Train the Model** → Back on the dashboard, click "Initialize Model Training". A progress bar will show the encoding progress. This usually takes 10-30 seconds per student.
4. **Start Attendance** → Open the "Live Attendance Camera". Anyone registered who steps into the frame and **blinks** will be automatically marked present.
5. **Review Logs** → Check the "Attendance Sessions" accordion on the dashboard to see grouped attendance records.

### Tips for Best Results
- **Registration:** Slowly turn your head left, right, up, and down during enrollment for diverse angle coverage.
- **Lighting:** Ensure even lighting on faces. The system applies CLAHE enhancement, but extreme backlighting can still reduce accuracy.
- **Distance:** Stand 1-3 feet from the camera for optimal face detection.
- **Threshold:** Adjust the confidence slider on the attendance page (lower = stricter matching, default is 0.40).

---

## 📁 Project Structure

```
AttendX/
├── app.py                  # Main FastAPI server (routes, WebSockets, AI pipeline)
├── database.py             # SQLite DatabaseManager (students, sessions, attendance)
├── attendance.py           # Attendance marking logic (CSV + DB dual-write)
├── train.py                # Model training script (generates encodings.pkl)
├── build_exe.py            # PyInstaller packaging script
├── requirements.txt        # Python dependencies
├── face_landmarker.task    # MediaPipe blink detection model
├── .env                    # Environment variables (create this yourself)
├── static/
│   ├── style.css           # Glassmorphism UI styles
│   ├── script.js           # Dashboard logic, polling, data management
│   ├── logo.png            # App logo
│   └── success.mp3         # Attendance confirmation sound
└── templates/
    ├── index.html           # Dashboard page
    ├── login.html           # Authentication page
    ├── register.html        # Student enrollment page
    └── attendance.html      # Live recognition camera page
```

### Generated at Runtime (git-ignored)
| File/Folder | Purpose |
|-------------|---------|
| `database.db` | SQLite database with all records |
| `encodings.pkl` | Trained face embeddings |
| `dataset/` | Captured face images per student |
| `attendance.csv` | CSV backup of attendance logs |
| `yolo11n-pose.pt` | YOLO model (auto-downloaded) |

---
