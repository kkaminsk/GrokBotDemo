# GrokBot for X — Reply Follow-up Spec

Status: Draft
Owner: Kevin Kaminski (@kkaminsk)
Last updated: 2026-09-30

## 1. Overview and Goals

GrokBot watches the replies to Kevin's recent posts on X, decides which ones are worth a personal follow-up, and emails a digest with a short explanation and a Grok-drafted suggested reply for each one.

### Goals

- Surface the handful of replies that actually deserve attention, instead of reading every reply.
- Explain *why* each reply was flagged.
- Provide a ready-to-edit suggested reply in Kevin's voice.
- Run unattended on a schedule on Kevin's machine at a predictable, capped API cost.

### Non-goals

- The bot never posts, replies, likes, reposts, follows, or sends DMs. It is read-only on X.
- No web dashboard or chat integrations (email only for v1).
- No analysis of mentions that are not replies to Kevin's posts.

## 2. User Stories

- As Kevin, I get an email at 8:00 and 17:00 listing the 5–10 replies most worth answering, so I can respond without scrolling through every thread.
- As Kevin, I see why each reply was flagged (for example "Verified account, 48k followers, asking about a partnership"), so I can trust the ranking.
- As Kevin, I get a suggested reply under 280 characters that I can copy, edit, and post myself.
- As Kevin, I never see the same reply in two digests.
- As Kevin, I get no email when nothing needs my attention.
- As Kevin, I get a short failure email if a scheduled run crashes, so I know the bot is not silently broken.
- As Kevin, I can add handles to a VIP list so those people are always surfaced.

## 3. X API Integration

Access: X API pay-per-use (or higher tier). All calls use an app-only OAuth 2.0 Bearer token (`X_BEARER_TOKEN`); no user-context write scopes are required.

### 3.1 Endpoints

| Purpose | Endpoint | Key parameters |
|---|---|---|
| Resolve my user ID (once, if `X_USER_ID` unset) | `GET /2/users/by/username/:username` | `X_USERNAME` |
| My recent posts | `GET /2/users/:id/tweets` | `exclude=replies,retweets`, `start_time=now-LOOKBACK_DAYS`, `max_results`, `tweet.fields=conversation_id,created_at,public_metrics` |
| Replies to a post | `GET /2/tweets/search/recent` | `query=conversation_id:<post_id> is:reply -from:<my_username>`, `since_id=<cursor>`, `tweet.fields=author_id,conversation_id,in_reply_to_user_id,referenced_tweets,created_at,public_metrics`, `expansions=author_id`, `user.fields=username,name,public_metrics,verified,verified_type,description` |
| Accounts I follow (cached daily) | `GET /2/users/:id/following` | `max_results=1000`, paginated |

### 3.2 Constraints

- `search/recent` only covers the last 7 days, so `LOOKBACK_DAYS` is capped at 7.
- By default only replies where `in_reply_to_user_id == my_id` (direct replies to Kevin, at any depth of his threads) are scored. `INCLUDE_THREAD_REPLIES=true` also scores side-conversations inside the thread.
- The VIP list is a plain text file (`vip.txt`, one handle per line, gitignored) merged with the cached following list.

### 3.3 Cost Controls

- A `since_id` cursor per post is stored in SQLite so each run only fetches new replies.
- `MAX_POSTS` caps how many recent posts are scanned per run (default 20).
- `MAX_REPLIES` caps replies fetched per post per run (default 100).
- The following list is refreshed at most once every 24 hours.
- Each run records the number of X calls and returned objects, and logs an estimated cost using configurable unit prices (`X_COST_PER_READ`). A run stops fetching once `X_RUN_BUDGET` would be exceeded and notes this in the digest.

## 4. Follow-up Criteria and Scoring

A reply is a candidate if **any** of these apply:

| Signal | Source | Default rule |
|---|---|---|
| Influential author | X user `public_metrics` | `followers_count >= INFLUENCER_MIN_FOLLOWERS` (5,000) |
| Verified author | X user `verified` / `verified_type` | verified is true |
| Followed or VIP author | following cache + `vip.txt` | author in set |
| High engagement | reply `public_metrics` | `like_count + reply_count + retweet_count >= ENGAGEMENT_MIN` (10) |
| Criticism or misinformation | Grok | `category` in (`criticism`, `misinformation`) |
| Business opportunity | Grok | `category == opportunity` |

### 4.1 Rule-based Weight

Computed locally with no API cost. Weights are configurable:

| Signal | Weight env var | Default |
|---|---|---|
| Influential | `W_INFLUENTIAL` | 2 |
| Verified | `W_VERIFIED` | 1 |
| Followed | `W_FOLLOWED` | 2 |
| VIP | `W_VIP` | 4 |
| High engagement | `W_ENGAGEMENT` | 2 |

### 4.2 Grok Classification

