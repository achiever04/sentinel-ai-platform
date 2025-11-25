# ============================================================================
# backend/api/alerts.py - Alerts API Routes
# ============================================================================

import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.services.alert_service import AlertService
from backend.services.auth_service import get_current_active_user
from backend.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    camera_id: Optional[int]
    title: str
    message: str
    timestamp: datetime.datetime
    acknowledged: bool
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    camera_id: Optional[int] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List alerts with filters"""
    alerts = AlertService.list_alerts(db, camera_id, severity, acknowledged, limit)
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get alert by ID"""
    alert = AlertService.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge alert"""
    alert = AlertService.acknowledge_alert(db, alert_id, current_user.id)
    return {"message": "Alert acknowledged", "alert": alert}

@router.get("/stats/summary")
async def get_alert_stats(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get alert statistics"""
    from backend.models.alert import Alert
    from datetime import datetime, timedelta
    
    cutoff = datetime.now() - timedelta(hours=hours)
    
    total = db.query(Alert).filter(Alert.timestamp >= cutoff).count()
    critical = db.query(Alert).filter(
        Alert.timestamp >= cutoff,
        Alert.severity == 'critical'
    ).count()
    unacknowledged = db.query(Alert).filter(
        Alert.timestamp >= cutoff,
        Alert.acknowledged == False
    ).count()
    
    return {
        "total": total,
        "critical": critical,
        "unacknowledged": unacknowledged,
        "time_window_hours": hours
    }
