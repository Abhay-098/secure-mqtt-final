# 🔒 Secure MQTT Web App (TLS + Client Certificates)

This project is a **Flask + MQTT Web Application** demonstrating **secure and unsecure MQTT communication** using TLS encryption and client certificates.

It’s containerized with Docker and deployable via **Render** or any cloud platform.  
You can compare **unencrypted MQTT (port 1883)** and **TLS-secured MQTT (port 8883)** connections live.

---

## 🚀 Features

✅ Generate CA, Broker & Client certificates (using OpenSSL or simulated in Render)  
✅ Publish/Subscribe to MQTT topics  
✅ Compare **Secure (TLS)** vs **Unsecure (Plain)** communication  
✅ Live message updates with **Flask-SocketIO**  
✅ Docker + CI/CD (GitHub Actions → Docker Hub → Render)

---

## 📦 Tech Stack

- **Backend:** Flask, Flask-SocketIO  
- **Frontend:** HTML + JavaScript + Bootstrap  
- **MQTT Client:** paho-mqtt  
- **Security:** TLS (X.509 Certificates)  
- **Deployment:** Docker + Render + GitHub CI/CD

---

## 🧰 Local Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/secure-mqtt-webapp.git
cd secure-mqtt-webapp
