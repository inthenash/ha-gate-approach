"""Checks the repo before every commit, and above all before making it public.

  1. Every YAML file parses (Home Assistant's !input / !secret / !include tags allowed).
  2. Privacy scan: no private words, IP addresses, map coordinates, emails or tokens in
     any file git would commit. The private words live in _dev/private_terms.txt (one
     per line, never committed - see .gitignore), so the list itself cannot leak.

Usage:  python _dev/check.py        (exit code 0 = PASS)
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TERMS = ROOT / "_dev" / "private_terms.txt"

PATTERNS = {
    "IP address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "map coordinate": r"-?\b\d{1,3}\.\d{5,}\b",
    "email": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
    "token": r"\b(sk-ant-\w+|gh[opsu]_\w{10,}|eyJ\w{20,})",
    "Windows user path": r"(?i)c:[\\/]users[\\/]",
}


class Loader(yaml.SafeLoader):
    pass


Loader.add_multi_constructor("!", lambda loader, suffix, node: None)


def tracked_files():
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / line for line in out.splitlines() if line]


def main():
    problems = []
    if not TERMS.exists():
        problems.append(f"{TERMS.relative_to(ROOT)} is missing - add the private words first")
        terms = []
    else:
        terms = [t.strip() for t in TERMS.read_text(encoding="utf-8").splitlines()
                 if t.strip() and not t.startswith("#")]
    files = tracked_files()
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        if f.suffix in (".yaml", ".yml"):
            try:
                yaml.load(text, Loader=Loader)
            except yaml.YAMLError as e:
                problems.append(f"{rel}: YAML does not parse - {e}")
        for n, line in enumerate(text.splitlines(), 1):
            for term in terms:
                if re.search(rf"(?i)(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", line):
                    problems.append(f"{rel}:{n}: private word ({term[0]}...)")
            if rel == "_dev/check.py":
                continue
            for name, pat in PATTERNS.items():
                if re.search(pat, line):
                    problems.append(f"{rel}:{n}: {name}")
    for p in problems:
        print("FAIL", p)
    print(f"{len(files)} files checked, {len(terms)} private words -",
          "PASS" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
