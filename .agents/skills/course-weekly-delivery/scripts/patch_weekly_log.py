#!/usr/bin/env python3
"""Patch approved Weekly Log cells without rebuilding or restyling the workbook."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import posixpath
import tempfile
import zipfile
from datetime import date
from pathlib import Path

from lxml import etree


SHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
EDITABLE_SHEETS = {"A Student Weekly", "D1 Evidence Register", "D2 AI Use", "Lists"}
PROTECTED_SHEETS = {"B Supervisor", "C Acceleration Gate"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict) or not isinstance(value.get("cells"), dict):
        raise ValueError("Spec must contain a top-level object named 'cells'.")
    return value


def workbook_sheet_paths(book: zipfile.ZipFile) -> dict[str, str]:
    workbook = etree.fromstring(book.read("xl/workbook.xml"))
    relationships = etree.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {
        rel.get("Id"): rel.get("Target")
        for rel in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
    }
    result: dict[str, str] = {}
    for sheet in workbook.findall(f".//{{{SHEET_NS}}}sheet"):
        name = sheet.get("name")
        rel_id = sheet.get(f"{{{REL_NS}}}id")
        target = rel_targets.get(rel_id)
        if not name or not target:
            continue
        if target.startswith("/"):
            member = target.lstrip("/")
        else:
            member = posixpath.normpath(posixpath.join("xl", target))
        result[name] = member
    return result


def get_cell(root: etree._Element, ref: str) -> etree._Element:
    cells = root.xpath(f'.//x:c[@r="{ref}"]', namespaces={"x": SHEET_NS})
    if len(cells) != 1:
        raise ValueError(f"Expected one existing cell {ref}, found {len(cells)}.")
    cell = cells[0]
    if cell.find(f"{{{SHEET_NS}}}f") is not None:
        raise ValueError(f"Refusing to overwrite formula cell {ref}.")
    return cell


def clear_payload(cell: etree._Element) -> None:
    for child in list(cell):
        if etree.QName(child).localname in {"v", "is"}:
            cell.remove(child)


def set_cell(cell: etree._Element, raw_value: object) -> None:
    kind = "text"
    value = raw_value
    if isinstance(raw_value, dict):
        kind = str(raw_value.get("type", "text"))
        value = raw_value.get("value", "")

    clear_payload(cell)
    if kind == "date":
        parsed = date.fromisoformat(str(value))
        cell.attrib.pop("t", None)
        node = etree.SubElement(cell, f"{{{SHEET_NS}}}v")
        node.text = str((parsed - date(1899, 12, 30)).days)
    elif kind == "number":
        number = float(value) if isinstance(value, str) and "." in value else int(value)
        cell.attrib.pop("t", None)
        node = etree.SubElement(cell, f"{{{SHEET_NS}}}v")
        node.text = str(number)
    elif kind == "boolean":
        cell.set("t", "b")
        node = etree.SubElement(cell, f"{{{SHEET_NS}}}v")
        node.text = "1" if bool(value) else "0"
    elif kind == "text":
        text_value = "" if value is None else str(value)
        cell.set("t", "inlineStr")
        inline = etree.SubElement(cell, f"{{{SHEET_NS}}}is")
        node = etree.SubElement(inline, f"{{{SHEET_NS}}}t")
        if text_value[:1].isspace() or text_value[-1:].isspace() or "\n" in text_value:
            node.set(XML_SPACE, "preserve")
        node.text = text_value
    else:
        raise ValueError(f"Unsupported cell type: {kind}")


def patch_sheet(xml_bytes: bytes, changes: dict[str, object]) -> bytes:
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(xml_bytes, parser)
    for ref, value in changes.items():
        if not isinstance(ref, str):
            raise ValueError("Cell references must be strings.")
        set_cell(get_cell(root, ref), value)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def validate_and_prepare(template: Path, base: Path, spec: dict) -> dict[str, bytes]:
    expected_hash = spec.get("expected_template_sha256")
    if expected_hash and sha256(template) != expected_hash:
        raise ValueError("Template SHA-256 does not match the handoff or spec.")

    cells = spec["cells"]
    unknown = set(cells) - EDITABLE_SHEETS
    if unknown:
        raise ValueError(f"Spec targets non-editable sheets: {sorted(unknown)}")

    replacements: dict[str, bytes] = {}
    with zipfile.ZipFile(template, "r") as template_zip, zipfile.ZipFile(base, "r") as base_zip:
        template_paths = workbook_sheet_paths(template_zip)
        base_paths = workbook_sheet_paths(base_zip)
        required = EDITABLE_SHEETS | PROTECTED_SHEETS
        missing = required - set(base_paths)
        template_missing = required - set(template_paths)
        if missing:
            raise ValueError(f"Workbook is missing required sheets: {sorted(missing)}")
        if template_missing:
            raise ValueError(f"Template is missing required sheets: {sorted(template_missing)}")
        for sheet in PROTECTED_SHEETS:
            if base_zip.read(base_paths[sheet]) != template_zip.read(template_paths[sheet]):
                raise ValueError(f"Protected sheet differs from the source template: {sheet}")
        for sheet, changes in cells.items():
            if not isinstance(changes, dict):
                raise ValueError(f"Cell map for {sheet} must be an object.")
            member = base_paths[sheet]
            replacements[member] = patch_sheet(base_zip.read(member), changes)
    return replacements


def write_workbook(base: Path, output: Path, replacements: dict[str, bytes]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=output.stem + ".",
        suffix=".xlsx",
        dir=output.parent,
        delete=False,
    ) as temp:
        temp_path = Path(temp.name)
    try:
        with zipfile.ZipFile(base, "r") as source_zip, zipfile.ZipFile(temp_path, "w") as output_zip:
            for info in source_zip.infolist():
                clone = copy.copy(info)
                clone.CRC = clone.compress_size = clone.file_size = 0
                output_zip.writestr(clone, replacements.get(info.filename, source_zip.read(info.filename)))
        os.replace(temp_path, output)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--base",
        type=Path,
        help="Existing DRAFT to preserve; defaults to output when it exists, otherwise template.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs without writing a workbook.")
    args = parser.parse_args()

    for path in (args.template, args.spec):
        if not path.is_file():
            parser.error(f"File not found: {path}")
    base = args.base or (args.output if args.output.exists() else args.template)
    if not base.is_file():
        parser.error(f"Base workbook not found: {base}")

    replacements = validate_and_prepare(args.template, base, read_json(args.spec))
    if args.dry_run:
        print(f"DRY RUN PASS: {len(replacements)} worksheet XML part(s) validated")
        return
    write_workbook(base, args.output, replacements)
    print(f"WROTE {args.output}")
    print(f"SHA256 {sha256(args.output)}")


if __name__ == "__main__":
    main()
