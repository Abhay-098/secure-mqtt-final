import argparse, ssl, time, os
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
CERT_DIR = os.path.join(os.getcwd(), "certs")

def make_client(client_id, secure):
    client = mqtt.Client(client_id=client_id)
    if secure:
        # Simplifies TLS connection for the public broker (test.mosquitto.org)
        client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        client.tls_insecure_set(True)
    return client

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # This log message will now be successfully streamed
        print(f"✅ Connected successfully to broker ({'Secure' if userdata.get('secure') else 'Unsecure'})")
        if userdata.get("mode") == "sub":
            topic = userdata["topic"]
            client.subscribe(topic)
            print(f"📡 Subscribed to topic: {topic}")
    else:
        print(f"❌ Connection failed with code {rc}. Please check network or broker status.")

def on_message(client, userdata, msg):
    print(f"💬 Message received → topic={msg.topic} payload={msg.payload.decode()}")

def run_pub(client_id, topic, payload, secure):
    port = 8883 if secure else 1883
    client = make_client(client_id, secure)
    client.user_data_set({"mode": "pub", "topic": topic, "secure": secure})
    client.on_connect = on_connect
    
    try:
        client.connect(BROKER, port)
    except Exception as e:
        print(f"❌ Publisher connection error: {e}")
        return

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
    
    try:
        client.connect(BROKER, port)
    except Exception as e:
        print(f"❌ Subscriber connection error: {e}")
        return

    # CRUCIAL FIX: Use a controlled loop instead of loop_forever()
    # This prevents the blocking call from being terminated by the host environment.
    print(f"📡 Subscriber running and listening for 30 seconds...")
    for _ in range(30): # Loop for 30 seconds
        client.loop(timeout=1.0) # Check for messages every second
        time.sleep(1)

    client.disconnect()
    print("✅ Subscriber finished listening (after 30 seconds).")


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
        run_sub(args.client, args.topic, args.payload, args.secure) # Added payload argument for consistency
