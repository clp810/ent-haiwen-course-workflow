# Analyze and Handoff

Read this reference only when the requested week has no usable `WEEK_HANDOFF.md` or its state is `ANALYZE`.

## Scope discovery

- Resolve one week from the request and folder name. Ask if more than one is plausible.
- Read every relevant file in that week's local folder and only the shared handbook, submission guide, or approved template needed to interpret the requirement.
- Ignore `.DS_Store`, Office lock files, rendered previews, generated deliverables, and scratch files.
- Record a relative file plus page, slide, section, sheet, or range for every explicit requirement. Suggested reading or preparation is not a submission unless the source says it must be delivered.
- The approved Weekly Log template is expected to contain `A Student Weekly`, `B Supervisor`, `C Acceleration Gate`, `D1 Evidence Register`, `D2 AI Use`, and `Lists`.

## First pass and intake

On the first pass, do not create directories, a handoff, research results, or submission files. Produce a compact analysis and ask no more than six grouped questions. Prefer questions that jointly close these gaps:

1. course or team identity changes and attendance;
2. work completed and change since the prior checkpoint;
3. strongest evidence, contrary evidence, provenance, and ethics;
4. team decision, rationale, blocker, and risk;
5. up to three supervisor decisions or questions;
6. link and FINAL declarations only when relevant.

Do not ask for information already confirmed in the local profile or current files. If external research is needed, follow the authorization recorded in the local profile. When authorization is absent, propose the decision, scope, and source classes before browsing. Public-web research cannot replace interviews or direct user evidence unless the course explicitly permits an alternative.

## Persist after the user replies

Create or update `course/deliverables/<week-id>/WEEK_HANDOFF.md` with these compact sections:

1. **Identity and state**: course, week, topic, state, last updated, and current completion point.
2. **Source manifest**: only relevant relative paths and stable locators.
3. **Explicit requirements**: requirement ID, deliverable, content, deadline, format or channel, acceptance rule, locator, and `已确认/合理推断/待确认`.
4. **Required evidence**: quantity, freshness if stated, traceability, and ethical constraints.
5. **Confirmed inputs**: attendance, work completed, change, evidence, contrary evidence, decision and rationale, risk, supervisor questions, and applicable local link reference.
6. **Artifact mapping**: Weekly Log fields, Coursework Pack sections, and whether a link wrapper is required.
7. **Pending and conflicts**: exact missing facts and unresolved source conflicts.
8. **Artifact status**: relative paths and `not_started/DRAFT/FINAL`.

Use `READY_FOR_DRAFT` only when the available information supports an honest DRAFT. Non-critical gaps may remain explicit pending items. Do not mark `READY_FOR_FINAL` while any requirement, evidence threshold, material fact, link, declaration, or source conflict remains unresolved.
