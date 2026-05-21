import math
from datetime import datetime
from typing import Dict, Any, List
from memory.base import MemoryRecord

class MemoryScoring:
    def __init__(self, half_life_hours: float = 24.0, 
                 weight_similarity: float = 0.5,
                 weight_importance: float = 0.2,
                 weight_recency: float = 0.15,
                 weight_frequency: float = 0.15):
        self.half_life_hours = half_life_hours
        
        # Calculate decay constant lambda = ln(2) / half_life
        self.decay_constant = math.log(2.0) / self.half_life_hours
        
        # Scoring weights
        self.w_sim = weight_similarity
        self.w_imp = weight_importance
        self.w_rec = weight_recency
        self.w_freq = weight_frequency

    def calculate_importance_score(self, record: MemoryRecord) -> float:
        """Normalize standard importance scale [1, 10] to [0.0, 1.0]."""
        # Ensure value is clamped
        imp = max(1, min(10, record.importance))
        return (imp - 1) / 9.0

    def calculate_recency_score(self, record: MemoryRecord, now: datetime) -> float:
        """
        Calculate exponential decay score based on the elapsed hours since last access.
        S = e^(-lambda * t) where t is in hours.
        """
        time_diff = now - record.last_accessed_at
        elapsed_seconds = max(0.0, time_diff.total_seconds())
        elapsed_hours = elapsed_seconds / 3600.0
        
        # Exponential decay
        return math.exp(-self.decay_constant * elapsed_hours)

    def calculate_frequency_score(self, record: MemoryRecord) -> float:
        """
        Calculate asymptotic access frequency score: 1.0 - 1.0/access_count.
        Gives 0.0 for 1 access, 0.5 for 2, 0.8 for 5, and asymptotic limits at 1.0.
        """
        count = max(1, record.access_count)
        return 1.0 - (1.0 / count)

    def compute_unified_score(self, record: MemoryRecord, similarity: float, now: datetime) -> Dict[str, float]:
        """
        Compute the comprehensive weighted ranking score.
        S_unified = w_sim * S_sim + w_imp * S_imp + w_rec * S_rec + w_freq * S_freq
        """
        s_sim = max(0.0, min(1.0, similarity))
        s_imp = self.calculate_importance_score(record)
        s_rec = self.calculate_recency_score(record, now)
        s_freq = self.calculate_frequency_score(record)
        
        unified = (
            self.w_sim * s_sim +
            self.w_imp * s_imp +
            self.w_rec * s_rec +
            self.w_freq * s_freq
        )
        
        return {
            "unified_score": unified,
            "similarity_score": s_sim,
            "importance_score": s_imp,
            "recency_score": s_rec,
            "frequency_score": s_freq
        }

    def rank_records(self, candidate_records: List[MemoryRecord], 
                     similarities: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Reranks a set of candidate records by their unified scores.
        returns: List of dicts representing rated memories.
        """
        now = datetime.now()
        ranked = []
        
        for record in candidate_records:
            similarity = similarities.get(record.id, 0.0)
            scores = self.compute_unified_score(record, similarity, now)
            
            # Combine record data with scores
            item = record.to_dict()
            item.update(scores)
            ranked.append(item)
            
        # Sort desc by unified score
        ranked.sort(key=lambda x: x["unified_score"], reverse=True)
        return ranked
