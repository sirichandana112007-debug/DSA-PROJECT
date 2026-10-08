"""
Server launcher for the Healthcare Resource Allocation Web Application.
Usage:
    python run_server.py
Access in your web browser:
    http://localhost:8000
"""

import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.5)
    print("\n[+] Opening Web Browser Dashboard at: http://localhost:8000\n")
    try:
        webbrowser.open("http://localhost:8000")
    except Exception:
        pass

if __name__ == "__main__":
    print("=" * 60)
    print(" Healthcare Resource Allocation & Optimization System")
    print(" Server starting on http://localhost:8000")
    print(" API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
