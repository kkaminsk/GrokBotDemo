# Questions and Recommendations

Review of [spec.md](spec.md) (rev 6), listing what is still needed before building.
Answers get folded back into `spec.md`, and resolved items are removed from this file.
Numbers stay the same as items are resolved, so references don't shift.

Resolved so far: all questions (Q1 to Q10), and recommendations R1 to R4 (see spec section 14).

## Recommendations (spec changes)

### R5. Reorder section 4 to match the pipeline

Section 4.0 (bot filter) currently sits after the candidate table. Restructure section 4 as: 4.1 bot filter, 4.2 rule-based signals and weights, 4.3 Grok classification, 4.4 final score. Also add a pipeline diagram to section 1.

### R6. Update `.gitignore` now, since the repo is public

Add `data/`, `vip.txt`, and `*.db` before any code writes them. VIP handles and stored reply data should never end up in a public repo.

### R7. Protect secrets

Locally, run `chmod 600 .env`, and add a startup check that warns if `.env` is readable by group or others. On Grok Bot, use the Bot's Secrets section rather than a `.env` file (spec section 8.1).

### R8. Handle partial Grok batch responses

When 10 replies are sent and Grok returns 9 results, or a mismatched `reply_id`, the missing ones should be retried individually instead of failing the whole batch. Add this to section 11.

### R9. Test with recorded fixtures

X has no sandbox. Save a few real search responses (with handles anonymized) under `tests/fixtures/`, for example from the M0 probe script. Use them in the `x_client` and end-to-end tests. This also makes it possible to rehearse the hackathon demo flow without waiting for real replies.

### R10. Add a simple quality loop (post-hackathon)

To tune the thresholds, add a "Useful? yes / no" `mailto:` link to each digest item that sends a reply to your Gmail. A later version could read those replies and adjust the weights. This is out of scope for v1, but worth noting in the spec's non-goals or future work.

## Setup checklist (not spec changes)

- [ ] Create an X developer app and Bearer token on the pay-per-use plan.
- [ ] Turn on 2-Step Verification for your Gmail and create an App Password.
- [ ] Add your Gmail address as a safe sender at bighatgroup.com.
- [ ] Create `vip.txt` with the handles you always want surfaced.
- [ ] Get a Grok API key from console.x.ai.
- [ ] Review `voice.md` and edit anything that doesn't sound like you.
- [ ] In Grok Bot, create the "X Reply Scout" Bot, add its Secrets, clone the repo to `/workspace`, and create the routine (spec section 8.1).
- [ ] Before the demo, post on X and have a few people reply, including one on-topic technical question.
