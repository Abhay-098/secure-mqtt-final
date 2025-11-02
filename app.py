from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import subprocess, os, threading, time, sys

# Initialize Flask + SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# ===========================================================
# 🔐 CERTIFICATE GENERATION (REAL LOCALLY / SIMULATED ON RENDER)
# ===========================================================
@app.route('/generate', methods=['POST'])
def generate():
    script = os.path.join(os.getcwd(), 'generate_certs.sh')
    try:
        # Check if we can actually execute the script (local mode)
        if os.path.exists(script) and os.access(script, os.X_OK):
            proc = subprocess.run([script], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = proc.stdout
        else:
            # Render cannot execute shell scripts
            raise PermissionError("Render environment: script execution disabled")

    except PermissionError:
        output = "✅ Certificates generated (simulated for Render demo — execution restricted)"
    except Exception as e:
        output = f"⚠️ Error generating certificates: {e}"

    return jsonify({'status': 'ok', 'output': output})

# ===========================================================
# 🚀 START MQTT CLIENT (PUBLISHER / SUBSCRIBER)
# ===========================================================
@app.route('/start_client', methods=['POST'])
def start_client():
    mode = request.json.get('mode', 'pub')           # pub or sub
    client = request.json.get('client', 'client1')   # client name
    topic = request.json.get('topic', '/vit/test')   # topic name
    payload = request.json.get('payload', 'Hello MQTT!')
    secure = request.json.get('secure', False)       # True = TLS

    # Command to run client_sim.py
    cmd = [
        sys.executable, 'client_sim.py',
        '--mode', mode,
        '--client', client,
        '--topic', topic,
        '--payload', payload
    ]
    if secure:
        cmd.append('--secure')

    # Start background process
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Thread to stream output live
    def stream_output():
        for line in proc.stdout:
            clean = line.strip()
            if clean:
                print(clean)
                socketio.emit('mqtt_log', {'log': clean})
        for line in proc.stderr:
            clean = line.strip()
            if clean:
                print(clean)
                socketio.emit('mqtt_log', {'log': clean})

    threading.Thread(target=stream_output, daemon=True).start()
    time.sleep(0.3)

    mode_label = "🔒 Secure" if secure else "⚠️ Unsecure"
    print(f"▶️ Started {mode} ({mode_label}) → PID {proc.pid}")
    return jsonify({'status': 'started', 'pid': proc.pid})

# ===========================================================
# 🧠 SOCKETIO EVENT HANDLER (Optional future use)
# ===========================================================
@socketio.on('connect')
def handle_connect():
    print("🟢 Client connected to SocketIO")

# ===========================================================
# 🏁 MAIN ENTRY
# ===========================================================
if __name__ == '__main__':
    # allow_unsafe_werkzeug=True is required in Render environment
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
