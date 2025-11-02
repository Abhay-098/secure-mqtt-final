import argparse, ssl, time, os
import paho.mqtt.client as mqtt
import sys

BROKER = "test.mosquitto.org"

# --- Client Functions (Now accept a custom logger) ---

def make_client(client_id, secure, logger):
    client = mqtt.Client(client_id=client_id)
    if secure:
        client.tls_set(cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        client.tls_insecure_set(True)
    return client

def on_connect(client, userdata, flags, rc):
    logger = userdata.get("logger")
    if rc == 0:
        logger(f"✅ Connected successfully to broker ({'Secure' if userdata.get('secure') else 'Unsecure'})")
        if userdata.get("mode") == "sub":
            topic = userdata["topic"]
            client.subscribe(topic)
            logger(f"📡 Subscribed to topic: {topic}")
    else:
        logger(f"❌ Connection failed with code {rc}. Please check network or broker status.")

def on_message(client, userdata, msg):
    logger = userdata.get("logger")
    logger(f"💬 Message received → topic={msg.topic} payload={msg.payload.decode()}")

def run_pub(client_id, topic, payload, secure, logger=print):
    port = 8883 if secure else 1883
    client = make_client(client_id, secure, logger)
    client.user_data_set({"mode": "pub", "topic": topic, "secure": secure, "logger": logger})
    client.on_connect = on_connect
    
    try:
        client.connect(BROKER, port)
    except Exception as e:
        logger(f"❌ Publisher connection error: {e}")
        return

    client.loop_start()
    time.sleep(2)
    for i in range(3):
        msg = f"{payload} [{i}]"
        logger(f"🚀 Publishing → {msg}")
        client.publish(topic, msg)
        time.sleep(2)
    client.loop_stop()
    client.disconnect()
    logger("✅ Publisher finished sending messages.")

def run_sub(client_id, topic, secure, logger=print):
    port = 8883 if secure else 1883
    client = make_client(client_id, secure, logger)
    client.user_data_set({"mode": "sub", "topic": topic, "secure": secure, "logger": logger})
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(BROKER, port)
    except Exception as e:
        logger(f"❌ Subscriber connection error: {e}")
        return

    logger(f"📡 Subscriber running and listening for 30 seconds...")
    client.loop_start()
    
    # Run loop for 30 seconds to simulate a live subscriber
    time.sleep(30) 
    
    client.loop_stop()
    client.disconnect()
    logger("✅ Subscriber finished listening (after 30 seconds).")


# --- Main Block (Kept for local testing, now calls with print()) ---

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["pub", "sub"], default="pub")
    p.add_argument("--client", default="client1")
    p.add_argument("--topic", default="/vit/test")
    p.add_argument("--payload", default="Hello MQTT!")
    p.add_argument("--secure", action="store_true")
    args = p.parse_args()

    # When run directly, use the default print()
    if args.mode == "pub":
        run_pub(args.client, args.topic, args.payload, args.secure, logger=print)
    else:
        # Note: If running locally via terminal, the subscriber will block for 30 seconds.
        run_sub(args.client, args.topic, args.payload, args.secure, logger=print)
