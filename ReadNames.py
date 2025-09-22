"""
Utilities for reading and sorting names from Navneliste.txt.

The source file can contain comma-separated names, so this module normalises the data
before exposing it to the rest of the program.
"""

from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud


def read_names(file_name: str = "Navneliste.txt") -> list[str]:
    """Read names from the companion text file and normalise formatting.

    The delivered dataset sometimes keeps many names on a single line separated by commas.
    Splitting the line lets us support both CSV-style and newline-separated inputs and
    makes downstream consumers work with a simple list of clean strings.
    """
    file_path = Path(__file__).with_name(file_name)
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find '{file_path}'.")

    with open(file_path, "r", encoding="utf-8") as file:
        names: list[str] = []
        for line in file:
            # Split on commas so badly formatted lines still yield individual names.
            parts = [part.strip() for part in line.split(",")]
            names.extend(part for part in parts if part)

    return names


def sort_names(
    names: list[str],
    *,
    ignore_case: bool = True,
    reverse: bool = False,
) -> list[str]:
    """Return the provided names sorted alphabetically.

    We filter out empty entries to avoid artifacts from extra delimiters and casefold
    by default so uppercase letters do not disturb the expected alphabetical order.
    The optional reverse flag flips the result when callers need descending output.
    """
    cleaned = [name for name in names if name]
    key_fn = str.casefold if ignore_case else None
    return sorted(cleaned, key=key_fn, reverse=reverse)


def count_letters(names: list[str]) -> int:
    """Count alphabetic characters across the provided names using nested loops.

    Two explicit loops keep the implementation easy to follow for beginners: the outer
    loop iterates over each name, while the inner loop walks through the characters in
    that name and increments the total whenever it encounters a letter.
    """
    total_letters = 0
    for name in names:
        for character in name:
            if character.isalpha():
                total_letters += 1
    return total_letters


if __name__ == "__main__":
    # When run directly, display each sorted name and the total letter count for feedback.
    try:
        sorted_names = sort_names(read_names())
        for name in sorted_names:
            print(name)
        print(f"Total letters: {count_letters(sorted_names)}")
    except FileNotFoundError as exc:
        print(exc)
