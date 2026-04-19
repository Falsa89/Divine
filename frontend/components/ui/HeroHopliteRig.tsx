/**
 * HeroHopliteRig
 * ---------------
 * Rig anatomico parent-child del Greek Hoplite.
 * Usa i 7 layer PNG originali + 5 helper rig_safe (underpaint).
 *
 * GERARCHIA (parent → child, composizione delle trasformazioni):
 *
 *   canvas (1024×1024, scale globale)
 *   ├── legs                                [foundation, static]
 *   └── pelvis  (breath translateY)
 *       ├── hip_fill                        [helper, static bridge]
 *       ├── skirt  (local sway, skirtRot@660,690)   [sibling del torso]
 *       └── torso  (torsoRot@640,540, breath scaleY)
 *           ├── hair            (headStyle, z-back, ereditata da torso)
 *           ├── torso image
 *           ├── under_arm_spear               [helper, child torso]
 *           ├── shoulder_shield_fill          [helper, child torso]
 *           ├── shield_arm  (shieldRot@700,440)
 *           ├── shoulder_spear_fill           [helper, child torso]
 *           ├── spear_arm   (spearRot@570,390)
 *           └── head_group  (headRot@620,280)
 *               ├── neck_fill                 [helper]
 *               └── head_helmet
 *
 * PROPRIETÀ GARANTITE
 *  - Se torso ruota 5°, TUTTE le braccia + testa ruotano insieme al torso
 *    (trasformazione ereditata), più la loro rotazione locale small-accent.
 *  - Se shield_arm ruota −6°, la spalla dx resta aderente al torso perché
 *    il pivot è applicato NEL frame già trasformato del torso.
 *  - Skirt segue il bacino (pelvis), NON il torso → stabilità tank.
 *  - Legs sono foundation rigida, mai animate.
 *  - Helper fills sono child del loro parent anatomico (torso/head) →
 *    si muovono CON la parte giusta, coprono le giunture in modo coerente.
 *
 * SISTEMA DI COORDINATE
 *  - canvas nativo 1024×1024
 *  - Hoplite nativamente guarda a SINISTRA
 *  - Ogni Animated.View è 1024×1024 absoluteFill → transformOrigin in
 *    coordinate canvas è identico a ogni livello di nesting.
 *  - BattleSprite esterno applica scaleX=-1 per team player.
 */
import React from 'react';
import { View, Image, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, useDerivedValue,
  withRepeat, withSequence, withTiming, withDelay,
  cancelAnimation, Easing,
} from 'react-native-reanimated';
import HeroHopliteAffondo from './HeroHopliteAffondo';

const BASE = 1024;

export type HopliteRigState = 'idle' | 'attack' | 'skill' | 'hit' | 'dead' | 'heal' | 'dodge' | 'stress';

type Props = {
  size: number;
  state?: HopliteRigState;
  /** Disabilita il breathing idle (es. morte). Default true. */
  animated?: boolean;
  /** Se false, NON renderizza gli helper safe (per confronto before/after). Default true. */
  safeFill?: boolean;
};

