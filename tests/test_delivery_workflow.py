from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "course-weekly-delivery"
TEMPLATE = ROOT / "course" / "templates" / "ENT303TC_Weekly_Checkpoint_Template.xlsx"
PATCHER = SKILL / "scripts" / "patch_weekly_log.py"
BUILDER = SKILL / "scripts" / "build_coursework_docx.py"
VALIDATOR = SKILL / "scripts" / "validate_delivery.py"


def run(*args: object, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *(str(arg) for arg in args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if expect_success and result.returncode != 0:
        raise AssertionError(f"Command failed: {result.args}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result


def archive_member(path: Path, member: str) -> bytes:
    with zipfile.ZipFile(path) as archive:
        return archive.read(member)


class DeliveryWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(TEMPLATE.is_file(), "Sanitized Weekly Log template is missing")

    def test_template_metadata_is_sanitized(self) -> None:
        with zipfile.ZipFile(TEMPLATE) as archive:
            core = ElementTree.fromstring(archive.read("docProps/core.xml"))
            values = {
                node.tag.rsplit("}", 1)[-1]: (node.text or "").strip()
                for node in core.iter()
            }
            self.assertEqual(values.get("creator", ""), "")
            self.assertEqual(values.get("lastModifiedBy", ""), "")
            custom = archive.read("docProps/custom.xml").decode("utf-8")
            self.assertNotIn('name="ICV"', custom)

    def test_weekly_log_patch_preserves_protected_sheets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            spec = temp / "weekly-log.json"
            output = temp / "Example_S1_W03_Weekly_Log_DRAFT.xlsx"
            spec.write_text(
                json.dumps(
                    {
                        "cells": {
                            "A Student Weekly": {
                                "B6": "Example Team",
                                "B7": "Example Venture",
                                "B8": "Semester 1",
                                "B9": "S1 W3",
                                "B10": {"type": "date", "value": "2030-01-17"},
                                "B15": "Fictional interview plan v0.1",
                            },
                            "D1 Evidence Register": {
                                "B6": "Example Team",
                                "C6": "A fictional user needs a clearer checklist.",
                                "D6": "Synthetic interview note",
                            },
                            "D2 AI Use": {
                                "A6": {"type": "date", "value": "2030-01-17"},
                                "B6": "Example Team",
                                "C6": "Generic AI assistant",
                                "D6": "Draft structure",
                                "F6": "Human review pending",
                            },
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            run(PATCHER, "--template", TEMPLATE, "--spec", spec, "--output", output, "--dry-run")
            run(PATCHER, "--template", TEMPLATE, "--spec", spec, "--output", output)
            run(VALIDATOR, "--stage", "DRAFT", "--template", TEMPLATE, "--workbook", output)

            workbook = load_workbook(output, data_only=False)
            try:
                self.assertEqual(workbook["A Student Weekly"]["B6"].value, "Example Team")
                self.assertEqual(workbook["D1 Evidence Register"]["A6"].value, '=IF(COUNTA(B6:G6)=0,"","EV-"&TEXT(ROW()-5,"000"))')
                self.assertEqual(workbook["A Student Weekly"]["B22"].value, "☐")
            finally:
                workbook.close()

            self.assertEqual(
                archive_member(TEMPLATE, "xl/worksheets/sheet2.xml"),
                archive_member(output, "xl/worksheets/sheet2.xml"),
            )
            self.assertEqual(
                archive_member(TEMPLATE, "xl/worksheets/sheet3.xml"),
                archive_member(output, "xl/worksheets/sheet3.xml"),
            )

    def test_docx_draft_build_and_final_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            draft_spec = temp / "draft.json"
            draft_docx = temp / "Example_S1_W03_Coursework_Pack_DRAFT.docx"
            draft_spec.write_text(
                json.dumps(
                    {
                        "title": "Example Course Week 3 Coursework Pack",
                        "subtitle": "Example Team",
                        "stage": "DRAFT",
                        "metadata": [{"label": "Week", "value": "S1 W3"}],
                        "opening": "This fictional pack records the current problem statement.",
                        "properties": {"author": "Course Team", "subject": "Weekly Coursework"},
                        "sections": [
                            {
                                "heading": "Problem Statement",
                                "level": 1,
                                "blocks": [
                                    {"type": "paragraph", "text": "A fictional team is testing a checklist."},
                                    {
                                        "type": "table",
                                        "headers": ["Item", "Evidence"],
                                        "rows": [["Checklist", "EV-001"]],
                                        "widths": [2.0, 4.8],
                                    },
                                ],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            run(BUILDER, "--spec", draft_spec, "--output", draft_docx, "--dry-run")
            run(BUILDER, "--spec", draft_spec, "--output", draft_docx)
            run(VALIDATOR, "--stage", "DRAFT", "--docx", draft_docx, "--require", "Problem Statement")

            final_spec = temp / "bad-final.json"
            final_spec.write_text(
                json.dumps(
                    {
                        "title": "Example Final",
                        "stage": "FINAL",
                        "sections": [
                            {
                                "heading": "Conclusion",
                                "blocks": [{"type": "paragraph", "text": "Pending confirmation"}],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = run(BUILDER, "--spec", final_spec, "--output", temp / "bad.docx", "--dry-run", expect_success=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FINAL spec contains", result.stderr)


if __name__ == "__main__":
    unittest.main()
