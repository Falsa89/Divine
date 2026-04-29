import React from 'react';
import { View, Text, StyleSheet, Image, useWindowDimensions } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withSequence,
  withTiming,
  Easing,
  useDerivedValue,
  interpolate,
} from 'react-native-reanimated';

/**
 * HeroHopliteIdle
 * ----------------
 * Rig a layer separati del Greek Hoplite.
 * I layer sono ritagli pixel-exclusive di combat_base.png (1024x1024),
 * composti in ordine back → front con transform Reanimated per l'idle.
 *
 * Movimenti:
 *  - torso: scale Y leggero (respiro)
 *  - capelli: sway orizzontale
 *  - braccio scudo: micro oscillazione rotazionale + traslazione
 *  - braccio lancia: quasi fermo
 *  - gambe: completamente fisse
 *  - head/skirt: seguono il respiro del torso (solidali)
 *
 * Tutti i layer hanno size = canvas base (1024x1024) e position:absolute(0,0).
 * Il rig intero viene scalato tramite la prop `size` (default 256).
 */

const BASE = 1024;

// Ogni layer ha un pivot (relativo al canvas 1024x1024) e il render order
// (back → front: hair, legs, skirt, torso, shield_arm, spear_arm, head_helmet)
const LAYERS = [
  {
    key: 'hair',
    src: require('../../assets/heroes/greek_hoplite/rig/hair.png'),
    pivot: { x: 625, y: 235 },
  },
  {
    key: 'legs',
    src: require('../../assets/heroes/greek_hoplite/rig/legs.png'),
    pivot: { x: 690, y: 800 },
  },
  {
    key: 'skirt',
    src: require('../../assets/heroes/greek_hoplite/rig/skirt.png'),
    pivot: { x: 660, y: 690 },
  },
  {
    key: 'torso',
    src: require('../../assets/heroes/greek_hoplite/rig/torso.png'),
    pivot: { x: 640, y: 540 }, // bacino = pivot del respiro
  },
  {
    key: 'shield_arm',
    src: require('../../assets/heroes/greek_hoplite/rig/shield_arm.png'),
    pivot: { x: 700, y: 440 }, // spalla destra
  },
  {
    key: 'spear_arm',
    src: require('../../assets/heroes/greek_hoplite/rig/spear_arm.png'),
    pivot: { x: 570, y: 390 }, // spalla sinistra
  },
  {
    key: 'head_helmet',
    src: require('../../assets/heroes/greek_hoplite/rig/head_helmet.png'),
    pivot: { x: 610, y: 245 }, // base del collo
  },
];

type Props = {
  size?: number; // dimensione renderizzata (lato), default 256
  animated?: boolean;
};

export default function HeroHopliteIdle({ size = 256, animated = true }: Props) {
  const scale = size / BASE;

  // Shared value: progress del ciclo idle in [0, 1] poi ripetuto
  const cycle = useSharedValue(0);

  React.useEffect(() => {
    if (!animated) return;
    cycle.value = 0;
    // Linear cycle 0→1 ripetuto; le funzioni sin() sotto creano l'oscillazione morbida
    cycle.value = withRepeat(
      withTiming(1, { duration: 2500, easing: Easing.linear }),
      -1,
      false
    );
  }, [animated, cycle]);

  // Derivo seno/coseno per i vari movimenti
  // cycle 0..1 → theta 0..2π
  const breath = useDerivedValue(() =>
    Math.sin(cycle.value * Math.PI * 2)
  );
  const hairPhase = useDerivedValue(() =>
    Math.sin(cycle.value * Math.PI * 2 + Math.PI / 3)
  );
  const shieldPhase = useDerivedValue(() =>
    Math.sin(cycle.value * Math.PI * 2 - Math.PI / 4)
  );

  // --- STYLES per layer ---

  // Torso: scale Y sottile, pivot = bacino
  const torsoStyle = useAnimatedStyle(() => {
    const s = 1 + 0.015 * breath.value; // ±1.5% scale Y
    return {
      transform: [
        { translateY: -0.8 * breath.value },
        { scaleY: s },
      ],
    };
  });

  // HEAD GROUP (head_helmet + hair + plume): si muovono SOLIDALI con sway + respiro
  // Poiche' la segmentazione mette l'elmo nel layer hair, animando entrambi uguale
  // si ottiene un movimento visivamente corretto di tutta la testa.
  const headGroupStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 1.5 * hairPhase.value },
      { translateY: -1.6 * breath.value },
      { rotate: `${0.6 * hairPhase.value}deg` },
    ],
  }));

  // Braccio scudo: micro oscillazione rotazionale + traslazione (pivot sulla spalla destra)
  const shieldStyle = useAnimatedStyle(() => ({
    transform: [
      { translateY: 1.0 * shieldPhase.value },
      { translateX: 0.6 * shieldPhase.value },
      { rotate: `${0.5 * shieldPhase.value}deg` },
    ],
  }));

  // Braccio lancia: quasi fermo (movimento minimo solidale col respiro)
  const spearStyle = useAnimatedStyle(() => ({
    transform: [
      { translateY: -0.4 * breath.value },
    ],
  }));

  // Skirt: leggero ondeggio
  const skirtStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 0.6 * hairPhase.value },
      { translateY: -0.3 * breath.value },
    ],
  }));

  // Legs: FISSE (nessuna transform)

  const styleMap: Record<string, any> = {
    hair: headGroupStyle,           // <- stesso del head_helmet
    head_helmet: headGroupStyle,    // <- gruppo testa
    torso: torsoStyle,
    spear_arm: spearStyle,
    shield_arm: shieldStyle,
    skirt: skirtStyle,
    legs: null, // fisse
  };

  return (
    <View style={[styles.root, { width: size, height: size }]}>
      <View
        style={{
          width: BASE,
          height: BASE,
          transform: [{ scale }],
          transformOrigin: '0 0' as any,
        }}
      >
        {LAYERS.map(layer => {
          const animStyle = styleMap[layer.key];
          const pivotStyle = {
            transformOrigin: `${layer.pivot.x}px ${layer.pivot.y}px` as any,
          };
          // v16.12 — FRAME ANIMATION STANDARD (Safety Audit Pass)
          // ────────────────────────────────────────────────────────────────
          // Prima questo branch ritornava `<View>` quando !animated o
          // !animStyle, e `<Animated.View>` altrimenti. A parità di `key`,
          // React vede DUE TIPI DI COMPONENTE DIVERSI → quando il flag
          // `animated` flippa a runtime (es. HeroPortrait con animated
          // toggle, o pause), il sottoalbero — INCLUSA la <Image> figlia —
          // viene UNMOUNTATO/RIMONTATO. Stesso identico pattern del flicker
          // in battle (vedi HeroHopliteIdleLoop v16.12).
          // Soluzione safe: SEMPRE `<Animated.View>` con animStyle che cade
          // su `undefined` quando non animato → l'<Image> resta montata,
          // zero flash su toggle animated.
          return (
            <Animated.View
              key={layer.key}
              style={[
                styles.layer,
                animStyle ? pivotStyle : null,
                animated && animStyle ? animStyle : null,
              ]}
            >
              <Image
                source={layer.src}
                style={styles.layerImg}
                resizeMode="contain"
              />
            </Animated.View>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    overflow: 'hidden',
  },
  layer: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: BASE,
    height: BASE,
  },
  layerImg: {
    width: BASE,
    height: BASE,
  },
});
