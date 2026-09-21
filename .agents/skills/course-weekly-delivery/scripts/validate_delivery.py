#!/usr/bin/env python3
"""Validate weekly workbook protection and DRAFT or FINAL document gates."""

from __future__ import annotations

import argparse
import hashlib
import posixpath
import re
import zipfile
from pathlib import Path

from lxml import etree
from openpyxl import load_workbook


SHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
PROTECTED_SHEETS = ("B Supervisor", "C Acceleration Gate")
REQUIRED_SHEETS = {
    "A Student Weekly",
    "B Supervisor",
    "C Acceleration Gate",
    "D1 Evidence Register",
    "D2 AI Use",
    "Lists",
}
UNCHECKED = {None, "", "☐", False, 0, "0", "FALSE", "False"}
CHECKED = {"☑", "✓", "✔", True, 1, "1", "TRUE", "True"}
PLACEHOLDERS = re.compile(
    r"\b(?:todo|tbc|tbd)\b|待确认|待补充|\{\{|\}\}|<placeholder>",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sheet_paths(book: zipfile.ZipFile) -> dict[str, str]:
    workbook = etree.fromstring(book.read("xl/workbook.xml"))
    relationships = etree.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {
        rel.get("Id"): rel.get("Target")
        for rel in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
    }
    result = {}
    for sheet in workbook.findall(f".//{{{SHEET_NS}}}sheet"):
        rel_id = sheet.get(f"{{{REL_NS}}}id")
        target = rel_targets.get(rel_id)
        name = sheet.get("name")
        if not name or not target:
            continue
        result[name] = (
            target.lstrip("/")
            if target.startswith("/")
            else posixpath.normpath(posixpath.join("xl", target))
        )
    return result


def validate_workbook(template: Path, workbook: Path, stage: str) -> None:
    with zipfile.ZipFile(template) as template_zip, zipfile.ZipFile(workbook) as workbook_zip:
        template_paths = sheet_paths(template_zip)
        workbook_paths = sheet_paths(workbook_zip)
        missing = REQUIRED_SHEETS - set(workbook_paths)
        if missing:
            raise ValueError(f"Workbook is missing required Weekly Log sheets: {sorted(missing)}")
        for sheet in PROTECTED_SHEETS:
            if workbook_zip.read(workbook_paths[sheet]) != template_zip.read(template_paths[sheet]):
                raise ValueError(f"Protected worksheet changed: {sheet}")

    loaded = load_workbook(workbook, data_only=False, read_only=False)
    try:
        declarations = [loaded["A Student Weekly"][ref].value for ref in ("B22", "B23", "B24")]
    finally:
        loaded.close()
    if stage == "DRAFT" and any(value not in UNCHECKED for value in declarations):
        raise ValueError(f"A DRAFT declaration appears checked: {declarations}")
    if stage == "FINAL" and any(value not in CHECKED for value in declarations):
        raise ValueError(f"A FINAL declaration is not confirmed: {declarations}")
    print(f"PASS workbook {workbook.name} sha256={sha256(workbook)}")


def document_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        root = etree.fromstring(archive.read("word/document.xml"))
    return "".join(root.itertext())


def validate_docx(path: Path, stage: str, required: list[str]) -> None:
    text = document_text(path)
    for value in required:
        if value not in text:
            raise ValueError(f"{path.name} is missing required text: {value!r}")
    if PLACEHOLDERS.search(text):
        raise ValueError(f"{path.name} contains an unfinished placeholder.")
    if stage == "DRAFT" and "DRAFT - Not Ready for Submission" not in text:
        raise ValueError(f"{path.name} lacks the required DRAFT banner.")
    if stage == "FINAL" and re.search(r"\b(?:DRAFT|Pending)\b", text, re.IGNORECASE):
        raise ValueError(f"{path.name} contains a DRAFT or Pending marker.")
    print(f"PASS docx {path.name} sha256={sha256(path)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=("DRAFT", "FINAL"))
    parser.add_argument("--template", type=Path)
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--docx", action="append", default=[], type=Path)
    parser.add_argument("--require", action="append", default=[])
    args = parser.parse_args()

    if args.workbook:
        if not args.template:
            parser.error("--template is required with --workbook")
        validate_workbook(args.template, args.workbook, args.stage)
    for path in args.docx:
        validate_docx(path, args.stage, args.require)
    if not args.workbook and not args.docx:
        parser.error("Provide --workbook or at least one --docx")


if __name__ == "__main__":
    main()
