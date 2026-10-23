# Surok — Geotechnical Reasoning Agent

**A traceable geotechnical calculation pipeline. Not another solver UI.**

Surok is an engineering co-pilot built on OpenClaw. It prepares, runs and verifies geotechnical
calculations over open-source solvers, wrapping every number in a normative chain
`data → norm clause → formula → implementation → test → report`, and treats **“not determined”**
as a first-class result instead of a green checkmark.

## Why

- Calculations live in proprietary silos; the protocol is retyped by hand.
- Expertise asks for provenance, not screenshots.
- AI output is worthless without a chain from clause to number.

## What is inside

| Path | What |
|---|---|
| `index.html` | bilingual landing page (EN + RU section) — GitHub Pages root |
| `presentation/en`, `presentation/ru` | slide decks: purpose, architecture, discipline, evidence, niche |
| `docs/TZ-geotech-surok.md` | engineering specification (public edition, sanitized; v1.6) |
| `docs/competitor-analysis.md` | competitor landscape and the free niche |
| `docs/status.md` | what exists today vs what is planned |
| `agent/` | working persona files of the live agent (SOUL, AGENTS, IDENTITY, TOOLS…) |

## Design pillars

1. **Traceability** — every number resolves to a clause, an edition and a tool version.
2. **Honest statuses** — `выполняется / не выполняется / не определено`; a missing check is never a pass.
3. **Reproducibility by contract** — frozen environments, recorded host, SHA-256 checksums, job journal.
4. **Async compute** — `jobs/<id>/{in,status,out}` over rsync; three retries, then an honest “no result”.
   Local substitution is forbidden.
5. **Human in the loop** — the agent prepares; a specialist signs.

## Status

Engineering spec **v1.6** · contour `geotech-base` (105 packages, import test 21/21) ·
async jobs runner **v2** (per-job timeouts, retention, checksums) · live agent passed **6/6**
acceptance checks incl. the anti-fallback trap · next: **D1 benchmark** — shallow foundations,
bearing resistance `R` and settlement by СП 22.13330.

## Pages

- Landing: <https://sasha-sazonova.github.io/geotech-surok/>
- Presentation EN: `/presentation/en/` · RU: `/presentation/ru/`

## License

Documentation and presentation: Apache-2.0 (see `LICENSE`, `NOTICE`).
Referenced open-source tools and normative documents remain with their respective authors;
normative texts are not included.
