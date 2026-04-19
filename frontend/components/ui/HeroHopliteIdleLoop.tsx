/**
 * HeroHopliteIdleLoop — IDLE FRAME-BASED (HARD SWAP, REFERENCE v2)
 * ==================================================================
 *
 * Source of truth: nuova idle sheet approvata dall'utente (v2, 5 pose).
 *   1. IDLE BASE           — spear dietro, guardia neutra
 *   2. BREATH IN START     — spear scende laterale
 *   3. GUARD TIGHT PEAK    — spear forward, stance compatta (key peak)
 *   4. SETTLE OPEN         — spear torna laterale
 *   5. LOOP RETURN         — ritorno a IDLE BASE (loop seamless)
 *
 * TIMING (richiesto utente — frame 3 più corto per evitare sensazione attack-like):
 *   Frame 1 → 520ms   (stabile)
 *   Frame 2 → 360ms   (transizione)
 *   Frame 3 → 260ms   (peak breve, evita "attack-like")
 *   Frame 4 → 360ms   (transizione)
 *   Frame 5 → 520ms   (stabile, pre-loop)
 *   Totale ciclo = 2020ms
 *
 * RENDERING:
 *  - Un solo <Image> renderizzato alla volta → ZERO ghosting, ZERO alone.
 *  - Swap frame netti (setTimeout + state swap), NO opacity crossfade.
 *  - Nessun translateY / scaleY / bob wrapper.
 *  - scaleX: -1 per facing coerente con Affondo/GuardiaFerrea.
 *
 * GEOMETRIA (allineata ad Affondo/GuardiaFerrea):
 *   Canvas 520×400, feet anchor (260, 390), body_h reale = 341px.
 *   → stessa presenza scenica, zero scatto su transizioni idle↔attack↔skill.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { HOPLITE_IDLE_ASSETS } from './hopliteAssetManifest';

const FRAMES = HOPLITE_IDLE_ASSETS;    // 5 frame idle (sheet v2)

// Durate per-frame (ms) — da richiesta utente Msg 510
const FRAME_DURATIONS_MS = [
  520,  // #1 IDLE BASE
  360,  // #2 BREATH IN START
  260,  // #3 GUARD TIGHT PEAK  (più corto: evita sensazione attack-like)
  360,  // #4 SETTLE OPEN
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
// Body height REALE dei PNG v2 = 341px (esattamente come Affondo)
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
