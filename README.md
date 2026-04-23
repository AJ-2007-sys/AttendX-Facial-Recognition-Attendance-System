# AttendX - Intelligent Face Recognition Attendance System

AttendX is a modern, web-based Face Recognition Attendance System built with Python, FastAPI, and DeepFace. It seamlessly registers users via a browser webcam interface, trains a facial recognition model backend, and performs real-time continuous attendance logging through a sleek, glassmorphic dashboard.

![AttendX Dashboard Concept](https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=2000) *(Illustration of data visualization)*

## 🌟 Key Features

### 1. Modern Web Dashboard
- **Glassmorphism UI:** A premium dark-mode interface featuring blurred frosted-glass cards, animated gradient background blobs, and floating interactive particles.
- **Real-Time Data Polling:** Dashboard stats and tables automatically refresh to show the latest attendance logs without needing a page reload.
- **Animated Data Feedback:** Smooth toast notifications, skeleton loading states, and continuous background indicators give the app a polished, sci-fi feel.

### 2. Intelligent Registration
- **Dedicated Camera UI:** Navigate to a dedicated full-screen page to enroll new students.
- **Live Face Overlays:** The webcam feed draws a real-time targeting box around detected faces during enrollment.
- **Automated Capture:** Automatically captures 20 face frames (at a controlled frame rate) once a face is consistently detected in the frame.

### 3. Session-Based Attendance Tracking
- **Continuous Monitoring:** Launch the attendance camera in a dedicated view. It continuously streams frames to the backend for inference.
- **Visual Confidence Metrics:** The video feed overlays color-coded bounding boxes (Green for known, Red for unknown) and displays the recognized name alongside the cosine confidence distance.
- **Anti-Spoofing:** Blink-based liveness detection using MediaPipe prevents photo/video spoofing. Attendance is only marked after a live blink is confirmed.
- **Smart Session Grouping:** Unlike flat databases, AttendX groups attendance logs by "Sessions." Every time you lock/unlock the camera, it creates a new session timestamp. Expanding a session in the dashboard reveals all students marked during that specific window.

### 4. Granular Data Management (The Danger Zone)
- **Targeted Deletion:** Individually delete specific students, entirely wipe out a specific attendance session, or single out a specific attendance log entry for deletion.
- **Bulk Wipes:** Options to securely wipe all models, all registered faces, or all global attendance history.

## 🏗️ Architecture

AttendX successfully migrated from a legacy Python Tkinter desktop script to a decoupled Web Application.

### Backend (Python / FastAPI)
- **Framework:** `FastAPI` + `Uvicorn` server.
- **Face Detection:** `YOLOv11-Pose` extracts body/head keypoints to localize faces with high accuracy, even in multi-person scenarios.
- **Face Recognition:** `DeepFace` (VGG-Face model) generates 2622-dimensional embeddings. Matching uses cosine distance with a configurable threshold.
- **Liveness Detection:** `MediaPipe Face Landmarker` computes Eye Aspect Ratio (EAR) to detect blinks and prevent spoofing.
- **Image Enhancement:** CLAHE (Contrast Limited Adaptive Histogram Equalization) normalizes lighting before recognition.
- **Database:** `SQLite` handles `students`, `sessions`, and `attendance` tables.
- **Real-Time Comm:** Uses `WebSockets` (`/ws/register` and `/ws/recognize`) to handle the rapid streaming of JPEG frames from the browser to the backend without HTTP overhead. REST APIs (`/api/...`) handle standard CRUD operations.
- **Concurrency:** Multi-person face embeddings are processed concurrently via `asyncio.gather` to prevent pipeline stalls.

### Frontend (HTML5 / Vanilla JS / CSS3)
- **No Heavy Frameworks:** Pure HTML, CSS, and vanilla JavaScript ensure ultra-fast load times.
- **Browser APIs:** Utilizes `navigator.mediaDevices.getUserMedia` for client-side webcam access.
- **Canvas Overlays:** Video feeds are drawn onto HTML5 `<canvas>` elements, which allows the JavaScript to draw the bounding boxes exactly over the video frame based on WebSocket coordinate responses.

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

This installs all required packages including FastAPI, DeepFace, OpenCV, MediaPipe, Ultralytics (YOLO), and TensorFlow. Installation may take 5-10 minutes depending on your internet speed.

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

> **If you skip this step**, AttendX will auto-generate a random admin password and print it to the terminal on startup. Look for the line:
> ```
> [AttendX] No ADMIN_PASSWORD env var set. Generated password: xxxxxxxx
> ```

#### 5. Launch the Server
```bash
python app.py
```

On first launch, the following AI models will be automatically downloaded:
| Model | Size | Purpose |
|-------|------|---------|
| `yolo11n-pose.pt` | ~6 MB | Body/head pose detection |
| VGG-Face weights | ~580 MB | Facial embedding generation |
| `face_landmarker.task` | ~4 MB | Blink detection (bundled in repo) |

> **Startup takes 15-30 seconds** as TensorFlow, YOLO, and MediaPipe all initialize. This is normal.

#### 6. Open in Browser

Navigate to **[http://localhost:8000](http://localhost:8000)** and log in with your admin password.

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

*Developed as part of an advanced AI modernization migration.*
