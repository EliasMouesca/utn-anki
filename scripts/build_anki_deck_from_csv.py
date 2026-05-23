from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from utn_anki.csv_export import build_deck_from_csv, default_deck_name_from_csv


def backup_existing_deck(output_path: Path, project_root: Path) -> Path | None:
    if not output_path.exists():
        return None

    backup_dir = project_root / "bkp"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{output_path.stem}_{timestamp}{output_path.suffix}"
    backup_path = backup_dir / backup_name
    shutil.move(str(output_path), str(backup_path))
    return backup_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an Anki .apkg deck directly from a CSV file."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=ROOT / "cards.csv",
        help="CSV input file. Defaults to 'cards.csv' in the project root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output .apkg path. Defaults to '<csv_stem>.apkg' in the project root.",
    )
    parser.add_argument(
        "-n",
        "--deck-name",
        default=None,
        help="Anki deck name. Defaults to a title derived from the CSV filename.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path = args.csv_path.resolve()
    output_path = (
        args.output.resolve()
        if args.output is not None
        else (ROOT / f"{csv_path.stem}.apkg").resolve()
    )
    deck_name = args.deck_name or default_deck_name_from_csv(csv_path)
    backup_path = backup_existing_deck(output_path=output_path, project_root=ROOT)
    if backup_path is not None:
        print(f"Previous deck moved to: {backup_path}")

    output_path = build_deck_from_csv(
        csv_path=csv_path,
        output_path=output_path,
        deck_name=deck_name,
    )
    print(f"Anki deck written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
