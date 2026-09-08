#!/usr/bin/env bash
set -e; cd "$(dirname "$0")"
python3 tools/build_porte.py | head -1
python3 tools/porte_ferr.py
python3 tools/assemble.py
node tests/regress.js
node tests/job_test.js
