#!/usr/bin/env bash
# setup.sh — create one isolated Python 3.12 virtual environment per tool.
#
# Requirements (see README.md):
#   - uv installed (https://docs.astral.sh/uv/getting-started/installation/)
#   - Python 3.12 installed through uv:  uv python install 3.12
#   - submodules checked out:            git submodule update --init --recursive
#
# Usage (from the repository root):
#   chmod +x setup.sh
#   ./setup.sh

set -euo pipefail

PYTHON_VERSION="3.12"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/venvs"
MOD_DIR="${ROOT_DIR}/modules"

info()  { printf '\n\033[1;34m[*] %s\033[0m\n' "$*"; }
ok()    { printf '\033[1;32m[+] %s\033[0m\n' "$*"; }
fail()  { printf '\033[1;31m[!] %s\033[0m\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- checks
command -v uv >/dev/null 2>&1 || fail "uv not found. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"

for tool in spiderfoot sherlock holehe; do
    if [ ! -e "${MOD_DIR}/${tool}/.git" ]; then
        fail "modules/${tool} is empty. Run: git submodule update --init --recursive"
    fi
done

info "Making sure Python ${PYTHON_VERSION} is available to uv"
uv python install "${PYTHON_VERSION}"

mkdir -p "${VENV_DIR}"

# make_venv <name>: (re)create venvs/<name> with Python 3.12
make_venv() {
    local name="$1"
    info "Creating venvs/${name} (Python ${PYTHON_VERSION})"
    uv venv --python "${PYTHON_VERSION}" --clear "${VENV_DIR}/${name}"
    "${VENV_DIR}/${name}/bin/python" --version
}

# ---------------------------------------------------------------- sherlock
make_venv sherlock
info "Installing Sherlock from modules/sherlock"
uv pip install --python "${VENV_DIR}/sherlock/bin/python" "${MOD_DIR}/sherlock"
ok "Sherlock installed"

# ---------------------------------------------------------------- holehe
make_venv holehe
info "Installing Holehe from modules/holehe"
uv pip install --python "${VENV_DIR}/holehe/bin/python" "${MOD_DIR}/holehe"
ok "Holehe installed"

# ---------------------------------------------------------------- spiderfoot
make_venv spiderfoot
info "Installing SpiderFoot requirements from modules/spiderfoot/requirements.txt"
# build-constraints.txt keeps Cython < 3 while PyYAML 5.4.1 is built from source.
uv pip install --python "${VENV_DIR}/spiderfoot/bin/python" \
    -b "${ROOT_DIR}/build-constraints.txt" \
    -r "${MOD_DIR}/spiderfoot/requirements.txt"
ok "SpiderFoot requirements installed"

info "Done. Activate a tool's venv before using it, for example:"
cat <<'EOF'
  source venvs/sherlock/bin/activate   && sherlock --help ; deactivate
  source venvs/holehe/bin/activate     && holehe --help   ; deactivate
  source venvs/spiderfoot/bin/activate && cd modules/spiderfoot && python sf.py -l 127.0.0.1:5001
EOF
