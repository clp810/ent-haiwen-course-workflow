#!/usr/bin/env python3
"""Fail when repository content contains common privacy, credential, or path leaks."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
    ".sh",
    ".toml",
    ".ini",
    ".cfg",
    ".gitignore",
}
OFFICE_SUFFIXES = {".xlsx", ".docx", ".pptx"}
IGNORED_PARTS = {".git", ".venv", "__pycache__", "work", "tmp"}
ALLOWED_LOCAL_READMES = {
    Path("course/weeks/README.md"),
    Path("course/deliverables/README.md"),
}
FORBIDDEN_PATTERNS = {
    "macOS absolute user path": re.compile("/" + "Users/" + r"[^\s'\"<>]+"),
    "Linux absolute home path": re.compile("/" + "home/" + r"[^\s'\"<>]+"),
    "Windows absolute user path": re.compile(r"[A-Za-z]:\\\\" + "Users" + r"\\\\[^\s'\"<>]+"),
    "Tencent Docs share link": re.compile(r"https?://(?:www\.)?docs\.qq\.com/", re.IGNORECASE),
    "Google Drive share link": re.compile(r"https?://drive\.google\.com/", re.IGNORECASE),
    "SharePoint share link": re.compile(r"https?://[^\s'\"]*sharepoint\.com/", re.IGNORECASE),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
}


def repository_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-co", "--exclude-standard"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        candidates = [root / line for line in result.stdout.splitlines() if line]
    except (OSError, subprocess.CalledProcessError):
        candidates = [path for path in root.rglob("*") if path.is_file()]
    return sorted(
        path
        for path in candidates
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
    )


def scan_text(label: str, text: str, failures: list[str]) -> None:
    for description, pattern in FORBIDDEN_PATTERNS.items():
        match = pattern.search(text)
        if match:
            sample = match.group(0)[:80]
            failures.append(f"{label}: {description}: {sample}")


def scan_office(path: Path, relative: Path, failures: list[str]) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if "docProps/core.xml" in names:
                root = ElementTree.fromstring(archive.read("docProps/core.xml"))
                for node in root.iter():
                    if node.tag.endswith("creator") or node.tag.endswith("lastModifiedBy"):
                        if (node.text or "").strip():
                            failures.append(f"{relative}: non-empty Office author metadata")
            if "docProps/custom.xml" in names:
                custom = ElementTree.fromstring(archive.read("docProps/custom.xml"))
                for node in custom.iter():
                    if node.tag.endswith("property") and node.attrib.get("name") == "ICV":
                        failures.append(f"{relative}: device-specific ICV metadata")
            for name in names:
                if name.endswith((".xml", ".rels")):
                    scan_text(f"{relative}!{name}", archive.read(name).decode("utf-8", "ignore"), failures)
    except (zipfile.BadZipFile, ElementTree.ParseError) as error:
        failures.append(f"{relative}: unreadable Office archive: {error}")


def audit(root: Path) -> list[str]:
    failures: list[str] = []
    for path in repository_files(root):
        relative = path.relative_to(root)
        if relative.parts[:2] in {("course", "weeks"), ("course", "deliverables")}:
            if relative not in ALLOWED_LOCAL_READMES:
                failures.append(f"{relative}: live weekly material or deliverable must not be tracked")
        suffix = path.suffix.lower()
        if suffix in TEXT_SUFFIXES or path.name == ".gitignore":
            scan_text(str(relative), path.read_text(encoding="utf-8", errors="ignore"), failures)
        elif suffix in OFFICE_SUFFIXES:
            scan_office(path, relative, failures)
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    failures = audit(root)
    if failures:
        print("REPOSITORY AUDIT FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS repository privacy audit ({len(repository_files(root))} files checked)")


if __name__ == "__main__":
    main()
