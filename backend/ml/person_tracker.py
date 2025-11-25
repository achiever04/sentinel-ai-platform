# ============================================================================
# backend/ml/person_tracker.py - Cross-Camera Person Tracking
# ============================================================================

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from scipy.optimize import linear_sum_assignment
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class PersonTracker:
    """
    Track persons across multiple cameras using appearance features
    
    ACADEMIC NOTE: Tracks anonymous IDs only. No real identity data.
    Uses deep learning embeddings for re-identification.
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.65,
        max_age: int = 300  # frames
    ):
        """
        Initialize person tracker
        
        Args:
            similarity_threshold: Minimum similarity for re-identification
            max_age: Maximum frames to keep inactive tracks
        """
        self.similarity_threshold = similarity_threshold
        self.max_age = max_age
        
        # Track database: person_id -> track info
        self.tracks = {}
        self.next_person_id = 1
        
        # Camera-wise active tracks
        self.camera_tracks = defaultdict(list)
        
        logger.info("PersonTracker initialized")
    
    def update(
        self,
        camera_id: int,
        detections: List[Dict],
        frame_id: int
    ) -> List[Dict]:
        """
        Update tracker with new detections
        
        Args:
            camera_id: Camera identifier
            detections: List of detection dictionaries with:
                - bbox: (x, y, w, h)
                - face_embedding: feature vector
                - body_embedding: optional body feature vector
            frame_id: Current frame number
            
        Returns:
            List of tracked detections with person_id assigned
        """
        # Extract embeddings from detections
        detection_embeddings = []
        for det in detections:
            emb = det.get('face_embedding')
            if emb is not None:
                detection_embeddings.append(emb)
            else:
                detection_embeddings.append(np.zeros(128))  # Placeholder
        
        # Match with existing tracks
        if self.camera_tracks[camera_id]:
            assignments = self._match_detections_to_tracks(
                camera_id,
                detection_embeddings,
                frame_id
            )
        else:
            assignments = [-1] * len(detections)
        
        # Update tracks and assign person IDs
        tracked_detections = []
        
        for i, det in enumerate(detections):
            track_idx = assignments[i]
            
            if track_idx == -1:
                # New track
                person_id = self._create_new_track(
                    camera_id,
                    det,
                    detection_embeddings[i],
                    frame_id
                )
            else:
                # Update existing track
                person_id = self.camera_tracks[camera_id][track_idx]['person_id']
                self._update_track(person_id, det, detection_embeddings[i], frame_id)
            
            # Add person_id to detection
            det['person_id'] = f"Person_{person_id:04d}"
            tracked_detections.append(det)
        
        # Remove old tracks
        self._remove_old_tracks(frame_id)
        
        return tracked_detections
    
    def _match_detections_to_tracks(
        self,
        camera_id: int,
        embeddings: List[np.ndarray],
        frame_id: int
    ) -> List[int]:
        """
        Match detections to existing tracks using Hungarian algorithm
        
        Returns:
            List of track indices (-1 for new detections)
        """
        active_tracks = self.camera_tracks[camera_id]
        
        if not active_tracks or not embeddings:
            return [-1] * len(embeddings)
        
        # Build cost matrix (distance matrix)
        n_detections = len(embeddings)
        n_tracks = len(active_tracks)
        cost_matrix = np.zeros((n_detections, n_tracks))
        
        for i, det_emb in enumerate(embeddings):
            for j, track in enumerate(active_tracks):
                track_emb = track['embedding']
                # Cosine distance (1 - similarity)
                similarity = self._compute_similarity(det_emb, track_emb)
                cost_matrix[i, j] = 1.0 - similarity
        
        # Solve assignment problem
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        # Create assignment list
        assignments = [-1] * n_detections
        for i, j in zip(row_ind, col_ind):
            # Only assign if similarity is above threshold
            if cost_matrix[i, j] < (1.0 - self.similarity_threshold):
                assignments[i] = j
        
        return assignments
    
    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings"""
        if emb1 is None or emb2 is None:
            return 0.0
        
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(emb1, emb2) / (norm1 * norm2)
        return float(similarity)
    
    def _create_new_track(
        self,
        camera_id: int,
        detection: Dict,
        embedding: np.ndarray,
        frame_id: int
    ) -> int:
        """Create new track for unmatched detection"""
        person_id = self.next_person_id
        self.next_person_id += 1
        
        # Create track entry
        track_info = {
            'person_id': person_id,
            'embedding': embedding,
            'last_seen': frame_id,
            'first_seen': frame_id,
            'detection_count': 1,
            'cameras_seen': {camera_id},
            'last_bbox': detection['bbox']
        }
        
        self.tracks[person_id] = track_info
        
        # Add to camera-specific tracks
        self.camera_tracks[camera_id].append({
            'person_id': person_id,
            'embedding': embedding,
            'last_seen': frame_id
        })
        
        logger.debug(f"Created new track: Person_{person_id:04d}")
        return person_id
    
    def _update_track(
        self,
        person_id: int,
        detection: Dict,
        embedding: np.ndarray,
        frame_id: int
    ):
        """Update existing track with new detection"""
        if person_id in self.tracks:
            track = self.tracks[person_id]
            track['last_seen'] = frame_id
            track['detection_count'] += 1
            track['last_bbox'] = detection['bbox']
            
            # Update embedding (moving average for robustness)
            alpha = 0.3  # Weight for new embedding
            track['embedding'] = (
                alpha * embedding + (1 - alpha) * track['embedding']
            )
    
    def _remove_old_tracks(self, current_frame: int):
        """Remove tracks that haven't been seen recently"""
        # Remove from global tracks
        to_remove = []
        for person_id, track in self.tracks.items():
            if current_frame - track['last_seen'] > self.max_age:
                to_remove.append(person_id)
        
        for person_id in to_remove:
            del self.tracks[person_id]
            logger.debug(f"Removed old track: Person_{person_id:04d}")
        
        # Remove from camera tracks
        for camera_id in self.camera_tracks:
            self.camera_tracks[camera_id] = [
                t for t in self.camera_tracks[camera_id]
                if current_frame - t['last_seen'] <= self.max_age
            ]
    
    def get_person_info(self, person_id: str) -> Optional[Dict]:
        """Get track information for a person"""
        # Extract numeric ID
        try:
            pid = int(person_id.split('_')[1])
            return self.tracks.get(pid)
        except:
            return None
    
    def cross_camera_reid(
        self,
        query_embedding: np.ndarray,
        camera_id: int = None
    ) -> List[Tuple[int, float]]:
        """
        Re-identify person across cameras
        
        Args:
            query_embedding: Query feature vector
            camera_id: Optional camera to exclude from search
            
        Returns:
            List of (person_id, similarity) tuples, sorted by similarity
        """
        matches = []
        
        for person_id, track in self.tracks.items():
            similarity = self._compute_similarity(query_embedding, track['embedding'])
            if similarity >= self.similarity_threshold:
                matches.append((person_id, similarity))
        
        # Sort by similarity (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
