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
import HeroHopliteGuardiaFerrea from './HeroHopliteGuardiaFerrea';

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
  // MOUNT STABILE — no early return, no unmount/mount su switch state.
  // ---------------------------------------------------------------------
  // Il BUG precedente:
  //   if (state === 'attack') return <HeroHopliteAffondo />
  //   if (state === 'skill')  return <HeroHopliteGuardiaFerrea />
  // ad ogni transizione state distruggeva il componente corrente e
  // montava il nuovo. Gli asset (12 layer rig + 8 affondo + 6 guardia)
  // venivano decodati ogni volta → flash/lag percepibile.
  //
  // Il FIX:
  //   Tutti e 3 i render path (rig idle / Affondo / GuardiaFerrea) sono
  //   montati insieme come overlay assoluti. La visibilità è controllata
  //   da `opacity + pointerEvents`; i player frame-based ricevono
  //   `active` in modo che la loro sequenza parta solo quando richiesta.
  //
  //   Conseguenze:
  //    - require() risolti UNA sola volta (al primo mount del rig in battle).
  //    - Image cache nativa popolata al primo render → decode istantaneo
  //      per tutti i frame successivi.
  //    - Shared values del breathing loop NON vengono mai distrutti →
  //      il respiro non si "resetta" visivamente tra attack e idle.
  // ───────────────────────────────────────────────────────────────────────
  const showIdleRig = state !== 'attack' && state !== 'skill';
  const attackActive = state === 'attack';
  const skillActive  = state === 'skill';

  const scale = size / BASE;

  // =========================================================================
  // IDLE BASELINE — respirazione + sway capelli + oscillazione scudo
  // Continuano SEMPRE (anche durante l'attack) perché la vita del personaggio
  // non deve "congelarsi" mentre colpisce.
  // =========================================================================
  // =========================================================================
  // IDLE BREATHING — rig-based, loop continuo sinusoidale.
  // Reference LOCKED: contact sheet approvata da utente (5 keyframe:
  //   IDLE BASE → BREATH IN START → BREATH PEAK → SETTLE → LOOP RETURN).
  // Filosofia: "oplita già pronto in battaglia, respira e fa micro
  // aggiustamenti di guardia senza mai perdere assetto".
  //
  // Loop period: 2800ms (respiro disciplinato, ~21 BPM — lento e controllato).
  // Mathematical perfect loop: sin(cycle*2π) → 0 at cycle 0 e 1 → no snap.
  // =========================================================================
  const cycle = useSharedValue(0);
  React.useEffect(() => {
    if (!animated) return;
    cycle.value = 0;
    cycle.value = withRepeat(
      withTiming(1, { duration: 2800, easing: Easing.linear }),
      -1, false,
    );
  }, [animated]);
  const breath = useDerivedValue(() => Math.sin(cycle.value * Math.PI * 2));
  // Fasi leggermente sfasate per dare organicità (non tutto si muove in sync)
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
  // =========================================================================
  // STYLES per layer (REFERENCE-LOCKED idle).
  // Ampiezze calibrate sui 5 frame della contact sheet approvata:
  //   - chest rises ~4-5px al PEAK (visibile ma disciplinato)
  //   - head micro-tilt ~0.8° (lettura "attento ma fermo")
  //   - shield micro-oscillazione ~0.4° (segue la spalla)
  //   - gonna micro-sway (follow-through minimo)
  //   - lancia PRESSOCHÉ ferma (disciplina tank)
  //   - gambe FISSE (foundation rigida)
  // Tutti i valori sono in unità di canvas 1024×1024 (poi scalato a `size`).
  // =========================================================================

  // PELVIS: micro-lift del bacino (respiro sollevato). Reference mostra
  // il torso che sale ~4px → a canvas 1024, sollevamento di ~1.2 unità.
  const pelvisStyle = useAnimatedStyle(() => ({
    transform: [
      { translateY: -1.2 * breath.value },  // ±1.2 unità canvas
    ],
  }));

  // TORSO: espansione toracica (scaleY) + rotazione combat locale.
  // scaleY ±1.5% → ad altezza torso ~300 unità, espansione visibile di ~4.5 unità.
  const torsoStyle = useAnimatedStyle(() => {
    const s = 1 + 0.015 * breath.value;
    return {
      transform: [
        { rotate: `${torsoRot.value}deg` },
        { scaleY: s },
      ],
    };
  });

  // SHIELD ARM — micro oscillazione che segue la spalla (shieldPhase sfasato).
  // ±0.4° di rotazione → tip dello scudo oscilla ~2-3 unità, quasi impercettibile.
  const shieldStyle = useAnimatedStyle(() => ({
    transform: [
      { rotate: `${0.4 * shieldPhase.value + shieldRot.value}deg` },
    ],
  }));

  // SPEAR ARM — QUASI FERMO durante idle (disciplina tank). Micro oscillazione
  // ~0.15° per dare vita senza "dipingere" movimento sulla lancia.
  const spearStyle = useAnimatedStyle(() => ({
    transform: [
      { rotate: `${0.15 * breath.value + spearRot.value}deg` },
    ],
  }));

  // HEAD GROUP — micro tilt (~0.8°) che segue il respiro. Reference mostra la
  // testa che si alza leggermente al PEAK ("chin up attento").
  const headStyle = useAnimatedStyle(() => ({
    transform: [
      { rotate: `${0.8 * hairPhase.value + headRot.value}deg` },
    ],
  }));

  // SKIRT — micro sway (follow-through). Reference mostra gonna essenzialmente
  // ferma → valore molto basso (±0.5 unità di translate).
  const skirtStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: 0.5 * hairPhase.value },
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
      {/* ═══════════════════════════════════════════════════════════════════
          LAYER 1 — RIG ANATOMICO (idle + transitori neutri)
          Sempre montato. Visibile solo quando NON è in attack/skill.
          Gli shared values del breathing restano vivi → quando riappare
          non "ri-parte" da zero, continua il suo loop.
         ═══════════════════════════════════════════════════════════════════ */}
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          {
            opacity: showIdleRig ? 1 : 0,
          },
        ]}
      >
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

      {/* ═══════════════════════════════════════════════════════════════════
          LAYER 2 — AFFONDO DI FALANGE (attack, frame-based)
          Sempre montato. Visibile + sequenza attiva solo se state==='attack'.
         ═══════════════════════════════════════════════════════════════════ */}
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          {
            opacity: attackActive ? 1 : 0,
          },
        ]}
      >
        <HeroHopliteAffondo size={size} active={attackActive} />
      </View>

      {/* ═══════════════════════════════════════════════════════════════════
          LAYER 3 — GUARDIA FERREA (skill, frame-based)
          Sempre montato. Visibile + sequenza attiva solo se state==='skill'.
         ═══════════════════════════════════════════════════════════════════ */}
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          {
            opacity: skillActive ? 1 : 0,
          },
        ]}
      >
        <HeroHopliteGuardiaFerrea size={size} active={skillActive} />
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
