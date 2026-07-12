from crewai import Task

class PrepTasks:
    def generate_question_task(self, agent, curriculum_path: str, kb_dirs: list, topic_name: str, difficulty: str):
        return Task(
            description=(
                f"You need to teach and test the user on the topic: '{topic_name}'. "
                f"1. Use the CurriculumReaderTool on '{curriculum_path}' to find the exact kb_tags associated with '{topic_name}'.\n"
                f"2. Use the KnowledgeBaseSearchTool with those kb_tags and these directories: {kb_dirs} to fetch the theoretical concepts.\n"
                f"3. Generate 8 to 10 dynamic, real-world scenario questions based on the fetched theory. "
                f"The question difficulty should be {difficulty}.\n"
                f"4. Format the output STRICTLY as a valid JSON array of Multiple Choice Questions (MCQs). Do not include markdown formatting blocks (like ```json) or any other conversational text outside the JSON."
            ),
            expected_output='''A valid JSON array containing 8 to 10 objects, matching exactly this structure:
[
    {
        "question": "The scenario and question text here...",
        "options": {
            "A": "Option A text",
            "B": "Option B text",
            "C": "Option C text",
            "D": "Option D text"
        },
        "correct_answer": "C",
        "explanation": "Detailed explanation of why C is correct and others are wrong."
    }
]''',
            agent=agent
        )

    def evaluate_response_task(self, agent, user_answer: str, kb_dirs: list, topic_name: str):
        return Task(
            description=(
                f"The user has submitted their answer: '{user_answer}' for a question on the topic: '{topic_name}'. "
                f"1. Use the KnowledgeBaseSearchTool with directories {kb_dirs} to get the correct mathematical/logical framework for '{topic_name}'.\n"
                f"2. Evaluate if the user's answer is correct based on the logic.\n"
                f"3. Write a constructive feedback response. If they are wrong, explain the steps clearly using the formulas from the KB."
            ),
            expected_output="A detailed feedback explaining if the answer is correct, and the step-by-step logic to solve it.",
            agent=agent
        )
