# jobseeeker

Daily job-match notifications to Telegram (personal DM or a channel), based
on a target-role profile (`config/profile.yaml`). Runs on a GitHub Actions
schedule — no server to maintain.

**Phase 1 (this repo today):** search [JobTech Search](https://jobtechdev.se/)
— Arbetsformedlingen's (Sweden's public employment service) free, keyless
job-search API — for your target roles, dedupe against what's already been
sent, and post new matches to Telegram once a day.

(Note: Adzuna was the original plan here, but it turns out Adzuna doesn't
cover the Nordics at all — no Swedish job index behind it. JobTech Search is
the official government source and needs no signup or API key, so it's a
better fit anyway.)

**Phase 2 (not built yet):** profile-improvement recommendations based on
gaps between your profile and the job postings that come back. Worth
revisiting once phase 1 has been running for a week or two and you've seen
what kind of matches actually show up.

## How it works

- `config/profile.yaml` — target job titles and skill keywords used to rank
  results. Edit this to change what you get notified about.
- `src/jobtech_client.py` — queries the JobTech Search API for each target role.
- `src/main.py` — dedupes results across roles, scores them against your
  skill keywords, drops anything already sent (tracked in
  `data/seen_jobs.json`), and sends the top matches to Telegram.
- `.github/workflows/daily-job-check.yml` — runs `src/main.py` daily and
  commits the updated `data/seen_jobs.json` back to the repo.

## One-time setup

### 1. Telegram bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot`,
   and follow the prompts. Save the bot token it gives you (looks like
   `123456789:AAH...`). Note the bot's `@username` too.

Then pick one:

**Option A — personal DM (simplest):**

1. In Telegram, search for your bot's `@username` and open a chat with it.
2. Send it any message (e.g. `/start`) — bots can't message you first, so
   this step is required.
3. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in a
   browser and find `"chat":{"id": ...}` in the response — that's your
   `TELEGRAM_CHAT_ID` (a positive number).

**Option B — dedicated channel:**

1. Create a new Telegram channel (can be private) for your job alerts.
2. Add your bot to the channel as an **administrator** (Channel settings →
   Administrators → Add Admin).
3. Get the channel's chat ID:
   - Public channel: use `@your_channel_username` directly as the chat ID.
   - Private channel: post any message in the channel, then visit
     `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in a browser
     and look for the `"chat":{"id": ...}` value (it'll be a negative
     number like `-1001234567890`).

### 2. Add GitHub repo secrets

In the repo: **Settings → Secrets and variables → Actions → New repository
secret**. Add:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 3. Push this code and enable the workflow

This folder isn't yet linked to the `jobseeeker` GitHub repo. From inside it:

```bash
git init -b main
git remote add origin https://github.com/msavin24601/jobseeeker.git
git add -A
git commit -m "Add daily job-match notifier"
git pull origin main --allow-unrelated-histories -X ours   # merges past the existing placeholder README
git push -u origin main
```

Then in the repo's **Actions** tab, run "Daily job check" manually
(`workflow_dispatch`) once to confirm it works before waiting for the
schedule.

## Local testing

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...
python src/main.py
```

## Tuning

Edit `config/profile.yaml`:

- `target_roles` — one search per entry; keep phrasing close to how job ads
  are actually titled. Results aren't restricted by location (JobTech Search
  only covers Sweden anyway) — each hit's municipality is shown in the
  Telegram message so you can judge fit.
- `skill_keywords` — used only for ranking (not searching); jobs mentioning
  more of these sort higher.
- `max_results_per_run` — cap on how many new jobs land in one message.
- `max_listing_age_days` — ignore listings older than this.
