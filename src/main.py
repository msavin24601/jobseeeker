"""Daily job search: query Adzuna for target roles, score against profile
skills, skip anything already notified, and post new matches to Telegram."""

import html
import sys
import time
from pathlib import Path

import yaml

from adzuna_client import AdzunaError, search_jobs
from storage import load_seen, save_seen
from telegram_notify import TelegramError, send_message

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "profile.yaml"
SEEN_JOBS_PATH = ROOT / "data" / "seen_jobs.json"


def load_config() -> dict:
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


def score_job(job: dict, skill_keywords: list[str]) -> int:
    text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    return sum(1 for kw in skill_keywords if kw.lower() in text)


def collect_candidate_jobs(cfg: dict) -> dict[str, dict]:
    """Search every target role and dedupe by Adzuna job id."""
    by_id: dict[str, dict] = {}
    for role in cfg["target_roles"]:
        try:
            results = search_jobs(
                role=role,
                country=cfg["country"],
                where=cfg.get("where", ""),
                max_days_old=cfg["max_listing_age_days"],
            )
        except AdzunaError as e:
            print(f"Skipping role '{role}': {e}", file=sys.stderr)
            continue
        for job in results:
            by_id[job["id"]] = job
    return by_id


def format_message(jobs: list[dict]) -> str:
    lines = [f"<b>{len(jobs)} new job match{'es' if len(jobs) != 1 else ''} today</b>", ""]
    for job in jobs:
        title = html.escape(job.get("title", "Untitled"))
        company = html.escape(job.get("company", {}).get("display_name", "Unknown company"))
        location = html.escape(job.get("location", {}).get("display_name", ""))
        url = job.get("redirect_url", "")
        lines.append(f'• <a href="{url}">{title}</a> — {company} ({location})')
    return "\n".join(lines)


def main() -> None:
    cfg = load_config()
    seen = load_seen(SEEN_JOBS_PATH)

    candidates = collect_candidate_jobs(cfg)
    new_jobs = [job for job_id, job in candidates.items() if job_id not in seen]

    for job in new_jobs:
        job["_score"] = score_job(job, cfg["skill_keywords"])
    new_jobs.sort(key=lambda j: (j["_score"], j.get("created", "")), reverse=True)
    top_jobs = new_jobs[: cfg["max_results_per_run"]]

    if not top_jobs:
        print("No new job matches today.")
        return

    try:
        send_message(format_message(top_jobs))
    except TelegramError as e:
        print(f"Failed to send Telegram notification: {e}", file=sys.stderr)
        sys.exit(1)

    now = time.time()
    for job in top_jobs:
        seen[job["id"]] = now
    save_seen(SEEN_JOBS_PATH, seen)
    print(f"Sent {len(top_jobs)} new job match(es).")


if __name__ == "__main__":
    main()
