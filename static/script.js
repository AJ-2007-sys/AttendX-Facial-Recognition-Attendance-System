// Global camera stream
let currentSocket = null;
let currentStream = null;

// --- Custom Modal System ---
function createModalHTML() {
    if (document.getElementById('custom-modal-root')) return;
    
    const root = document.createElement('div');
    root.id = 'custom-modal-root';
    root.className = 'modal-overlay';
    root.innerHTML = `
        <div class="modal-box">
            <div class="modal-header">
                <h3 class="modal-title" id="modal-title">Title</h3>
            </div>
            <div class="modal-body">
                <p id="modal-message">Message</p>
                <input type="text" id="modal-input" class="modal-input" autocomplete="off">
            </div>
            <div class="modal-footer">
                <button class="btn outline" id="modal-btn-cancel">Cancel</button>
                <button class="btn primary" id="modal-btn-confirm">Confirm</button>
            </div>
        </div>
    `;
    document.body.appendChild(root);
}

let modalCallback = null;

function showModal(options) {
    createModalHTML();
    const root = document.getElementById('custom-modal-root');
    const titleEl = document.getElementById('modal-title');
    const messageEl = document.getElementById('modal-message');
    const inputEl = document.getElementById('modal-input');
    const btnCancel = document.getElementById('modal-btn-cancel');
    const btnConfirm = document.getElementById('modal-btn-confirm');
    
    titleEl.innerText = options.title || 'Confirm';
    messageEl.innerHTML = options.message || '';
    
    if (options.type === 'prompt') {
        inputEl.style.display = 'block';
        inputEl.value = options.defaultValue || '';
        setTimeout(() => inputEl.focus(), 100);
    } else {
        inputEl.style.display = 'none';
        inputEl.value = '';
    }
    
    btnConfirm.innerText = options.confirmText || 'Confirm';
    btnConfirm.className = options.isDanger ? 'btn danger' : 'btn primary';
    
    modalCallback = options.onConfirm;
    
    // Cleanup old listeners
    const newCancel = btnCancel.cloneNode(true);
    btnCancel.parentNode.replaceChild(newCancel, btnCancel);
    const newConfirm = btnConfirm.cloneNode(true);
    btnConfirm.parentNode.replaceChild(newConfirm, btnConfirm);
    
    newCancel.addEventListener('click', closeModal);
    newConfirm.addEventListener('click', () => {
        const val = inputEl.value;
        closeModal();
        if (modalCallback) {
            if (options.type === 'prompt') modalCallback(val);
            else modalCallback(true);
        }
    });
    
    // Enter key support for prompt
    if (options.type === 'prompt') {
        inputEl.onkeydown = (e) => {
            if (e.key === 'Enter') newConfirm.click();
        };
    }
    
    // Show modal with animation
    requestAnimationFrame(() => {
        root.classList.add('active');
    });
}

function closeModal() {
    const root = document.getElementById('custom-modal-root');
    if (root) {
        root.classList.remove('active');
        setTimeout(() => {
            if (!root.classList.contains('active') && root.parentNode) {
                root.parentNode.removeChild(root);
            }
        }, 300);
    }
}
let takingAttendance = false;

let attendanceInterval = null;
let studentsInterval = null;

// --- Toast Notifications ---
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = '';
    if (type === 'success') icon = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
    else if (type === 'error') icon = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
    else icon = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
    
    toast.innerHTML = `${icon} <span>${message}</span>`;
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after 4s
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// --- Dashboard Stats ---
function fetchStats() {
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            const elStudents = document.getElementById('stat-students');
            const elAttendance = document.getElementById('stat-attendance');
            const elModel = document.getElementById('stat-model');
            
            elStudents.innerText = data.total_students;
            elAttendance.innerText = data.today_attendance;
            elModel.innerText = data.model_trained ? 'Trained ready' : 'No model';
            if(data.model_trained) {
                elModel.style.color = 'var(--accent-green)';
            } else {
                elModel.style.color = 'var(--accent-red)';
            }
            
            // Remove skeletons to reveal text
            elStudents.classList.remove('skeleton');
            elAttendance.classList.remove('skeleton');
            elModel.classList.remove('skeleton');
        })
        .catch(err => console.error("Error fetching stats:", err));
}

