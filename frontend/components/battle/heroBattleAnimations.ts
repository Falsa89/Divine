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
    // Float up-and-back: usiamo transY (combat motion) invece di idleY
    // (che non è più in loop). Coerente con la policy "no movimento
    // generico, solo stati approvati".
    h.transY.value = withSequence(
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
// GREEK HOPLITE PROFILE — 100% FRAME-BASED, ZERO WRAPPER MOTION
// --------------------------------------------------------------------------
// REGOLA DEFINITIVA (dall'utente):
//   Per Hoplite restano SOLO le animazioni approvate:
//     - idle   → HeroHopliteIdleLoop (crossfade 2 frame approvati)
//     - attack → HeroHopliteAffondo (8 frame Affondo di Falange)
//     - skill  → HeroHopliteGuardiaFerrea (6 frame Guardia Ferrea)
//   Tutti gli altri stati (hit / death / heal / dodge / ultimate) → STATICO.
//   Nessun fallback legacy, nessun bounce, nessun shake, nessuna hit reaction.
//
// ATTENZIONE: il wrapper motionStyle di BattleSprite applica
//   translateY = idleY + transY, scale = spriteScale, rotateZ = bodyRot,
//   opacity = spriteOp, ecc.
// Per garantire ZERO movimento parassita del wrapper su Hoplite, OGNI
// callback di questo profilo scrive valori neutri (0 o 1) ai shared
// values. I player frame-based interni (HeroHopliteIdleLoop /
// HeroHopliteAffondo / HeroHopliteGuardiaFerrea) sono gli unici
// responsabili di cosa si vede. Il wrapper resta congelato su Hoplite.
//
// Questo è l'equivalente di "no legacy interference":
//   - hit     → NO knockback, NO scale, NO rotation. Solo hitFlash molto
//               sottile (overlay di colore sull'immagine, non transform)
//               per leggere comunque la causalità del damage.
//   - death   → NO rotation, NO collapse. Solo opacity fade (la death
//               proper arriverà quando l'utente fornirà le reference).
//   - heal    → NO float. Solo micro aura boost.
//   - dodge   → NO side-step, NO opacity blink. Statico.
//   - ultimate → NO wrapper motion. (L'ultimate ha la propria overlay
//               cut-in gestita da combat.tsx, non dal wrapper sprite.)
// ==========================================================================
const HOPLITE_STATIC: (h: AnimHandles) => void = (h) => {
  // Reset istantaneo di TUTTI i shared values a valori neutri.
  // Cancella animazioni pendenti prima, per evitare che un tween
  // vecchio continui a muovere il wrapper dopo il reset.
  cancelAnimation(h.transX);
  cancelAnimation(h.transY);
  cancelAnimation(h.bodyRot);
  cancelAnimation(h.spriteScale);
  cancelAnimation(h.spriteOp);
  cancelAnimation(h.auraSc);
  cancelAnimation(h.auraOp);
  cancelAnimation(h.hitFlash);
  cancelAnimation(h.idleY);
  h.transX.value = 0;
  h.transY.value = 0;
  h.bodyRot.value = 0;
  h.spriteScale.value = 1;
  h.spriteOp.value = 1;
  h.auraSc.value = 1;
  h.auraOp.value = 0;
  h.hitFlash.value = 0;
  h.idleY.value = 0;
};

export const HOPLITE_PROFILE: HeroAnimProfile = {
  name: 'hoplite',

  // idleReset: reset totale a neutro (usato al ritorno a idle).
  idleReset: HOPLITE_STATIC,

  // attack: NO-OP. La vera animazione è in HeroHopliteAffondo.
  attack: HOPLITE_STATIC,

  // skill: NO-OP. La vera animazione è in HeroHopliteGuardiaFerrea.
  skill: HOPLITE_STATIC,

  // ultimate: NO-OP (per ora). L'ultimate vero arriverà quando l'utente
  // approverà la reference. NESSUN fallback al branch skill/attack.
  ultimate: HOPLITE_STATIC,

  // hit: NO-OP. Nessun knockback, nessun bounce, nessuna rotation, nessuno
  // shake. L'hit reaction "vera" sarà frame-based e si aggiungerà quando
  // l'utente approverà i frame hit. Fino ad allora, Hoplite resta
  // visivamente invariato quando riceve un colpo. Il damage number
  // floating (+NNN / -NNN overlay) e lo screen shake globale continuano
  // a essere gestiti da combat.tsx → causalità comunque leggibile.
  hit: HOPLITE_STATIC,

  // death: NO-OP. Nessun collapse, nessuna rotation, nessun sink. La
  // death reaction "vera" sarà frame-based. Per ora, Hoplite resta
  // statico nella sua cella anche se è KO. (Il flag is_alive è gestito
  // separatamente per logica di targeting.) Quando l'utente approverà
  // i frame death, aggiorneremo questo stato.
  death: HOPLITE_STATIC,

  // heal: NO-OP. Nessun float verso l'alto, nessun bob.
  heal: HOPLITE_STATIC,

  // dodge: NO-OP. Nessun side-step, nessun blink di opacity.
  dodge: HOPLITE_STATIC,
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
