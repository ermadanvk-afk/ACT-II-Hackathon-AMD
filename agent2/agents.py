import os
from crewai import Agent
from agent2.tools import CurriculumReaderTool, KnowledgeBaseSearchTool
from dotenv import load_dotenv

load_dotenv()

# We initialize the tools here so they can be assigned to the agents
curriculum_reader = CurriculumReaderTool()
kb_search = KnowledgeBaseSearchTool()

class PrepAgents:
    def quizmaster_agent(self):
        return Agent(
            role="Technical Quizmaster",
            goal="Generate highly relevant, dynamic aptitude questions based on the exact curriculum and current user performance.",
            backstory=(
                "You are an elite technical interviewer specializing in evaluating candidates for logic, math, and problem-solving skills. "
                "You use the provided curriculum to understand what topic to teach, and you search the knowledge base to get the formulas and context. "
                "You never repeat questions. You generate realistic, real-world data scenarios."
            ),
            tools=[curriculum_reader, kb_search],
            verbose=True,
            allow_delegation=False,
            # llm assignment can be added here if using a specific model, defaults to OPENAI_API_KEY from .env
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
        )

    def interviewer_agent(self):
        # TODO: The architecture for the voice-based interviewer agent is still being finalized.
        # This will be implemented once the STT/TTS pipeline is integrated.
        pass
