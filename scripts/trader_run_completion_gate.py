#!/usr/bin/env python3
"""Fail-closed completion checks for Trader repository runs.

The wrapper owns mutation (branch, commit, merge, push). This script only verifies
preflight, pre-commit residue, and final local/remote integration state.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SENSITIVE_BASENAMES = {
    "positions.yaml",
    "pmcc_positions.yaml",
    "auth.json",
    ".env",
    "credentials.json",
}
SENSITIVE_PREFIXES = (".cache/", ".hermes/", ".worktrees/")
REQUIRED_RUN_FILES = (
    "meta.json",
    "executor-closeout.md",
    "challenger-critique.md",
    "merged-next-seed.md",
    "learning-promotion.md",
)
REQUIRED_LEARNING_HEADINGS = (
    "## VERIFICATION",
    "## DURABLE",
    "## LESSON",
    "## NEXT",
)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret)"
    r"\s*[:=]\s*[\"']([^\"'\n]{8,})[\"']"
)
SAFE_SECRET_VALUES = ("[redacted]", "op://", "keychain://", "${", "<redacted", "example", "dummy")


class GateError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True
    )
    if check and proc.returncode:
        detail = (proc.stderr or proc.stdout).strip()
        raise GateError(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout.strip()


def local_head(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD")


def branch(repo: Path) -> str:
    return git(repo, "branch", "--show-current")


def status(repo: Path) -> str:
    return git(repo, "status", "--porcelain")


def remote_main(repo: Path) -> str:
    out = git(repo, "ls-remote", "--exit-code", "origin", "refs/heads/main")
    if not out:
        raise GateError("origin/main did not resolve")
    return out.split()[0]


def require_clean(repo: Path) -> None:
    dirty = status(repo)
    if dirty:
        preview = "\n".join(dirty.splitlines()[:20])
        raise GateError(f"repository is not clean:\n{preview}")


def require_main_remote_sync(repo: Path) -> None:
    if branch(repo) != "main":
        raise GateError(f"expected branch main, found {branch(repo)!r}")
    local = local_head(repo)
    remote = remote_main(repo)
    if local != remote:
        raise GateError(f"local HEAD {local} != origin/main {remote}")


def changed_paths(repo: Path, *, cached: bool) -> list[str]:
    args = ["diff", "--name-only", "--diff-filter=ACMR", "-z"]
    if cached:
        args.insert(1, "--cached")
    raw = git(repo, *args)
    return [item for item in raw.split("\0") if item]


def reject_sensitive_paths(paths: list[str]) -> None:
    bad = []
    for raw in paths:
        p = raw.replace("\\", "/")
        if p.startswith(SENSITIVE_PREFIXES) or Path(p).name in SENSITIVE_BASENAMES:
            bad.append(p)
    if bad:
        raise GateError("sensitive/runtime paths staged: " + ", ".join(sorted(bad)))


def reject_raw_secrets(repo: Path, paths: list[str]) -> None:
    findings: list[str] = []
    for rel in paths:
        proc = subprocess.run(
            ["git", "show", f":{rel}"], cwd=repo, capture_output=True
        )
        if proc.returncode or b"\x00" in proc.stdout:
            continue
        text = proc.stdout.decode("utf-8", errors="replace")
        for match in SECRET_ASSIGNMENT.finditer(text):
            value = match.group(1).strip().lower()
            if value.startswith(SAFE_SECRET_VALUES):
                continue
            findings.append(rel)
            break
    if findings:
        raise GateError(
            "possible raw secret assignment in staged content: "
            + ", ".join(sorted(findings))
        )


def require_run_artifacts(repo: Path, stamp: str, *, tracked: bool) -> None:
    run_dir = repo / "reports" / "trader-wakes" / "moa" / stamp
    missing = [name for name in REQUIRED_RUN_FILES if not (run_dir / name).is_file()]
    top_level = [
        repo / "reports" / "trader-wakes" / f"{stamp}-moa-exec.md",
        repo / "reports" / "trader-wakes" / f"{stamp}-moa-merge.md",
        repo / "reports" / "trader-wakes" / "LATEST.md",
        repo / "reports" / "trader-wakes" / "INDEX.md",
    ]
    missing.extend(str(p.relative_to(repo)) for p in top_level if not p.is_file())
    if missing:
        raise GateError("missing completion artifacts: " + ", ".join(missing))

    learning = (run_dir / "learning-promotion.md").read_text(encoding="utf-8")
    absent = [h for h in REQUIRED_LEARNING_HEADINGS if h not in learning]
    if absent:
        raise GateError("learning-promotion.md missing headings: " + ", ".join(absent))

    if tracked:
        required = [run_dir / name for name in REQUIRED_RUN_FILES] + top_level
        untracked = []
        for path in required:
            rel = str(path.relative_to(repo))
            proc = subprocess.run(
                ["git", "ls-files", "--error-unmatch", "--", rel],
                cwd=repo,
                text=True,
                capture_output=True,
            )
            if proc.returncode:
                untracked.append(rel)
        if untracked:
            raise GateError("completion artifacts not tracked: " + ", ".join(untracked))


def preflight(repo: Path) -> dict[str, object]:
    require_clean(repo)
    require_main_remote_sync(repo)
    return {"ok": True, "mode": "preflight", "head": local_head(repo), "branch": "main"}


def prepare(repo: Path, stamp: str, base_head: str, run_branch: str) -> dict[str, object]:
    if branch(repo) != run_branch:
        raise GateError(f"expected run branch {run_branch!r}, found {branch(repo)!r}")
    if local_head(repo) != base_head:
        raise GateError("run branch contains an unexpected pre-finalization commit")
    require_run_artifacts(repo, stamp, tracked=False)
    staged = changed_paths(repo, cached=True)
    if not staged:
        raise GateError("nothing staged for the run commit")
    reject_sensitive_paths(staged)
    reject_raw_secrets(repo, staged)
    diff_check = subprocess.run(
        ["git", "diff", "--cached", "--check"], cwd=repo, text=True, capture_output=True
    )
    if diff_check.returncode:
        raise GateError("git diff --cached --check failed:\n" + diff_check.stdout.strip())
    return {
        "ok": True,
        "mode": "prepare",
        "base_head": base_head,
        "branch": run_branch,
        "staged_files": len(staged),
    }


def postflight(repo: Path, stamp: str, base_head: str) -> dict[str, object]:
    require_clean(repo)
    require_main_remote_sync(repo)
    head = local_head(repo)
    if head == base_head:
        raise GateError("main HEAD did not advance from the run base")
    require_run_artifacts(repo, stamp, tracked=True)
    return {
        "ok": True,
        "mode": "postflight",
        "stamp": stamp,
        "base_head": base_head,
        "head": head,
        "branch": "main",
        "origin_main": remote_main(repo),
        "clean": True,
        "integrated": True,
        "pushed": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("preflight", "prepare", "postflight"))
    parser.add_argument("--repo", default=".")
    parser.add_argument("--stamp")
    parser.add_argument("--base-head")
    parser.add_argument("--run-branch")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    try:
        if args.mode == "preflight":
            result = preflight(repo)
        elif args.mode == "prepare":
            if not (args.stamp and args.base_head and args.run_branch):
                raise GateError("prepare requires --stamp, --base-head, and --run-branch")
            result = prepare(repo, args.stamp, args.base_head, args.run_branch)
        else:
            if not (args.stamp and args.base_head):
                raise GateError("postflight requires --stamp and --base-head")
            result = postflight(repo, args.stamp, args.base_head)
    except GateError as exc:
        print(json.dumps({"ok": False, "mode": args.mode, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
