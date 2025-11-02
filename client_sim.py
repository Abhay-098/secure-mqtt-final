import argparse, ssl, time, os
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
CERT_DIR = os.path.join(os.getcwd(), "certs")

def make_client(client_id, secure):
    client = mqtt.Client(client_id=client_id)
    if secure:
        client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        client.tls_insecure_set(True)
    return client

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected successfully to broker ({'Secure' if userdata.get('secure') else 'Unsecure'})")
        if userdata.get("mode") == "sub":
            topic = userdata["topic"]
            client.subscribe(topic)
            print(f"📡 Subscribed to topic: {topic}")
    else:
        print(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"💬 Message received → topic={msg.topic} payload={msg.payload.decode()}")

def run_pub(client_id, topic, payload, secure):
    port = 8883 if secure else 1883
    client = make_client(client_id, secure)
    client.user_data_set({"mode": "pub", "topic": topic, "secure": secure})
    client.on_connect = on_connect
    client.connect(BROKER, port)
    client.loop_start()
    time.sleep(2)
    for i in range(3):
        msg = f"{payload} [{i}]"
        print(f"🚀 Publishing → {msg}")
        client.publish(topic, msg)
        time.sleep(2)
    client.loop_stop()
    client.disconnect()
    print("✅ Publisher finished sending messages.")

def run_sub(client_id, topic, secure):
    port = 8883 if secure else 1883
    client = make_client(client_id, secure)
    client.user_data_set({"mode": "sub", "topic": topic, "secure": secure})
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, port)
    client.loop_forever()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pub", "sub"], default="pub")
    p.add_argument("--client", default="client1")
    p.add_argument("--topic", default="/vit/test")
    p.add_argument("--payload", default="Hello MQTT!")
    p.add_argument("--secure", action="store_true")
    args = p.parse_args()

    if args.mode == "pub":
        run_pub(args.client, args.topic, args.payload, args.secure)
    else:
        run_sub(args.client, args.topic, args.secure)
