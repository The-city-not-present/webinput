#!/usr/bin/env python3
"""Build-time helper for the webinput library.

Turns the static, non-importable files under `src/endpoints/assets_static/` into
an importable Python module `src/endpoints/GENERATED/ASSETS.py`, so the HTTP
asset handler can serve them from memory (no separate files at runtime).

`src/endpoints/GENERATED/` is gitignored and recreated here on every build.
This script is a build-time tool only — it is never imported at runtime.
"""

from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'src'
ASSETS_STATIC = SRC / 'endpoints' / 'assets_static'
GENERATED = SRC / 'endpoints' / 'GENERATED'

# Directory/file names skipped while scanning assets_static.
EXCLUDED_PARTS = {'__pycache__', '.git', '.DS_Store'}


def _collect_assets() -> dict[str, str]:
    assets: dict[str, str] = {}
    if not ASSETS_STATIC.is_dir():
        return assets

    for path in sorted(ASSETS_STATIC.rglob('*')):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(ASSETS_STATIC).parts
        if any(part in EXCLUDED_PARTS or part.startswith('.') for part in rel_parts):
            continue
        rel = path.relative_to(ASSETS_STATIC).as_posix()
        assets[rel] = path.read_text(encoding='utf-8')

    return assets


def main():
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / '__init__.py').write_text('', encoding='utf-8')

    assets = _collect_assets()
    now = datetime.now(timezone.utc)
    out_file = GENERATED / 'ASSETS.py'
    out_file.write_text(
        f'\n# THIS IS AUTO_GENERATED\n# updated {now}\n\nASSETS = {assets!r}\n\n',
        encoding='utf-8',
    )
    print(f'webinput build_assets: wrote {len(assets)} asset(s) to {out_file}')


if __name__ == '__main__':
    main()
