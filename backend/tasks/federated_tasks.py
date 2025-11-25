# ============================================================================
# backend/tasks/federated_tasks.py - Federated Learning Tasks
# ============================================================================

from backend.tasks.celery_app import celery_app
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

@celery_app.task(name='run_federated_round')
def run_federated_round(round_id: int):
    """Execute federated learning round"""
    logger.info(f"Running federated round {round_id}")
    
    try:
        from backend.database import SessionLocal
        from backend.services.federated_service import FederatedService
        from backend.ml.federated_learner import FederatedLearner
        
        db = SessionLocal()
        learner = FederatedLearner()
        
        # Simulate local training on nodes
        local_updates = []
        sample_counts = []
        
        for node_id in [1, 2, 3]:  # Simulate 3 nodes
            update = learner.simulate_local_training(
                f"node_{node_id}",
                num_samples=100 + node_id * 50
            )
            
            local_updates.append(update['model'])
            sample_counts.append(update['samples'])
            
            # Submit update
            FederatedService.submit_update(
                db,
                round_id,
                f"node_{node_id}",
                update['samples'],
                update['accuracy'],
                update['loss']
            )
        
        # Aggregate
        global_model = learner.federated_averaging(local_updates, sample_counts)
        
        # Complete round
        FederatedService.aggregate_round(db, round_id)
        
        db.close()
        
        return {'status': 'completed'}
        
    except Exception as e:
        logger.error(f"Error in federated round: {e}")
        return {'status': 'failed', 'error': str(e)}