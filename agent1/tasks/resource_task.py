from crewai import Task
from agents.resource_agent import resource_agent

resource_task = Task(
    description=(
        "Gather high-quality preparation resources for user '{user_id}' targeting the "
        "'{role}' role, focusing on '{topic}' at '{level}' level. "
        "First use the curriculum tool to understand what should be covered. "
        "Then use the web access tool to find current resources (GitHub, docs, YouTube). "
        "Finally, store the gathered resources using the database tool with action='store', "
        "using user_id='{user_id}', role='{role}', topic='{topic}', level='{level}'."
    ),
    expected_output=(
        "A structured summary of gathered resources: curriculum topics for this "
        "level, relevant GitHub repos, official docs/career page content, and "
        "YouTube video links — confirmed as stored in the database."
    ),
    agent=resource_agent
)