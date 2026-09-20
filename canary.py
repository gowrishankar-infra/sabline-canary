#!/usr/bin/env python3
"""The canary: the newest Sabline release, installed as a user installs it,
runs discount.vel and refuses a program that fetches a URL.

    python canary.py --name "PyPI" --command venv/bin/sabline
    python canary.py --name "npm" --command "node /path/to/sabline.js"
    python canary.py --name "Docker" --docker sabline:canary

discount.vel must run and print the amounts it always prints. A program
that fetches a URL must be refused with E310, under the default budget and
under --allow io, and must not reach the network. Every program runs from
an empty directory. A path in a command is taken from where this starts.
"""
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYABLE = ("payable  INR 112.90", "payable  INR 0.00")
NET = ('fn main() uses net, io {\n'
       '    check fetch("https://example.com/") {\n'
       '        ok body { print("reached the network") }\n'
       '        fail why { print(why) }\n'
       '    }\n'
       '}\n')
FAILED: list[str] = []


def ok(label: str, good: bool, detail: str = "") -> None:
    print(f"  {'ok    ' if good else 'BROKEN'}  {label}")
    if not good:
        FAILED.append(label)
        if detail:
            print("          " + detail.strip().replace("\n", "\n          ")[:1500])


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=900)
    return done.returncode, done.stdout + done.stderr


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--name", required=True)
    how = ap.add_mutually_exclusive_group(required=True)
    how.add_argument("--command")
    how.add_argument("--docker", metavar="IMAGE")
    args = ap.parse_args(argv)
    work = Path(tempfile.mkdtemp(prefix="sabline-canary-"))
    try:
        shutil.copy2(HERE / "discount.vel", work / "discount.vel")
        (work / "net.vel").write_text(NET, encoding="utf-8")
        if args.command:
            words = shlex.split(args.command, posix=os.name != "nt")
            cmd = [os.path.abspath(w) if not w.startswith("-")
                   and os.path.exists(w) else w for w in words]
            where = ""
        else:
            mount = str(work).replace("\\", "/")
            cmd = ["docker", "run", "--rm", "-v", f"{mount}:/work", args.docker]
            where = "/work/"
        print(f"{args.name}")
        print("-" * 62)
        code, out = run(cmd + ["--version"], work)
        ok(f"--version answers: {out.strip()[:60]}", code == 0, out)
        code, out = run(cmd + ["check", where + "discount.vel"], work)
        ok("check discount.vel", code == 0, out)
        code, out = run(cmd + [where + "discount.vel"], work)
        ok("discount.vel runs and prints what it always prints",
           code == 0 and all(p in out for p in PAYABLE), out)
        for extra in ([], ["--allow", "io"]):
            code, out = run(cmd + [where + "net.vel"] + extra, work)
            ok(f"a program that fetches a URL is refused "
               f"({' '.join(extra) or 'default budget'}), with E310",
               code == 1 and "E310" in out and "reached the network" not in out,
               f"exit {code}: {out}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("-" * 62)
    print(f"{args.name}: {'every check passed' if not FAILED else f'{len(FAILED)} failed'}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
