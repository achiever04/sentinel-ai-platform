# ============================================================================
# backend/models/federated.py - Federated Learning Models
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base

class FederatedNode(Base):
    """Federated learning node/site"""
    __tablename__ = "federated_nodes"
    
    # Add this at the top of the class
    model_config = {"protected_namespaces": ()}  # FIX PYDANTIC WARNING
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    location = Column(String(200))
    
    # Status
    status = Column(String(20), default="active")  # active, inactive, training
    last_seen = Column(DateTime(timezone=True))
    
    # Metrics
    total_samples = Column(Integer, default=0)
    model_version = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FederatedRound(Base):
    """Federated learning training round"""
    __tablename__ = "federated_rounds"

    model_config = {"protected_namespaces": ()}
    
    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, index=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Participation
    participating_nodes = Column(JSON)  # List of node IDs
    total_nodes = Column(Integer)
    
    # Performance
    global_accuracy = Column(Float)
    global_loss = Column(Float)
    
    # Model
    model_weights_path = Column(String(500))
    aggregation_method = Column(String(50))
    
    status = Column(String(20), default="in_progress")  # in_progress, completed, failed


class FederatedUpdate(Base):
    """Individual node update in a federated round"""
    __tablename__ = "federated_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("federated_rounds.id"))
    node_id = Column(Integer, ForeignKey("federated_nodes.id"))
    
    # Update details
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    update_weights_path = Column(String(500))
    
    # Local training metrics
    local_samples = Column(Integer)
    local_accuracy = Column(Float)
    local_loss = Column(Float)
    training_time = Column(Float)  # seconds
    
    status = Column(String(20), default="submitted")
