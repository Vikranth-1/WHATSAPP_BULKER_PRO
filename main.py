import webview
import threading
import sys
import os
import time
from app import start_server, automator

def cleanup():
    """Cleanup function to stop the background automator and close drivers."""
    global automator
    print("Desktop App closing. Cleaning up...")
    try:
        import app
        if app.automator:
            app.automator.stop()
            app.automator.close_driver()
    except Exception as e:
        print(f"Cleanup error: {e}")
    os._exit(0) # Force exit all threads

def run_logic():
    """Starts the Flask server."""
    # Run server on port 5000 (standard in app.py)
    start_server(debug=False, port=5000)

if __name__ == "__main__":
    # Start Flask in a background thread
    t = threading.Thread(target=run_logic, daemon=True)
    t.start()

    # Wait a bit for the server to start
    time.sleep(2)

    # Create the native window
    window = webview.create_window(
        'WhatsApp Bulk Messenger | Premium', 
        'http://127.0.0.1:5000',
        width=1200,
        height=850,
        min_size=(800, 600),
        background_color='#0f172a' # Matches CSS --bg-dark
    )

    # Set the cleanup hook
    window.events.closing += cleanup

    # Run the webview loop
    webview.start()
