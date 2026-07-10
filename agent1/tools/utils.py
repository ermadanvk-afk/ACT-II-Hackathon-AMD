import re
import json

def extract_first_url(search_results) -> str | None:
    """
    Extracts the first http(s) URL from SerperDevTool's output,
    regardless of whether it returns a string, dict, list, or custom object.
    """
    if not search_results:
        return None

    if isinstance(search_results, str):
        match = re.search(r'https?://[^\s\)\]]+', search_results)
        return match.group(0) if match else None

    if isinstance(search_results, dict):
        organic = search_results.get("organic", [])
        if organic and isinstance(organic, list):
            first = organic[0]
            if isinstance(first, dict) and "link" in first:
                return first["link"]
        text_repr = json.dumps(search_results)
        match = re.search(r'https?://[^\s\)\]"]+', text_repr)
        return match.group(0) if match else None

    if isinstance(search_results, list) and search_results:
        first = search_results[0]
        if isinstance(first, dict) and "link" in first:
            return first["link"]

    # Final fallback — force to string and search
    text_repr = str(search_results)
    match = re.search(r'https?://[^\s\)\]"]+', text_repr)
    return match.group(0) if match else None