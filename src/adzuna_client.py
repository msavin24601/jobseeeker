"""Thin client for the Adzuna job search API."""

import os

import requests

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"


class AdzunaError(RuntimeError):
    pass


def search_jobs(role: str, country: str, where: str, max_days_old: int, results_per_page: int = 20) -> list[dict]:
    """Search Adzuna for a single role query. Returns raw Adzuna job dicts."""
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise AdzunaError("ADZUNA_APP_ID / ADZUNA_APP_KEY environment variables are not set")

    url = f"{ADZUNA_BASE_URL}/{country}/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": role,
        "results_per_page": results_per_page,
        "max_days_old": max_days_old,
        "content-type": "application/json",
    }
    if where:
        params["where"] = where

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("results", [])
