# Email-OSINT-

A small workspace that bundles three open-source OSINT tools as **git submodules**.
Each submodule is pinned to a fixed upstream version, and each tool gets its **own Python 3.12
virtual environment**.

> Full step-by-step guide in Persian: [`docs/GUIDE.fa.md`](docs/GUIDE.fa.md)

## Structure

```
Email-OSINT-/
├── modules/
│   ├── spiderfoot/   -> https://github.com/smicallef/spiderfoot        (tag v4.0)
│   ├── sherlock/     -> https://github.com/sherlock-project/sherlock  (tag v0.16.2)
│   └── holehe/       -> https://github.com/megadose/holehe            (commit 14da70f, no tags upstream)
├── venvs/                  # created by setup.sh, ignored by git
├── build-constraints.txt   # Cython<3, needed to build PyYAML 5.4.1 for SpiderFoot
├── setup.sh                # creates venvs/{sherlock,holehe,spiderfoot} with uv + Python 3.12
└── docs/GUIDE.fa.md
```

| Tool | What it does | Pinned version | License (of the pinned version) |
|------|--------------|----------------|---------------------------------|
| SpiderFoot | OSINT automation framework with a web UI | `v4.0` (`b9c345d`) | **GPL-2.0** — the `LICENSE` file at tag v4.0 is GPLv2. Upstream switched `master` to MIT on 2022-05-06, after v4.0 was tagged. |
| Sherlock | Finds accounts by username across social networks | `v0.16.2` (`a38ba54`) | MIT |
| Holehe | Checks whether an email is registered on various sites | `14da70f` (master, 2024-09-10) | GPL-3.0 |

Each tool keeps its own license; see `modules/<tool>/LICENSE*`.

## Quick start

```bash
# Requires git, uv (https://docs.astral.sh/uv/) — Python 3.12 is installed by uv
git clone --recurse-submodules https://github.com/amirxoo13/Email-OSINT-.git
cd Email-OSINT-
chmod +x setup.sh
./setup.sh
```

If you cloned without `--recurse-submodules`, the `modules/*` folders are empty. Fix it with:

```bash
git submodule update --init --recursive
```

## Usage

```bash
source venvs/sherlock/bin/activate && sherlock --help; deactivate
source venvs/holehe/bin/activate   && holehe --help;   deactivate

source venvs/spiderfoot/bin/activate
cd modules/spiderfoot && python sf.py -l 127.0.0.1:5001   # then open http://127.0.0.1:5001
```

SpiderFoot stores its database and logs in `~/.spiderfoot/`, outside this repository.

## Legal and ethical use

These tools query third-party websites and services. Use them only:

- on data you own, or with **explicit written permission** from the person or organisation concerned
  (for example, an authorised penetration test or your own accounts);
- in compliance with the laws of your country and the target's country (data protection and
  computer-misuse laws such as the GDPR), and with each website's terms of service.

Do not use them to stalk, harass, dox, or profile people. You are solely responsible for how you use them.
