"""Convert a real pip --report resolution into a complete version lock.

Resolve again on each supported target after updating this file. No index URLs
or credentials from pip's report are copied into the lock.
"""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path, default=Path("requirements.lock"))
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    packages = {
        item["metadata"]["name"].lower().replace("_", "-"): item["metadata"]["version"]
        for item in report["install"]
    }
    if not packages or "psycopg-binary" not in packages:
        parser.error("Expected a complete clean resolution including psycopg-binary")
    lines = [
        "# Generated from pip --dry-run --ignore-installed --report; see runbook.",
        "# Complete version lock; package artifact hashes are not enforced.",
    ]
    for name, version in sorted(packages.items()):
        requirement = "psycopg[binary]" if name == "psycopg" else name
        lines.append(f"{requirement}=={version}")
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
