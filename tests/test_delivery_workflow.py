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


_OMIT = object()


def weekly_log_cells(*, final: bool, overrides: dict[str, object] | None = None) -> dict[str, dict[str, object]]:
    student: dict[str, object] = {
        "B6": "Example Team",
        "B7": "Example Venture",
        "B8": "Semester 1",
        "B9": "S1 W3",
        "B10": {"type": "date", "value": "2030-01-17"},
        "B11": "Standard",
        "B12": "Example Member",
        "B13": "None identified",
        "B14": "None",
        "B15": "Fictional interview plan v0.1",
        "B16": "Added a fictional checklist.",
        "B17": "EV-001: synthetic interview note.",
        "B18": "None identified",
        "B19": "Test the checklist because the synthetic note supports it.",
        "B20": "None identified",
        "B21": "1. Is the checklist scope appropriate?",
    }
    if final:
        student.update({"B22": "☑", "B23": "☑", "B24": "☑"})
    if overrides:
        for reference, value in overrides.items():
            if value is _OMIT:
                student.pop(reference, None)
            else:
                student[reference] = value
    return {"A Student Weekly": student}


class DeliveryWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(TEMPLATE.is_file(), "Sanitized Weekly Log template is missing")

    def write_spec(self, directory: Path, cells: dict[str, dict[str, object]], name: str = "weekly-log.json") -> Path:
        path = directory / name
        path.write_text(json.dumps({"cells": cells}, ensure_ascii=False), encoding="utf-8")
        return path

    def patch_workbook(
        self,
        directory: Path,
        name: str,
        *,
        final: bool,
        overrides: dict[str, object] | None = None,
    ) -> Path:
        output = directory / name
        spec = self.write_spec(directory, weekly_log_cells(final=final, overrides=overrides), f"{output.stem}.json")
        run(PATCHER, "--template", TEMPLATE, "--spec", spec, "--output", output)
        return output

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

    def test_weekly_log_cell_whitelist_rejects_forbidden_cells(self) -> None:
        cases = (
            ("A Student Weekly", "A2"),
            ("A Student Weekly", "C5"),
            ("D1 Evidence Register", "A6"),
            ("Lists", "A2"),
        )
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            for index, (sheet, reference) in enumerate(cases):
                with self.subTest(sheet=sheet, reference=reference):
                    spec = self.write_spec(temp, {sheet: {reference: "forbidden"}}, f"bad-{index}.json")
                    result = run(
                        PATCHER,
                        "--template",
                        TEMPLATE,
                        "--spec",
                        spec,
                        "--output",
                        temp / f"bad-{index}_DRAFT.xlsx",
                        "--dry-run",
                        expect_success=False,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("outside the editable range", result.stderr)

    def test_weekly_log_patch_preserves_protected_sheets_and_formulas(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            cells = weekly_log_cells(final=False, overrides={"B18": "Pending team confirmation"})
            cells.update(
                {
                    "D1 Evidence Register": {
                        "B6": "Example Team",
                        "C6": "A fictional user needs a clearer checklist.",
                        "G105": "Synthetic edge-row note",
                    },
                    "D2 AI Use": {
                        "A6": {"type": "date", "value": "2030-01-17"},
                        "B6": "Example Team",
                        "C6": "Generic AI assistant",
                        "D6": "Draft structure",
                        "F6": "Human review pending",
                        "G105": "Synthetic edge-row note",
                    },
                    "Lists": {"B35": "Example Roster Value"},
                }
            )
            spec = self.write_spec(temp, cells)
            output = temp / "Example_S1_W03_Weekly_Log_DRAFT.xlsx"
            run(PATCHER, "--template", TEMPLATE, "--spec", spec, "--output", output, "--dry-run")
            run(PATCHER, "--template", TEMPLATE, "--spec", spec, "--output", output)
            run(VALIDATOR, "--stage", "DRAFT", "--template", TEMPLATE, "--workbook", output)

            workbook = load_workbook(output, data_only=False)
            try:
                self.assertEqual(workbook["A Student Weekly"]["B6"].value, "Example Team")
                self.assertEqual(workbook["D1 Evidence Register"]["A6"].value, '=IF(COUNTA(B6:G6)=0,"","EV-"&TEXT(ROW()-5,"000"))')
                self.assertEqual(workbook["D1 Evidence Register"]["G105"].value, "Synthetic edge-row note")
                self.assertEqual(workbook["D2 AI Use"]["G105"].value, "Synthetic edge-row note")
                self.assertEqual(workbook["Lists"]["B35"].value, "Example Roster Value")
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

    def test_workbook_final_validation_gates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)

            valid = self.patch_workbook(
                temp,
                "Example_S1_W03_Weekly_Log_v1_FINAL.xlsx",
                final=True,
            )
            run(VALIDATOR, "--stage", "FINAL", "--template", TEMPLATE, "--workbook", valid)

            pending = self.patch_workbook(
                temp,
                "Example_S1_W03_Weekly_Log_v2_FINAL.xlsx",
                final=True,
                overrides={"B18": "pEnDiNg team confirmation"},
            )
            result = run(
                VALIDATOR,
                "--stage",
                "FINAL",
                "--template",
                TEMPLATE,
                "--workbook",
                pending,
                expect_success=False,
            )
            self.assertIn("unfinished markers", result.stderr)

            blank = self.patch_workbook(
                temp,
                "Example_S1_W03_Weekly_Log_v3_FINAL.xlsx",
                final=True,
                overrides={"B18": _OMIT},
            )
            result = run(
                VALIDATOR,
                "--stage",
                "FINAL",
                "--template",
                TEMPLATE,
                "--workbook",
                blank,
                expect_success=False,
            )
            self.assertIn("Required Weekly Log fields are blank", result.stderr)

            wrong_name = self.patch_workbook(
                temp,
                "Example_S1_W03_Weekly_Log_FINAL.xlsx",
                final=True,
            )
            result = run(
                VALIDATOR,
                "--stage",
                "FINAL",
                "--template",
                TEMPLATE,
                "--workbook",
                wrong_name,
                expect_success=False,
            )
            self.assertIn("filename rule", result.stderr)

    def test_workbook_declarations_match_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            checked_draft = self.patch_workbook(
                temp,
                "Example_S1_W03_Weekly_Log_DRAFT.xlsx",
                final=False,
                overrides={"B22": "☑"},
            )
            result = run(
                VALIDATOR,
                "--stage",
                "DRAFT",
                "--template",
                TEMPLATE,
                "--workbook",
                checked_draft,
                expect_success=False,
            )
            self.assertIn("DRAFT declaration appears checked", result.stderr)

            unchecked_final = self.patch_workbook(
                temp,
                "Example_S1_W03_Weekly_Log_v4_FINAL.xlsx",
                final=True,
                overrides={"B24": "☐"},
            )
            result = run(
                VALIDATOR,
                "--stage",
                "FINAL",
                "--template",
                TEMPLATE,
                "--workbook",
                unchecked_final,
                expect_success=False,
            )
            self.assertIn("FINAL declaration is not confirmed", result.stderr)

    def test_docx_stage_and_filename_validation(self) -> None:
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

            wrong_name = temp / "Example_S1_W03_Coursework_Pack.docx"
            wrong_name.write_bytes(draft_docx.read_bytes())
            result = run(VALIDATOR, "--stage", "DRAFT", "--docx", wrong_name, expect_success=False)
            self.assertIn("filename rule", result.stderr)

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
            result = run(
                BUILDER,
                "--spec",
                final_spec,
                "--output",
                temp / "Example_S1_W03_Coursework_Pack_v1_FINAL.docx",
                "--dry-run",
                expect_success=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FINAL spec contains", result.stderr)


if __name__ == "__main__":
    unittest.main()
