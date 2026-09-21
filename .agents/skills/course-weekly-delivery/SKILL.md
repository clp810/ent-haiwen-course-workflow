---
name: course-weekly-delivery
description: Prepare one requested course week's local handoff, single DRAFT set, or explicitly confirmed FINAL files from repository-local materials. Use only when a user explicitly invokes $course-weekly-delivery; do not use for ordinary course questions, scheduled runs, cloud uploads, or submission.
---

# Course Weekly Delivery

Run only after explicit invocation. Discuss and review in Chinese by default; write submission artifacts in English unless the course requires otherwise. Recover continuity from local project files, not chat history.

## Discover repository state

Walk upward from the current directory until both repo Skills exist. Use only paths relative to that root:

- local profile: `course/COURSE_PROFILE.local.md` when present;
- blank template: `course/templates/ENT303TC_Weekly_Checkpoint_Template.xlsx` unless the local profile names another approved template;
- weekly sources: `course/weeks/<week-id>/`;
- weekly state and outputs: `course/deliverables/<week-id>/`.

Never depend on a member's home directory. Do not copy live values from the tracked example profile.

## Route by state

1. Resolve exactly one requested week and read `AGENTS.md`, the local profile when present, and only that week directory.
2. Look for `course/deliverables/<week-id>/WEEK_HANDOFF.md`.
3. If no valid handoff exists or its state is `ANALYZE`, load the repository's `$course-analysis-companion` and read [references/analyze.md](references/analyze.md). Analyze first, ask at most six grouped high-information questions, then stop without creating files.
4. After the user answers, create or update the handoff. If its state becomes `READY_FOR_DRAFT`, `DRAFT`, or `FINAL_BLOCKED`, do not reload complete courseware unless the handoff records a conflict, changed source, or unresolved locator.
5. For DRAFT, revision, or FINAL work, read [references/artifacts.md](references/artifacts.md) and only the current handoff, current working files, local profile, approved blank template, and source locators needed for unresolved claims.

## State invariants

- `WEEK_HANDOFF.md` is the only weekly coordination record. Keep it compact and source-traceable; never paste full courseware or interview transcripts.
- Keep exactly one stable, unversioned DRAFT per deliverable. Build a temporary replacement, validate it, then atomically replace the current DRAFT while preserving confirmed manual edits.
- FINAL requires a fresh explicit request plus confirmation of all required declarations. FINAL files are immutable and named `_vN_FINAL`; never overwrite an existing FINAL.
- Create a link wrapper only when verified course instructions require a link-based submission.
- Update a course-wide profile only from user-confirmed course-wide facts. Never write local identity or access details into the tracked example.

## Permission and evidence boundaries

Never invent users, interviews, quotations, attendance, decisions, results, dates, teacher intent, metrics, or submission status. DRAFT may contain clearly labeled pending items; FINAL may not contain `待确认`, `Pending`, `TODO`, template markers, or unverified declarations.

Do not connect to cloud drives, operate LMO, upload, submit, send messages, or publish materials. A request to generate local deliverables does not authorize those actions.
