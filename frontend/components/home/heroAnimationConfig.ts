/**
 * HERO ANIMATION CONFIG — SCHELETRO (Msg 424)
 * ============================================
 *
 * Configurazione PER-EROE delle regioni di animazione home splash.
 *
 * OBIETTIVO FINALE (non ancora implementato — struttura predisposta):
 *  - blink sugli OCCHI (regione locale, non opacity globale)
 *  - respiro LOCALIZZATO sul TORACE (non scaleY dell'intero splash)
 *  - capelli / accessori: solo 5★ e 6★+
 *
 * Lo stato attuale del HomeHeroSplash è PROVVISORIO e va sostituito da
 * un motore unico che leggerà questa config.
 *
 * ──────────────────────────────────────────────────────────────────────
 * CONVENZIONE COORDINATE:
 * ──────────────────────────────────────────────────────────────────────
 * Le regioni sono espresse in PERCENTUALI (0-1) rispetto alle dimensioni
 * dello splash renderizzato. (0,0) = top-left, (1,1) = bottom-right.
 *
 * type HeroRegion = {
 *   x: number;      // center X as fraction of width
 *   y: number;      // center Y as fraction of height
 *   w: number;      // width  as fraction of width
 *   h: number;      // height as fraction of height
 * };
 *
 * ──────────────────────────────────────────────────────────────────────
 * COME SI ANIMERÀ (FASE FUTURA):
 * ──────────────────────────────────────────────────────────────────────
 *  - EYES: overlay mask sulla regione occhi, chiude una fascia scura
 *    verticale di ~15% dell'altezza regione per 80-100ms ogni 5-7s.
 *  - CHEST: overlay clip-path sulla regione torace con scaleY 1.0→1.015
 *    sinusoidale a 4000ms, limitato solo a quella sezione.
 *  - HAIR/ACCESSORIES: solo se rarity >= 5, leggera oscillazione scaleX.
 *
 * Finché il motore non esiste, questa è PURA configurazione di riferimento.
 */
export type HeroRegion = {
  x: number; y: number; w: number; h: number;
};

export type HeroAnimationConfig = {
  /** Regione occhi (obbligatoria se vuoi blink reale) */
  eyes?: HeroRegion;
  /** Regione torace per respiro localizzato */
  chest?: HeroRegion;
  /** Regione capelli (opzionale, solo 5★+ per extra movement) */
  hair?: HeroRegion;
  /** Regioni accessori vari (mantelli, gioielli, armi) */
  accessories?: HeroRegion[];
  /** Modalità ridotta: se true → niente extra, solo blink+breath. Default: auto in base a rarity. */
  minimal?: boolean;
};

// ──────────────────────────────────────────────────────────────────────
// HERO ID → ANIMATION CONFIG
// ──────────────────────────────────────────────────────────────────────
// Compilare queste regioni quando disponibili. Gli splash sono diversi
// per ogni eroe e le coordinate vanno MISURATE sull'asset reale (idealmente
// via tool di annotazione con preview).
const CONFIG: Record<string, HeroAnimationConfig> = {
  // Greek Hoplite — rarity 3. Extra DISABILITATI (niente capelli/accessori per <5★).
  greek_hoplite: {
    // VALORI DA MISURARE sul vero splash (/app/frontend/assets/heroes/greek_hoplite/base.png)
    // Placeholder ragionevoli da affinare empiricamente:
    eyes:  { x: 0.50, y: 0.22, w: 0.22, h: 0.05 },
    chest: { x: 0.50, y: 0.52, w: 0.36, h: 0.18 },
    minimal: true,  // 3★ → no hair/accessories extra
  },
  // Borea (tutorial) — no asset reale, tutto minimal.
  borea: {
    minimal: true,
  },
};

export function getHeroAnimationConfig(heroId: string, rarity?: number): HeroAnimationConfig {
  const cfg = CONFIG[heroId] || {};
  // Auto-minimal per rarity < 5 se non specificato
  const autoMinimal = cfg.minimal !== undefined
    ? cfg.minimal
    : (rarity !== undefined ? rarity < 5 : true);
  return { ...cfg, minimal: autoMinimal };
}

/**
 * Per il futuro motore: ritorna true se questo eroe supporta gli "extra"
 * (capelli / accessori) in base a rarity e config.
 */
export function heroSupportsExtras(heroId: string, rarity?: number): boolean {
  const cfg = getHeroAnimationConfig(heroId, rarity);
  if (cfg.minimal) return false;
  if (!cfg.hair && (!cfg.accessories || cfg.accessories.length === 0)) return false;
  return true;
}
