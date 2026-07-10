import os
from crewai import Crew, Process
from agent2.agents import PrepAgents
from agent2.tasks import PrepTasks

class PrepCrew:
    def __init__(self, role_profile: str):
        self.agents_config = PrepAgents()
        self.tasks_config = PrepTasks()
        self.base_dir = os.path.dirname(__file__)

        # Dynamically route to the correct curriculum and knowledge base folder based on the role!
        if role_profile == "Data Analyst":
            self.curriculum_path = os.path.join(self.base_dir, "Cirriculum", "da_curriculum.yaml")
            self.kb_dirs = [os.path.join(self.base_dir, "knowledge_base_DA")]
            
        elif role_profile == "Software Engineer":
            self.curriculum_path = os.path.join(self.base_dir, "Cirriculum", "y.yaml") # (Using your y.yaml file)
            self.kb_dirs = [os.path.join(self.base_dir, "knowledge_base_SWE")]
            
        elif role_profile == "Machine Learning Engineer":
            self.curriculum_path = os.path.join(self.base_dir, "Cirriculum", "x.yaml") # (Using your x.yaml file)
            self.kb_dirs = [os.path.join(self.base_dir, "knowledge_base_ML")]
            
        else:
            raise ValueError(f"Unknown role profile: {role_profile}")

    def run_aptitude_cycle(self, topic_name: str, difficulty: str, user_answer: str = None):
        """
        Runs a cycle of generating a question, or evaluating an answer if provided.
        """
        quizmaster = self.agents_config.quizmaster_agent()
        evaluator = self.agents_config.evaluator_agent()
        
        tasks_to_run = []
        
        if not user_answer:
            # Phase 1: Ask a question
            question_task = self.tasks_config.generate_question_task(
                agent=quizmaster,
                curriculum_path=self.curriculum_path,
                kb_dirs=self.kb_dirs,
                topic_name=topic_name,
                difficulty=difficulty
            )
            tasks_to_run.append(question_task)
        else:
            # Phase 2: Evaluate the provided answer
            evaluation_task = self.tasks_config.evaluate_response_task(
                agent=evaluator,
                user_answer=user_answer,
                kb_dirs=self.kb_dirs,
                topic_name=topic_name
            )
            tasks_to_run.append(evaluation_task)

        crew = Crew(
            agents=[quizmaster, evaluator],
            tasks=tasks_to_run,
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    # Example Usage:
    prep_crew = PrepCrew()
    print("=== Starting Aptitude Generation ===")
    
    # We simulate the first loop where we just ask for a question on a topic
    # topic = "Percentages & Growth Rates"
    # output = prep_crew.run_aptitude_cycle(topic_name=topic, difficulty="Medium")
    # print(output)
