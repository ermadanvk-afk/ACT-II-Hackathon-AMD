import os
import sys
import asyncio
import sqlite3
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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

try:
    from database.db_setup import init_db
except ImportError:
    from Backend.database.db_setup import init_db
from sqlite3 import IntegrityError

@app.on_event("startup")
def startup_event():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Make sure CORS headers appear even on unhandled 500 errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        },
    )

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

# --- Authentication & Database Endpoints ---

DB_PATH = os.path.join(current_dir, "database", "app.db")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# Import auth utilities directly (assuming Backend is in sys.path or we can use relative)
try:
    from auth import verify_password, get_password_hash, create_access_token, decode_access_token
except ImportError:
    from Backend.auth import verify_password, get_password_hash, create_access_token, decode_access_token

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: sqlite3.Connection = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return dict(user)

class UserCreate(BaseModel):
    username: str
    password: str

@app.post("/api/register")
def register(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pw = get_password_hash(user.password)
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (user.username, hashed_pw))
    db.commit()
    return {"message": "User created successfully"}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (form_data.username,))
    user = cursor.fetchone()
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me")
def get_me(current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    # Fetch user journeys
    cursor = db.cursor()
    cursor.execute("SELECT role, level, current_day FROM user_journeys WHERE user_id = ?", (current_user["id"],))
    journeys = [dict(row) for row in cursor.fetchall()]
    return {"username": current_user["username"], "journeys": journeys}

class JourneyUpdate(BaseModel):
    role: str
    level: str
    current_day: int = 1

@app.post("/api/journey/update")
def update_journey(journey: JourneyUpdate, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM user_journeys WHERE user_id = ? AND role = ? AND level = ?", 
                   (current_user["id"], journey.role, journey.level))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("UPDATE user_journeys SET current_day = ? WHERE id = ?", (journey.current_day, existing["id"]))
    else:
        cursor.execute("INSERT INTO user_journeys (user_id, role, level, current_day) VALUES (?, ?, ?, ?)", 
                       (current_user["id"], journey.role, journey.level, journey.current_day))
    db.commit()
    return {"message": "Journey updated successfully"}

@app.delete("/api/journey/reset")
def reset_journey(role: str, level: str, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM user_journeys WHERE user_id = ? AND role = ? AND level = ?", 
                   (current_user["id"], role, level))
    db.commit()
    return {"message": f"Journey reset for {role} - {level}"}

@app.get("/api/schedule/{role}")
def get_schedule(role: str, level: str = "Beginner"):
    """
    Return the 30-day schedule for a given role and level.
    
    Query params:
      - role  (path):  e.g. "Software Engineer", "Data Analyst", "Machine Learning Engineer"
      - level (query): "Beginner" | "Intermediate" | "Advanced"  (default: Beginner)
    """
    role_map = {
        "Software Development Engineer": "SWE",
        "Software Engineer":             "SWE",
        "Data Analyst":                  "DA",
        "Machine Learning Engineer":     "ML",
    }
    valid_levels = {"Beginner", "Intermediate", "Advanced"}

    short_role = role_map.get(role)
    if not short_role:
        raise HTTPException(status_code=400, detail=f"Invalid role '{role}'. Valid roles: {list(role_map.keys())}")

    # Normalize level casing
    level = level.capitalize()
    if level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"Invalid level '{level}'. Valid levels: {list(valid_levels)}")

    schedule_db_path = os.path.join(current_dir, "database", "scheduler.db")
    if not os.path.exists(schedule_db_path):
        raise HTTPException(status_code=500, detail="Schedule database not found. Run seed_scheduler.py first.")

    conn = sqlite3.connect(schedule_db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    table_name = f"Schedule_{short_role}_{level}"
    try:
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY day ASC")
        schedule = [dict(row) for row in cursor.fetchall()]
        return {"role": role, "level": level, "schedule": schedule}
    except sqlite3.OperationalError:
        raise HTTPException(
            status_code=500,
            detail=f"Table '{table_name}' not found. Re-run seed_scheduler.py to regenerate the database."
        )
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    # This single server now hosts the Orchestrator APIs AND the Live Voice WebSocket!
    uvicorn.run(app, host="0.0.0.0", port=8000)
