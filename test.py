import cv2
from ultralytics import YOLO

model_general = YOLO("yolov8n.pt")   # person + motorcycle
model_helmet = YOLO("helmet.pt")     # helmet / no_helmet

print("Helmet model labels:", model_helmet.names)

def is_overlap(box1, box2):
    x1, y1, x2, y2 = box1
    a1, b1, a2, b2 = box2
    return not (x2 < a1 or x1 > a2 or y2 < b1 or y1 > b2)

def get_head_region(box):
    x1, y1, x2, y2 = box
    h = y2 - y1
    return [x1, y1, x2, int(y1 + 0.4 * h)]

cap = cv2.VideoCapture("helmet.mp4")

violation_counter = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    res_gen = model_general(frame, verbose=False)
    res_hel = model_helmet(frame, verbose=False)

    persons = []
    motorcycles = []
    helmets = []
    no_helmets = []

    # General model detections
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

    # Helmet model detections
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

                # Only trust explicit no_helmet detection
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

    if violation_counter > 5:
        cv2.putText(frame, "VIOLATION CONFIRMED",
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 3)

    # Debug boxes
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