Every new reply (after dedupe) is sent to Grok, which returns JSON matching this schema:

```json
{
  "reply_id": "string",
  "category": "opportunity | criticism | misinformation | influential_engagement | vip | none",
  "urgency": 1,
  "reason": "One sentence on why Kevin should (or need not) respond.",
  "suggested_reply": "At most 280 characters, in Kevin's voice. Empty when category is none."
}
```

- `urgency` is an integer from 1 (can ignore) to 5 (respond today).
- Grok receives the original post text, the reply text, the author's handle, bio, and follower count, and the rule-based signals that fired, so it can explain its reasoning.

### 4.3 Final Score and Threshold

```
score = rule_weight + urgency
```

- A reply enters the digest when `score >= SCORE_THRESHOLD` (default 5), **or** the author is on the VIP list (always surfaced), **or** `category` is `misinformation` with `urgency >= 3`.
- Replies with `category == none` and no rule signals are dropped regardless of score.
- The digest is capped at `DIGEST_MAX_ITEMS` (default 10), highest score first.

## 5. Grok Usage

- Grok is called through the existing OpenAI-compatible client (`create_client()` in `src/bot.py`) against `GROK_BASE_URL` with model `GROK_MODEL`.
- Requests use structured output (`response_format` with a JSON schema) so the response parses without guesswork. Responses that fail validation are retried once and then skipped and logged.
- Replies are batched (`GROK_BATCH_SIZE`, default 10) into a single request that returns an array of results, to reduce cost and latency.
- The system prompt includes:
  - Kevin's voice description, loaded from `voice.md` (gitignored, optional; a neutral default is used if missing).
  - The category definitions and scoring guidance from section 4.
  - Rules for drafts: at most 280 characters, no hashtags unless the reply used them, no promises of meetings or money, polite even toward criticism, and corrections cite facts without being combative.
- Reply text is treated as untrusted input. It is wrapped in clear delimiters, and the prompt instructs Grok to ignore any instructions inside it.

## 6. State

SQLite database at `data/grokbot.db` (the `data/` directory is gitignored).

| Table | Columns |
|---|---|
| `posts` | `id` (PK), `created_at`, `text`, `since_id`, `last_checked_at` |
| `replies` | `id` (PK), `post_id`, `author_id`, `author_username`, `text`, `created_at`, `rule_weight`, `category`, `urgency`, `score`, `reason`, `suggested_reply`, `notified_at` (nullable) |
| `following_cache` | `user_id` (PK), `username`, `refreshed_at` |
| `runs` | `id` (PK), `started_at`, `finished_at`, `status`, `x_calls`, `x_objects`, `grok_calls`, `est_cost`, `error` |

- A reply already present in `replies` is never re-sent to Grok.
- `notified_at` is set only after the email is sent successfully, so a failed send is retried on the next run.
- Rows older than `RETENTION_DAYS` (default 30) are purged at the start of each run.

## 7. Email Digest

### 7.1 Transport

SMTP with STARTTLS, configured by `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `DIGEST_FROM`, and `DIGEST_TO`.

- Default example: Microsoft 365 (`smtp.office365.com`, port 587). This requires SMTP AUTH to be enabled for the sending mailbox.
- `DIGEST_TO=kevin.kaminski@bighatgroup.com`.

### 7.2 Content

- Subject: `GrokBot: 4 replies to follow up on (Sep 30, 08:00)`.
- The email is multipart, with HTML and plain-text bodies.
- Items are grouped by category in this order: VIP, Opportunity, Misinformation, Criticism, Influential engagement.
- Each item shows:
  - The author's display name, @handle, follower count, and a verified marker.
  - The reply text and a link to `https://x.com/<handle>/status/<reply_id>`.
  - A snippet of the original post.
  - The reason it was flagged, plus the score and signals that fired.
  - The suggested reply, in a copyable block.
- The footer shows run statistics: posts scanned, replies seen, replies flagged, and estimated cost.

### 7.3 Behavior

- If nothing is flagged, no email is sent unless `SEND_EMPTY_DIGEST=true`.
- If a run crashes, a short failure email with the error summary is sent to `DIGEST_TO`. Failure emails are limited to one per 6 hours.
- `--dry-run` prints the digest to stdout instead of sending it and does not set `notified_at`.

## 8. Scheduling

- Entry point: `python -m src.digest` (flags: `--dry-run`, `--verbose`).
- Example crontab line, which runs at 08:00 and 17:00 local time:

```
0 8,17 * * * cd /home/dev/GrokBotDemo && .venv/bin/python -m src.digest >> logs/digest.log 2>&1
```

- A lock file (`data/digest.lock`, using `fcntl.flock`) prevents two runs from overlapping. If the lock is held, the new run exits immediately with a log line.

## 9. Configuration

Add to `.env.example`:

