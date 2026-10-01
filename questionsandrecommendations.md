# Questions and Recommendations

Review of [spec.md](spec.md) (rev 4), listing what is still needed before building.
Each question includes a recommended default, so "go with the defaults" is a valid answer.
Answers get folded back into `spec.md`, and resolved items are removed from this file.
Numbers stay the same as items are resolved, so references don't shift.

Resolved so far: Q1, Q2, and Q4, and R1, R2, and R3 (see spec section 14).

## Questions

### Q3. Should plain direct questions count?

In the original Q&A, "direct questions asked to me" was not selected. But someone asking "How did you configure Intune for this?" is often the reply most worth answering.

**Recommended:** add a `question` category for Grok, scored on its urgency like the others.

### Q5. Should VIPs always be surfaced, even for "great post!"?

The spec currently surfaces every VIP reply regardless of content.

**Recommended:** VIP replies are always surfaced unless Grok returns `category = none`. Those are listed in a one-line "VIPs who engaged" section at the bottom of the digest, with no draft.

### Q6. What language should drafts be in?

**Recommended:** reply in the language of the reply. Most will be English. If you want English always, say so.

### Q7. What does the hackathon demo look like, and when is it?

This decides how much of milestones M0 to M4 is realistic and whether a demo mode is needed.

**Recommended:** add a `--demo` flag that runs the full pipeline against recorded sample replies (no X API calls) and prints or emails the digest. That way the demo works on stage even without Wi-Fi or API credits.

### Q8. Which Grok model?

`.env.example` says `grok-3`. Newer Grok models are available and may be cheaper or better at structured output.

**Recommended:** check the current model list at console.x.ai at build time and choose the cheapest model that supports JSON-schema structured output reliably. Keep it configurable through `GROK_MODEL`.

### Q9. How many accounts do you follow?

The following list is fetched daily, 1,000 accounts per call. Under pay-per-use, every account returned is a billed read.

**Recommended:** under about 2,000 follows, keep the daily refresh. Above that, refresh weekly, or drop the following list and rely on `vip.txt` only.

### Q10. How is the custom GrokBot application hosted? (replaces R3)

Spec section 8 is now host-neutral: one run per invocation, logs to stdout, secrets from environment variables, and state under `DATA_DIR`. Four details still decide how M4 is built:

1. **Platform:** what runs the application (for example an xAI or Grok agent runtime, a container service such as Azure Container Apps Jobs, or a VM)?
2. **Scheduler:** does the platform trigger runs at 08:00 and 17:00 itself, or does GrokBot need its own internal scheduler loop?
3. **Persistent storage:** does `DATA_DIR` survive between runs? If not, the SQLite state (cursor, dedupe, following cache) is lost every run, and every reply would be re-sent to Grok and re-emailed. Storage would then need to move to a mounted volume, a blob or file share, or a hosted database.
4. **Secrets:** how are the X token, Grok key, and Gmail App Password provided (platform secret store, Key Vault, or environment variables)?

**Recommended:** if you're not sure yet, use a scheduled container job (for example Azure Container Apps Jobs with a cron trigger), with `DATA_DIR` on a mounted Azure Files share and secrets from Key Vault. This needs no code changes beyond what section 8 already describes.

## Recommendations (spec changes)

### R4. Fix the Grok categories so they describe content only

The `vip` and `influential_engagement` categories duplicate the rule-based signals, and Grok can't know who your VIPs are anyway. Change the categories to:

`opportunity | question | criticism | misinformation | positive | none`

The rule-based weights continue to handle who the author is. The digest groups items by category, with VIP items listed first.

### R5. Reorder section 4 to match the pipeline

Section 4.0 (bot filter) currently sits after the candidate table. Restructure section 4 as: 4.1 bot filter, 4.2 rule-based signals and weights, 4.3 Grok classification, 4.4 final score. Also add a pipeline diagram to section 1.

### R6. Update `.gitignore` now, since the repo is public

Add `data/`, `vip.txt`, and `*.db` before any code writes them. VIP handles and stored reply data should never end up in a public repo.

### R7. Protect secrets

Locally, run `chmod 600 .env`, and add a startup check that warns if `.env` is readable by group or others. On the host, use the platform's secret store rather than a `.env` file (see Q10).

### R8. Handle partial Grok batch responses

When 10 replies are sent and Grok returns 9 results, or a mismatched `reply_id`, the missing ones should be retried individually instead of failing the whole batch. Add this to section 11.

### R9. Test with recorded fixtures

X has no sandbox. Save a few real search responses (with handles anonymized) under `tests/fixtures/`, for example from the M0 probe script. Use them in the `x_client` and end-to-end tests. The same fixtures can power `--demo` (Q7).

### R10. Add a simple quality loop (post-hackathon)

To tune the thresholds, add a "Useful? yes / no" `mailto:` link to each digest item that sends a reply to your Gmail. A later version could read those replies and adjust the weights. This is out of scope for v1, but worth noting in the spec's non-goals or future work.

## Setup checklist (not spec changes)

- [ ] Create an X developer app and Bearer token on the pay-per-use plan.
- [ ] Turn on 2-Step Verification for your Gmail and create an App Password.
- [ ] Add your Gmail address as a safe sender at bighatgroup.com.
- [ ] Create `vip.txt` with the handles you always want surfaced.
- [ ] Get a Grok API key from console.x.ai.
- [ ] Review `voice.md` and edit anything that doesn't sound like you.
