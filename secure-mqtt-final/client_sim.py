import argparse, ssl, time
import paho.mqtt.client as mqtt

BROKER_UNSECURE = "test.mosquitto.org"
BROKER_SECURE = "test.mosquitto.org"
PORT_UNSECURE = 1883
PORT_SECURE = 8883

def on_connect(client, userdata, flags, rc):
    print("✅ Connected with result code", rc)
    if userdata["mode"] == "sub":
        client.subscribe(userdata["topic"])
        print(f"📡 Subscribed to {userdata['topic']}")

def on_message(client, userdata, msg):
    print(f"💬 Received on {msg.topic}: {msg.payload.decode()}")

def run_pub(client_id, topic, payload, use_tls):
    client = mqtt.Client(client_id=client_id, userdata={"mode": "pub", "topic": topic})
    if use_tls:
        client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        client.connect(BROKER_SECURE, PORT_SECURE, 60)
        print("🔒 Using TLS (encrypted channel)")
    else:
        client.connect(BROKER_UNSECURE, PORT_UNSECURE, 60)
        print("⚠️ Using Unsecure connection")
    client.loop_start()
    for i in range(3):
        msg = f"{payload} [{i}]"
        print("🚀 Publishing:", msg)
        client.publish(topic, msg)
        time.sleep(1)
    client.loop_stop()
    client.disconnect()

def run_sub(client_id, topic, use_tls):
    client = mqtt.Client(client_id=client_id, userdata={"mode": "sub", "topic": topic})
    client.on_connect = on_connect
    client.on_message = on_message
    if use_tls:
        client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        client.connect(BROKER_SECURE, PORT_SECURE, 60)
        print("🔒 Subscribing using TLS (encrypted channel)")
    else:
        client.connect(BROKER_UNSECURE, PORT_UNSECURE, 60)
        print("⚠️ Subscribing using Unsecure connection")
    client.loop_forever()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pub", "sub"], default="pub")
    p.add_argument("--client", default="client1")
    p.add_argument("--topic", default="/vit/test")
    p.add_argument("--payload", default="Hello MQTT!")
    p.add_argument("--tls", action="store_true")
    args = p.parse_args()

    if args.mode == "pub":
        run_pub(args.client, args.topic, args.payload, args.tls)
    else:
        run_sub(args.client, args.topic, args.tls)