```
# X API
X_BEARER_TOKEN=
X_USERNAME=
X_USER_ID=
LOOKBACK_DAYS=3
MAX_POSTS=20
MAX_REPLIES=100
INCLUDE_THREAD_REPLIES=false
X_COST_PER_READ=0
X_RUN_BUDGET=1.00

# Scoring
INFLUENCER_MIN_FOLLOWERS=5000
ENGAGEMENT_MIN=10
W_INFLUENTIAL=2
W_VERIFIED=1
W_FOLLOWED=2
W_VIP=4
W_ENGAGEMENT=2
SCORE_THRESHOLD=5
DIGEST_MAX_ITEMS=10
GROK_BATCH_SIZE=10

# Email
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
DIGEST_FROM=
DIGEST_TO=kevin.kaminski@bighatgroup.com
SEND_EMPTY_DIGEST=false

# Storage
RETENTION_DAYS=30
```

Non-secret local files (gitignored): `vip.txt`, `voice.md`, `data/`, `logs/`.

## 10. Module Layout

| Module | Responsibility |
|---|---|
| `src/config.py` | Lazy, typed settings object (see section 15) |
| `src/x_client.py` | X API calls, pagination, rate-limit backoff, call counting |
| `src/store.py` | SQLite schema, migrations, cursors, dedupe, retention |
| `src/scoring.py` | Rule-based signals and weights, final score, threshold logic |
| `src/classifier.py` | Grok batching, prompt, JSON schema validation |
| `src/emailer.py` | Digest rendering (HTML and text) and SMTP send |
| `src/digest.py` | Orchestrates one run, CLI flags, lock file, failure email |

| Test file | Approach |
|---|---|
| `tests/test_x_client.py` | Mocked HTTP responses, including pagination and 429 |
| `tests/test_store.py` | In-memory SQLite |
| `tests/test_scoring.py` | Table-driven cases for each signal and threshold |
| `tests/test_classifier.py` | Mocked Grok client, including invalid JSON retry |
| `tests/test_emailer.py` | Rendering snapshots, mocked `smtplib.SMTP` |
| `tests/test_digest.py` | End-to-end with all external calls mocked, dry run |

New dependency: `httpx` for the X API (plus `respx` for test mocking). No X SDK is required.

## 11. Error Handling

- **X API 429:** wait until the `x-rate-limit-reset` header time (capped at 15 minutes), then retry. After 3 failures, skip the post and continue.
- **X API 5xx or timeouts:** exponential backoff, at most 3 attempts.
- **X API 401 or 403:** abort the run and send a failure email, since the token or plan is likely invalid.
- **Grok errors:** retry once with backoff. On a second failure, save the replies without a classification. They are retried next run and scored with rule weights only in the meantime.
- **SMTP failure:** the run is marked failed and `notified_at` is not set, so the items are included in the next digest.
- Every run writes a row to `runs` with its status and error.

## 12. Security and Privacy

- Secrets (`X_BEARER_TOKEN`, `GROK_API_KEY`, `SMTP_PASSWORD`) live only in `.env`, which is gitignored. They are never logged.
- Reply data is stored only in the local SQLite file and purged after `RETENTION_DAYS`.
- Reply text sent to Grok is limited to what is needed for classification (post text, reply text, and author public profile fields).
- Prompt-injection defense: reply text is delimited and treated as data (section 5). Drafts are never posted automatically.

## 13. Milestones

| Milestone | Scope | Done when |
|---|---|---|
| M1 | Fix scaffold issues (section 15), lazy config, `x_client`, `store`, and printing new replies in the CLI | `python -m src.digest --dry-run` lists new replies to recent posts |
| M2 | `scoring` and `classifier` | Dry run shows ranked items with reasons and drafts |
| M3 | `emailer` and SMTP | A real digest arrives at `DIGEST_TO`, and the same replies are not repeated |
| M4 | Cron, lock file, cost logging, failure email, retention | Two scheduled runs complete unattended, and `runs` shows the costs |

## 14. Open Questions

1. Which SMTP provider and mailbox should send the digest from bighatgroup.com? Does Microsoft 365 SMTP AUTH need to be enabled, or should the bot use Microsoft Graph `sendMail` instead?
2. How should Kevin's voice be described for drafts? (A few sample replies in `voice.md` would work well.)
3. What is the monthly X API budget cap, and the actual per-read pricing for the account's plan (to set `X_COST_PER_READ` and `X_RUN_BUDGET`)?
4. Should replies to quote-posts of Kevin's tweets be included in a later version?

## 15. Existing Scaffold Issues (fix in M1)

- `src/config.py` reads `os.environ["GROK_API_KEY"]` at import time, so `pytest` fails when the variable is not set. It should be replaced with a lazily loaded settings object, or tests should set the variable in a fixture.
- `src/bot.py` imports `src.config`, so `python src/bot.py` (as currently documented) fails with `ModuleNotFoundError`. The documented command should be `python -m src.bot`.
