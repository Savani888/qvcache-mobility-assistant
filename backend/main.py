from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from core.semantic_cache import SemanticCache
from core.mobility_engine import MobilityEngine

app = FastAPI(title="Sustainable Smart Mobility Assistant API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
cache = SemanticCache()
engine = MobilityEngine()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response: dict
    cache_status: str
    similarity_score: float
    total_latency: float

@app.get("/")
async def root():
    return {"message": "Mobility Assistant API is running"}

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    start_time = time.time()
    query = request.query

    # 1. Check Cache
    cache_result = cache.search(query)
    
    if cache_result:
        end_time = time.time()
        return QueryResponse(
            query=query,
            response=cache_result['response'],
            cache_status='HIT',
            similarity_score=cache_result['similarity'],
            total_latency=round(end_time - start_time, 4)
        )

    # 2. Cache MISS -> Call Engine
    engine_response = engine.process_query(query)
    
    # 3. Update Cache
    cache.update(query, engine_response)
    
    end_time = time.time()
    return QueryResponse(
        query=query,
        response=engine_response,
        cache_status='MISS',
        similarity_score=1.0, # Fresh query has 1.0 similarity with itself if we were to re-fetch
        total_latency=round(end_time - start_time, 4)
    )

@app.get("/metrics")
async def get_metrics():
    return cache.get_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
