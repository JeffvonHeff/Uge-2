# Project 1 - Name Analytics

Project&nbsp;1 processes the raw `Navneliste.txt` roster and produces both tabular summaries and visual artefacts that describe the collection of names. It normalises the source data, computes statistics, and exports plots that make it easier to reason about trends such as popular initials or name lengths.

## Key Features
- Cleans comma-separated name entries and returns a consistently formatted list.
- Sorts names with optional case-insensitive ordering.
- Computes descriptive statistics (min/max/mean/percentiles) for name lengths.
- Reports high-frequency initials, endings, and individual letters.
- Builds a `pandas.DataFrame` with derived columns for length and vowel flags.
- Generates plots (histogram, bar chart, heatmap) and a word cloud via Matplotlib/Seaborn/WordCloud.

## Prerequisites
- Python 3.9+
- Dependencies listed in `requirements.txt` (pandas, numpy, matplotlib, seaborn, wordcloud).
- Source file `Navneliste.txt` placed alongside `Project1.py`.

Install requirements into your virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Script
Execute the analytics pipeline directly:

```bash
python Project1.py
```

The script will:
1. Read and normalise names from `Navneliste.txt`.
2. Print the sorted roster to stdout.
3. Output headline statistics (counts, length distribution, frequent initials/letters).
4. Generate visualisations saved under `Data/analysis/` (histogram, bar chart, heatmap, word cloud).

## Outputs
- Console summary with total names, unique names, and aggregated metrics.
- Image files in `Data/analysis/`:
  - `length_distribution.png`
  - `initial_letter_frequency.png`
  - `initial_by_length_heatmap.png`
  - `name_wordcloud.png`

## Customisation
- Pass a different roster filename to `read_names()` if needed.
- Adjust `top_n` when calling `analyse_names()` to change the number of popular items reported.
- Provide a custom `output_dir` to redirect generated images.

## Troubleshooting
- **Missing file**: Ensure `Navneliste.txt` exists; the script raises `FileNotFoundError` otherwise.
- **Encoding issues**: The reader expects UTF-8 input; re-save the source file using UTF-8 if you encounter decode errors.
- **Large datasets**: Pandas handles sizable lists well, but you can trim the input file to focus on a subset for faster experimentation.

## Testing
No automated tests are bundled. To validate manually, run `python Project1.py` and inspect both the console output and the generated artefacts.
