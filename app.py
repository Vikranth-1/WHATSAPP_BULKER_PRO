from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from automator import WhatsAppAutomator
import threading
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'whatsapp_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global instance of automator
automator = None

def socket_logger(message):
    socketio.emit('log_update', {'message': message})

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'connected': True})

@socketio.on('start_browser')
def handle_start_browser():
    global automator
    if not automator:
        automator = WhatsAppAutomator(logger_callback=socket_logger)
    
    def run_browser():
        automator.login()
    
    threading.Thread(target=run_browser).start()

@socketio.on('send_messages')
def handle_send_messages(data):
    global automator
    if not automator or not automator.driver:
        emit('log_update', {'message': '❌ Browser not initialized. Please launch browser first.'})
        return

    numbers = data.get('numbers', [])
    message = data.get('message', '')
    min_delay = int(data.get('min_delay', 8))
    max_delay = int(data.get('max_delay', 15))

    if not numbers or not message:
        emit('log_update', {'message': '❌ Numbers or message missing.'})
        return

    def run_automation():
        automator.send_messages(numbers, message, min_delay, max_delay)
    
    threading.Thread(target=run_automation).start()

@socketio.on('stop_automation')
def handle_stop():
    global automator
    if automator:
        automator.stop()

@socketio.on('close_browser')
def handle_close_browser():
    global automator
    if automator:
        automator.close_driver()
        automator = None

def start_server(debug=False, port=5000):
    # Use eventlet for async support
    socketio.run(app, debug=debug, port=port, use_reloader=debug)

if __name__ == '__main__':
    start_server(debug=True)
