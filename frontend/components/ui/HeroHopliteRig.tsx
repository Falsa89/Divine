/**
 * HeroHopliteRig
 * ---------------
 * Rig a layer del Greek Hoplite unificato per idle + attack (Affondo di Falange).
 * Usa gli stessi 7 layer PNG di HeroHopliteIdle con i medesimi pivot anatomici.
 *
 * FILOSOFIA
 *  - Gambe sempre FISSE (disciplina tank, silhouette stabile).
 *  - Torso, braccia e testa si muovono in modo controllato con pivot anatomici.
 *  - Idle breathing resta SEMPRE attivo in background; gli effetti combat
 *    sono DELTA additivi applicati on top → la respirazione non si spezza.
 *  - Niente deformazione dell'immagine intera — nessuna scala del sprite
 *    complessivo, solo transform per-layer.
 *  - Niente drift esterno: tutto il movimento è locale al rig.
 *
 * SISTEMA DI COORDINATE
 *  - canvas nativo 1024x1024
 *  - Hoplite nativamente guarda a SINISTRA (combat_base.png)
 *  - quindi "forward" (verso il nemico) in frame nativo = -X
 *  - il wrapper esterno di BattleSprite applica scaleX=-1 per team player
 *    → flip visivo: quando usato nel campo, il thrust va verso destra
 *
 * ANIMAZIONE ATTACK — "AFFONDO DI FALANGE" (~700ms totali)
 *   Fase 1: RITRAZIONE    (150ms) — spear_arm +X (indietro), rot CCW, torso rot back
 *   Fase 2: AFFONDO       (160ms) — spear_arm thrust -X forward, torso rot forward
 *   Fase 3: IMPATTO       (90ms)  — hold estremo posizione thrust
 *   Fase 4: RITORNO GUARDIA (300ms) — tutto a 0 con easing out
 */
import React from 'react';
import { View, Image, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, useDerivedValue,
  withRepeat, withSequence, withTiming, withDelay,
  cancelAnimation, Easing,
} from 'react-native-reanimated';

const BASE = 1024;

const LAYERS = [
  { key: 'hair',        src: require('../../assets/heroes/greek_hoplite/rig/hair.png'),        pivot: { x: 625, y: 235 } },
  { key: 'legs',        src: require('../../assets/heroes/greek_hoplite/rig/legs.png'),        pivot: { x: 690, y: 800 } },
  { key: 'skirt',       src: require('../../assets/heroes/greek_hoplite/rig/skirt.png'),       pivot: { x: 660, y: 690 } },
  { key: 'torso',       src: require('../../assets/heroes/greek_hoplite/rig/torso.png'),       pivot: { x: 640, y: 540 } }, // bacino
  { key: 'shield_arm',  src: require('../../assets/heroes/greek_hoplite/rig/shield_arm.png'),  pivot: { x: 700, y: 440 } }, // spalla dx
  { key: 'spear_arm',   src: require('../../assets/heroes/greek_hoplite/rig/spear_arm.png'),   pivot: { x: 570, y: 390 } }, // spalla sx
  { key: 'head_helmet', src: require('../../assets/heroes/greek_hoplite/rig/head_helmet.png'), pivot: { x: 610, y: 245 } }, // base collo
];

export type HopliteRigState = 'idle' | 'attack' | 'skill' | 'hit' | 'dead' | 'heal' | 'dodge';

type Props = {
  size: number;
  state?: HopliteRigState;
  /** Disabilita il breathing idle (es. morte). Default true. */
  animated?: boolean;
};

