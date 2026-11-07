#!/usr/bin/env bash
set -e

# Temporary build script.
#
# webinput is a library, not a standalone app: it is bundled by the *outer*
# project (e.g. gitgui) via pinliner, not here. Until the real build steps are
# defined, this script only prepares the development environment so the module
# can be imported and tested after a fresh clone.

echo "Prep python"
echo "set venv"
if [ -x ".venv/Scripts/python.exe" ]; then
    pythonexecutable=".venv/Scripts/python.exe"
elif [ -x ".venv/bin/python" ]; then
    pythonexecutable=".venv/bin/python"
else
    python -m venv .venv
    if [ -x ".venv/Scripts/python.exe" ]; then
        pythonexecutable=".venv/Scripts/python.exe"
    elif [ -x ".venv/bin/python" ]; then
        pythonexecutable=".venv/bin/python"
    else
        echo "No Python virtual environment found"
        exit 1
    fi
fi
echo "done"
echo -
echo -

echo "Install dependencies"
"$pythonexecutable" -m pip install -r requirements.txt
echo "done"
echo -
echo -

echo "Build assets (assets_static -> GENERATED)"
"$pythonexecutable" build_assets.py
echo "done"
echo -
echo -

echo "Build: nothing to bundle yet (webinput is a library; see docs/roadmap.md)"
echo "Temporary build.sh — real build steps will be added later."
