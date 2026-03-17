from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
import time

class SemanticCache:
    def __init__(self, model_name='all-MiniLM-L6-v2', threshold=0.85):
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        self.cache = [] # List of dicts: {'query': str, 'embedding': tensor, 'response': dict, 'timestamp': float}
        self.miss_count = 0
        self.hit_count = 0

    def search(self, query: str):
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        best_score = -1
        best_response = None

        for entry in self.cache:
            score = util.cos_sim(query_embedding, entry['embedding']).item()
            if score > best_score:
                best_score = score
                best_response = entry['response']

        if best_score >= self.threshold:
            self.hit_count += 1
            return {
                'status': 'HIT',
                'response': best_response,
                'similarity': round(best_score, 4),
                'latency': 0.0 # Placeholder, will be calculated in main
            }
        
        self.miss_count += 1
        return None

    def update(self, query: str, response: dict):
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        self.cache.append({
            'query': query,
            'embedding': query_embedding,
            'response': response,
            'timestamp': time.time()
        })

    def get_metrics(self):
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total) if total > 0 else 0
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': round(hit_rate, 4),
            'total_queries': total
        }
