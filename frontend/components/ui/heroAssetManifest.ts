/**
 * HERO ASSET MANIFEST — CONVENZIONE UFFICIALE (Msg 424)
 * ======================================================
 *
 * Questo è il PUNTO UNICO di verità per gli asset immagine degli eroi.
 * NON importare più i file PNG direttamente dalle pagine UI — passa SEMPRE
 * da questo manifest.
 *
 * ──────────────────────────────────────────────────────────────────────
 * CONVENZIONE PER I PROSSIMI EROI (da adesso in avanti):
 * ──────────────────────────────────────────────────────────────────────
 *
 *   /app/frontend/assets/heroes/<hero_id>/
 *     ├─ card.png          → UI card / collection grid / homepage splash / preview piccola
 *     ├─ detail.png        → fullscreen detail art / scheda enciclopedia / santuario big
 *     ├─ combat_base.png   → sprite statico combat laterale (pose neutra)
 *     ├─ idle/              → cartella con frame idle
 *     ├─ attack/            → cartella con frame attacco
 *     ├─ skill/             → cartella con frame skill
 *     ├─ hit/               → (opzionale) frame colpito
 *     └─ death/             → (opzionale) frame morte
 *
 * Regole di naming:
 *   - `card.png`       → MAX 512x512, ottimizzata per UI piccola/card. Formato verticale.
 *   - `detail.png`     → Immagine completa alta risoluzione per fullscreen. Formato verticale.
 *   - `combat_base.png`→ Sprite combat laterale, canvas 520x400 pose neutra.
 *
 * ──────────────────────────────────────────────────────────────────────
 * ECCEZIONE STORICA: greek_hoplite
 * ──────────────────────────────────────────────────────────────────────
 * Per errore storico, i file di Greek Hoplite NON seguono la convenzione:
 *   - `base.png`   → è in realtà il CARD/UI art (quello da usare come splash piccolo)
 *   - `splash.png` → è in realtà il DETAIL/fullscreen art
 *
 * Per non rompere la cache bundler / storia git / altri riferimenti legacy,
 * NON rinominiamo i file fisici. Risolviamo qui nel manifest:
 *   greek_hoplite.card   = base.png
 *   greek_hoplite.detail = splash.png
 *
 * Per i prossimi eroi la convenzione corretta sarà card.png / detail.png /
 * combat_base.png e questo manifest userà il naming pulito.
 */
import type { ImageSourcePropType } from 'react-native';

export type HeroAssetKind = 'card' | 'detail' | 'combat_base';

type HeroAssetMap = {
  card?: ImageSourcePropType;
  detail?: ImageSourcePropType;
  combat_base?: ImageSourcePropType;
};

// ──────────────────────────────────────────────────────────────────────
// HERO ID → ASSET MAP
// ──────────────────────────────────────────────────────────────────────
// `require` statici: Metro bundler li risolve a build-time. Se il file
// non esiste, qui compare errore compile-time (proprio ciò che vogliamo).
const MANIFEST: Record<string, HeroAssetMap> = {
  // ── GREEK HOPLITE (eccezione storica documentata) ──
  greek_hoplite: {
    // UI card: file LEGACY chiamato base.png (è il vero splash piccolo)
    card: require('../../assets/heroes/greek_hoplite/base.png'),
    // Fullscreen detail: file LEGACY chiamato splash.png
    detail: require('../../assets/heroes/greek_hoplite/splash.png'),
    combat_base: require('../../assets/heroes/greek_hoplite/combat_base.png'),
  },

  // ── ALTRI EROI (seguiranno la convenzione pulita card/detail/combat_base) ──
  // Esempio di come aggiungerli quando avremo asset reali:
  //
  // amaterasu: {
  //   card: require('../../assets/heroes/amaterasu/card.png'),
  //   detail: require('../../assets/heroes/amaterasu/detail.png'),
  //   combat_base: require('../../assets/heroes/amaterasu/combat_base.png'),
  // },
};

/**
 * Ritorna l'asset richiesto per un eroe, o `null` se non esiste nel manifest.
 * Chi chiama deve gestire il fallback (es. usare image_url remoto dal DB).
 */
export function getHeroAsset(heroId: string, kind: HeroAssetKind): ImageSourcePropType | null {
  const entry = MANIFEST[heroId];
  if (!entry) return null;
  return entry[kind] || null;
}

/**
 * Indica se abbiamo asset LOCALI per questo eroe (almeno uno dei 3 slot).
 * Utile per decidere se usare asset locale o image_url remoto.
 */
export function hasLocalAssets(heroId: string): boolean {
  return !!MANIFEST[heroId];
}

/**
 * Lista gli hero_id che hanno asset locali dichiarati.
 * Utile per debug/admin.
 */
export function listLocalHeroes(): string[] {
  return Object.keys(MANIFEST);
}
