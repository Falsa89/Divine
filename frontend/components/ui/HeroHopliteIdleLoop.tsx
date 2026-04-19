/**
 * HeroHopliteIdleLoop — IDLE FRAME-BASED ANIMATO
 * ================================================
 *
 * Player idle per Greek Hoplite: loop sobrio a 2 frame reference-approved
 * con crossfade continuo e micro-breathing sul wrapper globale.
 *
 * FRAME USATI (reference-approved, da Affondo di Falange contact sheet):
 *   Frame A = HOPLITE_AFFONDO_ASSETS[0] — "IDLE entry snapshot"
 *             (posa base, guardia neutra)
 *   Frame B = HOPLITE_AFFONDO_ASSETS[7] — "IDLE finale (home)"
 *             (posa settle, stance post-attack)
 *
 * Tra i due frame c'è una micro-differenza di postura (stance leggermente
 * diversa). Alternandoli con crossfade lento simuliamo un respiro
 * disciplinato, senza lampeggi, senza snap.
 *
 * TIMING (loop totale 2800ms):
 *   - Frame A hold   :   0 → 1100ms  (opacity A=1, B=0)
 *   - Crossfade A→B  :  1100 → 1400ms (300ms smooth)
 *   - Frame B hold   :  1400 → 2500ms (opacity B=1, A=0)
 *   - Crossfade B→A  :  2500 → 2800ms (300ms smooth)
 *   - Loop
 *
 * MICRO-BREATHING (sobrio, disciplinato, applicato all'intero wrapper):
 *   - translateY sinusoidale ±2px (micro-lift del respiro)
 *   - scaleY 1.0 ↔ 1.012 (espansione toracica molto lieve)
 *   - Periodo 2800ms sincronizzato col crossfade
 *   - NB: è un transform del WRAPPER (unico Image intera), NON del rig
 *     frazionato. La silhouette resta un PNG completo e intero.
 *
 * POLICY (dall'utente):
 *  - NON lampeggiante
 *  - NON nervoso
 *  - NON snap
 *  - NON troppo vivo
 *  - Sobrio, leggero, continuo, stabile, disciplinato
 */
import React, { useEffect } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, useDerivedValue,
  withRepeat, withTiming, Easing,
} from 'react-native-reanimated';
import { HOPLITE_AFFONDO_ASSETS } from './hopliteAssetManifest';

const FRAME_A = HOPLITE_AFFONDO_ASSETS[0];   // IDLE entry (base)
const FRAME_B = HOPLITE_AFFONDO_ASSETS[7];   // IDLE settle (home)

// Canvas nativo (condiviso con Affondo/GuardiaFerrea)
const FRAME_W = 520;
const FRAME_H = 400;
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;

// Allineamento feet-to-ground (identico a Affondo/GuardiaFerrea)
const RIG_FEET_Y_NORM = 800 / 1024;
const RIG_BODY_H_NORM = 0.683;
const FRAME_BODY_H_PX = 341;

// Timing del loop (ms)
const LOOP_MS = 2800;
const HOLD_MS = 1100;
const FADE_MS = 300;

type Props = {
  size: number;
  /** Se false, mette in pausa il loop (es. quando il frame è coperto dall'attack). */
  animated?: boolean;
};

export default function HeroHopliteIdleLoop({ size, animated = true }: Props) {
  // ═══════════════════════════════════════════════════════════════════════
  // cycle: 0 → 1 linearmente su LOOP_MS, ripetuto all'infinito.
  // È la "fase del respiro" universale. Da cycle derivano via useDerivedValue
  // le opacità dei 2 frame e il micro-bob + scaleY sul wrapper.
  // ═══════════════════════════════════════════════════════════════════════
  const cycle = useSharedValue(0);
  useEffect(() => {
    cycle.value = 0;
    if (!animated) return;
    cycle.value = withRepeat(
      withTiming(1, { duration: LOOP_MS, easing: Easing.linear }),
      -1,
      false,
    );
  }, [animated]);

  // Opacità dei due frame — smooth crossfade senza mai entrambi a 0.
  // Convertiamo cycle [0..1] in segmenti: hold A → fade A→B → hold B → fade B→A
  const opacityA = useDerivedValue(() => {
    const t = cycle.value * LOOP_MS; // ms nel loop
    if (t < HOLD_MS) return 1;                                   // hold A
    if (t < HOLD_MS + FADE_MS) return 1 - (t - HOLD_MS) / FADE_MS; // fade A→B
    if (t < 2 * HOLD_MS + FADE_MS) return 0;                     // hold B
    return (t - 2 * HOLD_MS - FADE_MS) / FADE_MS;                // fade B→A
  });
  const opacityB = useDerivedValue(() => 1 - opacityA.value);

  // Micro-breathing sinusoidale sul wrapper (unica immagine → frame-based puro).
  // breath ∈ [-1, 1], periodo = LOOP_MS.
  const breath = useDerivedValue(() => Math.sin(cycle.value * Math.PI * 2));

  // ═══════════════════════════════════════════════════════════════════════
  // Container style (transform del singolo asset-frame wrapper).
  //
  // RIMOSSO il translateY breathing: l'utente riportava "il personaggio
  // saltella sulla posizione". Un translateY ±2px a 2.8s loop produce
  // proprio quel micro-bob verticale del contenitore → sembra che il
  // personaggio saltelli in place.
  //
  // TENIAMO SOLO scaleY sottile (±0.8%): è un'espansione verticale
  // IN-PLACE (non muove il baseline). Il personaggio non sale/scende,
  // si espande-contrae leggermente → respiro disciplinato, NO saltello.
  //
  // La vera animazione percepita resta il CROSSFADE tra FRAME_A e
  // FRAME_B che cambia la posa ogni ~1.4 secondi.
  // ═══════════════════════════════════════════════════════════════════════
  const containerStyle = useAnimatedStyle(() => ({
    transform: [
      { scaleY: 1 + 0.008 * breath.value },    // ±0.8% espansione sottile
      { scaleX: -1 },                          // facing (coerente con Affondo/Guardia)
    ],
  }));

  const frameAStyle = useAnimatedStyle(() => ({ opacity: opacityA.value }));
  const frameBStyle = useAnimatedStyle(() => ({ opacity: opacityB.value }));

  // Geometria di rendering (identica a Affondo/GuardiaFerrea).
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
      <Animated.View style={[
        {
          position: 'absolute',
          top: boxTop,
          left: boxLeft,
          width: renderedW,
          height: renderedH,
        },
        containerStyle,
      ]}>
        {/* Frame A — idle base (opacità gestita dall'animazione di crossfade). */}
        <Animated.View style={[StyleSheet.absoluteFillObject, frameAStyle]}>
          <Image
            source={FRAME_A}
            style={{ width: renderedW, height: renderedH }}
            resizeMode="contain"
            fadeDuration={0}
          />
        </Animated.View>
        {/* Frame B — idle settle (opacità complementare). */}
        <Animated.View style={[StyleSheet.absoluteFillObject, frameBStyle]}>
          <Image
            source={FRAME_B}
            style={{ width: renderedW, height: renderedH }}
            resizeMode="contain"
            fadeDuration={0}
          />
        </Animated.View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },
});
