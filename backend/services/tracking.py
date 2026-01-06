from ultralytics import YOLO
import supervision as sv
import os

# Get the correct path to the model
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "ai_models", "yolov8s.pt")
model = YOLO(model_path)
tracker = sv.ByteTrack()

def track_people(frame):
    results = model(frame, imgsz=640, conf=0.5, verbose=False)[0]
    det = sv.Detections.from_ultralytics(results)
    det = det[det.class_id == 0]  # Only persons

    tracked = tracker.update_with_detections(det)

    people = []
    for xyxy, tid in zip(tracked.xyxy, tracked.tracker_id):
        x1, y1, x2, y2 = map(int, xyxy)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        people.append({
            "id": int(tid),
            "bbox": (x1, y1, x2, y2),
            "centroid": (cx, cy)
        })
    return people