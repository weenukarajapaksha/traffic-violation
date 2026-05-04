import cv2
from ultralytics import YOLO
import easyocr
import re
import sqlite3
from datetime import datetime

model_general = YOLO("yolov8n.pt")
model_helmet = YOLO("helmet.pt")
model_plate = YOLO("license_plate_detector.pt")

reader = easyocr.Reader(['en'])

conn = sqlite3.connect("violations.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT,
    violation_type TEXT,
    date_time TEXT,
    image_path TEXT
)
""")

conn.commit()

print("Helmet model labels:", model_helmet.names)
print("Plate model labels:", model_plate.names)

def is_overlap(box1, box2):
    x1, y1, x2, y2 = box1
    a1, b1, a2, b2 = box2
    return not (x2 < a1 or x1 > a2 or y2 < b1 or y1 > b2)

def get_head_region(box):
    x1, y1, x2, y2 = box
    h = y2 - y1
    return [x1, y1, x2, int(y1 + 0.4 * h)]

def clean_plate_text(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

def save_violation(plate_number, violation_type, image_path):
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO violations (plate_number, violation_type, date_time, image_path)
    VALUES (?, ?, ?, ?)
    """, (plate_number, violation_type, date_time, image_path))

    conn.commit()
    print("Violation saved to database:", plate_number)

cap = cv2.VideoCapture("wh.mp4")

violation_counter = 0
ocr_done = False
detected_plate_text = ""

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # IMPORTANT: clean frame for detection/OCR
    raw_frame = frame.copy()

    res_gen = model_general(raw_frame, verbose=False)
    res_hel = model_helmet(raw_frame, verbose=False)

    persons = []
    motorcycles = []
    helmets = []
    no_helmets = []



    for box in res_gen[0].boxes:
        conf = float(box.conf[0])
        if conf < 0.5:
            continue

        cls_id = int(box.cls[0])
        label = model_general.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == "person":
            persons.append([x1, y1, x2, y2])
        elif label == "motorcycle":
            motorcycles.append([x1, y1, x2, y2])

    for box in res_hel[0].boxes:
        conf = float(box.conf[0])
        if conf < 0.5:
            continue

        cls_id = int(box.cls[0])
        label = model_helmet.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        label_lower = label.lower().replace(" ", "_")

        if label_lower in ["helmet", "with_helmet"]:
            helmets.append([x1, y1, x2, y2])
        elif label_lower in ["no_helmet", "without_helmet"]:
            no_helmets.append([x1, y1, x2, y2])

    violation_detected = False

    for person in persons:
        for bike in motorcycles:
            if is_overlap(person, bike):
                head = get_head_region(person)
                has_no_helmet = False

                for nh in no_helmets:
                    if is_overlap(head, nh):
                        has_no_helmet = True
                        break

                if has_no_helmet:
                    violation_detected = True

                    x1, y1, x2, y2 = person
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, "No Helmet!", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    if violation_detected:
        violation_counter += 1
    else:
        violation_counter = 0
        ocr_done = False
        detected_plate_text = ""

    if violation_counter > 5:

        # OCR only once per confirmed violation
        if not ocr_done:
            plate_results = model_plate(raw_frame, verbose=False)

            for plate_box in plate_results[0].boxes:
                conf = float(plate_box.conf[0])
                if conf < 0.4:
                    continue

                px1, py1, px2, py2 = map(int, plate_box.xyxy[0])

                # Crop from raw_frame, NOT drawn frame
                plate_crop = raw_frame[py1:py2, px1:px2]

                if plate_crop.size == 0:
                    continue

                # Draw plate box on display frame
                cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 255, 255), 2)
                cv2.putText(frame, "Plate Detected", (px1, py1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                plate_crop = cv2.resize(plate_crop, None, fx=3, fy=3)
                gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)

                ocr_result = reader.readtext(gray)

                for result in ocr_result:
                    text = result[1]
                    cleaned_text = clean_plate_text(text)

                    if len(cleaned_text) >= 4:
                        detected_plate_text = cleaned_text
                        print("Detected Number Plate:", detected_plate_text)

                        image_path = f"static/violations/violations_{detected_plate_text}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        cv2.imwrite(image_path, frame)

                        save_violation(
                            detected_plate_text,
                            "No Helmet",
                            image_path
                        )

                        ocr_done = True
                        break

                if ocr_done:
                    break

        cv2.putText(frame, "VIOLATION CONFIRMED",
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 3)

        if detected_plate_text:
            cv2.putText(frame, f"Plate: {detected_plate_text}",
                        (50, 90), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 255), 3)

    for h in helmets:
        x1, y1, x2, y2 = h
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "Helmet", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    for nh in no_helmets:
        x1, y1, x2, y2 = nh
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, "No Helmet", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    cv2.imshow("Helmet Violation Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()