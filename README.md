> ⚠️ **Research Prototype**  
> This repository contains unpublished work under active research. Please do not copy, fork, or share.

# 🛡️ AI-Powered Home Security System with Facial Recognition

An intelligent surveillance system that combines real-time **facial recognition** and **object detection** to enhance home security. Logs all activity and sends **SMS alerts** for unknown intrusions. Powered by **Firebase** for cloud logging and **Twilio** for real-time notifications, this project sets the groundwork for a modern smart home security solution.


---

## 📌 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architect)
- [How It Works](#-how-it-works)
- [Screenshots](#-screenshots)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Challenges Faced](#-challenges-faced)
- [Simulation & Results](#-simulation--results)
- [Hardware Implementation](#-hardware-implementation)
- [Future Scope](#-future-scope)
- [License](#-license)

---

## ✅ Features
- 🧠 Real-time facial recognition (known/unknown classification)
- 🔔 SMS alerts only for unknown individuals
- 📦 Object detection using MobileNet SSD or YOLOv5
- 💾 Saves frames for all detections with timestamped logs (faces + objects)
- ☁️ Firebase Realtime Database integration for metadata logging
- 🧭 Dashboard UI with separate views for face logs, object logs, alert logs, and full history. Admins can manage access by adding or removing individuals via the dashboard.
- 📹 Live feed control - system doesn't record continuously; users decide when to start surveillance
- 🛠️ Ready for ESP32 and weapon detection integration with Smart Lock integration

---

## 💻 Tech Stack
**Backend:**
- Python, OpenCV, `face_recognition` (dlib)
- YOLOv5
- Firebase Admin SDK, Twilio API
  
**Frontend:**
- HTML / CSS / JavaScript
- Flask for routing/dashboard
  
**Cloud Services:**
- Firebase Realtime Database
- Twilio for SMS notifications

---

## 💻 System Architect

![system-architect](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/system_architect.png)


---


## ⚙️ How It Works
📹 **Live Video Feed:**  
Captured via webcam or ESP32-CAM.
Starts on-demand (not 24/7), maintaining user privacy and resource efficiency.

🔍 **Per Frame Processing:**
- Facial recognition via `face_recognition` / `dlib`
- Object detection using YOLO
- Classification & Actions based on detection:
  - ✅ **Known Face:** Log saved (green), no alert.
  - ❌ **Unknown Face:** Log saved (red), **SMS alert triggered**.
  - 📦 **Object Detected:** Frame saved with logs(no alert).
    
📁 **Storage:**
- Frames saved locally
- Firebase stores **person logs only**
  
📊 **Dashboard:**
- Real-time logs categorized (person/object)
- Accessible visual interface
- live feed
  
---

## 📷 Screenshots

![index](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/index.png)


![login](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/login.png)


![home](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/home.png)


![manage-persons](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/manage_persons.png)


![dashboard](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/dashboard.png)


![object-logs](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/object_detection.png)


![alert-unknown](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/alert.png)


![firebase-realtime](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/firebase_console.png)


---

## 🔌 Requirements

Install the necessary Python packages:

     pip install opencv-python face_recognition firebase-admin twilio numpy 
     imutils


---

## 🚀 Installation

**Clone the repo:**

          git clone https://github.com/2200032091/AI-based-Home-Security-System.git
          cd ai-based-home-security-system
          pip install -r requirements.txt

    
    
Add your Firebase credentials (firebase_credentials.json).
    
Add your Twilio SID, Auth token, and number in sms_alert.py.


**Run:**

    python main.py


---

## ⚠️ Challenges Faced

🧵 **1. Multithreading Issues:**
Handling real-time video stream, face detection, object detection, and Firebase logging caused frame drops and stuttering. Solved via lightweight threading model and frame queue management.

🧠 **2. Caching Recognized Faces:**
Continuous re-checking of known faces slowed down performance. Implemented face encoding caching to speed up recognition.

🔐 **3. Privacy vs. Surveillance Trade-off:**
Instead of 24/7 recording, implemented a live feed toggle, giving the user control over when to monitor — aligning with privacy concerns and reducing CPU load.

🌐 **4. Firebase Write Conflicts:**
Concurrent writes from multiple detections sometimes caused malformed data. Solved using timestamped atomic writes with structured paths.

---

## 🧪 Simulation & Results
- Tested on 4+ known faces, multiple unknowns – accurate classification.
- Average face recognition accuracy > 90%
- Object detection identifies common items with confidence > 60%.
- SMS alert triggers in <3 seconds for unknown intrusions.
- Each detection frame is saved in organized folders.
- Firebase logs update in real time and are displayed on the dashboard.
- Logs categorized cleanly in dashboard

---

## Hardware Implementation
Though current tests are on laptop/webcam, future-ready for hardware deployment:

**Component	Purpose	Status:**
  | Component       | Purpose                          | Status     |
|----------------|----------------------------------|------------|
| ESP32-CAM      | Live feed source, remote usage   | 🔜 Planned |
| LCD Display    | Show logs or status              | 🔜 Optional|
| Raspberry Pi   | Replace PC for real-time detection | 🔜 Future  |
| Webcam         | Current input device             | ✅ In Use  |


---

## 📈 Future Scope
- 🔫 Weapon Detection module using YOLOv8 or ViT models
- 📱 Mobile App with Firebase integration
- 🏠 Face-based door lock/unlock automation
- 📼 Store short video clips instead of frames
- ☁️ Push object detection logs to Firebase
- 🌐 ESP32-CAM standalone + cloud upload module

---

## 📄 License
This project is **not open-source** in the traditional sense.  
It is a **private research prototype** intended solely for:

  - Hackathon evaluation
  - Academic demonstration
  - Personal learning

❗ This project is **not open source**.  
Do not copy, distribute, or reuse any part of this codebase without explicit permission from the author.

---

## “Secure your home like a pro — AI is watching , but only when it should.”






<div align="center">
  © 2025 Harika. All rights reserved.
</div>
