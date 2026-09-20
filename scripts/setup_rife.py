#!/usr/bin/env python3
"""Fetch the pinned official RIFE source and RIFE_m checkpoint without pip installs."""
from __future__ import annotations
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

SOURCE_URL = "https://github.com/hzwer/ECCV2022-RIFE.git"
SOURCE_COMMIT = "5d8adbdd40e12c2c8f91930eff838aebe561c086"
CHECKPOINT_ID = "RIFE_m_train_log/flownet.pkl"
CHECKPOINT_URL = "https://huggingface.co/hzwer/RIFE/resolve/19b0c859634efaf9dc63d56e7118c8c7bdfa5960/RIFE_m_train_log.zip?download=true"
ARCHIVE_SHA256 = "8cb49709fde0d53de8167273986458db1b15ff45b947a042026f1d383c99c8d7"
ARCHIVE_BYTES = 39819850
CHECKPOINT_SHA256 = "9f9e2e8b5c3fef311c9a782aa17a30f87c388ce6dc9c00e4993eba3d3941d3cb"
DEFAULT_ROOT = Path(__file__).resolve().parents[1] / ".local" / "rife"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksum(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"Checksum mismatch for {path}: expected {expected}, got {actual}")


def download(url: str, destination: Path, expected_hash: str, expected_bytes: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        verify_checksum(destination, expected_hash)
        print(f"Using verified archive: {destination} ({destination.stat().st_size:,} bytes)")
        return
    print(f"Downloading checkpoint archive ({expected_bytes:,} bytes, {expected_bytes / 1048576:.1f} MiB): {url}")
    temp = destination.with_suffix(destination.suffix + ".part")
    try:
        with urllib.request.urlopen(url, timeout=60) as response, temp.open("wb") as output:
            announced = response.headers.get("Content-Length")
            if announced:
                print(f"Server reports {int(announced):,} bytes")
            shutil.copyfileobj(response, output)
        if temp.stat().st_size != expected_bytes:
            raise RuntimeError(f"Download size mismatch: expected {expected_bytes:,}, got {temp.stat().st_size:,}")
        verify_checksum(temp, expected_hash)
        temp.replace(destination)
    finally:
        temp.unlink(missing_ok=True)


def prepare_source(root: Path) -> Path:
    source = root / "source"
    if source.exists():
        if not (source / ".git").is_dir():
            raise RuntimeError(f"Existing source directory is not a Git checkout: {source}")
    else:
        subprocess.run(["git", "clone", "--no-checkout", SOURCE_URL, str(source)], check=True)
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if actual != SOURCE_COMMIT:
        subprocess.run(["git", "fetch", "origin", SOURCE_COMMIT], cwd=source, check=True)
        subprocess.run(["git", "checkout", "--detach", SOURCE_COMMIT], cwd=source, check=True)
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if actual != SOURCE_COMMIT:
        raise RuntimeError(f"RIFE source commit mismatch: {actual}")
    return source


def extract_checkpoint(archive: Path, root: Path) -> Path:
    checkpoint = root / CHECKPOINT_ID
    if checkpoint.exists():
        verify_checksum(checkpoint, CHECKPOINT_SHA256)
        return checkpoint
    with zipfile.ZipFile(archive) as bundle:
        members = [member for member in bundle.infolist() if member.filename.endswith("/flownet.pkl") or member.filename == "flownet.pkl"]
        if len(members) != 1:
            raise RuntimeError(f"Expected one flownet.pkl in archive, found {len(members)}")
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        temp = checkpoint.with_suffix(".part")
        try:
            with bundle.open(members[0]) as source, temp.open("wb") as target:
                shutil.copyfileobj(source, target)
            temp.replace(checkpoint)
        finally:
            temp.unlink(missing_ok=True)
    verify_checksum(checkpoint, CHECKPOINT_SHA256)
    return checkpoint


def main() -> int:
    root = DEFAULT_ROOT
    try:
        source = prepare_source(root)
        archive = root / "RIFE_m_train_log.zip"
        download(CHECKPOINT_URL, archive, ARCHIVE_SHA256, ARCHIVE_BYTES)
        checkpoint = extract_checkpoint(archive, root)
        print(f"Source: {source} @ {SOURCE_COMMIT}")
        print(f"Checkpoint: {checkpoint} ({checkpoint.stat().st_size:,} bytes)")
        print(f"Checkpoint SHA256: {sha256(checkpoint)}")
        print(f"Remove assets with: rm -r {root}")
    except (OSError, RuntimeError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f"RIFE setup failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
