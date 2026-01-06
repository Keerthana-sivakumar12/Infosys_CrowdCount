import cv2
import os

cap = None

def start_camera(source=0):
    """
    source: 0 = webcam, "rtsp://..." = IP camera, or video file path
    """
    global cap
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print("Trying fallback video file...")
        video_path = os.path.join(os.path.dirname(__file__), "..", "videos", "sam1.mp4")
        cap = cv2.VideoCapture(video_path)  # fallback
        if not cap.isOpened():
            raise Exception("No camera or video file found!")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    print("Camera/Video ready")
    return cap

def get_camera_frame():
    global cap
    if cap is None or not cap.isOpened():
        return None
    ret, frame = cap.read()
    if not ret:
        return None
    return frame

def stop_camera():
    global cap
    if cap:
        cap.release()
        cap = None