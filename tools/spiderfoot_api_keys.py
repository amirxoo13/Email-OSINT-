#!/usr/bin/env python3
"""List every SpiderFoot module option that needs an API key.

The data comes from each module's own metadata (modules/spiderfoot/modules/sfp_*.py):
the option names, the pricing model ('model') and the vendor's
'apiKeyInstructions'. Nothing here is hard-coded.

Outputs:
  - a Markdown checklist (default: api-keys.md) with the sign-up steps per service
  - a SpiderFoot.cfg template with one empty "module:option=" line per key, in the
    same "name=value" format that the web UI's "Export API Keys" button produces and
    "Import API Keys" accepts (see sfwebui.py: optsexport / savesettings).

Usage (from the repository root):
  venvs/spiderfoot/bin/python tools/spiderfoot_api_keys.py
  venvs/spiderfoot/bin/python tools/spiderfoot_api_keys.py --free-only
"""

import argparse
import importlib
import os
import sys
import warnings

# Option names that hold credentials, as used by SpiderFoot modules.
KEY_HINTS = ("api_key", "apikey", "api_secret", "secret", "password", "token", "username", "user_id", "cse_id")

MODEL_LABELS = {
    "FREE_NOAUTH_UNLIMITED": "free, no key",
    "FREE_NOAUTH_LIMITED": "free, no key (rate-limited)",
    "FREE_AUTH_UNLIMITED": "free account",
    "FREE_AUTH_LIMITED": "free account (limited)",
    "COMMERCIAL_ONLY": "paid only",
    "PRIVATE_ONLY": "private / invite only",
}


def load_modules(sf_dir):
    sys.path.insert(0, sf_dir)
    warnings.simplefilter("ignore")
    mods = {}
    for filename in sorted(os.listdir(os.path.join(sf_dir, "modules"))):
        if not (filename.startswith("sfp_") and filename.endswith(".py")) or filename == "sfp_template.py":
            continue
        name = filename[:-3]
        mod = importlib.import_module(f"modules.{name}")
        mods[name] = getattr(mod, name)().asdict()
    return mods


def key_options(info):
    return [o for o in info["opts"] if any(h in o.lower() for h in KEY_HINTS) and isinstance(info["opts"][o], str)]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sf-dir", default=os.path.join(root, "modules", "spiderfoot"))
    parser.add_argument("--markdown", default="api-keys.md")
    parser.add_argument("--cfg", default="SpiderFoot-api-keys.cfg")
    parser.add_argument("--free-only", action="store_true", help="only services with a FREE_AUTH_* model")
    args = parser.parse_args()

    rows = []
    for name, info in load_modules(args.sf_dir).items():
        opts = key_options(info)
        if not opts:
            continue
        ds = info["meta"].get("dataSource", {})
        model = ds.get("model", "")
        if args.free_only and not model.startswith("FREE_AUTH"):
            continue
        rows.append((name, info["name"], model, ds.get("website", ""), ds.get("apiKeyInstructions", []), opts))

    with open(args.markdown, "w", encoding="utf-8") as md:
        md.write(f"# SpiderFoot API keys ({len(rows)} modules)\n\n")
        for name, title, model, site, steps, opts in rows:
            md.write(f"## [ ] {title} (`{name}`) - {MODEL_LABELS.get(model, model or 'unknown')}\n\n")
            if site:
                md.write(f"Website: {site}\n\n")
            for i, step in enumerate(steps, 1):
                md.write(f"{i}. {step}\n")
            md.write("\nOptions: " + ", ".join(f"`{name}:{o}`" for o in opts) + "\n\n")

    with open(args.cfg, "w", encoding="utf-8") as cfg:
        for name, _, _, _, _, opts in rows:
            for o in opts:
                cfg.write(f"{name}:{o}=\n")

    counts = {}
    for row in rows:
        counts[row[2]] = counts.get(row[2], 0) + 1
    print(f"{len(rows)} modules need credentials:")
    for model, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {n:3d}  {MODEL_LABELS.get(model, model or 'unknown')}")
    print(f"Wrote {args.markdown} and {args.cfg}")


if __name__ == "__main__":
    main()
