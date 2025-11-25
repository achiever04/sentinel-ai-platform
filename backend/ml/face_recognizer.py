# ============================================================================
# backend/ml/face_recognizer.py - Face Recognition Module
# ============================================================================

import cv2
import face_recognition
import numpy as np
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from backend.config import get_settings
from backend.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)

class FaceRecognizer:
    """
    Face recognition and matching using embeddings
    
    CRITICAL: This system works ONLY with synthetic identities.
    It must not be used to identify real individuals without consent.
    """
    
    def __init__(self, model: str = "small"):
        """
        Initialize face recognizer
        
        Args:
            model: 'small' (faster, 5 points) or 'large' (more accurate, 68 points)
        """
        self.model = model
        self.recognition_threshold = settings.FACE_RECOGNITION_THRESHOLD
        logger.info(f"FaceRecognizer initialized with model: {self.model}")
    
    def get_face_embedding(
        self, 
        image: np.ndarray, 
        face_location: Optional[Tuple] = None,
        num_jitters: int = 1
    ) -> Optional[np.ndarray]:
        """
        Generate face embedding (128-dimensional feature vector)
        
        Args:
            image: Input image (BGR)
            face_location: Known face location (top, right, bottom, left)
            num_jitters: Number of re-samplings for robustness
            
        Returns:
            128-dimensional embedding vector or None if face not found
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get face locations if not provided
        if face_location is None:
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
            if not face_locations:
                return None
            face_location = face_locations[0]
        
        # Generate encoding
        encodings = face_recognition.face_encodings(
            rgb_image,
            known_face_locations=[face_location],
            num_jitters=num_jitters,
            model=self.model
        )
        
        if encodings:
            return encodings[0]
        return None
    
    def compare_faces(
        self,
        known_embeddings: List[np.ndarray],
        query_embedding: np.ndarray,
        threshold: Optional[float] = None
    ) -> Tuple[List[bool], List[float]]:
        """
        Compare query embedding against known embeddings
        
        Args:
            known_embeddings: List of known face embeddings
            query_embedding: Query face embedding
            threshold: Custom threshold (default: use config)
            
        Returns:
            (matches, distances) - Boolean matches and distance scores
        """
        if threshold is None:
            threshold = self.recognition_threshold
        
        # Calculate distances
        distances = face_recognition.face_distance(known_embeddings, query_embedding)
        
        # Determine matches
        matches = [dist <= threshold for dist in distances]
        
        return matches, distances.tolist()
    
    def find_best_match(
        self,
        known_embeddings: List[np.ndarray],
        query_embedding: np.ndarray,
        known_labels: Optional[List[str]] = None
    ) -> Tuple[Optional[int], float, Optional[str]]:
        """
        Find the best matching face
        
        Args:
            known_embeddings: List of known embeddings
            query_embedding: Query embedding
            known_labels: Optional labels for known faces
            
        Returns:
            (best_match_idx, similarity_score, label)
        """
        if not known_embeddings:
            return None, 0.0, None
        
        matches, distances = self.compare_faces(known_embeddings, query_embedding)
        
        if not any(matches):
            return None, 0.0, None
        
        # Find best match (minimum distance)
        best_idx = np.argmin(distances)
        best_distance = distances[best_idx]
        
        # Convert distance to similarity score (1 - distance)
        similarity = 1.0 - best_distance
        
        label = known_labels[best_idx] if known_labels else None
        
        return best_idx, similarity, label
    
    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Returns:
            Similarity score (0-1, higher is more similar)
        """
        # Reshape for cosine_similarity
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def cluster_faces(
        self,
        embeddings: List[np.ndarray],
        threshold: Optional[float] = None
    ) -> List[List[int]]:
        """
        Cluster faces by similarity (simple hierarchical clustering)
        
        Args:
            embeddings: List of face embeddings
            threshold: Distance threshold for clustering
            
        Returns:
            List of clusters, each cluster is a list of indices
        """
        if threshold is None:
            threshold = self.recognition_threshold
        
        if not embeddings:
            return []
        
        clusters = []
        assigned = [False] * len(embeddings)
        
        for i in range(len(embeddings)):
            if assigned[i]:
                continue
            
            # Start new cluster
            cluster = [i]
            assigned[i] = True
            
            # Find similar faces
            for j in range(i + 1, len(embeddings)):
                if assigned[j]:
                    continue
                
                distance = face_recognition.face_distance([embeddings[i]], embeddings[j])[0]
                if distance <= threshold:
                    cluster.append(j)
                    assigned[j] = True
            
            clusters.append(cluster)
        
        return clusters