document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    
    // Initialize Particles.js background
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            "particles": {
                "number": { "value": 40, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": "#ffffff" },
                "shape": { "type": "circle" },
                "opacity": { "value": 0.1, "random": false, "anim": { "enable": false } },
                "size": { "value": 3, "random": true, "anim": { "enable": false } },
                "line_linked": {
                    "enable": true,
                    "distance": 150,
                    "color": "#ffffff",
                    "opacity": 0.05,
                    "width": 1
                },
                "move": {
                    "enable": true,
                    "speed": 1,
                    "direction": "none",
                    "random": false,
                    "straight": false,
                    "out_mode": "out",
                    "bounce": false,
                }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": {
                    "onhover": { "enable": true, "mode": "grab" },
                    "onclick": { "enable": false },
                    "resize": true
                },
                "modes": {
                    "grab": { "distance": 140, "line_linked": { "opacity": 0.15 } }
                }
            },
            "retina_detect": true
        });
    }
});

// UI Tab Management
function showTab(tabId) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Deactivate all nav links
    document.querySelectorAll('.nav-links li').forEach(link => {
        link.classList.remove('active');
    });

    // Activate selected
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');

    // Clear previous pollers
    clearInterval(attendanceInterval);
    clearInterval(studentsInterval);

    // Auto-refresh tables and set up polling if needed
    if (tabId === 'dashboard') {
        fetchStats();
    } else if (tabId === 'attendance-view') {
        fetchSessions();
        // No polling here — it would collapse open accordions
    }

    if (tabId === 'students-view') {
        fetchStudents();
        studentsInterval = setInterval(fetchStudents, 2500);
    }

    // Stop camera if navigating away from dashboard
    if (tabId !== 'dashboard') {
        stopAttendance();
    }
}

// --- Webcam Logic ---
async function startWebcam() {
    try {
        currentStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        const video = document.getElementById('webcam');
        video.srcObject = currentStream;
        document.getElementById('video-wrapper').classList.remove('hidden');
        return video;
    } catch (err) {
        showToast("Camera error: " + err, 'error');
        return null;
    }
}

function stopWebcam() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
    document.getElementById('video-wrapper').classList.add('hidden');

    if (currentSocket) {
        currentSocket.close();
        currentSocket = null;
    }
}

// --- Registration Logic ---
function startRegistration() {
    const sId = document.getElementById('reg-id').value.trim();
    const sName = document.getElementById('reg-name').value.trim();

    if (!sId || !sName) {
        showToast("Please enter Student ID and Name.", 'error');
        return;
    }

    // Navigate to dedicated registration camera page
    window.location.href = `/register?id=${encodeURIComponent(sId)}&name=${encodeURIComponent(sName)}`;
}

// --- Training Logic ---
function startTraining() {
    const statusMsg = document.getElementById('train-status');
    const progContainer = document.getElementById('train-progress-container');
    const progBar = document.getElementById('train-progress');

    showModal({
        title: 'Start Training',
        message: 'Start training the DeepFace model? This process may take some time depending on the number of registered faces.',
        confirmText: 'Start Training',
        onConfirm: () => {
            statusMsg.innerText = "Training initialized in background...";
            progContainer.style.display = 'block';
            progBar.style.width = '0%';

            // Call REST endpoint
            fetch('/api/train', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        // Polling for progress
                        pollTrainingProgress(progBar, statusMsg, progContainer);
                    } else {
                        statusMsg.innerText = "Failed to start training: " + data.message;
                    }
                });
        }
    });
}

function pollTrainingProgress(progBar, statusMsg, progContainer) {
    const interval = setInterval(() => {
        fetch('/api/train/status')
            .then(res => res.json())
            .then(data => {
                if (data.is_training) {
                    const pct = (data.current / Math.max(1, data.total)) * 100;
                    progBar.style.width = pct + '%';
                    statusMsg.innerText = `Processing ${data.student}... (${data.current}/${data.total})`;
                } else {
                    clearInterval(interval);
                    progBar.style.width = '100%';
                    setTimeout(() => {
                        progContainer.style.display = 'none';
                        statusMsg.innerText = data.error ? `Error: ${data.error}` : "Training completed successfully!";
                        if (!data.error) fetchStats(); // Automatically refresh stats
                        setTimeout(() => { statusMsg.innerText = ''; }, 5000);
                    }, 1000);
                }
            })
            .catch(err => {
                clearInterval(interval);
                statusMsg.innerText = "Error tracking progress.";
            });
    }, 1000);
}

// --- Live Attendance Logic ---
function startAttendance() {
    // Navigate to dedicated attendance camera page
    window.location.href = '/attendance';
}

function stopAttendance() {
    // No-op on dashboard (handled on the attendance page itself)
}

