/**
 * HeroHopliteAffondo
 * ===================
 * Frame-based player per l'attack "Affondo di Falange" di Greek Hoplite.
 * Usa gli 8 keyframe APPROVATI salvati in assets/heroes/greek_hoplite/affondo/.
 *
 * REFERENCE LOCKED: i frame sono la source of truth immutabile.
 * Questo player li swappa secondo il timing approvato. NON applica rotazioni
 * né trasformazioni al singolo frame → la silhouette resta esattamente
 * quella pittorica della reference.
 *
 * ─────────────────────────────────────────────────────────────────────────
 * PATTERN DI MOUNT STABILE (no "ricaricamento visivo")
 * ─────────────────────────────────────────────────────────────────────────
 * Questo componente è progettato per essere MONTATO UNA SOLA VOLTA per la
 * durata della battle (in overlay assoluto dentro HeroHopliteRig) e
 * controllato tramite la prop `active`:
 *  - `active=false` (default) → non avanza la sequenza, rimane fermo al
 *    frame 0 (o all'ultimo). Il componente RESTA montato, gli asset
 *    restano in memoria, nessun decode ripetuto.
 *  - `active=true` (transizione false→true) → resetta l'index a 0 e fa
 *    partire la sequenza cronometrata fino al settle. A fine sequenza
 *    chiama `onDone` (se presente) e si ferma sull'ultimo frame.
 *  - `active=true → false` (early stop) → clear timeout, nessun effetto
 *    visivo brutto perché il parent tipicamente lo nasconde via opacity.
 *
 * Vantaggi:
 *  - I 8 `require(...)` vengono risolti UNA volta al primo mount.
 *  - I PNG vengono decodati UNA volta (Image cache nativa + expo-asset).
 *  - Nessun unmount/mount → niente flash quando lo state di BattleSprite
 *    passa da 'attack' a 'idle' e viceversa.
 *
 * TIMING (totale ~800ms):
 *   #1 IDLE           0    → 0ms     (entry — snapshot, invisibile)
 *   #2 PRE-LOAD       0    → 90ms    (carica, spalla parte)
 *   #3 RITRAZIONE    90    → 200ms   (braccio si raccoglie indietro)
 *   #4 AFFONDO MID  200    → 300ms   (thrust parte, corpo avanti)
 *   #5 AFFONDO PEAK 300    → 420ms   (estensione massima)
 *   #6 IMPACT HOLD  420    → 560ms   (tenuta impatto, ~140ms)
 *   #7 RETURN MID   560    → 680ms   (rientro, corpo torna)
 *   #8 IDLE FINALE  680    → 800ms   (home, pronto per prossimo turno)
 *
 * Tutti i frame sono 384×900 RGBA con stesso ground baseline → nessuno
 * scatto verticale durante lo swap.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { HOPLITE_AFFONDO_ASSETS } from './hopliteAssetManifest';

// Require statico centralizzato nel manifest → il bundler risolve una sola volta.
const FRAMES = HOPLITE_AFFONDO_ASSETS;

// Durata (ms) di ciascun frame nella sequenza — cumulativi NO, ognuno ha
// la propria "hold duration". Somma: 90+110+100+120+140+120+120+120 = 920ms.
const FRAME_DURATIONS_MS = [
  90,   // #1 IDLE      (kickoff — 90ms)
  110,  // #2 PRE-LOAD
  100,  // #3 RITRAZIONE
  120,  // #4 AFFONDO MID
  140,  // #5 AFFONDO PEAK
  120,  // #6 IMPACT HOLD
  120,  // #7 RETURN MID
  120,  // #8 IDLE FINALE (settle)
];

// Dimensioni native dei frame (tutti uguali per costruzione).
// Canvas 520×400 con feet anchor a (260, 390) → piedi sempre in fondo-centro.
// Questo canvas include safe margin su TUTTI i lati → nessun clipping.
const FRAME_W = 520;
const FRAME_H = 400;
// Dove sono i piedi nel canvas del frame (usato per ground-align in render)
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;

type Props = {
  /** Dimensione quadrata della cella in px (come HeroHopliteRig) */
  size: number;
  /**
   * Gate di attivazione della sequenza. Transizione false→true = START.
   * Se omesso è `true` per retrocompatibilità con i preview isolati.
   */
  active?: boolean;
  /**
   * Chiave univoca per ogni invocazione dell'attack.
   * La sequenza parte UNA sola volta per ogni valore di playKey. Il parent
   * (HeroHopliteRig) incrementa playKey solo alla transizione
   * non-attack → attack, prevenendo doppi trigger causati da re-render
   * con `active: true → true` o microrimbalzi true→false→true.
   *
   * Se `playKey` resta costante, nessuna sequenza parte (anche se
   * `active` diventa true per errore).
   */
  playKey?: number;
  /** Callback opzionale a fine sequenza */
  onDone?: () => void;
};

