#!/usr/bin/env uv run --script
# /// script
# requires-python: >=3.14
# ///

import argparse
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy every .env.*.template file to a sibling .env.* file "
            "while keeping the template originals."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Directory to scan recursively (default: current working directory).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing .env.* files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without writing files.",
    )
    return parser.parse_args()


def find_template_files(root: Path) -> list[Path]:
    return sorted(root.rglob(".env.*.template"))


def target_for(template_path: Path) -> Path:
    return template_path.with_name(template_path.name.removesuffix(".template"))


def main() -> int:
    args = parse_args()
    root = args.root.resolve()

    if not root.exists() or not root.is_dir():
        print(f"error: root is not a directory: {root}")
        return

    templates = find_template_files(root)
    if not templates:
        print("No .env.*.template files found.")
        return

    copied = 0
    skipped = 0

    for template in templates:
        target = target_for(template)

        if target.exists() and not args.overwrite:
            print(f"SKIP  {template} -> {target} (target exists)")
            skipped += 1
            continue

        print(f"COPY  {template} -> {target}")
        if not args.dry_run:
            shutil.copy2(template, target)
        copied += 1

    print(f"Done. copied={copied} skipped={skipped} found={len(templates)}")


if __name__ == "__main__":
    main()