// --- Session-Based Attendance Logic ---
function fetchSessions() {
    fetch('/api/sessions')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('sessions-container');
            container.innerHTML = '';
            
            if (data.sessions.length === 0) {
                container.innerHTML = '<p style="color: var(--text-muted); font-size: 13px;">No attendance sessions recorded yet. Launch the camera to start a session.</p>';
                return;
            }

            data.sessions.forEach(session => {
                const sessionCard = document.createElement('div');
                sessionCard.className = 'session-accordion';
                
                const endedLabel = session.ended_at 
                    ? `<span style="color: var(--text-muted); font-size: 12px;">Ended: ${session.ended_at}</span>`
                    : `<span style="color: var(--accent-green); font-size: 12px;">● Active</span>`;
                
                sessionCard.innerHTML = `
                    <div class="session-header" onclick="toggleSession(this, ${session.id})">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <strong>${session.name}</strong>
                            <button class="btn info" style="padding: 2px 6px; min-width: auto; height: auto;" onclick="event.stopPropagation(); renameSession(${session.id}, '${session.name}')" title="Rename Session">
                                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                            </button>
                            <span style="color: var(--text-muted); font-size: 12px; margin-left: 12px;">Started: ${session.started_at}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            ${endedLabel}
                            <button class="btn outline small" style="padding: 4px 8px; min-width: auto; height: auto; display: flex; align-items: center; gap: 4px;" onclick="event.stopPropagation(); window.location.href='/api/sessions/${session.id}/export'">
                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                                CSV
                            </button>
                            <button class="btn danger" style="padding: 4px 8px; min-width: auto; height: auto;" onclick="event.stopPropagation(); deleteSession(${session.id})">
                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                            <svg class="chevron" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                        </div>
                    </div>
                    <div class="session-body" style="display: none;">
                        <p style="color: var(--text-muted); font-size: 12px; padding: 12px 16px;">Loading...</p>
                    </div>
                `;
                container.appendChild(sessionCard);
            });
        });
}

function toggleSession(headerEl, sessionId) {
    const body = headerEl.nextElementSibling;
    const chevron = headerEl.querySelector('.chevron');
    
    if (body.style.display === 'none') {
        body.style.display = 'block';
        chevron.style.transform = 'rotate(180deg)';
        
        // Fetch attendance for this session
        fetch(`/api/sessions/${sessionId}/attendance`)
            .then(res => res.json())
            .then(data => {
                if (data.records.length === 0) {
                    body.innerHTML = '<p style="color: var(--text-muted); font-size: 12px; padding: 12px 16px;">No attendance recorded in this session.</p>';
                    return;
                }
                
                let tableHTML = `
                    <table class="modern-table">
                        <thead><tr><th>Student ID</th><th>Name</th><th>Date</th><th>Time</th><th style="width: 60px; text-align: right;">Action</th></tr></thead>
                        <tbody>`;
                
                data.records.forEach(r => {
                    tableHTML += `<tr>
                                    <td>${r.student_id}</td>
                                    <td>${r.name}</td>
                                    <td>${r.date}</td>
                                    <td>${r.time}</td>
                                    <td style="text-align: right;">
                                        <button class="btn danger" style="padding: 4px 8px; min-width: auto; height: auto;" onclick="deleteAttendance(${r.id}, ${sessionId}, this)">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                        </button>
                                    </td>
                                  </tr>`;
                });
                
                tableHTML += '</tbody></table>';
                body.innerHTML = tableHTML;
            })
            .catch(err => {
                body.innerHTML = '<p style="color: var(--accent-red); font-size: 12px; padding: 12px 16px;">Failed to load attendance. Check connection.</p>';
            });
    } else {
        body.style.display = 'none';
        chevron.style.transform = 'rotate(0deg)';
    }
}

function fetchStudents() {
    fetch('/api/students')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('students-table-body');
            tbody.innerHTML = '';
            data.students.forEach(s => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${s.id}</td>
                    <td>${s.name}</td>
                    <td>${s.registered_at}</td>
                    <td style="text-align: right;">
                        <button class="btn danger" style="padding: 4px 8px; min-width: auto; height: auto;" onclick="deleteStudent('${s.id}')">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });
}

// --- Danger Zone Logic ---
function clearData(type) {
    showModal({
        title: 'Danger Zone',
        message: `Are you sure you want to completely delete <strong>${type}</strong> data?<br><br>This action cannot be undone.`,
        isDanger: true,
        confirmText: 'Delete Forever',
        onConfirm: () => {
            fetch(`/api/clear/${type}`, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    showToast(data.message, 'success');
                    if (type === 'attendance') fetchSessions();
                    if (type === 'students') fetchStudents();
                    fetchStats(); // Update stats as well
                });
        }
    });
}

