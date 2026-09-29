import json
import logging
from pathlib import Path

import pandas as pd
import yaml
import os
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


def inspect_csv(filepath):
    """Read a CSV file and display basic information."""
    data = pd.read_csv(filepath)
    logger.info(f"Inspecting CSV: {filepath.name}")
    print(data.head(3))


def inspect_json(filepath):
    """Read a JSON file and display basic information."""
    with open(filepath, "r") as f:
        data = json.load(f)

    logger.info(f"Inspecting JSON: {filepath.name}")
    print(data)


def inspect_yaml(filepath):
    """Read a YAML file and display basic information."""
    with open(filepath, "r") as f:
        config = yaml.safe_load(f)

    logger.info(f"Inspecting YAML: {filepath.name}")
    print(config)


def inspect_env():
    """Read a .env file and display basic information."""
    load_dotenv()

    keys = [
        key for key in ["USERNAME", "PASSWORD"]
        if os.getenv(key) is not None
    ]

    logger.info("Inspecting ENV")
    print(keys)


def main():
    data_dir = Path("data")

    filepath_csv = data_dir / "sample.csv"
    filepath_json = data_dir / "sample.json"
    filepath_yaml = data_dir / "sample.yaml"

    inspect_csv(filepath_csv)
    inspect_json(filepath_json)
    inspect_yaml(filepath_yaml)
    inspect_env()


if __name__ == "__main__":
    main()
