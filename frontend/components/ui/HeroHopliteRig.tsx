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
  //
  // BUGFIX: prima usavo anche translateX sui layer (spearTX -180, torsoTX -14, ecc.)
  // ma questo staccava visivamente i layer tra loro (il pivot si sposta col
  // translate → la "spalla" di spear_arm non coincide più con quella del torso).
  // Fix: SOLO ROTAZIONI intorno ai pivot anatomici → i giunti restano
  // aderenti (una spalla ruota, non trasla). Per compensare ampiezza visiva,
  // aumentiamo le rotazioni E deleghiamo al wrapper esterno (BattleSprite
  // HOPLITE_PROFILE) uno shift del corpo intero → nessun detach perché tutti
  // i layer si muovono insieme solidali al wrapper.
  // =========================================================================
  const spearRot = useSharedValue(0);   // rotazione braccio lancia (alla spalla)
  const torsoRot = useSharedValue(0);   // rotazione torso (pivot bacino) — mantenuta piccola
  const shieldRot = useSharedValue(0);  // rotazione scudo (alla spalla dx)
  const headRot = useSharedValue(0);    // tilt testa/casco
  const skirtRot = useSharedValue(0);   // rotazione gonna (follow-through)

  // =========================================================================
  // ATTACK SEQUENCE — "Affondo di Falange" (solo rotazioni, no translate)
  // =========================================================================
  React.useEffect(() => {
    // Reset ad ogni cambio state per evitare accumulo drift.
    cancelAnimation(spearRot);
    cancelAnimation(torsoRot);
    cancelAnimation(shieldRot);
    cancelAnimation(headRot);
    cancelAnimation(skirtRot);

    if (state === 'attack') {
      const RETR = 150;   // Fase 1: Ritrazione
      const THRU = 160;   // Fase 2: Affondo
      const IMP  = 90;    // Fase 3: Impatto (hold)
      const RET  = 300;   // Fase 4: Ritorno in guardia

      // SPEAR ARM — solo rotazione attorno alla spalla sx (pivot 570, 390)
      //   ritrazione: +12° (braccio si alza un po', hand va leggermente indietro)
      //   affondo: -22° (forte rotazione forward, hand si abbassa e spinge avanti)
      //   impatto: -26° (hold massima rotazione)
      //   ritorno: 0 con easeOut
      // Nota: NESSUN translate → la spalla del layer coincide SEMPRE col pivot
      // anatomico (570, 390) che è la posizione della spalla sul torso.
      spearRot.value = withSequence(
        withTiming(12,  { duration: RETR, easing: Easing.out(Easing.quad) }),
        withTiming(-22, { duration: THRU, easing: Easing.in(Easing.cubic) }),
        withTiming(-26, { duration: IMP }),
        withTiming(0,   { duration: RET,  easing: Easing.out(Easing.quad) }),
      );

      // TORSO — rotazione microscopica (pivot bacino). Deliberatamente piccola
      // perché il torso ruota attorno al bacino MA la "spalla" del torso non
      // è nello stesso punto del pivot spear_arm → rotating troppo crea
      // disallineamento. ±1° è il limite sicuro.
      torsoRot.value = withSequence(
        withTiming(1,  { duration: RETR }),
        withTiming(-1, { duration: THRU }),
        withTiming(-1, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );

      // SHIELD ARM — piccola rotazione per brace/follow-up alla spalla dx
      shieldRot.value = withSequence(
        withTiming(-2, { duration: RETR }),
        withTiming(-5, { duration: THRU }),
        withTiming(-4, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );

      // HEAD — focus stabile sul target (tilt piccolo, disciplina tank)
      headRot.value = withSequence(
        withTiming(-2, { duration: RETR }),
        withTiming(-4, { duration: THRU }),
        withTiming(-3, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );

      // SKIRT — piccolo follow-through rotazione (pivot vita)
      skirtRot.value = withSequence(
        withTiming(1,  { duration: RETR }),
        withTiming(-2, { duration: THRU }),
        withTiming(-1, { duration: IMP }),
        withTiming(0,  { duration: RET }),
      );
    } else {
      // Tutti gli altri state: ritorno morbido a 0 (idle pulito).
      // Le altre animazioni di combat (skill/hit/dead) non sono implementate
      // nel rig in questo step — saranno aggiunte nei prossimi task.
      const D = 200;
      spearRot.value = withTiming(0, { duration: D });
      torsoRot.value = withTiming(0, { duration: D });
      shieldRot.value = withTiming(0, { duration: D });
      headRot.value = withTiming(0, { duration: D });
      skirtRot.value = withTiming(0, { duration: D });
    }
  }, [state]);

  // =========================================================================
  // STYLES PER-LAYER — idle baseline + combat delta (SOLO ROTAZIONI)
  // Gli idle translate (hair sway, shield phase) sono mantenuti molto piccoli
  // (±1.5px) perché fanno parte del respiro: impercettibili come detach.
  // I combat deltas sono TUTTI rotazioni sui pivot anatomici → no detach.
  // =========================================================================

  // TORSO: scaleY respiro + rotazione combat minima (pivot bacino)
  const torsoStyle = useAnimatedStyle(() => {
    const s = 1 + 0.015 * breath.value;
    return {
      transform: [
        { translateY: -0.8 * breath.value },
        { rotate: `${torsoRot.value}deg` },
        { scaleY: s },
      ],
    };
  });

  // HEAD GROUP (head_helmet + hair): idle sway + tilt combat
  const headGroupStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 1.5 * hairPhase.value },    // idle sway — ±1.5px invisibile
      { translateY: -1.6 * breath.value },
      { rotate: `${0.6 * hairPhase.value + headRot.value}deg` },
    ],
  }));

  // SHIELD ARM: idle sway + rotazione brace alla spalla dx
  const shieldStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 0.6 * shieldPhase.value },  // idle sway ±0.6px
      { translateY: 1.0 * shieldPhase.value },
      { rotate: `${0.5 * shieldPhase.value + shieldRot.value}deg` },
    ],
  }));

  // SPEAR ARM: protagonista — SOLO ROTAZIONE alla spalla sx (pivot 570, 390).
  // Nessun translate → la spalla del layer resta esattamente sul pivot
  // anatomico (coincidente con la spalla del torso). Il braccio ruota
  // solidale, la connessione alla spalla è preservata in ogni frame.
  const spearStyle = useAnimatedStyle(() => ({
    transform: [
      { translateY: -0.4 * breath.value },  // solo respiro (micro)
      { rotate: `${spearRot.value}deg` },
    ],
  }));

  // SKIRT: idle sway + piccola rotazione follow-through
  const skirtStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 0.6 * hairPhase.value },   // idle sway
      { translateY: -0.3 * breath.value },
      { rotate: `${skirtRot.value}deg` },
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
