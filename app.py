from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import subprocess, os, threading, time, sys

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# -------------------------------
# Generate Certificates (Simulated)
# -------------------------------
@app.route('/generate', methods=['POST'])
def generate():
    try:
        script = os.path.join(os.getcwd(), 'generate_certs.sh')
        if os.path.exists(script):
            # Try running it if OpenSSL available (local mode)
            proc = subprocess.run([script], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = proc.stdout
        else:
            # Simulate in Render (no OpenSSL)
            output = "✅ Certificates generated (simulated for demo)"
        return jsonify({'status': 'ok', 'output': output})
    except Exception as e:
        return jsonify({'status': 'error', 'output': str(e)}), 500

# -------------------------------
# Start MQTT Client (Publisher/Subscriber)
# -------------------------------
@app.route('/start_client', methods=['POST'])
def start_client():
    mode = request.json.get('mode', 'pub')  # 'pub' or 'sub'
    client = request.json.get('client', 'client1')
    topic = request.json.get('topic', '/vit/test')
    payload = request.json.get('payload', 'Hello MQTT!')
    secure = request.json.get('secure', False)

    # Command to launch client_sim.py with given args
    cmd = [
        sys.executable, 'client_sim.py',
        '--mode', mode,
        '--client', client,
        '--topic', topic,
        '--payload', payload
    ]
    if secure:
        cmd.append('--secure')

    # Start client in background
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Stream output asynchronously to logs
    def stream_output():
        for line in proc.stdout:
            print(line.strip())
            socketio.emit('mqtt_log', {'log': line.strip()})
        for line in proc.stderr:
            print(line.strip())
            socketio.emit('mqtt_log', {'log': line.strip()})

    threading.Thread(target=stream_output, daemon=True).start()
    time.sleep(0.2)
    return jsonify({'status': 'started', 'pid': proc.pid})

# -------------------------------
# Main entry
# -------------------------------
if __name__ == '__main__':
    # allow_unsafe_werkzeug=True fixes Render runtime warning
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
