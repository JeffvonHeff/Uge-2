"""
Utilities for reading and analysing names from Navneliste.txt.

The source file can contain comma-separated names, so this module normalises the data
before exposing it to the rest of the program. On top of the basic helpers it now
offers a richer analytics pipeline that produces statistical summaries and
visualisations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud


def read_names(file_name: str = "Navneliste.txt") -> list[str]:
    """Read names from the companion text file and normalise formatting."""
    file_path = Path(__file__).with_name(file_name)
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find '{file_path}'.")

    with open(file_path, "r", encoding="utf-8") as file:
        names: list[str] = []
        for line in file:
            parts = [part.strip() for part in line.split(",")]
            names.extend(part for part in parts if part)

    return names


def sort_names(
    names: Iterable[str],
    *,
    ignore_case: bool = True,
    reverse: bool = False,
) -> list[str]:
    """Return the provided names sorted alphabetically."""
    cleaned = [name for name in names if name]
    key_fn = str.casefold if ignore_case else None
    return sorted(cleaned, key=key_fn, reverse=reverse)


def count_letters(names: Iterable[str]) -> int:
    """Count alphabetic characters across the provided names using nested loops."""
    total_letters = 0
    for name in names:
        for character in name:
            if character.isalpha():
                total_letters += 1
    return total_letters


def build_name_frame(names: Sequence[str]) -> pd.DataFrame:
    """Represent the name collection as a pandas DataFrame with derived features."""
    if not names:
        return pd.DataFrame(
            {
                "name": pd.Series(dtype="string"),
                "length": pd.Series(dtype="int16"),
                "initial": pd.Series(dtype="string"),
                "ending": pd.Series(dtype="string"),
                "vowel_initial": pd.Series(dtype="bool"),
                "vowel_ending": pd.Series(dtype="bool"),
            }
        )

    initials = [name[0].upper() for name in names]
    endings = [name[-1].upper() for name in names]
    vowels = set("AEIOUY")

    frame = pd.DataFrame(
        {
            "name": pd.Series(names, dtype="string"),
            "length": np.fromiter((len(name) for name in names), dtype=np.int16),
            "initial": pd.Series(initials, dtype="string"),
            "ending": pd.Series(endings, dtype="string"),
        }
    )
    frame["vowel_initial"] = frame["initial"].isin(vowels)
    frame["vowel_ending"] = frame["ending"].isin(vowels)
    return frame


def summarise_name_frame(frame: pd.DataFrame, *, top_n: int = 10) -> dict:
    """Return descriptive statistics about the provided frame."""
    if frame.empty:
        return {
            "total_names": 0,
            "unique_names": 0,
            "length": {},
            "initials": {},
            "endings": {},
            "letters": {},
        }

    lengths = frame["length"].astype(np.int32)
    quartiles = np.percentile(lengths, [25, 50, 75])
    length_summary = {
        "min": int(lengths.min()),
        "max": int(lengths.max()),
        "mean": float(np.round(lengths.mean(), 2)),
        "median": float(np.round(quartiles[1], 2)),
        "std": float(np.round(lengths.std(ddof=0), 2)),
        "percentile_25": float(np.round(quartiles[0], 2)),
        "percentile_75": float(np.round(quartiles[2], 2)),
    }

    initial_counts = frame["initial"].value_counts().head(top_n)
    ending_counts = frame["ending"].value_counts().head(top_n)
    vowel_initial_share = float(frame["vowel_initial"].mean())
    vowel_ending_share = float(frame["vowel_ending"].mean())

    all_letters = [
        character.upper()
        for name in frame["name"]
        for character in name
        if character.isalpha()
    ]
    letter_counts = pd.Series(all_letters).value_counts().head(top_n)

    return {
        "total_names": int(frame.shape[0]),
        "unique_names": int(frame["name"].nunique()),
        "length": length_summary,
        "initials": {
            "most_common": initial_counts.to_dict(),
            "vowel_share": vowel_initial_share,
        },
        "endings": {
            "most_common": ending_counts.to_dict(),
            "vowel_share": vowel_ending_share,
        },
        "letters": {
            "most_common": letter_counts.to_dict(),
        },
    }


def _configure_plotting() -> None:
    """Apply a consistent seaborn/matplotlib style for generated charts."""
    sns.set_theme(style="whitegrid", context="talk", palette="deep")


def _plot_length_distribution(frame: pd.DataFrame, output_dir: Path) -> Path:
    """Create a histogram visualising the distribution of name lengths."""
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(
        frame["length"].astype(int).to_numpy(),
        bins=range(int(frame["length"].min()), int(frame["length"].max()) + 2),
        kde=True,
        ax=ax,
    )
    ax.set_title("Name length distribution")
    ax.set_xlabel("Number of characters")
    ax.set_ylabel("Frequency")
    output_path = output_dir / "length_distribution.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def _plot_initial_frequency(frame: pd.DataFrame, output_dir: Path) -> Path:
    """Create a bar plot for the frequency of initial letters."""
    counts = frame["initial"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=counts.index, y=counts.values, ax=ax, color="#1f77b4")
    ax.set_title("Initial letter frequency")
    ax.set_xlabel("Initial letter")
    ax.set_ylabel("Count")
    output_path = output_dir / "initial_letter_frequency.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def _plot_initial_vs_length_heatmap(frame: pd.DataFrame, output_dir: Path) -> Path:
    """Create a heatmap that shows how initials relate to name length."""
    crosstab = pd.crosstab(frame["initial"], frame["length"])
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(crosstab, cmap="mako", ax=ax)
    ax.set_title("Initial letter by name length")
    ax.set_xlabel("Name length")
    ax.set_ylabel("Initial letter")
    output_path = output_dir / "initial_by_length_heatmap.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def _generate_wordcloud(names: Sequence[str], output_dir: Path) -> Path:
    """Create a word cloud highlighting name prominence."""
    wordcloud = WordCloud(
        width=1600, height=900, background_color="white", colormap="viridis"
    )
    image = wordcloud.generate(" ".join(names))
    output_path = output_dir / "name_wordcloud.png"
    image.to_file(output_path)
    return output_path


def create_visualisations(
    frame: pd.DataFrame, names: Sequence[str], output_dir: Path
) -> list[Path]:
    """Generate all visual assets and return their file paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    _configure_plotting()

    artefacts = [
        _plot_length_distribution(frame, output_dir),
        _plot_initial_frequency(frame, output_dir),
        _plot_initial_vs_length_heatmap(frame, output_dir),
        _generate_wordcloud(names, output_dir),
    ]
    return artefacts


