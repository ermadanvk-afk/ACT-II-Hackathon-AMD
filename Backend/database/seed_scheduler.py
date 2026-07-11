import os
import json
import sqlite3
import yaml
import itertools

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH  = os.path.join(BASE_DIR, "Backend", "database", "scheduler.db")
TECH_JSON_PATH = os.path.join(BASE_DIR, "agent1", "data", "curricula", "curricula.json")
YAMLS_DIR      = os.path.join(BASE_DIR, "agent2", "Curriculum")

ROLE_MAP = {
    "Software Development Engineer": "SWE",
    "Data Analyst":                  "DA",
    "Machine Learning Engineer":     "ML",
}

LEVELS = ["beginner", "intermediate", "advanced"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_tech_topics_for_level(json_data: dict, role_name: str, level: str) -> list:
    """Return all tech topics for a single role+level combination."""
    topics = []
    role_data = json_data.get("career_tracks", {}).get(role_name, {})
    diff_data  = role_data.get(level, {})
    for category, item_list in diff_data.items():
        for item in item_list:
            topics.append({"topic": item, "category": category, "type": "tech"})
    return topics


def extract_yaml_topics(yaml_path: str):
    """Return aptitude & interview topic lists from a YAML curriculum file."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    aptitude_topics  = []
    interview_topics = []

    for module in data.get("modules", []):
        m_type = module.get("type", "")
        for seq in module.get("sequence", []):
            if m_type == "aptitude":
                aptitude_topics.append({"topic": seq["topic"], "type": "aptitude"})
            else:
                interview_topics.append({"topic": seq["topic"], "type": "mock_interview"})

    return aptitude_topics, interview_topics


# ---------------------------------------------------------------------------
# Difficulty label per level
# ---------------------------------------------------------------------------
DIFFICULTY_LABEL = {
    "beginner":     "Beginner",
    "intermediate": "Intermediate",
    "advanced":     "Advanced",
}

# How aptitude / interview difficulty scales with level
APT_INT_DIFFICULTY = {
    "beginner":     "Beginner",
    "intermediate": "Intermediate",
    "advanced":     "Advanced",
}

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def create_table(cursor, table_name: str):
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            day        INTEGER PRIMARY KEY,
            phase      TEXT    NOT NULL,
            topic      TEXT    NOT NULL,
            difficulty TEXT    NOT NULL,
            status     TEXT    DEFAULT 'pending'
        )
    """)


def seed_level(cursor, table_name: str, tech_list: list,
               apt_list: list, int_list: list, difficulty_label: str,
               total_days: int = 30):
    """
    Fill `total_days` rows in the given table.
    Pattern (repeating): Tech  → Aptitude → Mock Interview
    All rows carry the same difficulty label for the level.
    """
    tech_cycle = itertools.cycle(tech_list) if tech_list else None
    apt_cycle  = itertools.cycle(apt_list)  if apt_list  else None
    int_cycle  = itertools.cycle(int_list)  if int_list  else None

    for day in range(1, total_days + 1):
        remainder = day % 3

        if remainder == 1 and tech_cycle:
            item   = next(tech_cycle)
            phase  = "tech"
            topic  = item["topic"]
        elif remainder == 2 and apt_cycle:
            item   = next(apt_cycle)
            phase  = "aptitude"
            topic  = item["topic"]
        elif remainder == 0 and int_cycle:
            item   = next(int_cycle)
            phase  = "mock_interview"
            topic  = item["topic"]
        else:
            # Fallback: repeat tech if other lists are empty
            if tech_cycle:
                item   = next(tech_cycle)
                phase  = "tech"
                topic  = item["topic"]
            else:
                continue

        cursor.execute(
            f"INSERT INTO {table_name} (day, phase, topic, difficulty, status) VALUES (?, ?, ?, ?, ?)",
            (day, phase, topic, difficulty_label, "pending"),
        )


# ---------------------------------------------------------------------------
# Main seeder
# ---------------------------------------------------------------------------

def seed_database():
    # Ensure the scheduler.db directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with open(TECH_JSON_PATH, "r", encoding="utf-8") as f:
        tech_json = json.load(f)

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for full_role, short_role in ROLE_MAP.items():
        yaml_file = os.path.join(YAMLS_DIR, f"{short_role.lower()}_Curriculum.yaml")
        apt_list, int_list = extract_yaml_topics(yaml_file)

        for level in LEVELS:
            tech_list = extract_tech_topics_for_level(tech_json, full_role, level)
            if not tech_list:
                print(f"  ⚠  No tech topics found for {full_role} / {level} — skipping.")
                continue

            difficulty_label = DIFFICULTY_LABEL[level]
            table_name       = f"Schedule_{short_role}_{difficulty_label}"

            create_table(cursor, table_name)
            seed_level(
                cursor, table_name,
                tech_list, apt_list, int_list,
                difficulty_label,
                total_days=30,
            )
            print(f"  [OK]  Created & seeded: {table_name}  (tech={len(tech_list)}, apt={len(apt_list)}, interview={len(int_list)})")

    conn.commit()
    conn.close()
    print(f"\n[OK]  scheduler.db fully seeded at:\n    {DB_PATH}")


if __name__ == "__main__":
    seed_database()
