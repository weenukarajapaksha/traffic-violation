# 🚦 AI-Powered Helmet Violation Detection System

A real-time computer vision system that detects motorcycle helmet violations, extracts license plate numbers using OCR, stores violation data in a database, and provides a web-based monitoring dashboard with search, image preview, and report generation features.

---

# 📌 Features

- 🎥 Real-time helmet violation detection using YOLOv8
- 🧠 Rule-based violation logic
- 🏍️ Person and motorcycle detection
- ⛑️ Helmet / No-Helmet classification
- 🔍 License plate detection
- 🔠 OCR-based number plate extraction using EasyOCR
- 🖼️ Automatic evidence image capture
- 💾 SQLite database storage
- 🌐 Flask-based dashboard
- 🔎 Search violations by plate number
- 🔍 Click-to-enlarge evidence images
- 📊 CSV/PDF report generation
- 🔄 Auto-refreshing dashboard updates
- 📅 Timestamped violation records

---

# 🧠 System Architecture

```text
Camera / Video
      ↓
YOLO Detection (Person, Motorcycle, Helmet)
      ↓
Violation Logic Engine
      ↓
License Plate Detection
      ↓
OCR (Extract Plate Number)
      ↓
Database Storage (SQLite)
      ↓
Flask Dashboard
      ↓
Search / Reports / Evidence Review
