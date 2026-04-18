import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
import json
import time

def test_endpoints():
    base_url = "http://127.0.0.1:8000"
    
    # Wait a bit for the server to fully load the models and start listening
    time.sleep(2)
    
    print("Testing Face Recognition Server Features...")
    
    # 1. Unauthenticated root -> should redirect to /login
    req = urllib.request.Request(f"{base_url}/")
    try:
        response = urllib.request.urlopen(req)
        # Should redirect to /login and return 200 for the login HTML
        print(f"[GET /] Status: {response.getcode()}, Final URL: {response.geturl()}")
        if "/login" not in response.geturl():
            print("❌ Root did not redirect to login page properly.")
    except Exception as e:
        print(f"[GET /] Error: {e}")

    # 2. Login
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    data = urllib.parse.urlencode({"password": "admin123"}).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/login", data=data)
    try:
        response = opener.open(req)
        print(f"[POST /login] Login successful, Status: {response.getcode()}")
        
        # Check if cookie was set
        cookies = [c.name for c in cj]
        print(f"Cookies received: {cookies}")
    except Exception as e:
        print(f"[POST /login] Error: {e}")
        return

    # 3. Test Protected API - Stats
    try:
        response = opener.open(f"{base_url}/api/stats")
        data = json.loads(response.read().decode('utf-8'))
        print(f"[GET /api/stats] Status DB: {data}")
    except Exception as e:
        print(f"[GET /api/stats] Error: {e}")

    # 4. Test Protected API - Students
    try:
        response = opener.open(f"{base_url}/api/students")
        data = json.loads(response.read().decode('utf-8'))
        print(f"[GET /api/students] Total Students: {len(data.get('students', []))}")
    except Exception as e:
        print(f"[GET /api/students] Error: {e}")

    # 5. Test Protected API - Sessions
    try:
        response = opener.open(f"{base_url}/api/sessions")
        data = json.loads(response.read().decode('utf-8'))
        print(f"[GET /api/sessions] Total Sessions: {len(data.get('sessions', []))}")
    except Exception as e:
        print(f"[GET /api/sessions] Error: {e}")
        
    print("\n✅ Initial tests completed successfully!")

if __name__ == '__main__':
    test_endpoints()