// --- Individual Deletion Functions ---
function deleteSession(sessionId) {
    showModal({
        title: 'Delete Session',
        message: 'Are you sure you want to delete this session and ALL its attendance records?',
        isDanger: true,
        confirmText: 'Delete Session',
        onConfirm: () => {
            fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        showToast("Session deleted", 'success');
                        fetchSessions();
                        fetchStats();
                    } else {
                        showToast(data.message, 'error');
                    }
                })
                .catch(err => showToast("Error deleting session", 'error'));
        }
    });
}

function deleteAttendance(logId, sessionId, btnElement) {
    showModal({
        title: 'Delete Record',
        message: 'Are you sure you want to delete this individual attendance record?',
        isDanger: true,
        confirmText: 'Delete Record',
        onConfirm: () => {
            fetch(`/api/attendance/${logId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        showToast("Attendance record deleted", 'success');
                        btnElement.closest('tr').remove();
                        fetchStats();
                    } else {
                        showToast(data.message, 'error');
                    }
                })
                .catch(err => showToast("Error deleting attendance", 'error'));
        }
    });
}

function deleteStudent(studentId) {
    showModal({
        title: 'Delete Student',
        message: `Are you sure you want to delete student ${studentId} and their face data? You will need to retrain the model afterwards.`,
        isDanger: true,
        confirmText: 'Delete Student',
        onConfirm: () => {
            fetch(`/api/students/${studentId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(data => {
                    showToast(data.message, data.success ? 'success' : 'error');
                    if (data.success) {
                        fetchStudents();
                        fetchStats();
                    }
                })
                .catch(err => showToast("Error deleting student", 'error'));
        }
    });
}

// --- Search Filter Logic ---
function filterStudents() {
    const input = document.getElementById("search-students").value.toLowerCase();
    const rows = document.getElementById("students-table-body").getElementsByTagName("tr");
    
    for (let i = 0; i < rows.length; i++) {
        const idCol = rows[i].getElementsByTagName("td")[0];
        const nameCol = rows[i].getElementsByTagName("td")[1];
        if (idCol || nameCol) {
            const idText = idCol.textContent || idCol.innerText;
            const nameText = nameCol.textContent || nameCol.innerText;
            if (idText.toLowerCase().indexOf(input) > -1 || nameText.toLowerCase().indexOf(input) > -1) {
                rows[i].style.display = "";
            } else {
                rows[i].style.display = "none";
            }
        }       
    }
}

function renameSession(sessionId, oldName) {
    showModal({
        title: 'Rename Session',
        message: 'Enter a new name for this session:',
        type: 'prompt',
        defaultValue: oldName,
        confirmText: 'Save',
        onConfirm: (newName) => {
            if (!newName || newName.trim() === "" || newName === oldName) return;

            fetch(`/api/sessions/${sessionId}/rename`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: newName.trim() })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, 'success');
                    fetchSessions();
                } else {
                    showToast(data.message, 'error');
                }
            })
            .catch(err => showToast("Error renaming session", 'error'));
        }
    });
}

function filterAttendance() {
    const input = document.getElementById("search-attendance").value.toLowerCase();
    
    // First, filter the actual rows inside expanded tables
    const tables = document.querySelectorAll('.session-body table');
    tables.forEach(table => {
        const rows = table.getElementsByTagName("tbody")[0].getElementsByTagName("tr");
        let activeCount = 0;
        
        for (let i = 0; i < rows.length; i++) {
            const idCol = rows[i].getElementsByTagName("td")[0];
            const nameCol = rows[i].getElementsByTagName("td")[1];
            if (idCol || nameCol) {
                const idText = idCol.textContent || idCol.innerText;
                const nameText = nameCol.textContent || nameCol.innerText;
                if (idText.toLowerCase().indexOf(input) > -1 || nameText.toLowerCase().indexOf(input) > -1) {
                    rows[i].style.display = "";
                    activeCount++;
                } else {
                    rows[i].style.display = "none";
                }
            }       
        }
    });

    // Second, if they are searching for a Session name itself, keep the whole session visible
    const sessionCards = document.querySelectorAll('.session-accordion');
    sessionCards.forEach(card => {
        const sessionName = card.querySelector('strong').innerText.toLowerCase();
        
        // Let's also check if any row inside this session matches
        const hasVisibleRows = card.querySelectorAll("tbody tr:not([style*='display: none'])").length > 0;
        
        if (input === "" || sessionName.indexOf(input) > -1 || hasVisibleRows) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}
