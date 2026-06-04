#!/usr/bin/env python3
# Validator: PROJECT-HERO-ASSET-DRYRUN-MANIFEST-READINESS
# Pack: MEGA_RELEASE_ACCELERATION_18_v69
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "contract": "data/design/assets/hero_asset_dryrun_manifest_contract_v1.json",
    "schema": "data/design/assets/hero_asset_expected_folder_schema_v1.json",
    "matrix": "data/design/assets/hero_asset_readiness_matrix_v1.json",
    "forbidden": "data/design/assets/hero_asset_import_forbidden_scope_v1.json",
    "scanner": "backend/scripts/hero_asset_dryrun_manifest_scanner_v1.py",
}

CONTRACT_EXP = {
    "dry_run_only": True,
    "real_asset_import": False,
    "file_copy_enabled": False,
    "asset_runtime_resolver_changed": False,
    "character_bible_changed": False,
    "hero_roster_changed": False,
    "db_writes": 0,
    "image_processing_required": False,
    "pil_required": False,
    "opencv_required": False,
    "generated_image_modification": False,
    "asset_overwrite": False,
    "public_runtime_exposure": False,
}
EXPECTED_SLOTS = {
    "splash", "no_background", "combat_base", "idle_sheet", "attack_sheet",
    "skill_sheet", "hit_sheet", "death_sheet", "chibi_home_later",
}

FORBIDDEN_SCANNER_SUBSTRINGS = [
    "pymongo", "motor", "MONGO_URL", "redis",
    "from PIL", "import PIL", "import cv2",
    "shutil.copy", "shutil.copyfile", "shutil.copytree",
    "shutil.move", "os.replace",
]


def strip_py_comments(src: str) -> str:
    src = re.sub(r"#[^\n]*", "", src)
    return src


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if errors:
        for e in errors:
            print(e)
        return 1

    contract = json.load(open(os.path.join(ROOT, FILES["contract"]), "r", encoding="utf-8"))
    for k, v in CONTRACT_EXP.items():
        if contract.get(k) != v:
            errors.append(f"CONTRACT_BAD: {k}={contract.get(k)!r} expected {v!r}")
    if not EXPECTED_SLOTS.issubset(set(contract.get("expected_asset_slots") or [])):
        errors.append("CONTRACT_SLOTS_MISSING")

    schema = json.load(open(os.path.join(ROOT, FILES["schema"]), "r", encoding="utf-8"))
    if schema.get("db_writes") != 0:
        errors.append("SCHEMA_BAD_DB_WRITES")
    if schema.get("file_copy_enabled") is not False:
        errors.append("SCHEMA_BAD_FILE_COPY")

    matrix = json.load(open(os.path.join(ROOT, FILES["matrix"]), "r", encoding="utf-8"))
    if matrix.get("db_writes") != 0:
        errors.append("MATRIX_BAD_DB_WRITES")
    if matrix.get("real_asset_import") is not False:
        errors.append("MATRIX_BAD_REAL_ASSET_IMPORT")
    if matrix.get("file_copy_enabled") is not False:
        errors.append("MATRIX_BAD_FILE_COPY")

    forbidden = json.load(open(os.path.join(ROOT, FILES["forbidden"]), "r", encoding="utf-8"))
    for must in [
        "real_asset_import", "file_copy", "asset_overwrite",
        "asset_runtime_resolver_change", "character_bible_changes",
        "image_processing", "db_writes", "validator_weakening", "fake_pass",
    ]:
        if must not in (forbidden.get("forbidden") or []):
            errors.append(f"FORBIDDEN_MISSING: {must}")

    scanner_src = open(os.path.join(ROOT, FILES["scanner"]), "r", encoding="utf-8").read()
    scanner_code = strip_py_comments(scanner_src)
    for bad in FORBIDDEN_SCANNER_SUBSTRINGS:
        if bad in scanner_code:
            errors.append(f"SCANNER_FORBIDDEN: {bad}")

    if errors:
        for e in errors:
            print(e)
        return 1
    print("PROJECT-HERO-ASSET-DRYRUN-MANIFEST-READINESS: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
