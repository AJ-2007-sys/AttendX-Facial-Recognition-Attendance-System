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
- **Smart Session Grouping:** Unlike flat databases, AttendX groups attendance logs by "Sessions." Every time you lock/unlock the camera, it creates a new session timestamp. Expanding a session in the dashboard reveals all students marked during that specific window.

### 4. Granular Data Management (The Danger Zone)
- **Targeted Deletion:** Individually delete specific students, entirely wipe out a specific attendance session, or single out a specific attendance log entry for deletion.
- **Bulk Wipes:** Options to securely wipe all models, all registered faces, or all global attendance history.

## 🏗️ Architecture

AttendX successfully migrated from a legacy Python Tkinter desktop script to a decoupled Web Application.

### Backend (Python / FastAPI)
- **Framework:** `FastAPI` + `Uvicorn` server.
- **AI/ML Engine:** `DeepFace` (utilizing the VGG-Face model by default) handles the heavy facial encoding and recognition. `OpenCV` is used for face detection (Haar Cascades) and image preprocessing.
- **Database:** `SQLite` handles `students`, `sessions`, and `attendance` tables.
- **Real-Time Comm:** Uses `WebSockets` (`/ws/register` and `/ws/recognize`) to handle the rapid streaming of massive JPEG frames from the browser to the backend without HTTP overhead. REST APIs (`/api/...`) handle standard CRUD operations.

### Frontend (HTML5 / Vanilla JS / CSS3)
- **No Heavy Frameworks:** Pure HTML, CSS, and vanilla JavaScript ensure ultra-fast load times.
- **Browser APIs:** Utilizes `navigator.mediaDevices.getUserMedia` for client-side webcam access.
- **Canvas Overlays:** Video feeds are drawn onto HTML5 `<canvas>` elements, which allows the JavaScript to draw the bounding boxes exactly over the video frame based on WebSocket coordinate responses.

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- A working webcam connected to your device.
- Modern web browser (Chrome/Edge/Firefox).

### Installation

1. **Clone & Setup Virtual Environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```
   *(Note: DeepFace relies on TensorFlow/Keras which may require additional C++ build tools on Windows).*

3. **Run the Server**
   ```powershell
   python app.py
   ```
   *(The app will start on port `8000` via Uvicorn).*

4. **Access the App**
   Open your browser and navigate to `http://localhost:8000`.

## 📖 Usage Workflow

1. **Dashboard:** Start at `localhost:8000`.
2. **Register:** Click "Start Camera Enrollment", enter an ID and Name, and slowly turn your head while the AI captures 20 frames of your face.
3. **Train:** Back on the dashboard, click "Initialize Model Training". Wait for the progress bar to complete.
4. **Attendance:** Open the "Live Attendance Camera". Anyone who steps into the frame with their face registered will automatically be recorded under the current active "Session".
5. **Review:** Check the "Attendance Sessions" tab to see the accordion-style grouped logs. 

---
*Developed as part of an advanced AI modernization migration.*
