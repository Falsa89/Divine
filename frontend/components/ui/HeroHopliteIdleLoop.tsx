/**
 * HeroHopliteIdleLoop — IDLE FRAME-BASED ANIMATO
 * ================================================
 *
 * Usa i 5 frame idle DEDICATI approvati (idle_01..idle_05.png), NON i
 * frame dell'Affondo. Loop a 5 fasi con crossfade smoothed.
 *
 * TIMING (cycle totale 3000ms):
 *   frame #1 hold+fade   0 → 600ms
 *   frame #2 hold+fade  600 → 1200ms
 *   frame #3 hold+fade 1200 → 1800ms
 *   frame #4 hold+fade 1800 → 2400ms
 *   frame #5 hold+fade 2400 → 3000ms
 *   → loop dal frame #1
 *
 * RENDERING:
 *  - Tutti i 5 Image sempre montati come overlay assoluti
 *  - Opacity gestita da useDerivedValue (blend crossfade lineare)
 *  - Nessun translateY sul wrapper → ZERO saltello
 *  - Nessun scaleY/breathing extra → frame è unica fonte di movimento
 *  - scaleX: -1 per facing coerente con Affondo/GuardiaFerrea
 *
 * Geometria identica a Affondo/GuardiaFerrea per transizioni seamless.
 */
import React, { useEffect } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, useDerivedValue,
  withRepeat, withTiming, Easing,
} from 'react-native-reanimated';
import { HOPLITE_IDLE_ASSETS } from './hopliteAssetManifest';

const FRAMES = HOPLITE_IDLE_ASSETS;          // 5 frame idle dedicati
const N = FRAMES.length;                      // 5
const LOOP_MS = 3000;                         // ciclo completo (~0.6s per frame)

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

/**
 * Blend opacity per il frame all'indice i.
 * Ciclo diviso in N segmenti uguali; in ogni segmento il frame attivo
 * fade-in (prima metà) e fade-out (seconda metà). Il frame successivo
 * fa il complementare → crossfade continuo senza mai frame scuri.
 */
function segmentOpacity(cyclePos: number, i: number): number {
  'worklet';
  const segLen = 1 / N;               // lunghezza segmento normalizzata
  const center = (i + 0.5) * segLen;  // centro del segmento i
  // distanza dal centro, con wrapping circolare (loop)
  let d = Math.abs(cyclePos - center);
  if (d > 0.5) d = 1 - d;
  // opacity = 1 al centro, 0 a segLen (fuori dal range)
  const t = 1 - (d / segLen);
  return Math.max(0, Math.min(1, t));
}

export default function HeroHopliteIdleLoop({ size, animated = true }: Props) {
  const cycle = useSharedValue(0);

  useEffect(() => {
    cycle.value = 0;
    if (!animated) return;
    cycle.value = withRepeat(
      withTiming(1, { duration: LOOP_MS, easing: Easing.linear }),
      -1, false,
    );
  }, [animated]);

  // Opacity per ogni frame (useDerivedValue × 5)
  const op0 = useDerivedValue(() => segmentOpacity(cycle.value, 0));
  const op1 = useDerivedValue(() => segmentOpacity(cycle.value, 1));
  const op2 = useDerivedValue(() => segmentOpacity(cycle.value, 2));
  const op3 = useDerivedValue(() => segmentOpacity(cycle.value, 3));
  const op4 = useDerivedValue(() => segmentOpacity(cycle.value, 4));

  const s0 = useAnimatedStyle(() => ({ opacity: op0.value }));
  const s1 = useAnimatedStyle(() => ({ opacity: op1.value }));
  const s2 = useAnimatedStyle(() => ({ opacity: op2.value }));
  const s3 = useAnimatedStyle(() => ({ opacity: op3.value }));
  const s4 = useAnimatedStyle(() => ({ opacity: op4.value }));
  const styles_arr = [s0, s1, s2, s3, s4];

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
        {FRAMES.map((src, i) => (
          <Animated.View key={i} style={[StyleSheet.absoluteFillObject, styles_arr[i]]}>
            <Image
              source={src}
              style={{ width: renderedW, height: renderedH }}
              resizeMode="contain"
              fadeDuration={0}
            />
          </Animated.View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },
});
