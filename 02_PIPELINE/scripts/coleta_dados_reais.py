#!/usr/bin/env python3
"""Orquestra a coleta reproduzível das fontes reais do Sensus Health AI — SP/2025."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_DIR))

from src.collect_cnes import collect_cnes_api, collect_cnes_snapshot, collect_regioes_csv
from src.collect_sih import collect_sih
from src.validate_sources import validate_existing, write_manifest


def run_all(*, keep_dbc: bool = False, workers: int = 6) -> None:
    collect_sih(keep_dbc=keep_dbc)
    collect_cnes_api(workers=workers)
    collect_cnes_snapshot()
    collect_regioes_csv()
    validate_existing()
    write_manifest()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Coleta real Sensus Health AI — SP/2025")
    p.add_argument("--stage", choices=("all", "sih", "cnes-api", "cnes-2025", "regioes", "validate"), default="all")
    p.add_argument("--keep-dbc", action="store_true")
    p.add_argument("--workers", type=int, default=6)
    return p.parse_args()


def main() -> int:
    a = parse_args()
    if a.stage == "all":
        run_all(keep_dbc=a.keep_dbc, workers=a.workers)
    elif a.stage == "sih":
        collect_sih(keep_dbc=a.keep_dbc); write_manifest()
    elif a.stage == "cnes-api":
        collect_cnes_api(workers=a.workers); write_manifest()
    elif a.stage == "cnes-2025":
        collect_cnes_snapshot(); write_manifest()
    elif a.stage == "regioes":
        collect_regioes_csv(); write_manifest()
    elif a.stage == "validate":
        validate_existing(); write_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
