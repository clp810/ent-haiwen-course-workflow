# Repository Instructions

This repository contains reusable course-delivery Skills, tests, and a course-provided Weekly Log template. It does not contain a team's live course state.

- Discover the repository root by walking upward until both `.agents/skills/course-analysis-companion` and `.agents/skills/course-weekly-delivery` exist. Never assume a user home directory.
- Keep raw course materials under `course/weeks/<week-id>/`; this path is ignored by Git.
- Keep real `WEEK_HANDOFF.md`, DRAFT, FINAL, links, names, supervisor details, and interview material under ignored local paths.
- Never invent requirements, users, evidence, interviews, decisions, results, dates, or submission status.
- Cite each course requirement with a file and stable page, slide, section, sheet, or range locator.
- Keep exactly one current DRAFT per deliverable. Create a FINAL only after explicit confirmation and use a versioned filename.
- Do not upload, submit, send messages, or modify cloud documents unless a user separately authorizes that action.
- Run `scripts/test.sh` and `scripts/audit_repository.py` before committing workflow changes.
