import os
from crewai import Agent, LLM
from agent2.tools import CurriculumReaderTool, KnowledgeBaseSearchTool
from dotenv import load_dotenv

# Use a relative path to load the .env file from the root directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Monkeypatch LLM.call to strip out 'cache_breakpoint'
# This completely bypasses CrewAI's buggy injection of this field!
_orig_call = LLM.call
def _patched_call(self, messages, *args, **kwargs):
    for m in messages:
        if isinstance(m, dict):
            m.pop('cache_breakpoint', None)
    return _orig_call(self, messages, *args, **kwargs)
LLM.call = _patched_call

# Initialize the Fireworks API via OpenAI-compatible endpoint (no LiteLLM needed).
# Passing provider="openai" explicitly bypasses CrewAI's model-constants validation
# and routes directly to the native OpenAI SDK pointed at Fireworks' base URL.
fireworks_llm = LLM(
    model="accounts/fireworks/models/minimax-m3",
    provider="openai",
    api_key=os.getenv("FIREWORKS_API_KEY"),
    base_url="https://api.fireworks.ai/inference/v1"
)

# We initialize the tools here so they can be assigned to the agents
curriculum_reader = CurriculumReaderTool()
kb_search = KnowledgeBaseSearchTool()

class PrepAgents:
    def quizmaster_agent(self):
        return Agent(
            role="Technical Quizmaster",
            goal="Generate a highly relevant, dynamic set of 8 to 10 Multiple Choice Questions (MCQs) formatted strictly as a JSON array based on the exact curriculum and current user performance.",
            backstory=(
                "You are an elite technical interviewer specializing in evaluating candidates for logic, math, and problem-solving skills. "
                "You use the provided curriculum to understand what topic to teach, and you search the knowledge base to get the formulas and context. "
                "You never repeat questions. You generate realistic, real-world data scenarios and frame them as tricky MCQs with 4 options. "
                "You must always generate exactly 8 to 10 questions covering different aspects of the topic."
            ),
            tools=[curriculum_reader, kb_search],
            verbose=True,
            allow_delegation=False,
            llm=fireworks_llm
        )

    def evaluator_agent(self):
        return Agent(
            role="Performance Evaluator",
            goal="Evaluate the user's answers objectively, explain the correct logic if they fail, and assign a score to track their progress.",
            backstory=(
                "You are an analytical evaluator. You read the user's answer and compare it against the core concepts in the knowledge base. "
                "If the user is wrong, you explain exactly where they made a logical or mathematical error. "
                "If they are right, you praise them and recommend increasing the difficulty."
            ),
            tools=[kb_search],
            verbose=True,
            allow_delegation=False,
            llm=fireworks_llm
        )

    def interviewer_agent(self):
        # TODO: The architecture for the voice-based interviewer agent is still being finalized.
        # This will be implemented once the STT/TTS pipeline is integrated.
        pass
