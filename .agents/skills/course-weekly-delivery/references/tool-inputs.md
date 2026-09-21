# Office Helper Inputs

Read only during DRAFT or FINAL artifact generation.

## Weekly Log patch

Pass `patch_weekly_log.py` a JSON object with a `cells` map. Sheet names and cell references must already exist. Raw values are text; use typed objects for dates, numbers, or booleans.

```json
{
  "expected_template_sha256": "optional hash",
  "cells": {
    "A Student Weekly": {
      "B6": "Example Team",
      "B10": {"type": "date", "value": "2030-01-17"}
    },
    "D1 Evidence Register": {
      "B6": "Example Team"
    },
    "D2 AI Use": {
      "C6": "Generic AI assistant"
    }
  }
}
```

The exact whitelist is `A Student Weekly!B6:B24`, `D1 Evidence Register!B6:G105`, `D2 AI Use!A6:G105`, and `Lists!B6:B35`. `D1 Evidence Register!A6:A105` and every cell outside those ranges are immutable. To preserve manual edits, pass the current DRAFT with `--base`; otherwise the script uses the output when it already exists, then the template.

## Coursework DOCX

Pass `build_coursework_docx.py` a JSON object. Use only the blocks required by the course.

```json
{
  "title": "Example Course Week 3 Coursework Pack",
  "subtitle": "Example Team",
  "stage": "DRAFT",
  "metadata": [
    {"label": "Week", "value": "S1 W3"}
  ],
  "opening": "A concise scope and current conclusion.",
  "properties": {"author": "Course Team", "subject": "Weekly Coursework"},
  "sections": [
    {
      "heading": "Problem Statement",
      "level": 1,
      "blocks": [
        {"type": "paragraph", "text": "Pending team review.", "bold": true},
        {"type": "bullets", "items": ["Fictional example only"]},
        {"type": "table", "headers": ["Item", "Evidence"], "rows": [["Example", "EV-001"]], "widths": [2.0, 4.8]}
      ]
    }
  ]
}
```

Supported block types are `paragraph`, `bullets`, `table`, `sources`, and `page_break`. A FINAL input is rejected if it contains a DRAFT, pending, or placeholder marker.

## Validation

Run `validate_delivery.py` with `--stage DRAFT` or `--stage FINAL`. Supply `--template` with `--workbook`; repeat `--docx` for multiple documents and `--require` for text every supplied DOCX must contain. DRAFT filenames must end in `_DRAFT` and FINAL filenames in `_vN_FINAL`. `A Student Weekly!B6:B21` is always required; absence or contrary evidence must be written explicitly rather than left blank. Dynamic weekly requirements remain in `WEEK_HANDOFF.md` and `--require`, not in the script. This structural validator complements, rather than replaces, render and visual inspection.
