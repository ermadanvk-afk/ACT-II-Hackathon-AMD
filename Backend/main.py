import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import ResourceRequest, QuizGenerateRequest, QuizEvaluateRequest

# Add the parent directory to sys.path so we can import from agent1 and agent2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="AMD Hackathon Agents API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/resources")
def get_resources(request: ResourceRequest):
    try:
        from agent1.main import crew as agent1_crew
        
        result = agent1_crew.kickoff(inputs={
            "user_id": request.user_id,
            "role": request.role,
            "topic": request.topic,
            "level": request.level
        })
        return {"result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/quiz/generate")
def generate_quiz(request: QuizGenerateRequest):
    try:
        from agent2.crew import PrepCrew
        
        prep_crew = PrepCrew(role_profile=request.role_profile)
        result = prep_crew.run_aptitude_cycle(
            topic_name=request.topic_name, 
            difficulty=request.difficulty
        )
        return {"result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/quiz/evaluate")
def evaluate_quiz(request: QuizEvaluateRequest):
    try:
        from agent2.crew import PrepCrew
        
        prep_crew = PrepCrew(role_profile=request.role_profile)
        result = prep_crew.run_aptitude_cycle(
            topic_name=request.topic_name, 
            difficulty=request.difficulty,
            user_answer=request.user_answer
        )
        return {"result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
