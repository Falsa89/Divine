/**
 * Hero Battle Animations — profili per-eroe
 * ==========================================
 *
 * Obiettivo: dare a ogni eroe un set di animazioni di battaglia (attack,
 * skill, hit, death, heal, dodge) con identità chiara, invece di avere
 * un'unica routine generica condivisa da tutti.
 *
 * Architettura:
 *   - Un `HeroAnimProfile` espone una funzione per ogni state combat.
 *   - Ogni funzione riceve `AnimHandles` (shared values di Reanimated già
 *     creati in BattleSprite) e `AnimCtx` (size/isEnemy/dir).
 *   - BattleSprite chiama `profile.attack(handles, ctx)` etc. senza
 *     preoccuparsi della fantasy specifica dell'eroe.
 *   - `DEFAULT_PROFILE` preserva ESATTAMENTE il comportamento attuale per
 *     ogni eroe che non ha un profilo dedicato → zero regressione.
 *   - `HOPLITE_PROFILE` è il primo profilo custom: spear+shield tank.
 *
 * Convenzioni:
 *   - dir = +1 per player (isEnemy=false), -1 per enemy.
 *   - Tutte le animazioni devono TORNARE esplicitamente alla home (value 0).
 *   - Il wrapper globale di combat.tsx è IMMUTABILE — qui muoviamo solo
 *     i transform LOCALI del motion container interno a BattleSprite.
 *
 * Per aggiungere un nuovo eroe:
 *   1. Definisci un `XXX_PROFILE: HeroAnimProfile` con le funzioni che
 *      differiscono dal default. Quelle non ridefinite possono usare
 *      `DEFAULT_PROFILE.xxx`.
 *   2. Estendi `getAnimationProfile()` con la condizione (es. `isXXX(id, name)`).
 */
import {
  withTiming, withSequence, withDelay,
  cancelAnimation, Easing, SharedValue,
} from 'react-native-reanimated';
import { isGreekHoplite } from '../ui/hopliteAssets';

// ---- Types ------------------------------------------------------------------

export interface AnimHandles {
  transX: SharedValue<number>;
  transY: SharedValue<number>;
  bodyRot: SharedValue<number>;
  spriteScale: SharedValue<number>;
  spriteOp: SharedValue<number>;
  auraOp: SharedValue<number>;
  auraSc: SharedValue<number>;
  hitFlash: SharedValue<number>;
  idleY: SharedValue<number>;
}

export interface AnimCtx {
  size: number;
  isEnemy: boolean;
  /** +1 = player verso destra, -1 = enemy verso sinistra */
  dir: number;
}

export interface HeroAnimProfile {
  name: string;
  attack: (h: AnimHandles, c: AnimCtx) => void;
  skill: (h: AnimHandles, c: AnimCtx) => void;
  ultimate: (h: AnimHandles, c: AnimCtx) => void;
  hit: (h: AnimHandles, c: AnimCtx) => void;
  death: (h: AnimHandles, c: AnimCtx) => void;
  heal: (h: AnimHandles, c: AnimCtx) => void;
  dodge: (h: AnimHandles, c: AnimCtx) => void;
  /** Re-anchor alla home position quando lo state torna a 'idle'. */
  idleReset: (h: AnimHandles, c: AnimCtx) => void;
}

