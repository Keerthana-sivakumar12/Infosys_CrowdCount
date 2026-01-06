import json
import os
import numpy as np
import cv2
import datetime

# Path to zones file - go up from services to backend, then to project root, then to shared
backend_dir = os.path.dirname(os.path.dirname(__file__))  # services -> backend
project_root = os.path.dirname(backend_dir)  # backend -> project root
shared_dir = os.path.join(project_root, "shared")

# Create shared directory if it doesn't exist
os.makedirs(shared_dir, exist_ok=True)

ZONES_FILE = os.path.join(shared_dir, "zones.json")
zones = []
zone_current_inside = {}      # {zone_id: set of track_ids currently inside}
heatmap_accumulator = None
heatmap_overlay = None

# Optional: for heatmap intensity graph
heat_history = []
heat_timestamps = []
MAX_HEAT_HISTORY = 60

ZONE_COLORS = [
    (0, 255, 0), (255, 0, 0), (0, 0, 255),
    (0, 255, 255), (255, 0, 255), (255, 255, 0)
]

def load_zones():
    global zones
    if os.path.exists(ZONES_FILE) and os.path.getsize(ZONES_FILE) > 0:
        try:
            with open(ZONES_FILE, "r") as f:
                data = json.load(f)
                zones = data.get("zones", [])
        except Exception as e:
            print(f"Error loading zones: {e}")
            zones = []
    else:
        zones = []

def save_zones():
    with open(ZONES_FILE, "w") as f:
        json.dump({"zones": zones}, f, indent=4)

def add_zone(name, points):
    zid = max([z["id"] for z in zones], default=0) + 1
    zones.append({"id": zid, "name": name, "points": points})

def delete_zone_by_id(zid):
    global zones
    zones = [z for z in zones if z["id"] != zid]

def update_zone(zid, points):
    for z in zones:
        if z["id"] == zid:
            z["points"] = points
            break

def is_point_inside_zone(x, y, zone):
    pts = np.array(zone["points"], np.int32)
    return cv2.pointPolygonTest(pts, (float(x), float(y)), False) >= 0

# Initialize heatmap
def init_heatmap(h, w):
    global heatmap_accumulator, heatmap_overlay
    heatmap_accumulator = np.zeros((h, w), dtype=np.float32)
    heatmap_overlay = np.zeros((h, w, 3), dtype=np.uint8)

# Update heatmap - stronger for visibility
def update_heatmap(people, frame_shape):
    global heatmap_accumulator, heat_history, heat_timestamps
    h, w = frame_shape[:2]
    if heatmap_accumulator is None:
        init_heatmap(h, w)

    # Add heat
    for p in people:
        cx, cy = p["centroid"]
        cv2.circle(heatmap_accumulator, (cx, cy), 35, 180, -1)

    heatmap_accumulator *= 0.96

    # Colorize
    temp = cv2.normalize(heatmap_accumulator, None, 0, 255, cv2.NORM_MINMAX)
    temp = np.uint8(temp)
    colored = cv2.applyColorMap(temp, cv2.COLORMAP_JET)
    global heatmap_overlay
    heatmap_overlay = colored

    # Intensity history
    avg_intensity = np.mean(temp)
    heat_history.append(avg_intensity)
    heat_timestamps.append(datetime.datetime.now().strftime("%H:%M:%S"))
    if len(heat_history) > MAX_HEAT_HISTORY:
        heat_history.pop(0)
        heat_timestamps.pop(0)

# Count current unique people
def count_people_in_zones(people):
    global zone_current_inside
    zone_current_inside = {z["id"]: set() for z in zones}

    for p in people:
        pid = p["id"]
        cx, cy = p["centroid"]
        for z in zones:
            if is_point_inside_zone(cx, cy, z):
                zone_current_inside[z["id"]].add(pid)

def get_counts_for_api():
    total = sum(len(zone_current_inside.get(z["id"], set())) for z in zones)
    zone_dict = {z["name"]: len(zone_current_inside.get(z["id"], set())) for z in zones}
    return {
        "total_people": total,
        "zones": zone_dict,
        "heat_intensity_history": heat_history.copy(),
        "heat_timestamps": heat_timestamps.copy()
    }

def draw_all_zones(frame):
    global heatmap_overlay
    for i, z in enumerate(zones):
        pts = np.array(z["points"], np.int32).reshape((-1, 1, 2))
        color = ZONE_COLORS[i % len(ZONE_COLORS)]
        cv2.polylines(frame, [pts], True, color, 3)
        cv2.putText(frame, z["name"], (z["points"][0][0], z["points"][0][1] - 10),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 2)

    # Visible heatmap overlay
    if heatmap_overlay is not None and heatmap_overlay.shape[:2] == frame.shape[:2]:
        frame[:] = cv2.addWeighted(frame, 0.6, heatmap_overlay, 0.4, 0)

def draw_zone_count_display(frame):
    y_offset = 60
    total = sum(len(zone_current_inside.get(z["id"], set())) for z in zones)
    cv2.putText(frame, f"Total People: {total}", (20, y_offset),
                cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 255, 255), 3)
    y_offset += 80

    cv2.putText(frame, "Current Occupancy", (20, y_offset),
                cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
    y_offset += 50

    for i, z in enumerate(zones):
        count = len(zone_current_inside.get(z["id"], set()))
        color = ZONE_COLORS[i % len(ZONE_COLORS)]
        cv2.putText(frame, f"{z['name']}: {count}", (40, y_offset),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 2)
        y_offset += 40