"""Shared Weekly Log edit and validation boundaries."""

from __future__ import annotations

import re
from collections.abc import Iterator


EDITABLE_RANGES = {
    "A Student Weekly": ((2, 6, 2, 24),),
    "D1 Evidence Register": ((2, 6, 7, 105),),
    "D2 AI Use": ((1, 6, 7, 105),),
    "Lists": ((2, 6, 2, 35),),
}
EDITABLE_RANGE_LABELS = {
    "A Student Weekly": "B6:B24",
    "D1 Evidence Register": "B6:G105",
    "D2 AI Use": "A6:G105",
    "Lists": "B6:B35",
}
EDITABLE_SHEETS = set(EDITABLE_RANGES)
PROTECTED_SHEETS = {"B Supervisor", "C Acceleration Gate"}
REQUIRED_SHEETS = EDITABLE_SHEETS | PROTECTED_SHEETS
CORE_REQUIRED_CELLS = tuple(("A Student Weekly", f"B{row}") for row in range(6, 22))

CELL_REF = re.compile(r"^([A-Z]{1,3})([1-9][0-9]*)$")


def column_number(label: str) -> int:
    value = 0
    for character in label:
        value = value * 26 + ord(character) - ord("A") + 1
    return value


def parse_cell_reference(reference: str) -> tuple[int, int]:
    match = CELL_REF.fullmatch(reference)
    if not match:
        raise ValueError(f"Invalid cell reference: {reference!r}")
    return column_number(match.group(1)), int(match.group(2))


def assert_editable_cell(sheet: str, reference: str) -> None:
    column, row = parse_cell_reference(reference)
    ranges = EDITABLE_RANGES.get(sheet, ())
    if not any(
        first_column <= column <= last_column and first_row <= row <= last_row
        for first_column, first_row, last_column, last_row in ranges
    ):
        expected = EDITABLE_RANGE_LABELS.get(sheet, "no editable cells")
        raise ValueError(
            f"{sheet}!{reference} is outside the editable range {expected}."
        )


def iter_editable_coordinates(sheet: str) -> Iterator[tuple[int, int]]:
    for first_column, first_row, last_column, last_row in EDITABLE_RANGES[sheet]:
        for row in range(first_row, last_row + 1):
            for column in range(first_column, last_column + 1):
                yield row, column