// ==========================================================================
// DEFAULT PROFILE
// --------------------------------------------------------------------------
// Preservo ESATTAMENTE il comportamento generico precedente per TUTTI gli
// eroi che non hanno un profilo dedicato. Nessuna regressione.
// ==========================================================================
export const DEFAULT_PROFILE: HeroAnimProfile = {
  name: 'default',

  attack: (h, c) => {
    const ATTACK_DASH = Math.round(c.size * 0.10);
    const ATTACK_LUNGE = Math.round(c.size * 0.12);
    h.transX.value = withSequence(
      withTiming(c.dir * ATTACK_DASH, { duration: 140 }),
      withTiming(c.dir * ATTACK_LUNGE, { duration: 60 }),
      withTiming(0, { duration: 260 }),
    );
    h.spriteScale.value = withSequence(
      withTiming(1.08, { duration: 120 }),
      withTiming(1, { duration: 220 }),
    );
  },

  skill: (h, c) => {
    const SKILL_DASH = Math.round(c.size * 0.07);
    h.auraOp.value = withSequence(
      withTiming(0.8, { duration: 150 }),
      withDelay(400, withTiming(0.15, { duration: 300 })),
    );
    h.auraSc.value = withSequence(
      withTiming(1.5, { duration: 200 }),
      withTiming(1, { duration: 300 }),
    );
    h.transX.value = withSequence(
      withTiming(c.dir * SKILL_DASH, { duration: 160 }),
      withTiming(0, { duration: 280 }),
    );
    h.spriteScale.value = withSequence(
      withTiming(1.12, { duration: 160 }),
      withTiming(1, { duration: 280 }),
    );
  },

  ultimate: (h, c) => DEFAULT_PROFILE.skill(h, c),

  hit: (h, c) => {
    const HIT_KNOCK = Math.round(c.size * 0.05);
    h.transX.value = withSequence(
      withTiming(-c.dir * HIT_KNOCK, { duration: 70 }),
      withTiming(0, { duration: 220 }),
    );
    h.hitFlash.value = withSequence(
      withTiming(0.6, { duration: 50 }),
      withTiming(0, { duration: 200 }),
    );
    h.spriteScale.value = withSequence(
      withTiming(0.94, { duration: 70 }),
      withTiming(1, { duration: 180 }),
    );
    h.bodyRot.value = withSequence(
      withTiming(-c.dir * 4, { duration: 70 }),
      withTiming(0, { duration: 200 }),
    );
  },

  death: (h, c) => {
    cancelAnimation(h.idleY);
    cancelAnimation(h.auraSc);
    cancelAnimation(h.auraOp);
    h.idleY.value = 0;
    h.bodyRot.value = withTiming(c.isEnemy ? -20 : 20, { duration: 600 });
    h.spriteOp.value = withTiming(0.25, { duration: 800 });
    h.spriteScale.value = withTiming(0.85, { duration: 600 });
    h.auraOp.value = withTiming(0, { duration: 300 });
  },

  heal: (h) => {
    h.auraOp.value = withSequence(
      withTiming(0.6, { duration: 300 }),
      withTiming(0.15, { duration: 500 }),
    );
    h.idleY.value = withSequence(
      withTiming(-5, { duration: 250 }),
      withTiming(0, { duration: 250 }),
    );
  },

  dodge: (h, c) => {
    const DODGE_STEP = Math.round(c.size * 0.10);
    h.transX.value = withSequence(
      withTiming(-c.dir * DODGE_STEP, { duration: 110 }),
      withDelay(180, withTiming(0, { duration: 240 })),
    );
    h.spriteOp.value = withSequence(
      withTiming(0.3, { duration: 80 }),
      withTiming(1, { duration: 200 }),
    );
  },

  idleReset: (h) => {
    h.transX.value = withTiming(0, { duration: 180 });
    h.transY.value = withTiming(0, { duration: 180 });
    h.bodyRot.value = withTiming(0, { duration: 180 });
    h.spriteScale.value = withTiming(1, { duration: 180 });
    h.spriteOp.value = withTiming(1, { duration: 180 });
  },
};

