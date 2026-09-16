#!/usr/bin/env python3
"""Secret gate for MATA — scan tracked files for high-confidence credential patterns.

Exit 1 if anything is found. Never prints the secret itself (masks to 6 chars).
Self-excludes: this file (it contains the patterns by design).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PATTERNS = {
    "telegram bot token": r"\b\d{8,12}:[A-Za-z0-9_\-]{30,}\b",
    "openai-style api key": r"\bsk-[A-Za-z0-9_\-]{20,}",
    "github token": r"\b(ghp_|github_pat_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9_]{20,}",
    "aws access key": r"\bAKIA[0-9A-Z]{16}\b",
    "private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "jwt": r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}",
}

BINARY_SUFFIX = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".mp4", ".mov", ".mp3",
    ".zip", ".gz", ".tgz", ".tar", ".pdf", ".xlsx", ".xls", ".docx", ".db", ".sqlite",
    ".woff", ".woff2", ".ttf", ".otf", ".icns", ".pyc",
}
SKIP_DIRS = ("node_modules/", ".git/", ".next/", ".venv/", "venv/", "dist/", "build/")
SELF = "scripts/secret_scan.py"


def mask(value: str) -> str:
    value = value.strip()
    return value[:6] + "…[MASKED]" if len(value) > 6 else "[MASKED]"


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True).stdout
    files = [f for f in out.splitlines() if f]

    findings: list[str] = []
    scanned = 0
    for rel in files:
        if rel == SELF or any(d in rel for d in SKIP_DIRS):
            continue
        if Path(rel).suffix.lower() in BINARY_SUFFIX:
            continue
        p = root / rel
        if not p.is_file() or p.stat().st_size > 8_000_000:
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        scanned += 1
        for label, rx in PATTERNS.items():
            for m in re.finditer(rx, text):
                line = text[: m.start()].count("\n") + 1
                findings.append(f"{rel}:{line}: {label} → {mask(m.group(0))}")

    print(f"[secret-scan] {scanned} file dipindai, {len(files)} tracked")
    if findings:
        print(f"[secret-scan] FAIL — {len(findings)} temuan:")
        for f in findings:
            print(f"  {f}")
        print("\nJangan commit kredensial. Simpan di config.json lokal (git-ignored) "
              "atau di submodule private aihackfest-mata-media.")
        return 1
    print("[secret-scan] OK — tidak ada kredensial terdeteksi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
