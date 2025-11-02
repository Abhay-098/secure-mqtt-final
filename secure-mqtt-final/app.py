from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import subprocess, threading, sys, time, os, shutil

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    script_path = os.path.join(os.getcwd(), 'generate_certs.sh')
    if shutil.which("openssl") and os.path.exists(script_path):
        try:
            proc = subprocess.run(["bash", script_path], check=True, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = proc.stdout
        except subprocess.CalledProcessError as e:
            output = f"⚠️ Error while generating certificates:\n{e.output}"
    else:
        output = "✅ Certificates generated (simulated - OpenSSL not available)."
    return jsonify({'status': 'ok', 'output': output})

@app.route('/start_client', methods=['POST'])
def start_client():
    mode = request.json.get('mode', 'pub')
    client = request.json.get('client', 'client1')
    topic = request.json.get('topic', '/vit/test')
    payload = request.json.get('payload', 'Hello MQTT!')
    use_tls = request.json.get('use_tls', False)

    cmd = [sys.executable, "-u", "client_sim.py",
           "--mode", mode,
           "--client", client,
           "--topic", topic,
           "--payload", payload]
    if use_tls:
        cmd.append("--tls")

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def stream_output():
        for line in iter(proc.stdout.readline, ''):
            if line.strip():
                socketio.emit('mqtt_log', {'line': line.strip()})
        proc.stdout.close()
        proc.wait()

    threading.Thread(target=stream_output, daemon=True).start()
    return jsonify({'status': 'started', 'pid': proc.pid})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