// ==========================================================================
// GREEK HOPLITE PROFILE — spear + shield frontliner
// --------------------------------------------------------------------------
// Fantasia: oplita greco con lancia + scudo. Tank/frontliner con peso.
//   Attack   → "Affondo di Falange" (spear thrust lineare, body push forward)
//   Skill    → "GUARDIA FERREA" (iron stance difensiva, single shield pulse)
//   Hit      → Tank stagger solido (poco knockback, più "piantato")
//   Death    → Kneel + collapse (sink → fall sideways + fade)
// ==========================================================================
export const HOPLITE_PROFILE: HeroAnimProfile = {
  name: 'hoplite',

  // --- ATTACK: "Affondo di Falange" ---------------------------------------
  // Motion split (post-fix thrust lineare):
  //   - INTERNO (HeroHopliteRig): solo rotazioni piccole (±8°) → braccio
  //     resta quasi orizzontale, la spalla non si stacca MAI dal torso.
  //   - ESTERNO (qui): body push forward ampliato a ~8% size → il thrust
  //     visibile è dato dallo spostamento del corpo intero, non dal braccio
  //     che si abbassa. Questo è anatomicamente ciò che fa un oplita: il
  //     corpo spinge, la lancia va in linea col bersaglio.
  //
  // Il shift di 8% resta sotto la soglia di drift percepibile perché torna
  // a 0 nel RITORNO (300ms easeOut), e il size del sprite in battle è
  // limitato da tankSize ≤ ~150 quindi 8% = max ~12px visivi = shift
  // disciplinato, non un dash.
  attack: (h, c) => {
    const RETR_BACK = Math.round(c.size * 0.025);  // micro step back nel wind-up
    const THRUST_FWD = Math.round(c.size * 0.08);   // body push forward al thrust
    h.transX.value = withSequence(
      withTiming(-c.dir * RETR_BACK,  { duration: 150, easing: Easing.out(Easing.quad) }),
      withTiming(c.dir * THRUST_FWD,  { duration: 160, easing: Easing.in(Easing.cubic) }),
      withTiming(c.dir * THRUST_FWD,  { duration: 90 }),   // hold al max
      withTiming(0,                   { duration: 300, easing: Easing.out(Easing.quad) }),
    );
    h.spriteScale.value = withSequence(
      withTiming(0.98, { duration: 150 }),  // micro crouch
      withTiming(1.05, { duration: 160 }),  // stretch forward (peso sul colpo)
      withTiming(1.04, { duration: 90 }),
      withTiming(1,    { duration: 300 }),
    );
    h.bodyRot.value = withTiming(0, { duration: 200 });
  },

  // --- SKILL "GUARDIA FERREA": Iron defensive stance ----------------------
  // Difensiva, non offensiva. L'oplita pianta i piedi e alza lo scudo
  // mentre un singolo pulse metallico illumina lo scudo.
  //
  // Timing (totale ~1050ms):
  //   ANC 180ms  → anchor (wrapper: crouch + peso al suolo; rig: scudo su)
  //   HLD 600ms  → hold (posa tenuta + SINGLE shield pulse a metà)
  //   REL 270ms  → release (ritorno morbido)
  //
  // Vincoli dall'UX brief:
  //   - NESSUNO step-back visibile → transX stays at 0 per tutto il tempo
  //   - Singolo pulse più marcato (non doppio)
  //   - Lancia sobria (gestita nel rig: +4°, non protagonista)
  //   - Hoplite deve "piantarsi", non fare un passo
  skill: (h, c) => {
    const ANC = 180;
    const HLD = 600;
    const REL = 270;
    const SINK = Math.round(c.size * 0.02);  // micro-crouch "piantato"

    // HORIZONTAL MOVEMENT — ZERO. La skill è radicata al suolo.
    // Cancella qualsiasi residuo e forza a 0.
    h.transX.value = withTiming(0, { duration: 80 });

    // VERTICAL — crouch leggero, hold, ritorno.
    h.transY.value = withSequence(
      withTiming(SINK, { duration: ANC, easing: Easing.out(Easing.quad) }),
      withTiming(SINK, { duration: HLD }),
      withTiming(0,    { duration: REL, easing: Easing.out(Easing.quad) }),
    );

    // BODY SCALE — peso al suolo (0.98) durante anchor+hold, poi torno a 1.
    h.spriteScale.value = withSequence(
      withTiming(0.98, { duration: ANC }),
      withTiming(0.98, { duration: HLD }),
      withTiming(1,    { duration: REL }),
    );

    // --- SHIELD PULSE — singolo, marcato, a metà hold ---------------------
    // Timing: parte 170ms dentro l'HOLD (t ≈ 350ms dall'inizio skill) →
    // è il punto di max lettura della posa difensiva.
    // Forma: ramp-up 150ms → decay 330ms → fade finale col release.
    const PULSE_DELAY = ANC + 170;  // 350ms dall'inizio

    h.auraOp.value = withSequence(
      withDelay(PULSE_DELAY, withTiming(0.7, { duration: 150, easing: Easing.out(Easing.quad) })),
      withTiming(0.1, { duration: 280 }),
      withTiming(0,   { duration: REL }),
    );
    h.auraSc.value = withSequence(
      withDelay(PULSE_DELAY, withTiming(1.5, { duration: 180, easing: Easing.out(Easing.quad) })),
      withTiming(1, { duration: 280 }),
    );
    // Brillio metallico sincronizzato col pulse (legge come "scudo scintilla")
    h.hitFlash.value = withSequence(
      withDelay(PULSE_DELAY, withTiming(0.25, { duration: 120 })),
      withTiming(0, { duration: 200 }),
    );

    // Nessuna rotazione globale del wrapper (le rotazioni sono per-layer nel rig)
    h.bodyRot.value = withTiming(0, { duration: 200 });
  },

  ultimate: (h, c) => HOPLITE_PROFILE.skill(h, c),

  // --- HIT: Tank stagger solido -------------------------------------------
  // Minore knockback del default (tank piantato), bodyRot ridotto,
  // return con easing back leggero → sensazione di peso che recupera.
  hit: (h, c) => {
    const KNOCK = Math.round(c.size * 0.03);  // default era 0.05
    h.transX.value = withSequence(
      withTiming(-c.dir * KNOCK, { duration: 80 }),
      withTiming(0, { duration: 260, easing: Easing.out(Easing.back(1.5)) }),
    );
    h.hitFlash.value = withSequence(
      withTiming(0.5, { duration: 50 }),
      withTiming(0, { duration: 220 }),
    );
    h.spriteScale.value = withSequence(
      withTiming(0.96, { duration: 80 }),
      withTiming(1, { duration: 220 }),
    );
    // Rotazione ridotta a 2° (default era 4°) — il tank non "oscilla" molto
    h.bodyRot.value = withSequence(
      withTiming(-c.dir * 2, { duration: 80 }),
      withTiming(0, { duration: 220 }),
    );
  },

  // --- DEATH: Kneel + collapse --------------------------------------------
  // Phase 1 (0→250ms): drop to knees → sink giù, leggera rotazione laterale
  // Phase 2 (350→900ms): collapse completo → cade di lato con forte
  //                      rotazione, scale si riduce, opacity fade pesante.
  // Il wrapper resta fermo, il character si "accascia" dentro la cella.
  death: (h, c) => {
    cancelAnimation(h.idleY);
    cancelAnimation(h.auraSc);
    cancelAnimation(h.auraOp);
    h.idleY.value = 0;
    // Sink + collapse (translateY positivo = scende verso il suolo)
    h.transY.value = withSequence(
      withTiming(Math.round(c.size * 0.05), { duration: 250 }),                     // kneel
      withDelay(100, withTiming(Math.round(c.size * 0.12), { duration: 500 })),      // collapse
    );
    // Forte rotazione finale: cade di lato (lean away dal centro)
    h.bodyRot.value = withSequence(
      withTiming((c.isEnemy ? -15 : 15), { duration: 250 }),
      withDelay(100, withTiming((c.isEnemy ? -35 : 35), { duration: 500 })),
    );
    // Shrink progressivo (anchor bottom → si accascia verso il basso)
    h.spriteScale.value = withSequence(
      withTiming(0.94, { duration: 250 }),
      withDelay(100, withTiming(0.80, { duration: 500 })),
    );
    // Opacity fade pesante
    h.spriteOp.value = withSequence(
      withTiming(0.7, { duration: 250 }),
      withDelay(100, withTiming(0.25, { duration: 600 })),
    );
    h.auraOp.value = withTiming(0, { duration: 350 });
  },

  heal: DEFAULT_PROFILE.heal,
  dodge: DEFAULT_PROFILE.dodge,
  idleReset: DEFAULT_PROFILE.idleReset,
};

// ==========================================================================
// RESOLVER — sceglie il profilo in base al character
// ==========================================================================
export function getAnimationProfile(character: any): HeroAnimProfile {
  const id = character?.hero_id || character?.id;
  const name = character?.hero_name || character?.name;
  if (isGreekHoplite(id, name)) return HOPLITE_PROFILE;
  // Tutti gli altri eroi mantengono il comportamento pre-esistente.
  return DEFAULT_PROFILE;
}
