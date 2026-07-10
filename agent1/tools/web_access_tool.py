# tools/web_access_tool.py
import json
import os
import re
import asyncio
import httpx
from crewai.tools import tool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from tools.utils import extract_first_url

async def search_github(client: httpx.AsyncClient, topic: str, role: str) -> str:
    query = f"{topic} {role} roadmap OR interview OR notes"
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars"
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"} if os.getenv("GITHUB_TOKEN") else {}
    try:
        resp = await client.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return "GitHub search failed."
        items = resp.json().get("items", [])[:5]
        if not items:
            return "No GitHub results found."
        return "\n".join([f"- {i['full_name']}: {i['html_url']} ({i['description']})" for i in items])
    except httpx.TimeoutException:
        return "GitHub search timed out."
    except Exception as e:
        return f"GitHub search error: {str(e)}"


async def search_youtube(client: httpx.AsyncClient, topic: str, role: str, level: str) -> str:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return "YouTube API key not configured."
    query = f"{role} {topic} {level} interview preparation tutorial"
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet", "q": query, "type": "video",
        "maxResults": 5, "relevanceLanguage": "en", "key": api_key
    }
    try:
        resp = await client.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return "YouTube search failed."
        items = resp.json().get("items", [])
        if not items:
            return "No YouTube results found."
        results = []
        for item in items:
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            channel = item["snippet"]["channelTitle"]
            results.append(f"- {title} (by {channel}): https://www.youtube.com/watch?v={video_id}")
        return "\n".join(results)
    except httpx.TimeoutException:
        return "YouTube search timed out."
    except Exception as e:
        return f"YouTube search error: {str(e)}"


def _sync_docs_and_career_pages(topic: str, role: str, level: str) -> str:
    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()
    query = f"{role} {topic} {level} official documentation OR career preparation"
    try:
        search_results = search_tool.run(search_query=query)
        top_url = extract_first_url(search_results)
        if not top_url:
            return "No relevant docs/career page found."
        page_content = scrape_tool.run(website_url=top_url)
        return page_content[:2000]
    except Exception as e:
        return f"Docs/career page search error: {str(e)}"


async def search_docs_and_career_pages(topic: str, role: str, level: str) -> str:
    return await asyncio.to_thread(_sync_docs_and_career_pages, topic, role, level)


@tool("Web Access Tool")
async def webaccess(role: str, topic: str, level: str) -> str:
    """
    Gathers preparation resources for a given role, topic, and difficulty level
    by searching GitHub, official documentation/career pages, and YouTube — concurrently.
    """
    async with httpx.AsyncClient() as client:
        github_results, youtube_results, docs_results = await asyncio.gather(
            search_github(client, topic, role),
            search_youtube(client, topic, role, level),
            search_docs_and_career_pages(topic, role, level),
        )

    return f"""
=== GitHub Resources ===
{github_results}

=== Official Docs / Career Pages ===
{docs_results}

=== YouTube Videos ===
{youtube_results}
"""