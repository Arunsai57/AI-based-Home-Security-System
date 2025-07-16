>  **Research Prototype**  
> This repository contains unpublished work under active research. Please do not copy, fork, or share.

#  AI-Powered Home Security System with Facial Recognition

An intelligent surveillance system that combines real-time **facial recognition** and **object detection** to enhance home security. It logs activity and sends **SMS alerts** when unknown individuals are detected. Powered by **Firebase** and **Twilio**, this was built as a research prototype to explore how AI can be applied in real-world home automation and security.


---

##  Features
-  Real-time facial recognition (known/unknown classification)
-  SMS alerts only for unknown individuals
-  Object detection using MobileNet SSD or YOLOv5
-  Saves frames for all detections with timestamped logs (faces + objects)
-  Firebase Realtime Database integration for metadata logging
-  Dashboard UI with views for face logs, object logs, alerts, and full detection history. Admins can manage access by adding or removing individuals via the dashboard.
-  Live feed is user-controlled — the system doesn’t record continuously, offering more privacy and control.
-  Ready for ESP32 and weapon detection integration with Smart Lock integration


---

##  Tech Stack

**Backend:** Python, OpenCV, `face_recognition` (dlib) ,YOLOv5 ,Firebase Admin SDK, Twilio API

**Frontend:** - HTML, CSS, JavaScript, Flask

**Cloud:** Firebase Realtime Database, Twilio API

---

##  System Architect

![system-architect](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/system_architect.png)


---


##  How It Works
**Live Video Feed:**  
Captured via webcam or ESP32-CAM.
Starts on-demand (not 24/7), maintaining user privacy and resource efficiency.

**Per Frame Processing:**
- Facial recognition via `face_recognition` / `dlib`
- Object detection using YOLO
- Detection flow:
  -  **Known Face:** Log saved (green), no alert.
  -  **Unknown Face:** Log saved (red), **SMS alert triggered**.
  -  **Object Detected:** Frame saved with logs(no alert).
    
**Storage:**
- Frames saved locally
- Firebase stores **person logs only**
  
**Dashboard:**
- Real-time logs categorized (person/object)
- Accessible visual interface
- live feed
  
---

##  Screenshots

![index](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/index.png)


![login](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/login.png)


![home](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/home.png)


![manage-persons](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/manage_persons.png)


![dashboard](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/dashboard.png)


![object-logs](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/object_detection.png)


![alert-unknown](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/alert.png)


![firebase-realtime](https://github.com/2200032091/AI-based-Home-Security-System/blob/main/static/firebase_console.png)


---

##  Requirements

Install the necessary Python packages:

     pip install opencv-python face_recognition firebase-admin twilio numpy 
     imutils


---

##  Installation

**Clone the repo:**

          git clone https://github.com/2200032091/AI-based-Home-Security-System.git
          cd ai-based-home-security-system
          pip install -r requirements.txt

    
    
Add your Firebase credentials (firebase_credentials.json).
    
Add your Twilio SID, Auth token, and number in sms_alert.py.


**Run:**

    python main.py

---

##  License
This project is **not open-source** in the traditional sense.  
It is a **private research prototype** intended solely for:

  - Hackathon evaluation
  - Academic demonstration
  - Personal learning

  Do not copy, distribute, or reuse any part of this codebase without explicit permission from the author.

---

## “Secure your home like a pro — AI is watching, but only when it should.”






<div align="center">
  © 2025 Harika. All rights reserved.
</div>
