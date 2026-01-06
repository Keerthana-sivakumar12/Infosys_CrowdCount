from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import json

# Use shared folder for database (go up two levels from models/ to backend/, then to shared/)
backend_dir = os.path.dirname(os.path.dirname(__file__))
shared_dir = os.path.join(os.path.dirname(backend_dir), "shared")

# Create shared directory if it doesn't exist
os.makedirs(shared_dir, exist_ok=True)

DB_PATH = os.path.join(shared_dir, "crowd_history.db")
ENGINE = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
Base = declarative_base()

class LogEntry(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_people = Column(Integer)
    zone_data = Column(String)  # JSON string of zones

class Threshold(Base):
    __tablename__ = 'thresholds'
    id = Column(Integer, primary_key=True)
    zone_name = Column(String, unique=True)
    max_capacity = Column(Integer, default=30)
    alert_enabled = Column(Integer, default=1)  # 1=true, 0=false

Base.metadata.create_all(bind=ENGINE)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_entry(total_people, zone_data):
    try:
        db = SessionLocal()
        entry = LogEntry(total_people=total_people, zone_data=str(zone_data))
        db.add(entry)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Database log error: {e}")

def get_threshold(zone_name):
    try:
        db = SessionLocal()
        threshold = db.query(Threshold).filter(Threshold.zone_name == zone_name).first()
        db.close()
        return threshold.max_capacity if threshold else 30
    except Exception as e:
        print(f"Get threshold error: {e}")
        return 30

def set_threshold(zone_name, max_capacity):
    try:
        db = SessionLocal()
        threshold = db.query(Threshold).filter(Threshold.zone_name == zone_name).first()
        if threshold:
            threshold.max_capacity = max_capacity
        else:
            threshold = Threshold(zone_name=zone_name, max_capacity=max_capacity)
            db.add(threshold)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Set threshold error: {e}")

def get_all_thresholds():
    """Get all zone thresholds"""
    try:
        db = SessionLocal()
        thresholds = db.query(Threshold).all()
        result = {t.zone_name: {"max_capacity": t.max_capacity, "alert_enabled": bool(t.alert_enabled)} for t in thresholds}
        db.close()
        return result
    except Exception as e:
        print(f"Get all thresholds error: {e}")
        return {}

def get_recent_logs(limit=100):
    """Get recent log entries for analytics"""
    try:
        db = SessionLocal()
        logs = db.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(limit).all()
        result = []
        for log in logs:
            result.append({
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "total_people": log.total_people,
                "zone_data": json.loads(log.zone_data) if log.zone_data else {}
            })
        db.close()
        return result
    except Exception as e:
        print(f"Get recent logs error: {e}")
        return []