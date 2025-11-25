# ============================================================================
# backend/services/federated_service.py - Federated Learning Service
# ============================================================================

from sqlalchemy.orm import Session
from typing import List, Dict
from backend.models.federated import FederatedNode, FederatedRound, FederatedUpdate
from backend.utils.logger import setup_logger
from datetime import datetime
import numpy as np

logger = setup_logger(__name__)

class FederatedService:
    """
    Service for federated learning coordination
    
    ACADEMIC DEMONSTRATION: Simulates privacy-preserving distributed learning
    """
    
    @staticmethod
    def list_nodes(db: Session) -> List[FederatedNode]:
        """List all federated nodes"""
        return db.query(FederatedNode).all()
    
    @staticmethod
    def list_rounds(db: Session, limit: int = 20) -> List[FederatedRound]:
        """List federated learning rounds"""
        return db.query(FederatedRound).order_by(
            FederatedRound.round_number.desc()
        ).limit(limit).all()
    
    @staticmethod
    def start_round(db: Session) -> FederatedRound:
        """Start new federated learning round"""
        # Get active nodes
        active_nodes = db.query(FederatedNode).filter(
            FederatedNode.status == 'active'
        ).all()
        
        if len(active_nodes) < 2:
            raise ValueError("Need at least 2 active nodes for federated learning")
        
        # Get next round number
        last_round = db.query(FederatedRound).order_by(
            FederatedRound.round_number.desc()
        ).first()
        
        round_number = (last_round.round_number + 1) if last_round else 1
        
        # Create new round
        new_round = FederatedRound(
            round_number=round_number,
            total_nodes=len(active_nodes),
            participating_nodes=[node.node_id for node in active_nodes],
            status='in_progress'
        )
        
        db.add(new_round)
        db.commit()
        db.refresh(new_round)
        
        logger.info(f"Started federated round {round_number} with {len(active_nodes)} nodes")
        return new_round
    
    @staticmethod
    def submit_update(
        db: Session,
        round_id: int,
        node_id: str,
        local_samples: int,
        local_accuracy: float,
        local_loss: float
    ) -> FederatedUpdate:
        """Submit local update from a node"""
        node = db.query(FederatedNode).filter(
            FederatedNode.node_id == node_id
        ).first()
        
        if not node:
            raise ValueError(f"Node {node_id} not found")
        
        update = FederatedUpdate(
            round_id=round_id,
            node_id=node.id,
            local_samples=local_samples,
            local_accuracy=local_accuracy,
            local_loss=local_loss,
            status='submitted'
        )
        
        db.add(update)
        db.commit()
        db.refresh(update)
        
        return update
    
    @staticmethod
    def aggregate_round(db: Session, round_id: int) -> FederatedRound:
        """Aggregate updates and complete round"""
        round_obj = db.query(FederatedRound).filter(
            FederatedRound.id == round_id
        ).first()
        
        if not round_obj:
            raise ValueError(f"Round {round_id} not found")
        
        # Get all updates
        updates = db.query(FederatedUpdate).filter(
            FederatedUpdate.round_id == round_id
        ).all()
        
        if not updates:
            raise ValueError("No updates to aggregate")
        
        # Aggregate metrics (FedAvg approach - weighted by samples)
        total_samples = sum(u.local_samples for u in updates)
        
        global_accuracy = sum(
            u.local_accuracy * u.local_samples for u in updates
        ) / total_samples
        
        global_loss = sum(
            u.local_loss * u.local_samples for u in updates
        ) / total_samples
        
        # Update round
        round_obj.global_accuracy = global_accuracy
        round_obj.global_loss = global_loss
        round_obj.completed_at = datetime.now()
        round_obj.status = 'completed'
        
        db.commit()
        db.refresh(round_obj)
        
        logger.info(f"Completed round {round_obj.round_number}: "
                   f"accuracy={global_accuracy:.4f}, loss={global_loss:.4f}")
        
        return round_obj
    
    @staticmethod
    def get_round_status(db: Session, round_id: int) -> Dict:
        """Get detailed status of a round"""
        round_obj = db.query(FederatedRound).filter(
            FederatedRound.id == round_id
        ).first()
        
        if not round_obj:
            return {"error": "Round not found"}
        
        updates = db.query(FederatedUpdate).filter(
            FederatedUpdate.round_id == round_id
        ).all()
        
        return {
            "round_number": round_obj.round_number,
            "status": round_obj.status,
            "total_nodes": round_obj.total_nodes,
            "updates_received": len(updates),
            "global_accuracy": round_obj.global_accuracy,
            "global_loss": round_obj.global_loss,
            "started_at": round_obj.started_at.isoformat(),
            "completed_at": round_obj.completed_at.isoformat() if round_obj.completed_at else None
        }
