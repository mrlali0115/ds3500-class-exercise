import argparse
import csv
import sys
from pathlib import Path


def check_data(filename):
    """Read the CSV file and check for missing values."""
    with open(filename, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    header = rows[0]
    data = rows[1:]
    missing_rows = []

    for row_number, row in enumerate(data, start=2):
        if any(value == "" for value in row):
            missing_rows.append(row_number)

    return header, data, missing_rows


parser = argparse.ArgumentParser(
    description="Check the quality of a CSV file."
)

parser.add_argument(
    "--input", "-i",
    required=True,
    help="CSV file to check"
)

parser.add_argument(
    "--output", "-o",
    default="data_quality.txt",
    help="Output report filename"
)

parser.add_argument(
    "--verbose", "-v",
    action="store_true",
    help="Show detailed DEBUG messages"
)

args = parser.parse_args()


p = Path(args.input)

if not p.is_file():
    print(f"File not found: '{args.input}'")
    sys.exit(1)

print(f"File validated: '{args.input}'")

header, data, missing_rows = check_data(args.input)

with open(args.output, "w") as f:
    f.write(f"Number of rows: {len(data)}\n")
    f.write(f"Number of columns: {len(header)}\n")
    f.write(f"Number of rows with missing values: {len(missing_rows)}\n")