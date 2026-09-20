# sabline-canary

A daily check, from outside, that the newest release of
[Sabline](https://github.com/gowrishankar-infra/sabline-lang) installs and
works as its README says: from PyPI, from npm, as the Docker image, as the
GitHub Action, and as the standalone executables for Linux, macOS and
Windows.

Each install is asked two things by [`canary.py`](canary.py):

- `discount.vel`, a copy of the release's `examples/discount.vel`, runs and
  prints the amounts it always prints;
- a program that fetches a URL is refused with E310, under the default
  budget and under `--allow io`, and never reaches the network.

This repository holds no Sabline source, and installs only what was
released. The workflow is [`.github/workflows/canary.yml`](.github/workflows/canary.yml).
A failed run opens an issue here, or comments on the one already open.

The main repository checks its own `main` the same way every night, before
anything is released (`nightly.yml` and `check_install.py` there; its
MAINTENANCE.md says what each check is for).

---

This project was called **Velaris** until 8.6.0; the name belongs to an
unrelated company (velaris.io). <https://sabline.dev/renamed.html> lists
every address and where it now points. The committed `velaris.capabilities`
keeps the old name until the Action pin above moves past v8.6.0, because
the pinned release looks for that file.