export default function HeroHopliteRig({
  size,
  state = 'idle',
  animated = true,
  safeFill = true,
}: Props) {
  // ───────────────────────────────────────────────────────────────────────
  // ATTACK OVERRIDE — frame-based sequence (reference LOCKED)
  // L'Affondo di Falange è stato approvato come sequenza pittorica di 8
  // keyframe. Durante state === 'attack' bypassiamo completamente il rig
  // anatomico e renderizziamo i frame swappati nei timing approvati.
  // Il rig anatomico resta attivo per tutti gli altri stati (idle, skill,
  // hit, dead, heal, dodge, stress).
  // ───────────────────────────────────────────────────────────────────────
  if (state === 'attack') {
    return <HeroHopliteAffondo size={size} />;
  }

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
      //
      // Design del gesto — "Affondo di falange":
      // il braccio NON cala in basso, resta quasi-orizzontale durante tutto
      // il thrust. Il movimento "forward" visibile è dato dal body push
      // esterno (wrapper transX nel HOPLITE_PROFILE.attack). Così il colpo
      // legge come affondo LINEARE disciplinato, non come sweep diagonale.
      //
      //   ritrazione: +8°  (spear tip si alza un po', classica "aim" falange)
      //   affondo mid: +2° (torna verso orizzontale, body inizia il push)
      //   affondo peak: -2° (orizzontale, lancia in linea col bersaglio)
      //   impatto: -4° (micro-dip hold, max forward)
      //   ritorno: 0° (home)
      //
      // Angoli volutamente ridotti (±8° max) → disciplina tank + spalla
      // sempre integra (nessun translate, pivot statico sulla spalla).
      spearRot.value = withSequence(
        withTiming(8,  { duration: RETR, easing: Easing.out(Easing.quad) }),
        withTiming(-2, { duration: THRU, easing: Easing.in(Easing.cubic) }),
        withTiming(-4, { duration: IMP }),
        withTiming(0,  { duration: RET, easing: Easing.out(Easing.quad) }),
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
    } else if (state === 'skill') {
      // =====================================================================
      // SKILL — "GUARDIA FERREA" (difensiva) — MASS-FIRST PASS
      // ---------------------------------------------------------------------
      // v2: ridotti drasticamente i delta per-layer per evitare la
      // "scomposizione" della silhouette. L'idea: il corpo intero si abbassa
      // + comprime (wrapper: sink + scale), e sopra questa massa c'è UN SOLO
      // piccolo accento (scudo che sale appena). Tutti gli altri layer
      // restano quasi-glued al corpo → silhouette compatta, lettura "chiuso
      // dietro lo scudo" invece di "rig che si apre".
      //
      // Timing invariato (~1050ms):
      //   ANC 180ms  → anchor (shield +crouch si attivano)
      //   HLD 600ms  → hold (posa tenuta + shield pulse via wrapper)
      //   REL 270ms  → release (ritorno morbido)
      //
      // Angoli v2 (mass-first):
      //   - shield   -6° (era -12°) → ancora protagonista ma spalla glued
      //   - spear    +1° (era +4°)  → quasi fermo, spalla sx glued
      //   - torso     0° (era -2°)  → rimossa, torso resta solidale braccia
      //   - head     -1° (era -4°)  → solo un accenno di focus
      //   - skirt     0° (era +1°)  → peso al suolo senza swing
      //
      // La massa la fa il wrapper (HOPLITE_PROFILE.skill): sink +3% + scale 0.96
      // → "il corpo si chiude" è il messaggio globale, non i layer che si
      // spostano l'uno dall'altro.
      // =====================================================================
      const ANC = 180;
      const HLD = 600;
      const REL = 270;

      // SPEAR ARM — quasi fermo (+1°), solo hint di raccolta
      spearRot.value = withSequence(
        withTiming(1,  { duration: ANC, easing: Easing.out(Easing.quad) }),
        withTiming(1,  { duration: HLD }),
        withTiming(0,  { duration: REL, easing: Easing.out(Easing.quad) }),
      );

      // SHIELD ARM — accento PRINCIPALE ma ridotto (-6°), la spalla non si
      // allontana più dal torso in modo visibile.
      shieldRot.value = withSequence(
        withTiming(-6, { duration: ANC, easing: Easing.out(Easing.quad) }),
        withTiming(-6, { duration: HLD }),
        withTiming(0,  { duration: REL, easing: Easing.out(Easing.quad) }),
      );

      // TORSO — FERMO. Se il torso ruota e le braccia ruotano su pivot
      // diversi, si apre la silhouette. Tieniamo torso solidale.
      torsoRot.value = withTiming(0, { duration: ANC });

      // HEAD — micro focus (-1°), quasi impercettibile ma aggiunge intenzione
      headRot.value = withSequence(
        withTiming(-1, { duration: ANC }),
        withTiming(-1, { duration: HLD }),
        withTiming(0,  { duration: REL }),
      );

      // SKIRT — nulla, peso al suolo è già gestito dal sink globale
      skirtRot.value = withTiming(0, { duration: ANC });
    } else if (state === 'stress') {
      // =====================================================================
      // STRESS POSE — solo per validazione visiva del rig pack animation-safe.
      // Applica rotazioni DELIBERATAMENTE grandi su tutti i layer mobili per
      // esporre potenziali gap delle giunture. Se i fill safe funzionano,
      // anche con questi angoli estremi non si deve vedere il vuoto dietro
      // spalle/collo/vita.
      // Angoli stress (volutamente sopra i limiti operativi delle skill reali):
      //   spear  -18° (grande apertura braccio lancia)
      //   shield -22° (shield braced high)
      //   torso   -4° (ruota leggermente)
      //   head    -8° (tilt evidente)
      //   skirt   +5°
      // =====================================================================
      const D = 220;
      spearRot.value  = withTiming(-18, { duration: D, easing: Easing.out(Easing.quad) });
      shieldRot.value = withTiming(-22, { duration: D, easing: Easing.out(Easing.quad) });
      torsoRot.value  = withTiming(-4,  { duration: D });
      headRot.value   = withTiming(-8,  { duration: D });
      skirtRot.value  = withTiming(5,   { duration: D });
    } else {
      // idle / hit / dead / heal / dodge: ritorno morbido a 0 (idle pulito).
      // Gli stati hit/dead/heal/dodge non sono ancora implementati nel rig.
      const D = 200;
      spearRot.value  = withTiming(0, { duration: D });
      torsoRot.value  = withTiming(0, { duration: D });
      shieldRot.value = withTiming(0, { duration: D });
      headRot.value   = withTiming(0, { duration: D });
      skirtRot.value  = withTiming(0, { duration: D });
    }
  }, [state]);

  // =========================================================================
  // STYLES PER-LAYER — parent-child chain.
  //
  // Gerarchia di trasformazioni ereditate:
  //   pelvis (breath)
  //     └─ skirt   (local sway + skirtRot)
  //     └─ torso   (torsoRot + breath scaleY)
  //          ├─ hair       (headStyle, z-back)
  //          ├─ shield_arm (shieldRot, child-of-torso)
  //          ├─ spear_arm  (spearRot,  child-of-torso)
  //          └─ head_group (headRot, z-front)
  //
  // Principio: ogni "accent" locale è PICCOLO perché la massa base è già
  // mossa dal parent. In passato i translate idle erano duplicati in ogni
  // layer (hair/spear/shield) perché non c'era gerarchia → ora si ereditano.
  // =========================================================================

  // PELVIS: respiro (traslazione molto piccola del bacino)
  const pelvisStyle = useAnimatedStyle(() => ({
    transform: [
      { translateY: -0.6 * breath.value },
    ],
  }));

  // TORSO: respiro scaleY + rotazione combat (pivot bacino 640,540).
  // Le braccia e la testa sono child e ereditano questa rotazione.
  const torsoStyle = useAnimatedStyle(() => {
    const s = 1 + 0.012 * breath.value;  // leggera espansione toracica
    return {
      transform: [
        { rotate: `${torsoRot.value}deg` },
        { scaleY: s },
      ],
    };
  });

  // SHIELD ARM — accento LOCALE alla spalla dx, applicato DOPO il transform
  // del torso. Se torso ruota 5°, shield ruota 5° + shieldRot locale.
  const shieldStyle = useAnimatedStyle(() => ({
    transform: [
      { rotate: `${0.3 * shieldPhase.value + shieldRot.value}deg` },
    ],
  }));

  // SPEAR ARM — accento LOCALE alla spalla sx, idem.
  const spearStyle = useAnimatedStyle(() => ({
    transform: [
      { rotate: `${spearRot.value}deg` },
    ],
  }));

  // HEAD GROUP — ruota al base collo (620, 280). Hair sway idle + headRot.
  // Applicato sia all'hair (z-back) sia all'head_helmet group (z-front).
  const headStyle = useAnimatedStyle(() => ({
    transform: [
      { rotate: `${0.5 * hairPhase.value + headRot.value}deg` },
    ],
  }));

  // SKIRT: sibling del torso, segue il BACINO (non il torso).
  // Idle sway micro + rotazione combat locale.
  const skirtStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 0.4 * hairPhase.value },
      { rotate: `${skirtRot.value}deg` },
    ],
  }));

  // ─── Utility: Animated layer wrapper con pivot canvas ─────────────────────
  const pivot = (x: number, y: number) =>
    ({ transformOrigin: `${x}px ${y}px` as any });

  // Static image layer (no transform). Used for legs and for helper fills
  // whose transform is inherited from the parent wrapper.
  const StaticImg: React.FC<{ src: any }> = ({ src }) => (
    <View style={styles.layer}>
      <Image source={src} style={styles.layerImg} resizeMode="contain" />
    </View>
  );

  // ─── Require map (comodità) ────────────────────────────────────────────────
  const A = {
    hair:                 require('../../assets/heroes/greek_hoplite/rig/hair.png'),
    legs:                 require('../../assets/heroes/greek_hoplite/rig/legs.png'),
    skirt:                require('../../assets/heroes/greek_hoplite/rig/skirt.png'),
    torso:                require('../../assets/heroes/greek_hoplite/rig/torso.png'),
    shield_arm:           require('../../assets/heroes/greek_hoplite/rig/shield_arm.png'),
    spear_arm:            require('../../assets/heroes/greek_hoplite/rig/spear_arm.png'),
    head_helmet:          require('../../assets/heroes/greek_hoplite/rig/head_helmet.png'),
    hip_fill:             require('../../assets/heroes/greek_hoplite/rig_safe/hip_fill.png'),
    under_arm_spear:      require('../../assets/heroes/greek_hoplite/rig_safe/under_arm_spear.png'),
    shoulder_shield_fill: require('../../assets/heroes/greek_hoplite/rig_safe/shoulder_shield_fill.png'),
    shoulder_spear_fill:  require('../../assets/heroes/greek_hoplite/rig_safe/shoulder_spear_fill.png'),
    neck_fill:            require('../../assets/heroes/greek_hoplite/rig_safe/neck_fill.png'),
  };

  return (
    <View style={[styles.root, { width: size, height: size }]}>
      <View style={{ width: BASE, height: BASE, transform: [{ scale }], transformOrigin: '0 0' as any }}>

        {/* ─── FOUNDATION: gambe fisse ─────────────────────────────────────── */}
        <StaticImg src={A.legs} />

        {/* ─── PELVIS group: breath, root dell'upper body ─────────────────── */}
        <Animated.View style={[styles.layer, pelvisStyle]}>

          {/* hip_fill: bridge vita (sibling di skirt/torso, static) */}
          {safeFill && <StaticImg src={A.hip_fill} />}

          {/* Skirt: sibling del torso (segue il bacino, NON il torso) */}
          <Animated.View style={[styles.layer, pivot(660, 690), skirtStyle]}>
            <StaticImg src={A.skirt} />
          </Animated.View>

          {/* Torso: parent di braccia + testa */}
          <Animated.View style={[styles.layer, pivot(640, 540), torsoStyle]}>

            {/* Hair al back del torso (z-lowest dentro torso), rotates con head */}
            <Animated.View style={[styles.layer, pivot(620, 280), headStyle]}>
              <StaticImg src={A.hair} />
            </Animated.View>

            {/* Torso image */}
            <StaticImg src={A.torso} />

            {/* Helper fills (child del torso: si muovono CON il torso) */}
            {safeFill && <StaticImg src={A.under_arm_spear} />}
            {safeFill && <StaticImg src={A.shoulder_shield_fill} />}

            {/* Shield arm: ruota alla spalla dx, dentro il frame torso */}
            <Animated.View style={[styles.layer, pivot(700, 440), shieldStyle]}>
              <StaticImg src={A.shield_arm} />
            </Animated.View>

            {/* Fill dietro spalla sx (sotto spear_arm ma sopra torso) */}
            {safeFill && <StaticImg src={A.shoulder_spear_fill} />}

            {/* Spear arm: ruota alla spalla sx, dentro il frame torso */}
            <Animated.View style={[styles.layer, pivot(570, 390), spearStyle]}>
              <StaticImg src={A.spear_arm} />
            </Animated.View>

            {/* Head group: ruota al base collo, dentro il frame torso */}
            <Animated.View style={[styles.layer, pivot(620, 280), headStyle]}>
              {safeFill && <StaticImg src={A.neck_fill} />}
              <StaticImg src={A.head_helmet} />
            </Animated.View>

          </Animated.View>
        </Animated.View>

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
