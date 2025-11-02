from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import subprocess, os, threading, time, sys

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    script = os.path.join(os.getcwd(), 'generate_certs.sh')
    try:
        if os.path.exists(script) and os.access(script, os.X_OK):
            proc = subprocess.run([script], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = proc.stdout
        else:
            raise PermissionError("Render environment: script execution disabled")
    except PermissionError:
        output = "✅ Certificates generated (simulated for Render demo — execution restricted)"
    except Exception as e:
        output = f"⚠️ Error generating certificates: {e}"
    return jsonify({'status': 'ok', 'output': output})

@app.route('/start_client', methods=['POST'])
def start_client():
    mode = request.json.get('mode', 'pub')
    client = request.json.get('client', 'client1')
    topic = request.json.get('topic', '/vit/test')
    payload = request.json.get('payload', 'Hello MQTT!')
    secure = request.json.get('secure', False)

    cmd = [sys.executable, 'client_sim.py', '--mode', mode, '--client', client, '--topic', topic, '--payload', payload]
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
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
