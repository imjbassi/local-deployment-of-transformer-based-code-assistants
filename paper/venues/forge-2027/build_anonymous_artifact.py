"""Build a reproducible review archive, excluding history and compiled caches."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

VENUE = Path(__file__).resolve().parent
ROOT = VENUE.parents[2]
IDENTITY = re.compile(r"jaive|bassi|DESKTOP-3TNM9JL|22848609|22800650", re.I)


def scrub(text: str) -> str:
    text = re.sub(
        r"(?:/mnt/c/Users/[^/]+/Desktop/|C:[\\/]Users[\\/][^\\/]+[\\/]Desktop[\\/])"
        r"Local-Deployment-of-Transformer-based-Code-Assistants-main[\\/]?",
        "./",
        text,
        flags=re.I,
    )
    text = re.sub(r"(?:/home/[^/\s]+|[A-Z]:[\\/]Users[\\/][^\\/\s]+)", "<ANONYMOUS_HOME>", text)
    text = re.sub(
        r"https://github.com/imjbassi/[^\s\"<>]+", "<WITHHELD_REPOSITORY_URL>", text, flags=re.I
    )
    text = re.sub(r"10\.5281/zenodo\.(?:22848609|22800650)", "<WITHHELD_DOI>", text)
    text = text.replace("Jaiveer Bassi", "Anonymous study authors")
    return text


def scrub_json(value):
    if isinstance(value, dict):
        return {
            key: (item if key in {"solution", "completion", "prompt"} else scrub_json(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [scrub_json(item) for item in value]
    return scrub(value) if isinstance(value, str) else value


def build() -> Path:
    files = {}
    changes = []
    selections = [ROOT / "LICENSE", ROOT / "pyproject.toml", ROOT / ".dockerignore"]
    for directory, suffixes in (
        ("src", {".py"}),
        ("tests", {".py"}),
        ("scripts", {".py", ".sh"}),
        ("protocol", {".json", ".txt"}),
        ("artifacts", {".json", ".jsonl", ".txt"}),
    ):
        selections.extend(
            path
            for path in (ROOT / directory).rglob("*")
            if path.suffix in suffixes and "__pycache__" not in path.parts
        )
    selections.extend((ROOT / "containers").rglob("Dockerfile"))
    selections.extend((VENUE / "licenses").glob("*.txt"))
    for path in sorted(set(selections)):
        if path.name in {"test_paper.py", "repository-commit.txt", "repository-status.txt"}:
            continue
        name = path.relative_to(ROOT).as_posix()
        if path.parent == VENUE / "licenses":
            name = "licenses/" + path.name
        original = path.read_bytes()
        text = original.decode("utf-8")
        # Preserve JSONL sample bytes; parse metadata to handle escaped Windows paths.
        if path.suffix == ".json":
            data = json.loads(text)
            revised = scrub_json(data)
            text = json.dumps(revised, indent=2) + "\n" if revised != data else text
        elif path.suffix != ".jsonl":
            text = scrub(text)
        if path.name == "pyproject.toml":
            text = re.sub(r"\[project.urls\].*?(?=\n\[)", "", text, flags=re.S)
            text = text.replace(
                'name = "local-code-assistant-benchmark"', 'name = "anonymous-benchmark-artifact"'
            )
        if path.name == "python-freeze.txt":
            lines = (line for line in text.splitlines() if not line.startswith("-e "))
            text = "\n".join(lines) + "\n"
        payload = text.encode("utf-8")
        if payload != original:
            changes.append(name)
        files[name] = payload
    files["README.md"] = (VENUE / "ARTIFACT_README.md").read_bytes()
    files["paper/evidence-audit.json"] = (ROOT / "paper/evidence-audit.json").read_bytes()
    protocol = subprocess.check_output(
        ["git", "show", "1025978:EXPERIMENT_PLAN.md"], cwd=ROOT
    ).decode("utf-8")
    files["protocol/PRESPECIFIED_PLAN.md"] = scrub(protocol).encode("utf-8")
    files["ANONYMIZATION.json"] = (
        json.dumps(
            {
                "modified_files": changes,
                "policy": "Metadata paths and own author attribution anonymized for review. "
                "JSONL generation bytes and evaluator solution strings are unchanged. "
                "Original third-party license notices are retained. Historical nested checksum "
                "manifests are omitted; use the archive root manifest.",
            },
            indent=2,
        )
        + "\n"
    ).encode()
    for name, payload in files.items():
        if IDENTITY.search(name) or IDENTITY.search(payload.decode("utf-8")):
            raise ValueError(f"Identifying text remains in {name}")
    files["SHA256SUMS"] = "".join(
        f"{hashlib.sha256(data).hexdigest()}  {name}\n" for name, data in sorted(files.items())
    ).encode()
    output = VENUE / "output/forge-2027-anonymous-artifact.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, payload)
    print(f"{output}: {len(files)} files")
    return output


if __name__ == "__main__":
    build()
