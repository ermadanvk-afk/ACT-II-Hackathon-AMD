import os
import json
import sqlite3
import yaml
import itertools

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "backend", "database", "scheduler.db")
TECH_JSON_PATH = os.path.join(BASE_DIR, "agent1", "data", "curricula", "curricula.json")
YAMLS_DIR = os.path.join(BASE_DIR, "agent2", "Curriculum")

ROLE_MAP = {
    "Software Development Engineer": "SWE",
    "Data Analyst": "DA",
    "Machine Learning Engineer": "ML"
}

def extract_tech_topics(json_data, role_name):
    topics = []
    role_data = json_data.get("career_tracks", {}).get(role_name, {})
    for difficulty in ["beginner", "intermediate", "advanced"]:
        diff_data = role_data.get(difficulty, {})
        for category, item_list in diff_data.items():
            for item in item_list:
                topics.append({"topic": item, "difficulty": difficulty.capitalize(), "type": "tech"})
    return topics

def extract_yaml_topics(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    aptitude_topics = []
    interview_topics = []
    
    for module in data.get("modules", []):
        m_type = module.get("type", "")
        for seq in module.get("sequence", []):
            if m_type == "aptitude":
                aptitude_topics.append({"topic": seq["topic"], "type": "aptitude"})
            else:
                interview_topics.append({"topic": seq["topic"], "type": "mock_interview"})
    return aptitude_topics, interview_topics

def create_table(cursor, table_name):
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            day INTEGER PRIMARY KEY,
            phase TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)

def seed_database():
    with open(TECH_JSON_PATH, 'r', encoding='utf-8') as f:
        tech_json = json.load(f)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    difficulties = ["Beginner", "Intermediate", "Advanced"]

    for full_role, short_role in ROLE_MAP.items():
        table_name = f"Schedule_{short_role}"
        create_table(cursor, table_name)
        
        # 1. Get Tech Topics
        tech_list = extract_tech_topics(tech_json, full_role)
        
        # 2. Get YAML Topics
        yaml_file = os.path.join(YAMLS_DIR, f"{short_role.lower()}_Curriculum.yaml")
        apt_list, int_list = extract_yaml_topics(yaml_file)
        
        if not tech_list: continue
        
        # We need at least 10 interview sessions.
        # So we interleave: Tech, Aptitude, Interview
        
        tech_cycle = itertools.cycle(tech_list)
        apt_cycle = itertools.cycle(apt_list)
        int_cycle = itertools.cycle(int_list)
        
        # Calculate how many total days to seed.
        # Let's seed 30 days (10 Tech, 10 Apt, 10 Interview)
        TOTAL_DAYS = 30
        
        apt_loops = 0
        int_loops = 0
        last_apt = None
        last_int = None
        
        for day in range(1, TOTAL_DAYS + 1):
            if day % 3 == 1:
                item = next(tech_cycle)
                phase = "tech"
                topic = item["topic"]
                difficulty = item["difficulty"]
            elif day % 3 == 2:
                item = next(apt_cycle)
                # If we cycled back to the beginning, increase difficulty
                if last_apt == item["topic"]:
                    apt_loops += 1
                last_apt = item["topic"]
                phase = "aptitude"
                topic = item["topic"]
                diff_idx = min(apt_loops, len(difficulties) - 1)
                difficulty = difficulties[diff_idx]
            else:
                item = next(int_cycle)
                if last_int == item["topic"]:
                    int_loops += 1
                last_int = item["topic"]
                phase = "mock_interview"
                topic = item["topic"]
                diff_idx = min(int_loops, len(difficulties) - 1)
                difficulty = difficulties[diff_idx]

            cursor.execute(
                f"INSERT INTO {table_name} (day, phase, topic, difficulty, status) VALUES (?, ?, ?, ?, ?)",
                (day, phase, topic, difficulty, "pending")
            )
            
    conn.commit()
    conn.close()
    print(f"Successfully created and seeded SQLite database at {DB_PATH}")

if __name__ == "__main__":
    seed_database()
