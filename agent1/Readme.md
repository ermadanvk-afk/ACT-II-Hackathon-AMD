# Agent 1: Resource Gatherer — TechGuide

Gathers personalized preparation resources (curriculum topics, GitHub repos, 
official docs, YouTube tutorials) for a user's target tech role and skill level.

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in your API keys
3. `python main.py`

## Tools
- **webaccess**: searches GitHub, official docs/career pages, and YouTube (async, concurrent)
- **curriculumaccess**: retrieves structured local curriculum + live roadmap enrichment
- **database_interact**: stores/retrieves gathered resources (SQLite, async)

## Notes on data sources
Reddit and LinkedIn were deliberately excluded due to API access restrictions 
(Reddit's Responsible Builder Policy approval requirement; LinkedIn's partner-only 
data access). GitHub, official docs, and YouTube provide reliable, ToS-compliant 
alternatives.