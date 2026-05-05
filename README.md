AI-Powered Helmet Violation Detection System

A real-time computer vision system that detects motorcycle helmet violations, extracts license plate numbers using OCR, and stores violation data with a web-based monitoring dashboard.

Features

Real-time detection using video/webcam
Helmet violation detection using YOLOv8
License plate detection + OCR (EasyOCR)
Automatic violation logging (SQLite database)
Evidence image capture
Flask-based dashboard for monitoring
Export reports as CSV/PDF

System Architecture

Camera / Video
↓
YOLO Detection (Person, Motorcycle, Helmet)
↓
Violation Logic (No Helmet)
↓
License Plate Detection
↓
OCR (Extract Plate Number)
↓
Database Storage (SQLite)
↓
Flask Dashboard (Real-time view)

Tech Stack

Python
OpenCV
YOLOv8 (Ultralytics)
EasyOCR
SQLite
Flask
HTML / CSS

Project Structure

project/

detection.py → Main AI detection script
app.py → Flask dashboard
requirements.txt
README.md

models/

helmet.pt
license_plate_detector.pt

database/

violations.db

static/

violations/ (saved violation images)

templates/

dashboard.html

reports/

CSV/PDF reports

Setup Instructions

Clone repository

git clone https://github.com/weenukarajapaksha/traffic-violation.git
cd helmet-violation-detection

Install dependencies

pip install -r requirements.txt

Run detection system

python detection.py

Run dashboard

python app.py

Open browser:
http://127.0.0.1:5000

How It Works

Detects rider and motorcycle using YOLO
Checks helmet compliance using rule-based logic
Detects license plate of violators
Extracts plate number using OCR
Saves:
Plate number
Timestamp
Violation type
Evidence image
Displays results in dashboard

Sample Output

Plate Number: WPAB1234
Violation: No Helmet
Time: 2026-05-04
Image: Saved in static/violations

Future Improvements

DeepSORT tracking for multi-frame tracking
Automatic fine generation system
Cloud deployment (AWS / Firebase)
Mobile app integration
Email/SMS alert system

Key Learning Outcomes

Multi-model AI system integration
Real-time computer vision pipeline
OCR-based information extraction
Backend + database + frontend integration
Full-stack AI application design

License

This project is for educational and research purposes.

Author

T.N.D. Weenuka Rajapaksha,
Deparment Of Computer Science & Engineering,
University of Moratuwa.
