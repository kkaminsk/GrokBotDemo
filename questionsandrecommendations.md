# Questions and Recommendations

Review of [spec.md](spec.md) (rev 3), listing what is still needed before building.
Each question includes a recommended default, so "go with the defaults" is a valid answer.
Answers get folded back into `spec.md`, and resolved items are removed from this file.

## Questions

### Q1. Should items you've already answered be hidden?

Right now the search excludes your own posts, so the bot can't tell whether you already replied to someone. You could get a digest item for a conversation you handled an hour ago.

**Recommended:** yes. Each run makes one extra search call (`from:<you> is:reply since_id=<cursor>`) to find your own recent replies. Any item you've already answered is suppressed and marked handled.

### Q2. Should replies that gain traction later be re-checked?

Engagement is measured once, when a reply is first seen, and replies are never re-evaluated. A fresh reply almost never has 10+ likes yet, so the "high engagement" signal will rarely fire.

**Recommended:** re-fetch metrics once for un-notified replies that are 12 to 24 hours old, in one batched `GET /2/tweets?ids=...` call (up to 100 IDs). The alternative is to drop the engagement signal.

### Q3. Should plain direct questions count?

In the original Q&A, "direct questions asked to me" was not selected. But someone asking "How did you configure Intune for this?" is often the reply most worth answering.

**Recommended:** add a `question` category for Grok, scored on its urgency like the others.

### Q4. Should every blue checkmark count as "verified"?

Paid X Premium checkmarks are cheap, and many bot accounts have them. Right now any verified account gets a weight of 1 **and** bypasses the bot filter.

**Recommended:** only `verified_type` of `business` or `government` gets the weight and the bypass. A plain blue checkmark is treated like any other account.

### Q5. Should VIPs always be surfaced, even for "great post!"?

The spec currently surfaces every VIP reply regardless of content.

**Recommended:** VIP replies are always surfaced unless Grok returns `category = none`. Those are listed in a one-line "VIPs who engaged" section at the bottom of the digest, with no draft.

### Q6. What language should drafts be in?

**Recommended:** reply in the language of the reply. Most will be English. If you want English always, say so.

### Q7. What does the hackathon demo look like, and when is it?

This decides how much of milestones M1 to M4 is realistic and whether a demo mode is needed.

**Recommended:** add a `--demo` flag that runs the full pipeline against recorded sample replies (no X API calls) and prints or emails the digest. That way the demo works on stage even without Wi-Fi or API credits.

### Q8. Which Grok model?

`.env.example` says `grok-3`. Newer Grok models are available and may be cheaper or better at structured output.

**Recommended:** check the current model list at console.x.ai at build time and choose the cheapest model that supports JSON-schema structured output reliably. Keep it configurable through `GROK_MODEL`.

### Q9. How many accounts do you follow?

The following list is fetched daily, 1,000 accounts per call. Under pay-per-use, every account returned is a billed read.

**Recommended:** under about 2,000 follows, keep the daily refresh. Above that, refresh weekly, or drop the following list and rely on `vip.txt` only.

## Recommendations (spec changes)

### R1. Use one search per run instead of one per post (biggest cost saving)

The spec makes one search call per recent post, so 20 posts means 20 calls every run, even when nothing is new. A single query covers all of them:

```
query: (to:<you> is:reply) OR quotes_of_tweet_id:<id1> OR quotes_of_tweet_id:<id2> ...  -from:<you>
since_id: <one global cursor>
```

Results are then matched to posts using `conversation_id`, or the quoted post ID for quote posts. If the query hits the length limit (512 characters on lower tiers), split the quote IDs across 2 to 3 calls. This replaces the per-post `since_id` column with a single cursor.

### R2. Verify search operators against your plan before M1

Confirm on your pay-per-use plan that `quotes_of_tweet_id:`, `to:`, and `conversation_id:` are available, and check the maximum query length. Build a tiny `scripts/probe_x.py` that runs one query and prints the results. This is the riskiest assumption in the spec.

### R3. Make cron reliable in WSL2

Cron doesn't start automatically in WSL2. Runs are also missed while the laptop is asleep or WSL is shut down.

- Option A: enable systemd in WSL (`/etc/wsl.conf`, `[boot] systemd=true`) and use a systemd timer with `Persistent=true`, so missed runs fire on the next start.
- Option B: use Windows Task Scheduler to run `wsl.exe -d <distro> -- /home/dev/GrokBotDemo/.venv/bin/python -m src.digest` with "run task as soon as possible after a scheduled start is missed."

Option B is simpler and survives WSL being idle. Missing a run loses no data, because the cursor catches up on the next run, as long as the gap is under 7 days.

### R4. Fix the Grok categories so they describe content only

The `vip` and `influential_engagement` categories duplicate the rule-based signals, and Grok can't know who your VIPs are anyway. Change the categories to:

`opportunity | question | criticism | misinformation | positive | none`

The rule-based weights continue to handle who the author is. The digest groups items by category, with VIP items listed first.

### R5. Reorder section 4 to match the pipeline

Section 4.0 (bot filter) currently sits after the candidate table. Restructure section 4 as: 4.1 bot filter, 4.2 rule-based signals and weights, 4.3 Grok classification, 4.4 final score. Also add the pipeline diagram from the plan to section 1.

### R6. Update `.gitignore` now, since the repo is public

Add `data/`, `logs/`, `vip.txt`, and `*.db` before any code writes them. VIP handles and stored reply data should never end up in a public repo.

### R7. Protect the `.env` file

The Gmail App Password and X token sit in plain text. Run `chmod 600 .env`, and add a startup check that warns if `.env` is readable by group or others.

### R8. Handle partial Grok batch responses

When 10 replies are sent and Grok returns 9 results, or a mismatched `reply_id`, the missing ones should be retried individually instead of failing the whole batch. Add this to section 11.

### R9. Test with recorded fixtures

X has no sandbox. Save a few real search responses (with handles anonymized) under `tests/fixtures/` and use them in the `x_client` and end-to-end tests. The same fixtures can power `--demo` (Q7).

### R10. Add a simple quality loop (post-hackathon)

To tune the thresholds, add a "Useful? yes / no" `mailto:` link to each digest item that sends a reply to your Gmail. A later version could read those replies and adjust the weights. This is out of scope for v1, but worth noting in the spec's non-goals or future work.

## Setup checklist (not spec changes)

- [ ] Create an X developer app and Bearer token on the pay-per-use plan.
- [ ] Turn on 2-Step Verification for your Gmail and create an App Password.
- [ ] Add your Gmail address as a safe sender at bighatgroup.com.
- [ ] Create `vip.txt` with the handles you always want surfaced.
- [ ] Get a Grok API key from console.x.ai.
- [ ] Review `voice.md` and edit anything that doesn't sound like you.
