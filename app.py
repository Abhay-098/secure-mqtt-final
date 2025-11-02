from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import subprocess, os, threading, time, sys

app = Flask(__name__)
# Render requires WebSocket connections to be allowed from its public URL
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Render cannot run shell scripts like generate_certs.sh
    output = "✅ Certificates generated (simulated — Render cannot run shell commands)"
    return jsonify({'status': 'ok', 'output': output})

@app.route('/start_client', methods=['POST'])
def start_client():
    mode = request.json.get('mode', 'pub')
    client = request.json.get('client', 'client1')
    topic = request.json.get('topic', '/vit/test')
    payload = request.json.get('payload', 'Hello MQTT!')
    secure = request.json.get('secure', False)

    # Note: client_sim.py uses the public test.mosquitto.org broker.
    cmd = [sys.executable, 'client_sim.py', '--mode', mode,
           '--client', client, '--topic', topic, '--payload', payload]
    if secure:
        cmd.append('--secure')

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def stream_output():
        for line in proc.stdout:
            if line.strip():
                socketio.emit('mqtt_log', {'log': line.strip()})
        for line in proc.stderr:
            if line.strip():
                socketio.emit('mqtt_log', {'log': line.strip()})

    threading.Thread(target=stream_output, daemon=True).start()
    time.sleep(0.3)

    mode_label = "🔒 Secure" if secure else "⚠️ Unsecure"
    print(f"▶️ Started {mode} ({mode_label}) → PID {proc.pid}")
    return jsonify({'status': 'started', 'pid': proc.pid})

@socketio.on('connect')
def handle_connect():
    print("🟢 Client connected to WebSocket")

if __name__ == '__main__':
    # 💥 CRUCIAL FIX for Render: Use the dynamic $PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
