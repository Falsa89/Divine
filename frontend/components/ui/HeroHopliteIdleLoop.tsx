/**
 * HeroHopliteIdleLoop — IDLE FRAME-BASED (HARD SWAP, NO GHOSTING)
 * ================================================================
 *
 * Usa i 5 frame idle DEDICATI (idle_01..idle_05.png). Loop a 5 fasi con
 * SWAP FRAME NETTI — NESSUN CROSSFADE DI OPACITY.
 *
 * Solo UN frame alla volta è visibile (opacity 1). Gli altri frame non
 * vengono nemmeno renderizzati → zero doppia silhouette, zero alone.
 *
 * TIMING (cycle totale ~3000ms):
 *   frame #i visibile per 3000/5 = 600ms ciascuno, in loop.
 *
 * RENDERING:
 *  - Un solo <Image> attivo, sorgente swappata via state.
 *  - Nessun translateY / scaleY / breathing → frame è unica fonte di movimento.
 *  - scaleX: -1 per facing coerente con Affondo/GuardiaFerrea.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { HOPLITE_IDLE_ASSETS } from './hopliteAssetManifest';

const FRAMES = HOPLITE_IDLE_ASSETS;          // 5 frame idle dedicati
const N = FRAMES.length;                      // 5
const FRAME_MS = 600;                         // 600ms per frame (loop totale 3s)

// Canvas nativo dei frame idle (stesso sistema Affondo: 520×400, feet 260/390)
const FRAME_W = 520;
const FRAME_H = 400;
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;

// Allineamento feet-to-ground (identico a Affondo/GuardiaFerrea)
const RIG_FEET_Y_NORM = 800 / 1024;
const RIG_BODY_H_NORM = 0.683;
const FRAME_BODY_H_PX = 341;

type Props = {
  size: number;
  /** Se false, mette in pausa il loop (es. durante attack/skill). */
  animated?: boolean;
};

export default function HeroHopliteIdleLoop({ size, animated = true }: Props) {
  const [idx, setIdx] = useState(0);
  const idxRef = useRef(0);

  useEffect(() => {
    if (!animated) return;
    const id = setInterval(() => {
      idxRef.current = (idxRef.current + 1) % N;
      setIdx(idxRef.current);
    }, FRAME_MS);
    return () => clearInterval(id);
  }, [animated]);

  // Geometria
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
