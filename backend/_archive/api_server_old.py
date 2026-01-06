from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import cv2
import datetime
import os
import sys
import pandas as pd
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Add paths for imports
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'services'))
sys.path.insert(0, os.path.join(backend_dir, 'models'))
sys.path.insert(0, os.path.join(backend_dir, 'auth'))

import camera_feed
import tracking
import zones
import database as db
import auth_service as auth

app = FastAPI(title="CrowdCount - Infosys API", version="1.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
# Since this file is in _archive/, we need to go up two levels to get to project root
backend_dir = os.path.dirname(os.path.dirname(__file__))  # Go up from _archive to backend
project_root = os.path.dirname(backend_dir)  # Go up from backend to project root
frontend_path = os.path.join(project_root, "frontend")

print(f"📁 Frontend path: {frontend_path}")
print(f"📁 Frontend exists: {os.path.exists(frontend_path)}")

if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    print("✅ Frontend static files mounted at /static")
else:
    print(f"❌ Frontend directory not found at: {frontend_path}")

# Global state
live_count = {
    "total_people": 0,
    "zones": {},
    "heat_intensity_history": [],
    "heat_timestamps": []
}

history_log = []  # For CSV export

# ==================== PUBLIC ENDPOINTS ====================

@app.get("/")
def home():
    return {
        "message": "CrowdCount - Infosys API",
        "version": "1.0",
        "endpoints": {
            "auth": ["/login"],
            "public": ["/get_count", "/video_feed"],
            "protected": ["/export_csv", "/export_pdf", "/thresholds", "/analytics"],
            "admin": ["/set_threshold", "/zones"]
        }
    }

@app.post("/login", response_model=auth.Token)
def login(login_data: auth.LoginRequest):
    """Authenticate user and return JWT token"""
    user = auth.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"]
    }

@app.get("/get_count")
def get_count():
    """Get current crowd count (public endpoint)"""
    return live_count

# Shared frame buffer for video feed (updated by main.py)
latest_frame = None

@app.get("/video_feed")
def video_feed():
    """Live video stream with heatmap and detection boxes"""
    print("=== VIDEO FEED ENDPOINT CALLED ===")
    import time
    import numpy as np
    
    def generate():
        print("=== GENERATOR STARTED ===")
        frame_count = 0
        while True:
            try:
                # Use the latest processed frame from main.py
                global latest_frame
                
                if latest_frame is not None:
                    frame_count += 1
                    if frame_count % 30 == 0:  # Log every 30 frames
                        print(f"Streaming frame {frame_count}, shape: {latest_frame.shape}")
                    
                    # Resize for web streaming
                    frame_to_send = cv2.resize(latest_frame, (854, 480))
                    ret, buffer = cv2.imencode('.jpg', frame_to_send, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    else:
                        print("ERROR: Failed to encode frame")
                else:
                    # Send a placeholder frame if no data yet
                    if frame_count == 0:
                        print("No frame available yet, sending placeholder")
                    placeholder = np.zeros((480, 854, 3), dtype=np.uint8)
                    cv2.putText(placeholder, "Waiting for video feed...", (200, 240),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    ret, buffer = cv2.imencode('.jpg', placeholder)
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"=== VIDEO FEED ERROR: {e} ===")
                import traceback
                traceback.print_exc()
                time.sleep(0.1)

    try:
        return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")
    except Exception as e:
        print(f"=== RESPONSE CREATION ERROR: {e} ===")
        import traceback
        traceback.print_exc()
        raise


# ==================== PROTECTED ENDPOINTS (Require Login) ====================

@app.get("/export_csv")
def export_csv(current_user: auth.User = Depends(auth.require_admin)):
    """Export historical data as CSV (Admin only)"""
    if not history_log:
        df = pd.DataFrame(columns=["timestamp", "total_people"] + list(live_count["zones"].keys()))
    else:
        df = pd.DataFrame(history_log)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"crowd_report_{timestamp}.csv"
    file_path = os.path.join(os.path.dirname(__file__), filename)
    df.to_csv(file_path, index=False)

    return FileResponse(file_path, media_type="text/csv", filename=filename)

@app.get("/export_pdf")
def export_pdf(current_user: auth.User = Depends(auth.require_admin)):
    """Export professional PDF report with statistics (Admin only)"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"crowd_report_{timestamp}.pdf"
    file_path = os.path.join(os.path.dirname(__file__), filename)
    
    # Create PDF
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("<b>CrowdCount - Infosys</b><br/>Crowd Analytics Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Report Info
    info = Paragraph(f"<b>Generated:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
                     f"<b>Generated By:</b> {current_user.username} ({current_user.role})<br/>"
                     f"<b>Total People (Current):</b> {live_count['total_people']}", 
                     styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 20))
    
    # Zone Summary Table
    zone_data = [["Zone Name", "Current Count", "Threshold"]]
    thresholds = db.get_all_thresholds()
    for zone_name, count in live_count["zones"].items():
        threshold = thresholds.get(zone_name, {}).get("max_capacity", 30)
        zone_data.append([zone_name, str(count), str(threshold)])
    
    table = Table(zone_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Historical Summary
    if history_log:
        recent = history_log[-10:]
        hist_data = [["Timestamp", "Total People"]]
        for entry in recent:
            hist_data.append([entry["timestamp"], str(entry["total_people"])])
        
        hist_table = Table(hist_data)
        hist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(Paragraph("<b>Recent Activity (Last 10 Entries)</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        elements.append(hist_table)
    
    doc.build(elements)
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

@app.get("/thresholds")
def get_thresholds(current_user: auth.User = Depends(auth.get_current_user)):
    """Get all zone thresholds"""
    return db.get_all_thresholds()

@app.get("/analytics")
def get_analytics(current_user: auth.User = Depends(auth.get_current_user)):
    """Get analytics data from database"""
    recent_logs = db.get_recent_logs(limit=50)
    return {
        "recent_logs": recent_logs,
        "total_entries": len(recent_logs)
    }

# ==================== ADMIN ONLY ENDPOINTS ====================

@app.post("/set_threshold")
def set_threshold(zone_name: str, max_capacity: int, 
                  current_user: auth.User = Depends(auth.require_admin)):
    """Set threshold for a zone (Admin only)"""
    db.set_threshold(zone_name, max_capacity)
    return {"message": f"Threshold for {zone_name} set to {max_capacity}"}

@app.get("/zones")
def get_zones(current_user: auth.User = Depends(auth.require_admin)):
    """Get all zones configuration (Admin only)"""
    from zones import zones
    return {"zones": zones}

# ==================== HELPER FUNCTIONS ====================

def log_current_data(total, zones_data):
    """Log data to history (called from main.py)"""
    global history_log
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_people": total
    }
    entry.update(zones_data)
    history_log.append(entry)
    
    # Also log to database
    try:
        db.log_entry(total, json.dumps(zones_data))
    except Exception as e:
        print(f"Database logging error: {e}")