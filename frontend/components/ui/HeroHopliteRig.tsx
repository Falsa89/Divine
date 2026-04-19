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

/**
 * LAYER STACK — drawn bottom → top.
 *
 * Layer tipo `rig/*.png` = artwork originale del character.
 * Layer tipo `rig_safe/*.png` = helper animation-safe (flag helper=true):
 *   - NON ruotano con le animazioni (sono ancorati al corpo)
 *   - stanno DIETRO al limb che devono "supportare"
 *   - in idle/neutral sono coperti dal limb → invisibili
 *   - quando il limb ruota, riempiono il vuoto dietro la giuntura
 *
 * Ordine motivato:
 *   hair → legs → skirt → hip_fill → torso → under_arm_spear →
 *   shoulder_shield_fill → shield_arm → shoulder_spear_fill →
 *   spear_arm → neck_fill → head_helmet
 */
const LAYERS = [
  { key: 'hair',                 src: require('../../assets/heroes/greek_hoplite/rig/hair.png'),                      pivot: { x: 625, y: 235 } },
  { key: 'legs',                 src: require('../../assets/heroes/greek_hoplite/rig/legs.png'),                      pivot: { x: 690, y: 800 } },
  { key: 'skirt',                src: require('../../assets/heroes/greek_hoplite/rig/skirt.png'),                     pivot: { x: 660, y: 690 } },
  // safe helper: bridge vita ↔ gonna
  { key: 'hip_fill',             src: require('../../assets/heroes/greek_hoplite/rig_safe/hip_fill.png'),             pivot: { x: 650, y: 565 }, helper: true },
  { key: 'torso',                src: require('../../assets/heroes/greek_hoplite/rig/torso.png'),                     pivot: { x: 640, y: 540 } },
  // safe helper: riempimento ascella / pettorale spear
  { key: 'under_arm_spear',      src: require('../../assets/heroes/greek_hoplite/rig_safe/under_arm_spear.png'),      pivot: { x: 605, y: 460 }, helper: true },
  // safe helper: disco dietro spalla dx (shield)
  { key: 'shoulder_shield_fill', src: require('../../assets/heroes/greek_hoplite/rig_safe/shoulder_shield_fill.png'), pivot: { x: 690, y: 450 }, helper: true },
  { key: 'shield_arm',           src: require('../../assets/heroes/greek_hoplite/rig/shield_arm.png'),                pivot: { x: 700, y: 440 } },
  // safe helper: disco dietro spalla sx (spear)
  { key: 'shoulder_spear_fill',  src: require('../../assets/heroes/greek_hoplite/rig_safe/shoulder_spear_fill.png'),  pivot: { x: 590, y: 420 }, helper: true },
  { key: 'spear_arm',            src: require('../../assets/heroes/greek_hoplite/rig/spear_arm.png'),                 pivot: { x: 570, y: 390 } },
  // safe helper: disco base collo sotto head
  { key: 'neck_fill',            src: require('../../assets/heroes/greek_hoplite/rig_safe/neck_fill.png'),            pivot: { x: 620, y: 280 }, helper: true },
  { key: 'head_helmet',          src: require('../../assets/heroes/greek_hoplite/rig/head_helmet.png'),               pivot: { x: 610, y: 245 } },
];

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
  // HELPER layers (hip_fill, under_arm_spear, shoulder_*_fill, neck_fill):
  // completamente statici → nessun animStyle, nessuna rotazione. Sono
  // "ancorati al corpo" per coprire i gap delle giunture in animazione.
  const styleMap: Record<string, any> = {
    hair:        headGroupStyle,
    head_helmet: headGroupStyle,
    torso:       torsoStyle,
    spear_arm:   spearStyle,
    shield_arm:  shieldStyle,
    skirt:       skirtStyle,
    legs:        null,
    // helpers: null (statici)
  };

  const renderLayers = LAYERS.filter(l => safeFill || !(l as any).helper);

  return (
    <View style={[styles.root, { width: size, height: size }]}>
      <View style={{ width: BASE, height: BASE, transform: [{ scale }], transformOrigin: '0 0' as any }}>
        {renderLayers.map(layer => {
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
