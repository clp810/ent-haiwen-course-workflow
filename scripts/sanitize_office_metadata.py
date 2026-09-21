#!/usr/bin/env python3
"""Copy an OOXML file while removing common personal metadata fields."""

from __future__ import annotations

import argparse
import copy
import os
import tempfile
import zipfile
from pathlib import Path

from lxml import etree


CORE_NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
}
CUSTOM_NS = {
    "p": "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties",
}
CORE_FIELDS = ("dc:creator", "cp:lastModifiedBy")
CUSTOM_NAMES_TO_REMOVE = {"ICV"}


def scrub_core(data: bytes) -> bytes:
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(data, parser)
    for expression in CORE_FIELDS:
        for node in root.xpath(expression, namespaces=CORE_NS):
            node.text = ""
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def scrub_custom(data: bytes) -> bytes:
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(data, parser)
    for node in root.xpath("p:property", namespaces=CUSTOM_NS):
        if node.get("name") in CUSTOM_NAMES_TO_REMOVE:
            root.remove(node)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def sanitize(source: Path, output: Path) -> None:
    replacements = {}
    with zipfile.ZipFile(source, "r") as archive:
        if "docProps/core.xml" in archive.namelist():
            replacements["docProps/core.xml"] = scrub_core(archive.read("docProps/core.xml"))
        if "docProps/custom.xml" in archive.namelist():
            replacements["docProps/custom.xml"] = scrub_custom(archive.read("docProps/custom.xml"))

        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix=output.stem + ".",
            suffix=output.suffix,
            dir=output.parent,
            delete=False,
        ) as temp:
            temp_path = Path(temp.name)
        try:
            with zipfile.ZipFile(temp_path, "w") as target:
                for info in archive.infolist():
                    clone = copy.copy(info)
                    clone.CRC = clone.compress_size = clone.file_size = 0
                    target.writestr(clone, replacements.get(info.filename, archive.read(info.filename)))
            os.replace(temp_path, output)
        finally:
            if temp_path.exists():
                temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not args.source.is_file():
        parser.error(f"Source not found: {args.source}")
    sanitize(args.source, args.output)
    print(f"WROTE {args.output}")


if __name__ == "__main__":
    main()
