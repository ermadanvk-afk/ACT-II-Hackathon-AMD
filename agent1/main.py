from crewai import Crew
from tasks.resource_task import resource_task
from agents.resource_agent import resource_agent

crew = Crew(
    agents=[resource_agent],
    tasks=[resource_task],
    verbose=True
)

if __name__ == "__main__":
    result = crew.kickoff(inputs={
    "user_id": "test_user_001",
    "role": "SDE",
    "topic": "Dynamic Programming",
    "level": "intermediate"
    })
    print("\n--- FINAL RESULT ---")
    print(result)