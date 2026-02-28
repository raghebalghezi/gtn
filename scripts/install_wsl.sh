#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -eq 0 ]]; then
  echo "Run this script as a normal user (not root)."
  exit 1
fi

if ! command -v apt >/dev/null 2>&1; then
  echo "This script is intended for Debian/Ubuntu-based WSL distributions."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not installed."
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"

echo "[1/4] Installing system build dependencies..."
sudo apt update
sudo apt install -y build-essential cmake ninja-build python3-dev python3-pip

echo "[2/4] Upgrading pip..."
python3 -m pip install --upgrade pip

echo "[3/4] Installing GTN from local repo..."
python3 -m pip install "${REPO_ROOT}/bindings/python"

echo "[4/4] Verifying import..."
python3 - <<'PY'
import gtn
print("gtn import OK")
print("version:", getattr(gtn, "__version__", "unknown"))
PY

echo "Done."