export default function HeroHopliteRig({ size, state = 'idle', animated = true }: Props) {
  const scale = size / BASE;

  // =========================================================================
  // IDLE BASELINE — respirazione + sway capelli + oscillazione scudo
  // Continuano SEMPRE (anche durante l'attack) perché la vita del personaggio
  // non deve "congelarsi" mentre colpisce.
  // =========================================================================
  const cycle = useSharedValue(0);
  React.useEffect(() => {
    if (!animated) return;
    cycle.value = 0;
    cycle.value = withRepeat(
      withTiming(1, { duration: 2500, easing: Easing.linear }),
      -1, false,
    );
  }, [animated]);
  const breath = useDerivedValue(() => Math.sin(cycle.value * Math.PI * 2));
  const hairPhase = useDerivedValue(() => Math.sin(cycle.value * Math.PI * 2 + Math.PI / 3));
  const shieldPhase = useDerivedValue(() => Math.sin(cycle.value * Math.PI * 2 - Math.PI / 4));

  // =========================================================================
  // COMBAT DELTAS — shared values dedicati all'attack
  // Valori in coordinate canvas 1024 (poi scalati da `scale`). Tutti a 0
  // significa idle puro. L'attack li anima in sequenza tramite withSequence
  // e poi torna a 0 (ritorno in guardia).
  // =========================================================================
  const spearTX = useSharedValue(0);    // translateX del braccio lancia (-= forward)
  const spearRot = useSharedValue(0);   // rotazione spalla lancia (gradi)
  const torsoTX = useSharedValue(0);    // translateX torso (push forward micro)
  const torsoRot = useSharedValue(0);   // rotazione torso (negativo = lean forward)
  const shieldRot = useSharedValue(0);  // rotazione scudo (-= brace in guardia)
  const shieldTX = useSharedValue(0);   // translateX scudo (segue il torso)
  const headRot = useSharedValue(0);    // tilt testa sul target
  const skirtTX = useSharedValue(0);    // follow-through gonna

  // =========================================================================
  // ATTACK SEQUENCE — "Affondo di Falange"
  // =========================================================================
  React.useEffect(() => {
    // Reset ad ogni cambio state per evitare accumulo drift.
    cancelAnimation(spearTX); cancelAnimation(spearRot);
    cancelAnimation(torsoTX); cancelAnimation(torsoRot);
    cancelAnimation(shieldRot); cancelAnimation(shieldTX);
    cancelAnimation(headRot); cancelAnimation(skirtTX);

    if (state === 'attack') {
      const RETR = 150;   // Fase 1: Ritrazione
      const THRU = 160;   // Fase 2: Affondo
      const IMP  = 90;    // Fase 3: Impatto (hold)
      const RET  = 300;   // Fase 4: Ritorno in guardia

      // SPEAR ARM — protagonista del movimento
      //   ritrazione: tira indietro (+X = backward, +rot = alza la punta)
      //   affondo:    spinge avanti (-X forte, rot decisa verso orizzontale)
      //   impatto:    posizione di massimo allungamento, piccolo hold
      //   ritorno:    elastico out.quad al punto 0
      spearTX.value = withSequence(
        withTiming(70,   { duration: RETR, easing: Easing.out(Easing.quad) }),
        withTiming(-180, { duration: THRU, easing: Easing.in(Easing.cubic) }),
        withTiming(-200, { duration: IMP }),
        withTiming(0,    { duration: RET,  easing: Easing.out(Easing.quad) }),
      );
      spearRot.value = withSequence(
        withTiming(8,  { duration: RETR }),   // punta in alto in ritrazione
        withTiming(-3, { duration: THRU }),   // orizzontale durante il thrust
        withTiming(-4, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );

      // TORSO — accompagna il thrust ma senza esagerare (disciplina)
      //   lean forward 4° + micro push 14px
      torsoRot.value = withSequence(
        withTiming(2,  { duration: RETR }),
        withTiming(-4, { duration: THRU }),
        withTiming(-3, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );
      torsoTX.value = withSequence(
        withTiming(4,   { duration: RETR }),
        withTiming(-14, { duration: THRU }),
        withTiming(-12, { duration: IMP }),
        withTiming(0,   { duration: RET }),
      );

      // SHIELD ARM — resta in guardia ma segue il torso (brace leggero)
      shieldRot.value = withSequence(
        withTiming(-3, { duration: RETR }),  // brace più stretto in ritrazione
        withTiming(-5, { duration: THRU }),
        withTiming(-4, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );
      shieldTX.value = withSequence(
        withTiming(-2, { duration: RETR }),
        withTiming(-6, { duration: THRU }),
        withTiming(-5, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );

      // HEAD — focus stabile sul target (tilt piccolo, disciplina)
      headRot.value = withSequence(
        withTiming(-2, { duration: RETR }),
        withTiming(-3, { duration: THRU }),
        withTiming(-2, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );

      // SKIRT — piccolo follow-through (inerzia panno)
      skirtTX.value = withSequence(
        withTiming(3,  { duration: RETR }),
        withTiming(-5, { duration: THRU }),
        withTiming(-3, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );
    } else {
      // Tutti gli altri state: ritorno morbido a 0 (idle pulito).
      // Le altre animazioni di combat (skill/hit/dead) non sono implementate
      // nel rig in questo step — saranno aggiunte nei prossimi task.
      const D = 200;
      spearTX.value = withTiming(0, { duration: D });
      spearRot.value = withTiming(0, { duration: D });
      torsoTX.value = withTiming(0, { duration: D });
      torsoRot.value = withTiming(0, { duration: D });
      shieldRot.value = withTiming(0, { duration: D });
      shieldTX.value = withTiming(0, { duration: D });
      headRot.value = withTiming(0, { duration: D });
      skirtTX.value = withTiming(0, { duration: D });
    }
  }, [state]);

  // =========================================================================
  // STYLES PER-LAYER — idle baseline + combat delta
  // =========================================================================

  // TORSO: scale Y respiro + combat lean/push
  const torsoStyle = useAnimatedStyle(() => {
    const s = 1 + 0.015 * breath.value;
    return {
      transform: [
        { translateX: torsoTX.value },
        { translateY: -0.8 * breath.value },
        { rotate: `${torsoRot.value}deg` },
        { scaleY: s },
      ],
    };
  });

  // HEAD GROUP (head_helmet + hair): segue idle + tilt combat
  const headGroupStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 1.5 * hairPhase.value + torsoTX.value * 0.8 },
      { translateY: -1.6 * breath.value },
      { rotate: `${0.6 * hairPhase.value + headRot.value}deg` },
    ],
  }));

  // SHIELD ARM: idle sway + combat brace
  const shieldStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 0.6 * shieldPhase.value + shieldTX.value },
      { translateY: 1.0 * shieldPhase.value },
      { rotate: `${0.5 * shieldPhase.value + shieldRot.value}deg` },
    ],
  }));

  // SPEAR ARM: protagonista dell'attack
  const spearStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: spearTX.value },
      { translateY: -0.4 * breath.value },
      { rotate: `${spearRot.value}deg` },
    ],
  }));

  // SKIRT: idle + follow-through
  const skirtStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 0.6 * hairPhase.value + skirtTX.value },
      { translateY: -0.3 * breath.value },
    ],
  }));

  // LEGS: FISSE (disciplina tank)
  const styleMap: Record<string, any> = {
    hair:        headGroupStyle,
    head_helmet: headGroupStyle,
    torso:       torsoStyle,
    spear_arm:   spearStyle,
    shield_arm:  shieldStyle,
    skirt:       skirtStyle,
    legs:        null,
  };

  return (
    <View style={[styles.root, { width: size, height: size }]}>
      <View style={{ width: BASE, height: BASE, transform: [{ scale }], transformOrigin: '0 0' as any }}>
        {LAYERS.map(layer => {
          const animStyle = styleMap[layer.key];
          const pivotStyle = { transformOrigin: `${layer.pivot.x}px ${layer.pivot.y}px` as any };
          const content = (
            <Image source={layer.src} style={styles.layerImg} resizeMode="contain" />
          );
          if (!animStyle) {
            return (<View key={layer.key} style={styles.layer}>{content}</View>);
          }
          return (
            <Animated.View key={layer.key} style={[styles.layer, pivotStyle, animStyle]}>
              {content}
            </Animated.View>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'hidden' },
  layer: {
    position: 'absolute',
    top: 0, left: 0,
    width: BASE, height: BASE,
  },
  layerImg: {
    width: BASE, height: BASE,
  },
});
