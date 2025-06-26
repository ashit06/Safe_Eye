# Safe Eye 🚦👁️
A Smart Road Safety Surveillance System using real-time computer vision and AI.

---

## 🧠 Overview

**Safe Eye** is an AI-powered road surveillance system designed to enhance road safety by automatically detecting accidents from camera feeds. It combines real-time video processing, YOLOv8-based object detection, Django backend, and a Next.js frontend dashboard to monitor incidents and notify authorities promptly.

---

## 🎯 Objectives

- Detect road accidents using computer vision.
- Provide real-time alerts to concerned authorities.
- Display live surveillance footage and incident reports.
- Log incidents in a secure and searchable format.
- Send automated email notifications on detection.

---

## 📂 Project Structure

Safe_Eye/\
│\
├── ai_model/ # YOLOv8 accident detection logic\
│ ├── camera_detection.py # Frame grabbing + AI inference\
│ ├── urls.py # Detection-related routes\
│ └── views.py # APIs: start/stop detection, status\
│\
├── incidents/ # Stores incident data and notification logic\
│ ├── models.py # Incident + Notification schema\
│ ├── views.py # Incident API endpoints\
│ └── email_utils.py # Email sending service\
│\
├── camera_feeds/ # Stores camera stream details\
│ ├── models.py\
│ └── admin.py\
│\
├── Safe_Eye/ # Django settings and URL routing\
│ ├── settings.py\
│ └── urls.py\
│\
├── safe_eye-frontend/ # React + Tailwind frontend dashboard\
│ └── components/\
│ └── AlertPanel.tsx # Real-time alert viewer\
│\
├── manage.py\
└── requirements.txt
---

## 🛠️ Tech Stack

| Layer       | Technology                  |
|-------------|------------------------------|
| Frontend    | Next.js |
| Backend     | Django + Django REST Framework |
| WebSocket   | Django Channels               |
| AI Model    | YOLOv8 (Ultralytics) + PyTorch |
| Video Input | OpenCV                        |
| DB          | SQLite / PostgreSQL (configurable) |
| Mail        | SMTP (Gmail App Password)     |

---

## ⚙️ Features

✅ Real-time accident detection  
✅ Push alerts to frontend dashboard (WebSockets)  
✅ Incident logging and analytics  
✅ Email notifications to registered authorities  
✅ Secure backend + token-based frontend auth  
✅ Modular and scalable design  

---

## 📸 System Architecture


    ┌────────────┐     Video Feed     ┌────────────┐
    │ CCTV/Camera│ ─────────────────▶ │   Backend  │
    └────────────┘                   │  (Django +  │
                                     │   YOLOv8)   │
                                     └────┬───────┘
                                          │
                                   Incident API
                                          │
                               ┌──────────▼───────────┐
                               │   PostgreSQL / SQLite│
                               └──────────┬───────────┘
                                          │
                                 WebSocket + REST API
                                          │
                               ┌──────────▼───────────┐
                               │   React Frontend     │
                               │ (Dashboard + Alerts) │
                               └──────────────────────┘


🚦 How It Works

Cameras are registered in the admin panel.\
The backend captures video frames using OpenCV.\
YOLOv8 processes frames for crash/accident detection.\
If a detection is made:\
Incident is stored in the DB.\
Notification is sent via email.\
Frontend dashboard receives live alert via WebSocket.\


🚀 How to Run Locally

Backend (Django)\
git clone https://github.com/your-username/Safe_Eye.git\
cd Safe_Eye\
python3 -m venv venv\
source venv/bin/activate\
pip install -r requirements.txt\
python manage.py makemigrations\
python manage.py migrate\
daphne Safe_Eye.asgi:application\

Frontend (Next.js)\
cd safe_eye-frontend\
npm install\
npm run dev\

🧪 Features

🚨 Real-time accident detection from camera feeds\
🌐 Live video stream with alert panel\
📧 Email notification on accident detection\
📦 REST APIs to manage incidents and camera feeds\
🧠 Fast AI inference using YOLOv8 + OpenCV\
🔐 JWT-based secure auth for frontend/backend\

✅ Future Plans

GPS-based live map tracking of incidents\
SOS button & mobile app integration\
Upload-from-device support (for dashcams)\
Admin portal with detailed analytics\

🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

🙏 Acknowledgements

Ultralytics YOLOv8\
Django & DRF\
OpenCV
