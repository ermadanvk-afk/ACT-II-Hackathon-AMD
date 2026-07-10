import os
import sys
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(current_dir, "database", "scheduler.db")

# Mount the WebSocket endpoint from agent2
# This ensures everything runs under ONE single server and port!
app.add_api_websocket_route("/ws/interview", interview_endpoint)

class OrchestratorRequest(BaseModel):
    user_id: str
    target_role: str
    current_phase: str  # e.g., "tech", "aptitude", "mock_interview", or "auto"

class AptitudeRequest(BaseModel):
    target_role: str
    topic_name: str
    difficulty: str

class ScheduleUpdateRequest(BaseModel):
    user_id: str
    target_role: str
    day: int
    status: str

@app.post("/api/next-action")
def get_next_action(request: OrchestratorRequest):
    """
    The Master Router. The frontend calls this to figure out what the user should do next.
    """
    role_map = {
        "Software Development Engineer": "SWE",
        "Data Analyst": "DA",
        "Machine Learning Engineer": "ML",
        "SWE": "SWE",
        "DA": "DA",
        "ML": "ML"
    }
    short_role = role_map.get(request.target_role, request.target_role)
    table_name = f"Schedule_{short_role}"
    
    db_phase = None
    db_topic = "General"
    db_difficulty = "Beginner"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE status = 'pending' ORDER BY day ASC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            db_phase = row['phase']
            db_topic = row['topic']
            db_difficulty = row['difficulty']
    except Exception:
        pass # Fallback to mock logic if DB fails
        
    actual_phase = db_phase if request.current_phase in ["auto", "current", ""] and db_phase else request.current_phase
    
    if actual_phase == "tech":
        return {
            "action": "RUN_TECH_PRACTICE",
            "message": f"Starting Technical Practice on {db_topic}.",
            "endpoint": "/api/run-tech",
            "topic": db_topic,
            "difficulty": db_difficulty
        }
    
    elif actual_phase == "aptitude":
        return {
            "action": "RUN_APTITUDE_PRACTICE",
            "message": f"Starting Aptitude Practice on {db_topic}.",
            "endpoint": "/api/run-aptitude",
            "topic": db_topic,
            "difficulty": db_difficulty
        }
        
    elif actual_phase == "mock_interview":
        from urllib.parse import quote
        safe_role = quote(request.target_role)
        safe_topic = quote(db_topic)
        
        return {
            "action": "START_MOCK_INTERVIEW",
            "message": f"Transitioning to Live Video Call for {db_topic}.",
            "websocket_url": f"ws://localhost:8000/ws/interview?role={safe_role}&topic={safe_topic}" 
        }
        
    raise HTTPException(status_code=400, detail="Unknown phase requested.")

@app.get("/api/schedule/{role}")
def get_schedule(role: str):
    """
    Fetch the 30-day schedule for a specific role (SWE, DA, ML).
    """
    role_map = {
        "Software Development Engineer": "SWE",
        "Data Analyst": "DA",
        "Machine Learning Engineer": "ML",
        "SWE": "SWE",
        "DA": "DA",
        "ML": "ML"
    }
    short_role = role_map.get(role, role)
    table_name = f"Schedule_{short_role}"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY day ASC")
        rows = cursor.fetchall()
        conn.close()
        return {"status": "success", "schedule": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule/update")
def update_schedule(request: ScheduleUpdateRequest):
    """
    Update the status of a specific day's task (e.g., 'completed').
    """
    role_map = {
        "Software Development Engineer": "SWE",
        "Data Analyst": "DA",
        "Machine Learning Engineer": "ML",
        "SWE": "SWE",
        "DA": "DA",
        "ML": "ML"
    }
    short_role = role_map.get(request.target_role, request.target_role)
    table_name = f"Schedule_{short_role}"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table_name} SET status = ? WHERE day = ?", (request.status, request.day))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run-aptitude")
def run_aptitude(request: AptitudeRequest):
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
def run_tech(request: TechRequest):
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
