#!/usr/bin/env python3
"""
Pack 125 — Validator: Home Borea asset resolution.
Verifica che HomeHeroSplash NON usi fallback blu/emoji come path primario per
legacy `borea` o `greek_borea` quando l'asset locale esiste.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "frontend" / "components" / "home" / "HomeHeroSplash.tsx"
ASSET_DIR = REPO_ROOT / "frontend" / "assets" / "heroes" / "greek_borea"


def main() -> int:
    errors: list[str] = []
    if not TARGET.exists():
        errors.append(f"missing: {TARGET}")
        return _emit(errors)
    # Asset esiste?
    if not ASSET_DIR.exists():
        errors.append(f"greek_borea asset dir missing: {ASSET_DIR}")
    else:
        if not (ASSET_DIR / "transparent.png").exists() and not (ASSET_DIR / "splash.png").exists():
            errors.append("greek_borea has no transparent.png OR splash.png")
        else:
            print("OK    greek_borea local asset exists")

    src = TARGET.read_text(encoding="utf-8")
    # Pack 125: il branch isBorea deve essere PRIMA del gradient fallback.
    # 1. isBoreaLikeId(hero.id) o equivalente alias check
    if "isBoreaLikeId" not in src and "BOREA_HERO_ID_ALIASES" not in src:
        errors.append("no Borea alias mapping (legacy borea + canonical greek_borea)")
    else:
        print("OK    Borea alias mapping present")
    # 2. Import asset greek_borea
    if "greek_borea/transparent" not in src and "greek_borea/splash" not in src:
        errors.append("HomeHeroSplash does not import greek_borea asset")
    else:
        print("OK    greek_borea asset imported")
    # 3. isBorea branch DEVE rendere RNImage/Image con asset, non LinearGradient.
    #    Verifichiamo posizionale e contenutistico.
    idx_isborea = src.find("{isBorea ? (")
    idx_uictx = src.find("useUiContract ? (")
    if idx_isborea == -1:
        errors.append("isBorea branch not rendered as primary path before useUiContract")
    elif idx_uictx != -1 and idx_isborea > idx_uictx:
        errors.append("isBorea branch is NOT before useUiContract (must be primary)")
    else:
        branch_body = src[idx_isborea:idx_isborea + 800]
        if "GREEK_BOREA" in branch_body and ("RNImage" in branch_body or "<Image" in branch_body):
            print("OK    isBorea PRIMARY path renders local image asset (GREEK_BOREA)")
        elif "LinearGradient" in branch_body or "fallbackIcon" in branch_body:
            errors.append("isBorea PRIMARY path uses LinearGradient/emoji (must use image)")
        else:
            errors.append("isBorea PRIMARY path does not render image asset")
    # 4. No ownership grant in HomeHeroSplash (read-only display).
    forbidden_patterns = [
        "/api/user/heroes/grant", "/api/gacha/", "/api/shop/",
        "unlock_borea", "grant_borea",
    ]
    for fp in forbidden_patterns:
        if fp in src:
            errors.append(f"forbidden pattern in HomeHeroSplash: `{fp}`")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 125 — Home Borea asset resolution")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_125_HOME_BOREA_ASSET_RESOLUTION",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_125_home_borea_asset_resolution_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  Home Borea uses local asset, no fallback blue/emoji, no ownership grant")
    return 0


if __name__ == "__main__":
    sys.exit(main())
