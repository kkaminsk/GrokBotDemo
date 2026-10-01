# Questions and Recommendations

Review of [spec.md](spec.md) (rev 7).

All questions (Q1 to Q10) and recommendations (R1 to R10) are resolved and folded into the spec. See spec section 14 for where each one landed. New questions or recommendations will be added here as building surfaces them.

## Setup checklist (not spec changes)

- [ ] Create an X developer app and Bearer token on the pay-per-use plan.
- [ ] Turn on 2-Step Verification for your Gmail and create an App Password.
- [ ] Add your Gmail address as a safe sender at bighatgroup.com.
- [ ] Create `vip.txt` with the handles you always want surfaced (gitignored).
- [ ] Get a Grok API key from console.x.ai.
- [ ] Review `voice.md` and edit anything that doesn't sound like you.
- [ ] For local development: copy `.env.example` to `.env`, fill it in, and run `chmod 600 .env`.
- [ ] In Grok Bot, create the "X Reply Scout" Bot, add its Secrets, clone the repo to `/workspace`, and create the routine (spec section 8.1).
- [ ] Before the demo, post on X and have a few people reply, including one on-topic technical question.
