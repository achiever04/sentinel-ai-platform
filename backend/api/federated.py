# ============================================================================
# backend/api/federated.py - Federated Learning API Routes
# ============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.services.federated_service import FederatedService
from backend.services.auth_service import get_current_active_user, require_admin
from backend.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/federated", tags=["Federated Learning"])

class NodeResponse(BaseModel):
    id: int
    node_id: str
    name: str
    status: str
    total_samples: int
    model_version: int
    
    class Config:
        from_attributes = True

class RoundResponse(BaseModel):
    id: int
    round_number: int
    total_nodes: int
    global_accuracy: Optional[float]
    status: str
    
    class Config:
        from_attributes = True

@router.get("/nodes", response_model=List[NodeResponse])
async def list_federated_nodes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all federated learning nodes"""
    nodes = FederatedService.list_nodes(db)
    return nodes

@router.get("/rounds", response_model=List[RoundResponse])
async def list_federated_rounds(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List federated learning rounds"""
    rounds = FederatedService.list_rounds(db, limit)
    return rounds

@router.post("/rounds/start")
async def start_federated_round(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Start new federated learning round (Admin only)"""
    round_data = FederatedService.start_round(db)
    return {"message": "Federated round started", "round": round_data}

@router.get("/rounds/{round_id}/status")
async def get_round_status(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get federated round status"""
    status = FederatedService.get_round_status(db, round_id)
    return status
