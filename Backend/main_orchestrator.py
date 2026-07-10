import os
import sys
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Inject the parent directory into sys.path so we can import agent1 and agent2 without path conflicts
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the existing Interview WebSocket logic
from agent2.interview_server import interview_endpoint

# Attempt to import the Tech Crew (agent1)
try:
    from agent1.main import crew as tech_crew_instance
except ImportError:
    tech_crew_instance = None

# Attempt to import the Aptitude Crew (agent2)
try:
    from agent2.crew import PrepCrew
except ImportError:
    PrepCrew = None

app = FastAPI(title="Principal Orchestrator")

# Mount the WebSocket endpoint from agent2
# This ensures everything runs under ONE single server and port!
app.add_api_websocket_route("/ws/interview", interview_endpoint)

class OrchestratorRequest(BaseModel):
    user_id: str
    target_role: str
    current_phase: str  # e.g., "tech", "aptitude", "mock_interview"

class AptitudeRequest(BaseModel):
    target_role: str
    topic_name: str
    difficulty: str

@app.post("/api/next-action")
async def get_next_action(request: OrchestratorRequest):
    """
    The Master Router. The frontend calls this to figure out what the user should do next.
    """
    # In a real app, you would query the database to see the user's progress.
    # Here, we simulate the routing logic based on the 'current_phase' requested.
    
    if request.current_phase == "tech":
        return {
            "action": "RUN_TECH_PRACTICE",
            "message": "Starting Technical Practice via Agent 1.",
            "endpoint": "/api/run-tech" # Frontend would call this next
        }
    
    elif request.current_phase == "aptitude":
        return {
            "action": "RUN_APTITUDE_PRACTICE",
            "message": "Starting Aptitude Practice via Agent 2.",
            "endpoint": "/api/run-aptitude" # Frontend would call this next
        }
        
    elif request.current_phase == "mock_interview":
        # We pass the role and topic as query parameters so the WebSocket knows what to search the Knowledge Base for!
        from urllib.parse import quote
        safe_role = quote(request.target_role)
        safe_topic = quote(request.topic_name) if hasattr(request, 'topic_name') else "General"
        
        return {
            "action": "START_MOCK_INTERVIEW",
            "message": "Transitioning to Live Video Call.",
            "websocket_url": f"ws://localhost:8000/ws/interview?role={safe_role}&topic={safe_topic}" 
        }
        
    raise HTTPException(status_code=400, detail="Unknown phase requested.")


@app.post("/api/run-aptitude")
async def run_aptitude(request: AptitudeRequest):
    """
    Endpoint to trigger Agent 2's CrewAI logic synchronously.
    """
    if not PrepCrew:
        raise HTTPException(status_code=500, detail="Agent 2 Crew not found.")
        
    try:
        prep_crew = PrepCrew(role_profile=request.target_role)
        output = prep_crew.run_aptitude_cycle(
            topic_name=request.topic_name, 
            difficulty=request.difficulty
        )
        return {"status": "success", "mcq_data": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TechRequest(BaseModel):
    user_id: str
    target_role: str
    topic_name: str
    difficulty: str

@app.post("/api/run-tech")
async def run_tech(request: TechRequest):
    """
    Endpoint to trigger Agent 1's Tech Practice logic synchronously.
    """
    if not tech_crew_instance:
        raise HTTPException(status_code=500, detail="Agent 1 Crew not found.")
        
    try:
        # Agent 1 uses slightly different naming (role, topic, level)
        # The Orchestrator handles mapping these variables so the frontend doesn't have to!
        output = tech_crew_instance.kickoff(inputs={
            "user_id": request.user_id,
            "role": request.target_role,
            "topic": request.topic_name,
            "level": request.difficulty
        })
        return {"status": "success", "tech_data": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # This single server now hosts the Orchestrator APIs AND the Live Voice WebSocket!
    uvicorn.run(app, host="0.0.0.0", port=8000)
