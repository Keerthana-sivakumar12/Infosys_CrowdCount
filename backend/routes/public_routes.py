"""
Public Routes
Public endpoints that don't require authentication
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

router = APIRouter(tags=["Public"])

# Global state (imported from api_server)
live_count = {"total_people": 0, "zones": {}}
latest_frame = None

@router.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "CrowdCount API - Infosys",
        "version": "1.0",
        "status": "operational"
    }

@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CrowdCount API"}

@router.get("/count")
def get_count():
    """
    Get current people count
    Public endpoint - no authentication required
    """
    return live_count

@router.get("/video_feed")
def video_feed():
    """
    Video stream endpoint
    Returns MJPEG stream
    """
    import cv2
    
    def generate():
        global latest_frame
        while True:
            if latest_frame is not None:
                try:
                    _, buffer = cv2.imencode('.jpg', latest_frame)
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                except Exception as e:
                    print(f"Video feed error: {e}")
                    break
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
