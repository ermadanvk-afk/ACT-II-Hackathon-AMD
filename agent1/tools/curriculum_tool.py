import os
import json
import asyncio
from crewai.tools import tool
from crewai_tools import SerperDevTool

CURRICULA_PATH = os.path.join("data", "curricula", "curricula.json")

# Maps whatever an agent/user might call a role -> the exact key in curricula.json
ROLE_ALIAS_MAP = {
    "sde": "Software Development Engineer",
    "swe": "Software Development Engineer",
    "software development engineer": "Software Development Engineer",
    "software engineer": "Software Development Engineer",
    "data analyst": "Data Analyst",
    "ml engineer": "Machine Learning Engineer",
    "machine learning engineer": "Machine Learning Engineer",
}

VALID_LEVELS = {"beginner", "intermediate", "advanced"}


def _load_curricula() -> dict:
    if not os.path.exists(CURRICULA_PATH):
        return {}
    with open(CURRICULA_PATH, "r") as f:
        return json.load(f)


def _resolve_role_key(role: str) -> str | None:
    key = role.strip().lower()
    return ROLE_ALIAS_MAP.get(key)


def _get_local_curriculum(role: str, level: str) -> dict | str:
    """Returns the {category: [topics]} dict for a role+level, or an error string."""
    role_key = _resolve_role_key(role)
    if not role_key:
        return f"Unsupported role: '{role}'. Supported roles: SDE/SWE, Data Analyst, ML Engineer."

    level_key = level.strip().lower()
    if level_key not in VALID_LEVELS:
        return f"Invalid level: '{level}'. Must be one of {VALID_LEVELS}."

    data = _load_curricula()
    track = data.get("career_tracks", {}).get(role_key)
    if not track:
        return f"No curriculum data found for role: '{role_key}'"

    level_data = track.get(level_key)
    if not level_data:
        return f"No curriculum data found for '{role_key}' at level '{level_key}'"

    return level_data  # dict of {category: [topics]}


def _sync_search_roadmap(role: str, level: str) -> str:
    search_tool = SerperDevTool()
    query = f"{role} {level} interview roadmap 2026 topics to learn"
    try:
        results = search_tool.run(search_query=query)
        if not results:
            return "No roadmap results found."
        results_str = str(results)  # works no matter what type it actually is
        return results_str[:1500]
    except Exception as e:
        return f"Roadmap search error: {str(e)}"


async def search_web_roadmap(role: str, level: str) -> str:
    return await asyncio.to_thread(_sync_search_roadmap, role, level)


@tool("Curriculum Access Tool")
async def curriculumaccess(role: str, level: str = "beginner") -> str:
    """
    Retrieves the structured curriculum (categories and topics) for a given tech role
    and skill level from a locally maintained curriculum file, enriched with a
    live web-sourced roadmap for current industry context.
    Supported roles: SDE/SWE, Data Analyst, ML Engineer.
    Supported levels: beginner, intermediate, advanced.
    """
    local_result = _get_local_curriculum(role, level)

    if isinstance(local_result, str):
        # It's an error message, not curriculum data
        return local_result

    role_key = _resolve_role_key(role)
    roadmap_context = await search_web_roadmap(role_key, level)

    return f"""
=== Local Curriculum ({role_key} - {level.strip().lower()}) ===
{json.dumps(local_result, indent=2)}

=== Live Web Roadmap Context ===
{roadmap_context}
"""