export default function HeroHopliteAffondo({ size, active = true, playKey = 0, onDone }: Props) {
  const [index, setIndex] = useState(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Tracciamo l'ultimo playKey davvero eseguito → difesa contro
  // ri-esecuzione spuria (es. React fast-refresh in dev).
  const lastPlayedKeyRef = useRef<number | null>(null);

  // =========================================================================
  // SEQUENZA — parte SOLO quando playKey cambia E active=true.
  // Il pattern `playKey` garantisce:
  //  - UN solo playback per ogni invocazione logica dell'attack (anche se
  //    `active` oscilla per colpa di re-render spuri).
  //  - Nessun restart se il parent re-renderizza senza incrementare playKey.
  //  - Cleanup corretto quando playKey cambia prima che la seq sia finita
  //    (edge case improbabile: attack re-triggered a metà).
  // =========================================================================
  useEffect(() => {
    // Se active è false, cleanup e reset a frame 0 (ready for next play)
    if (!active) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      setIndex(0);
      return;
    }
    // Se abbiamo già eseguito questo esatto playKey, NON ripartire.
    if (lastPlayedKeyRef.current === playKey) return;
    lastPlayedKeyRef.current = playKey;

    let cancelled = false;
    let i = 0;

    const advance = () => {
      if (cancelled) return;
      setIndex(i);
      if (i >= FRAMES.length - 1) {
        timeoutRef.current = setTimeout(() => {
          if (!cancelled) onDone?.();
        }, FRAME_DURATIONS_MS[i]);
        return;
      }
      timeoutRef.current = setTimeout(() => {
        i += 1;
        advance();
      }, FRAME_DURATIONS_MS[i]);
    };

    advance();

    return () => {
      cancelled = true;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
    // Deps: playKey è il trigger univoco; active è letto dentro e abilita/
    // disabilita l'esecuzione. Non mettiamo `onDone` nelle deps per evitare
    // restart se il parent passa una closure nuova ad ogni render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playKey, active]);

  // =========================================================================
  // SCALE + POSITION per allineamento con HeroHopliteRig.
  // Obiettivo: feet del frame allineati ai feet del rig → ZERO scatto
  // quando BattleSprite passa da idle (rig) a attack (frame-based).
  // =========================================================================
  const RIG_FEET_Y_NORM = 800 / 1024;        // 0.781
  const RIG_BODY_H_NORM = 0.683;              // 700/1024 approx
  const FRAME_BODY_H_PX = 341;                // altezza corpo nativa nel frame

  const frameScale = (RIG_BODY_H_NORM * size) / FRAME_BODY_H_PX;
  const renderedH = FRAME_H * frameScale;
  const renderedW = FRAME_W * frameScale;

  const rigFeetYInCell   = RIG_FEET_Y_NORM * size;
  const frameFeetYInBox  = FEET_CY_IN_FRAME * frameScale;
  const frameFeetXInBox  = FEET_CX_IN_FRAME * frameScale;

  const boxTop  = rigFeetYInCell - frameFeetYInBox;  // solitamente ~0
  const boxLeft = size / 2 - frameFeetXInBox;         // center feet on cell

  return (
    <View style={[styles.root, { width: size, height: size }]} pointerEvents="none">
      <View style={{
        position: 'absolute',
        top: boxTop,
        left: boxLeft,
        width: renderedW,
        height: renderedH,
      }}>
        {/* v16.12 — RIMOSSA `key` per-frame: causava unmount/mount della
            <Image> ad ogni transizione di frame Affondo, generando il
            flicker percepito. Vedi commento esteso in HeroHopliteIdleLoop. */}
        <Image
          source={FRAMES[index]}
          style={{ width: renderedW, height: renderedH }}
          resizeMode="contain"
          // fadeDuration=0 previene il piccolo crossfade Android che può
          // aggiungere "lampeggio" tra frame consecutivi.
          fadeDuration={0}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },  // spear tip può estendersi fuori dalla cella
});
