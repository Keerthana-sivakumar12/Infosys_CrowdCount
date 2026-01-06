"""
Unified CrowdCount Server
Combines API server and video processing in one application
"""
import sys
import os
import threading
import cv2
import datetime
import time

# Setup paths
backend_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(backend_dir, 'services'))
sys.path.insert(0, os.path.join(backend_dir, 'models'))
sys.path.insert(0, os.path.join(backend_dir, 'auth'))

print("=" * 60)
print("🔧 Loading modules...")
print("=" * 60)

# Import modules
from _archive.api_server_old import app
import _archive.api_server_old as api_server
import camera_feed as cam
import tracking as tr
import zones as zn
import database as db
import json
import uvicorn

print("✅ Modules loaded successfully")

def video_processing_loop():
    """Process video and update global state"""
    print("=" * 60)
    print("📹 Starting video processing...")
    print("=" * 60)
    
    # Load zones
    zn.load_zones()
    print("✅ Zones loaded")
    
    # Start camera
    try:
        cam.start_camera(0)
        print("✅ Camera started")
    except Exception as e:
        print(f"⚠️ Camera not found: {e}")
        print("📹 Trying video file...")
        try:
            video_path = os.path.join(backend_dir, "videos", "sam1.mp4")
            cam.start_camera(video_path)
            print(f"✅ Video file loaded: {video_path}")
        except Exception as e2:
            print(f"❌ Video file failed: {e2}")
            print("⚠️ Video processing will not work")
            return
    
    print("✅ Video processing started")
    print("=" * 60)
    
    frame_count = 0
    
    while True:
        try:
            frame = cam.get_camera_frame()
            if frame is None:
                time.sleep(0.1)
                continue
            
            frame = cv2.resize(frame, (1280, 720))
            frame_count += 1
            
            # Track people
            people = tr.track_people(frame)
            zn.update_heatmap(people, frame.shape)
            
            # Count people in zones (this function exists in zones.py)
            for person in people:
                cx, cy = person["centroid"]
                for zone in zn.zones:
                    if zn.is_point_inside_zone(cx, cy, zone):
                        zone_name = zone["name"]
                        if zone_name not in zn.zone_current_inside:
                            zn.zone_current_inside[zone_name] = set()
                        zn.zone_current_inside[zone_name].add(person["id"])
            
            # Get counts
            counts = zn.get_counts_for_api()
            
            # Update global state
            api_server.live_count.update(counts)
            
            # Draw on frame
            zn.draw_all_zones(frame)
            zn.draw_zone_count_display(frame)
            
            for p in people:
                x1,y1,x2,y2 = p["bbox"]
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(frame, f"ID:{p['id']}", (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            
            # Update frame for video feed
            api_server.latest_frame = frame.copy()
            
            # Log to database every 5 seconds
            if frame_count % 150 == 0:  # Assuming ~30 FPS
                try:
                    db.log_entry(counts["total_people"], json.dumps(counts["zones"]))
                except Exception as e:
                    print(f"Database logging error: {e}")
            
            # Print status every 10 seconds
            if frame_count % 300 == 0:
                print(f"📊 Processed {frame_count} frames | People: {counts['total_people']}")
            
            time.sleep(0.033)  # ~30 FPS
            
        except Exception as e:
            print(f"⚠️ Video processing error: {e}")
            time.sleep(1)
            continue

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 UNIFIED CROWDCOUNT SERVER")
    print("=" * 60)
    print("")
    print("This server combines:")
    print("  ✅ Web API (FastAPI)")
    print("  ✅ Video Processing (OpenCV + YOLO)")
    print("  ✅ Real-time Updates")
    print("")
    print("=" * 60)
    
    # Start video processing in background thread
    video_thread = threading.Thread(target=video_processing_loop, daemon=True)
    video_thread.start()
    print("✅ Video processing thread started")
    
    # Give video thread time to initialize
    time.sleep(2)
    
    # Start API server
    print("=" * 60)
    print("🌐 Starting API server...")
    print("=" * 60)
    print("📊 Dashboard: http://localhost:8000/static/login.html")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔐 Login: admin / admin123")
    print("=" * 60)
    print("")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        cam.stop_camera()
