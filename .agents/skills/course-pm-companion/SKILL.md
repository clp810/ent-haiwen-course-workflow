---
name: course-pm-companion
description: Analyze one requested course week's local slides, PDFs, documents, images, brief, or rubric; extract source-traceable requirements and produce a compact delivery handoff. Use for course requirement analysis, not for generic summarization or Office file generation.
---

# Course PM Companion

Analyze course materials without creating submission files. Discuss in Chinese by default while retaining useful English course terms.

## Resolve scope

1. Discover the nearest repository root containing both `.agents/skills/course-pm-companion` and `.agents/skills/course-weekly-delivery`. Do not use a user home directory or a globally installed copy as project state.
2. Resolve exactly one requested week under `course/weeks/<week-id>/`. If multiple weeks are plausible, ask which one.
3. Read only that week's files and the minimum shared course instruction or blank template needed to interpret them. Do not scan other weeks unless a cited requirement depends on them.

## Select the smallest mode

- **Submission requirements**: return only explicit deliverables, locators, unknowns, and decision-relevant questions.
- **Course application**: when the user asks how the lesson applies to Haiwen, also read `docs/HAIWEN_PROJECT_CONTEXT.md`. Do not introduce personal career, portfolio, or contribution framing.
- **Delivery handoff**: when invoked by `$course-weekly-delivery`, return the compact fields in [references/analysis-contract.md](references/analysis-contract.md). Do not write files or generate Office artifacts.

When a current local `WEEK_HANDOFF.md` already contains verified requirements for the requested week, do not re-analyze unchanged courseware unless the user asks, a source changed, or a locator is unresolved.

## Evidence rules

Use `已确认`, `合理推断`, `建议`, and `待确认`. Only explicit deliver, upload, present, demonstrate, assessment, or equivalent wording establishes a submission requirement. Keep conflicting sources side by side unless one explicitly supersedes another.

Cite every requirement by file and stable page, slide, section, sheet, or range. Inspect relevant text, visuals, tables, diagrams, rubric structure, and presenter notes when available. Summarize instead of copying long passages. Treat worked examples as structural guidance, not reusable facts or evidence.

Never invent deadlines, channels, grading rules, teacher intent, users, interviews, attendance, team decisions, findings, results, metrics, or submission status. Use `not found` or `待确认` instead of filling gaps.

## Permission boundary

Standalone use returns analysis in the conversation. This Skill does not authorize file generation, tracker changes, public-web research, authenticated access, cloud writes, uploads, LMO submission, deployment, external messages, or FINAL creation.
