"""Build a deterministic public release candidate from Git-tracked files."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "local-code-benchmark-publication-v1.9-rc1.zip"
ARCHIVE_ROOT = "local-code-benchmark-publication-v1.9-rc1"
ZIP_TIME = (2026, 9, 23, 0, 0, 0)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()


def tracked_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    paths = [Path(item.decode("utf-8")) for item in raw.split(b"\0") if item]
    missing = [path for path in paths if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"tracked files missing from checkout: {missing}")
    return sorted(paths, key=lambda path: path.as_posix())


def zip_write(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/{name}", ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data, compresslevel=9)


def build(output: Path, allow_dirty: bool) -> None:
    status = git("status", "--porcelain")
    if status and not allow_dirty:
        raise SystemExit(
            "refusing to package a dirty worktree; commit/stash changes or pass "
            "--allow-dirty for a non-archival test"
        )

    files = tracked_files()
    hashes: list[tuple[str, str]] = []
    payloads: list[tuple[str, bytes]] = []
    for relative in files:
        data = (ROOT / relative).read_bytes()
        name = relative.as_posix()
        hashes.append((hashlib.sha256(data).hexdigest(), name))
        payloads.append((name, data))

    manifest = {
        "archive_format": 1,
        "archive_root": ARCHIVE_ROOT,
        "manuscript_version": "1.9",
        "release_candidate": "v1.9-rc1",
        "source_commit": git("rev-parse", "HEAD"),
        "source_dirty": bool(status),
        "tracked_file_count": len(files),
        "historical_release": {
            "version": "1.3.0",
            "doi": "10.5281/zenodo.22848609",
            "contains_this_candidate": False,
        },
        "warning": (
            "Generated Python in artifacts is untrusted; use the documented "
            "isolated evaluator."
        ),
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    sums = "".join(f"{digest}  {name}\n" for digest, name in hashes).encode()

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w") as archive:
        for name, data in payloads:
            zip_write(archive, name, data)
        zip_write(archive, "RELEASE_MANIFEST.json", manifest_bytes)
        zip_write(archive, "SHA256SUMS", sums)
    temporary.replace(output)
    print(output)
    print(f"sha256={hashlib.sha256(output.read_bytes()).hexdigest()}")
    print(f"tracked_files={len(files)} dirty={bool(status)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="build a test archive while recording source_dirty=true",
    )
    args = parser.parse_args()
    build(args.output.resolve(), args.allow_dirty)


if __name__ == "__main__":
    main()
