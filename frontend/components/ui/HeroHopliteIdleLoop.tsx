/**
 * HeroHopliteIdleLoop — IDLE FRAME-BASED (HARD SWAP, SHEET v3 DEFINITIVA)
 * =========================================================================
 *
 * Source of truth DEFINITIVA: idle sheet v3 approvata dall'utente
 * (layout 3 top-row + 2 bottom-row, 5 pose).
 *
 *   1. IDLE BASE          — (top-left)    spear al fianco rilassato
 *   2. BREATH IN START    — (top-center)  spear inizia a salire
 *   3. GUARD TIGHT PEAK   — (top-right)   spear FORWARD esteso (peak teso)
 *   4. SETTLE OPEN        — (bottom-left) stance apre, spear indietro
 *   5. LOOP RETURN        — (bottom-right) ritorno a IDLE BASE
 *
 * TIMING DEFINITIVO (richiesto utente Msg 512):
 *   Frame 1 → 520ms   (stabile — IDLE BASE)
 *   Frame 2 → 280ms   (transizione breath in)
 *   Frame 3 → 220ms   (PEAK TESO — il più corto, evita sensazione attack-like)
 *   Frame 4 → 320ms   (settle open)
 *   Frame 5 → 520ms   (stabile — pre-loop)
 *   Totale ciclo = 1860ms
 *
 * RENDERING:
 *  - Un solo <Image> renderizzato alla volta → ZERO ghosting.
 *  - Swap frame netti (setTimeout ricorsivo + state), NO crossfade opacity.
 *  - Nessun translateY / scaleY / bob wrapper.
 *  - scaleX: -1 per facing coerente con Affondo/GuardiaFerrea.
 *
 * GEOMETRIA (allineata ad Affondo/GuardiaFerrea):
 *   Canvas 520×400, feet anchor (260, 390), body_h = 341px esatto.
 *   → stessa presenza scenica, zero scatto su transizioni idle↔attack↔skill.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { HOPLITE_IDLE_ASSETS } from './hopliteAssetManifest';

const FRAMES = HOPLITE_IDLE_ASSETS;    // 5 frame idle (sheet v3 definitiva)

// Durate per-frame (ms) — DEFINITIVE da richiesta utente Msg 512
const FRAME_DURATIONS_MS = [
  520,  // #1 IDLE BASE
  280,  // #2 BREATH IN START
  220,  // #3 GUARD TIGHT PEAK (peak teso — più corto di tutti)
  320,  // #4 SETTLE OPEN
  520,  // #5 LOOP RETURN
];

// Canvas nativo dei frame (520×400, feet baseline comune alla suite)
const FRAME_W = 520;
const FRAME_H = 400;
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;

// Allineamento feet-to-ground (stesso schema di Affondo/GuardiaFerrea)
const RIG_FEET_Y_NORM = 800 / 1024;
const RIG_BODY_H_NORM = 0.683;
// Body height REALE dei PNG v3 = 341px (exact match con Affondo)
const FRAME_BODY_H_PX = 341;

type Props = {
  size: number;
  /** Se false, mette in pausa il loop (es. durante attack/skill). */
  animated?: boolean;
};

export default function HeroHopliteIdleLoop({ size, animated = true }: Props) {
  const [idx, setIdx] = useState(0);
  const idxRef = useRef(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!animated) {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      return;
    }
    let cancelled = false;
    const scheduleNext = () => {
      if (cancelled) return;
      const holdMs = FRAME_DURATIONS_MS[idxRef.current];
      timeoutRef.current = setTimeout(() => {
        if (cancelled) return;
        idxRef.current = (idxRef.current + 1) % FRAMES.length;
        setIdx(idxRef.current);
        scheduleNext();
      }, holdMs);
    };
    scheduleNext();
    return () => {
      cancelled = true;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [animated]);

  // Geometria (usa body_h e feet_cy REALI dei frame idle)
  const frameScale = (RIG_BODY_H_NORM * size) / FRAME_BODY_H_PX;
  const renderedH = FRAME_H * frameScale;
  const renderedW = FRAME_W * frameScale;
  const rigFeetYInCell  = RIG_FEET_Y_NORM * size;
  const frameFeetYInBox = FEET_CY_IN_FRAME * frameScale;
  const frameFeetXInBox = FEET_CX_IN_FRAME * frameScale;
  const boxTop  = rigFeetYInCell - frameFeetYInBox;
  const boxLeft = size / 2 - frameFeetXInBox;

  return (
    <View style={[styles.root, { width: size, height: size }]} pointerEvents="none">
      <View style={{
        position: 'absolute',
        top: boxTop,
        left: boxLeft,
        width: renderedW,
        height: renderedH,
        transform: [{ scaleX: -1 }],
      }}>
        {/* UN SOLO frame renderizzato alla volta → swap netto, zero ghosting */}
        <Image
          source={FRAMES[idx]}
          style={{ width: renderedW, height: renderedH }}
          resizeMode="contain"
          fadeDuration={0}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },
});
