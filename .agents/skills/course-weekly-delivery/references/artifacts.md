# DRAFT and FINAL Artifacts

Read this reference only after a current local `WEEK_HANDOFF.md` exists.

## File layout

Use the current handoff, local profile, approved blank template, current DRAFTs, and only the source locators marked unresolved.

```text
course/deliverables/<week-id>/
├── WEEK_HANDOFF.md
├── draft/
│   ├── <course>_<week-id>_Weekly_Log_DRAFT.xlsx
│   ├── <course>_<week-id>_Coursework_Pack_DRAFT.docx
│   └── <course>_<week-id>_Link_Submission_DRAFT.docx
└── final/
    └── corresponding <course>_<week-id>_*_vN_FINAL files
```

Create the link wrapper only when verified instructions require it. Maintain one current DRAFT per deliverable. Build in a temporary directory, validate, and atomically replace the DRAFT. Never overwrite a FINAL.

## Deterministic helpers

Use the bundled workspace Python and the scripts beside this reference:

- `scripts/patch_weekly_log.py`: patch a small JSON cell map while protecting `B Supervisor` and `C Acceleration Gate`;
- `scripts/build_coursework_docx.py`: build a consistently styled DOCX from a small JSON specification;
- `scripts/validate_delivery.py`: verify protected tabs, declarations, stage markers, placeholders, and required DOCX strings.

Both builders accept `--dry-run`. Read `--help` before use; inspect source only when debugging or changing the helper. Read [tool-inputs.md](tool-inputs.md) before preparing JSON. Keep JSON in a temporary local directory, not in Git.

Before Office authoring, follow the available spreadsheet or document Skill, use its bundled runtimes and renderers, and run the required artifact-operation marker.

## Weekly Log contract

- Fill only `A Student Weekly`, `D1 Evidence Register`, and `D2 AI Use`.
- Change `Lists` only when a confirmed local team value is missing.
- Do not change `B Supervisor` or `C Acceleration Gate`.
- Preserve formulas, validations, styles, merges, dimensions, print settings, sheet order, and hidden state.
- Keep all declarations unchecked in DRAFT. Check them in FINAL only after the user explicitly confirms each statement.
- Record one row per material AI use. Human verification remains pending until the user describes the review and changes.

## DOCX contract

- Use the course-required language and exact headings where stated.
- Put `DRAFT - Not Ready for Submission` on the first page of every DRAFT.
- Combine related weekly outputs unless the course explicitly requires separate files.
- Distinguish sourced facts, team interpretation, decisions, limitations, and pending confirmations.
- Do not reuse fictional identities, figures, quotations, or results from examples.
- Use normal human citations or Evidence IDs, never internal tool citation tokens.

## QA and FINAL gate

For DRAFT, run structural validation; render and inspect every DOCX page; inspect each populated Excel sheet or range; and report pending fields, evidence gaps, declarations, and submission risks.

For FINAL, require an explicit request and confirmation that the team reviewed the pack, evidence is traceable and ethically obtained, and AI use is recorded and human-verified. Block FINAL while any required item, declaration, placeholder, or pending marker remains. Run full structural and visual checks, write the next `_vN_FINAL`, update the handoff, and remind the user that upload and LMO submission remain manual.
