/**
 * HeroHopliteIdleLoop — IDLE FRAME-BASED (HARD SWAP + SCALE ALIGNED)
 * ===================================================================
 *
 * Usa i 5 frame idle DEDICATI (idle_01..idle_05.png). Loop a 5 fasi con
 * SWAP FRAME NETTI — NESSUN CROSSFADE DI OPACITY.
 *
 * ANCHOR GEOMETRY (misurata dai PNG reali, non assunta):
 *   canvas: 520×400
 *   bbox corpo: (x:140..379, y:59..382)   → body_h = 323px
 *   feet Y:  382  (era 390 wrongly)
 *   body_h:  323  (era 341 wrongly → frame era ~5.3% più piccolo)
 *
 * Questi due valori sono la VERA ragione per cui l'idle risultava
 * visibilmente più piccolo dell'Affondo (che ha body_h=341 reali) e
 * leggermente più in basso.
 *
 * LEGGIBILITÀ:
 *  - Timing non-uniforme (emphasis su breath peak):
 *      #1 IDLE BASE     480ms   (baseline, pausa respiro)
 *      #2 BREATH IN     360ms   (transizione fluida)
 *      #3 BREATH PEAK   620ms   (KEY — posa caratteristica tenuta più a lungo)
 *      #4 SETTLE        360ms   (ritorno)
 *      #5 LOOP RETURN   480ms   (pre-loop)
 *    Total cycle: 2300ms (era 3000ms → più vivo).
 *  - Un solo <Image> renderizzato → zero ghosting, zero alone.
 *
 * Canvas/scale identici a Affondo/GuardiaFerrea → ZERO scatto quando
 * BattleSprite transiziona tra idle ↔ attack ↔ skill.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { HOPLITE_IDLE_ASSETS } from './hopliteAssetManifest';

const FRAMES = HOPLITE_IDLE_ASSETS;    // 5 frame idle dedicati

// Durate per-frame (ms) — non uniformi per enfatizzare breath peak
const FRAME_DURATIONS_MS = [
  480,  // #1 IDLE BASE
  360,  // #2 BREATH IN START
  620,  // #3 BREATH PEAK (key anchor)
  360,  // #4 SETTLE
  480,  // #5 LOOP RETURN
];

// Canvas nativo dei frame (520×400, feet baseline comune a tutta la suite)
const FRAME_W = 520;
const FRAME_H = 400;
// Feet Y REALE dei nuovi PNG idle rigenerati (allineato ad Affondo: 390)
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;

// Allineamento feet-to-ground (stesso schema di Affondo/GuardiaFerrea)
const RIG_FEET_Y_NORM = 800 / 1024;
const RIG_BODY_H_NORM = 0.683;
// Body height REALE dei nuovi PNG idle rigenerati: 341 (identica ad Affondo
// → zero differenza di scala tra idle/attack/skill).
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