def analyse_names(
    names: Sequence[str],
    *,
    output_dir: Path | None = None,
    top_n: int = 10,
) -> dict:
    """Run the full analytical pipeline and return structured results."""
    frame = build_name_frame(names)
    summary = summarise_name_frame(frame, top_n=top_n)

    if output_dir is None:
        output_dir = Path(__file__).with_name("Data") / "analysis"
    artefacts = create_visualisations(frame, names, output_dir)
    summary["artefacts"] = [str(path) for path in artefacts]
    return summary


if __name__ == "__main__":
    try:
        names = read_names()
        sorted_names = sort_names(names)
        for name in sorted_names:
            print(name)

        results = analyse_names(sorted_names)
        print("\nStatistical overview:")
        length_stats = results["length"]
        print(
            f"  Names: {results['total_names']} unique entries: {results['unique_names']}\n"
            f"  Length mean/median: {length_stats['mean']:.2f}/{length_stats['median']:.2f}"
        )
        print("  Most common initials:")
        for letter, count in results["initials"]["most_common"].items():
            print(f"    {letter}: {count}")
        print("  Most common endings:")
        for letter, count in results["endings"]["most_common"].items():
            print(f"    {letter}: {count}")
        print("  Top letters used:")
        for letter, count in results["letters"]["most_common"].items():
            print(f"    {letter}: {count}")
        print("\nGenerated visualisations:")
        for path in results["artefacts"]:
            print(f"  {path}")
        print(f"\nTotal alphabetic characters: {count_letters(sorted_names)}")
    except FileNotFoundError as exc:
        print(exc)
