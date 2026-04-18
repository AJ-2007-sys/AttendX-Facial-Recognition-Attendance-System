import os
import sys
import base64
import requests

GITHUB_TOKEN = "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"
OWNER = "AJ-2007-sys"
REPO = "AttendX-Facial-Recognition-Attendance-System"
BRANCH = "main"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"

def get_base_tree_sha():
    res = requests.get(f"{API_BASE}/git/ref/heads/{BRANCH}", headers=HEADERS)
    if res.status_code == 200:
        commit_sha = res.json()["object"]["sha"]
        res2 = requests.get(f"{API_BASE}/git/commits/{commit_sha}", headers=HEADERS)
        return commit_sha, res2.json()["tree"]["sha"]
    return None, None

def create_blob(content_bytes):
    res = requests.post(f"{API_BASE}/git/blobs", headers=HEADERS, json={
        "content": base64.b64encode(content_bytes).decode("utf-8"),
        "encoding": "base64"
    })
    res.raise_for_status()
    return res.json()["sha"]

def ignore_file(path):
    # Skip ignored files
    ignores = [".venv", "__pycache__", "dataset", "database.db", "attendance.csv", "encodings.pkl", ".env", ".git", ".idea", ".vscode", "runs"]
    for ig in ignores:
        if ig in path or path.endswith(".pt") or path.endswith(".pyc") or path.endswith(".log") or path.endswith(".msi") or path.endswith(".docx"):
            return True
    return False

def push_all():
    print("Fetching base tree...")
    parent_commit_sha, base_tree_sha = get_base_tree_sha()
    
    tree_items = []
    
    print("Uploading files...")
    for root, dirs, files in os.walk("."):
        if ignore_file(root):
            continue
            
        for name in files:
            path = os.path.relpath(os.path.join(root, name), ".").replace("\\", "/")
            if ignore_file(path) or ignore_file(root):
                continue
                
            print(f"  Uploading {path}...")
            # We must open the actual relative path
            with open(os.path.join(root, name), "rb") as f:
                blob_sha = create_blob(f.read())
            tree_items.append({
                "path": path,
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            })
            
    print("Creating tree...")
    tree_payload = {"tree": tree_items}
    if base_tree_sha:
        tree_payload["base_tree"] = base_tree_sha
        
    res = requests.post(f"{API_BASE}/git/trees", headers=HEADERS, json=tree_payload)
    res.raise_for_status()
    new_tree_sha = res.json()["sha"]
    
    print("Creating commit...")
    commit_payload = {
        "message": "Initial commit for AttendX AI Platform",
        "tree": new_tree_sha
    }
    if parent_commit_sha:
        commit_payload["parents"] = [parent_commit_sha]
        
    res = requests.post(f"{API_BASE}/git/commits", headers=HEADERS, json=commit_payload)
    res.raise_for_status()
    new_commit_sha = res.json()["sha"]
    
    print("Updating reference...")
    if parent_commit_sha:
        res = requests.patch(f"{API_BASE}/git/refs/heads/{BRANCH}", headers=HEADERS, json={"sha": new_commit_sha})
    else:
        res = requests.post(f"{API_BASE}/git/refs", headers=HEADERS, json={"ref": f"refs/heads/{BRANCH}", "sha": new_commit_sha})
    res.raise_for_status()
    print("Successfully pushed to GitHub!")

if __name__ == "__main__":
    push_all()
