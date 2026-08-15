"""Client for Arbetsformedlingen's JobTech Search API (jobsearch.api.jobtechdev.se).

Free, public, no API key required. Covers the Swedish job market.
"""

import requests

SEARCH_URL = "https://jobsearch.api.jobtechdev.se/search"


def search_jobs(role: str, limit: int = 20) -> list[dict]:
    """Free-text search for a role. Returns normalized job dicts."""
    return _search({"q": role, "limit": limit, "sort": "pubdate-desc"})


def search_by_occupation_group(concept_id: str, limit: int = 20) -> list[dict]:
    """Search within a Swedish taxonomy occupation-group (e.g. IT managers)."""
    return _search({"occupation-group": concept_id, "limit": limit, "sort": "pubdate-desc"})


def _search(params: dict) -> list[dict]:
    response = requests.get(
        SEARCH_URL,
        params=params,
        headers={"accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    hits = response.json().get("hits", [])
    return [_normalize(hit) for hit in hits]


def _normalize(hit: dict) -> dict:
    employer = hit.get("employer") or {}
    address = hit.get("workplace_address") or {}
    description = hit.get("description") or {}
    return {
        "id": hit["id"],
        "title": hit.get("headline") or "Untitled",
        "company": employer.get("name") or employer.get("workplace") or "Unknown company",
        "location": address.get("municipality") or address.get("region") or "",
        "url": hit.get("webpage_url") or "",
        "description": description.get("text") or "",
        "published_date": hit.get("publication_date") or "",
    }
