from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import os, threading, time, sys

# Import the core logic directly (requires client_sim.py to be in the same directory)
from client_sim import run_pub, run_sub, BROKER

app = Flask(__name__)
# Enable gevent/eventlet for SocketIO threading
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet") 

# --- Existing Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Simulation logic for Render
    output = "✅ Certificates generated (simulated — Render cannot run shell commands)"
    return jsonify({'status': 'ok', 'output': output})

# --- Client Start Route (FIXED) ---

@app.route('/start_client', methods=['POST'])
def start_client():
    data = request.json
    mode = data.get('mode', 'pub')
    client_id = data.get('client', 'client1')
    topic = data.get('topic', '/vit/test')
    payload = data.get('payload', 'Hello MQTT!')
    secure = data.get('secure', False)

    # Use the logger function inside the thread to send messages back
    def log_and_emit(log_message):
        print(log_message)
        socketio.emit('mqtt_log', {'log': log_message})

    # Function to run in the background thread
    def run_client_thread():
        log_and_emit(f"🔌 Starting {mode} client on thread...")
        
        # We now pass the log_and_emit function to the client code
        if mode == 'pub':
            run_pub(client_id, topic, payload, secure, log_and_emit)
        else:
            # Subscriber will run for 30s as per the client_sim.py fix
            run_sub(client_id, topic, secure, log_and_emit)
        
        log_and_emit(f"✅ Client thread for {mode} finished.")


    # Start the client logic in a background thread
    thread = threading.Thread(target=run_client_thread, daemon=True)
    thread.start()

    mode_label = "🔒 Secure" if secure else "⚠️ Unsecure"
    pid = os.getpid() # Use Flask process PID for identification
    
    # Send immediate confirmation back to the frontend
    return jsonify({'status': 'started', 'pid': pid})

@socketio.on('connect')
def handle_connect():
    print("🟢 Client connected to WebSocket")

if __name__ == '__main__':
    # CRUCIAL FIX for Render: Use the dynamic $PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    # Note: Using eventlet/gevent mode for stable SocketIO threading
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
