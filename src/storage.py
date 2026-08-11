"""Persistence for which job IDs have already been notified about."""

import json
import time
from pathlib import Path

SEEN_JOBS_MAX_AGE_SECONDS = 90 * 24 * 60 * 60  # prune entries older than 90 days


def load_seen(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_seen(path: Path, seen: dict[str, float]) -> None:
    now = time.time()
    pruned = {job_id: ts for job_id, ts in seen.items() if now - ts < SEEN_JOBS_MAX_AGE_SECONDS}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(pruned, f, indent=2, sort_keys=True)
