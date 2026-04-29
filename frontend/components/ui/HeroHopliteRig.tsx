/**
 * HeroHopliteRig — State Multiplexer FRAME-BASED
 * ================================================
 *
 * ⚠ IL NOME "Rig" È LEGACY. QUESTO FILE NON È PIÙ UN RIG ANATOMICO.
 *    È un semplice MULTIPLEXER che sceglie quale frame-player mostrare in
 *    base allo `state` logico ricevuto dal sistema battle.
 *
 * ─────────────────────────────────────────────────────────────────────────
 * DECISIONE DI DIREZIONE (utente):
 *   Per Greek Hoplite usiamo SOLO i frame reference-locked approvati.
 *   Nessun rig frazionato, nessun layer separato, nessun breathing
 *   ricostruito via pezzi. Un solo player attivo per stato.
 * ─────────────────────────────────────────────────────────────────────────
 *
 * Render path finale di Hoplite in battle:
 *   idle   → HeroHopliteIdleFrame     (frame statico, reference-approved)
 *   attack → HeroHopliteAffondo        (8 frame, Affondo di Falange)
 *   skill  → HeroHopliteGuardiaFerrea  (6 frame, Guardia Ferrea)
 *   hit/death/heal/dodge → fallback temporaneo all'idle frame
 *     (verranno implementati con propri frame quando saranno forniti
 *     i riferimenti; NON vengono renderizzati via rig anatomico).
 *
 * Proprietà del multiplexer:
 *  - I 3 player sono MONTATI SEMPRE in overlay assoluti → no unmount/
 *    mount su cambio state → no decode lazy, no flash, no restart del
 *    breathing (che comunque non c'è più).
 *  - Visibilità gestita da `opacity + pointerEvents`.
 *  - Attack/Skill ricevono `playKey` incrementato alla TRANSIZIONE
 *    (non-attack → attack, non-skill → skill) + `active` flag.
 *    La sequenza parte UNA sola volta per ogni playKey nuovo.
 *  - Idle è un frame statico — non ha sequenza, non ha doppio trigger.
 *
 * Questo componente non applica alcun transform locale (scale/rotate/
 * translate). I frame sono già reference-locked e completi.
 */
import React from 'react';
import { View, StyleSheet } from 'react-native';
import HeroHopliteIdleLoop from './HeroHopliteIdleLoop';
import HeroHopliteAffondo from './HeroHopliteAffondo';
import HeroHopliteGuardiaFerrea from './HeroHopliteGuardiaFerrea';

export type HopliteRigState =
  | 'idle' | 'attack' | 'skill' | 'hit' | 'dead' | 'heal' | 'dodge' | 'stress';

type Props = {
  size: number;
  state?: HopliteRigState;
  /**
   * actionInstanceId — sorgente esterna univoca per ogni invocazione
   * logica di attack/skill. Generato in combat.tsx (incrementale per
   * ogni dispatch di stato attack o skill) e passato down attraverso
   * BattleSprite. I player frame-based partono SOLO quando cambia
   * questo id, non quando cambia `state`.
   *
   * Perché questo pattern risolve definitivamente il doppio trigger:
   *  - `state === 'attack'` può essere rivalutato molte volte durante
   *    una sola azione (hp update, damage float, isCrit su target, ecc.)
   *  - Ogni rivalutazione creava un potenziale restart del frame player
   *  - `actionInstanceId` invece cambia SOLO quando il sistema battle
   *    dispatcha una NUOVA azione. È la verità della state machine
   *    battle, non un derivato della visibilità.
   */
  actionInstanceId?: number;
  /** Facing scaleX: 1 = no flip (native right-facing), -1 = flip to left */
  facingScaleX?: number;
  /** v16.8 — Pause toggle. Quando true, IdleLoop e i player attack/skill
   *  smettono di avanzare i frame (frozen on current frame). */
  paused?: boolean;
  /** LEGACY: non più usato. */
  animated?: boolean;
  /** LEGACY: non più usato. */
  safeFill?: boolean;
};

export default function HeroHopliteRig({
  size,
  state = 'idle',
  actionInstanceId = 0,
  facingScaleX = 1,
  paused = false,
}: Props) {
  // ───────────────────────────────────────────────────────────────────────
  // VISIBILITY MAP
  // ───────────────────────────────────────────────────────────────────────
  const attackActive = state === 'attack';
  const skillActive = state === 'skill';
  const showIdle = !attackActive && !skillActive;

  // ═══════════════════════════════════════════════════════════════════════
  // PLAY KEYS — snapshottiamo l'actionInstanceId al momento della
  // transizione logica (non-attack → attack, non-skill → skill) e lo
  // passiamo ai player. Così, se actionInstanceId cambia DURANTE uno
  // stato 'attack' già attivo (caso che non dovrebbe capitare ma
  // proteggiamoci comunque), il player NON riparte. Parte solo quando
  // il parent dichiara una NUOVA invocazione passando un nuovo id E lo
  // stato transisce verso attack/skill.
  // ═══════════════════════════════════════════════════════════════════════
  const [attackPlayKey, setAttackPlayKey] = React.useState(0);
  const [skillPlayKey, setSkillPlayKey] = React.useState(0);
  const prevStateRef = React.useRef<HopliteRigState>(state);
  React.useEffect(() => {
    const prev = prevStateRef.current;
    if (state === 'attack' && prev !== 'attack') {
      // Transizione valida: snapshotta l'actionInstanceId come nuovo playKey.
      setAttackPlayKey(actionInstanceId || 0);
    }
    if (state === 'skill' && prev !== 'skill') {
      setSkillPlayKey(actionInstanceId || 0);
    }
    prevStateRef.current = state;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state]);

  return (
    <View style={[
      styles.root,
      { width: size, height: size, transform: [{ scaleX: facingScaleX }] },
    ]}>

      {/* ═══════════════════════════════════════════════════════════════════
          LAYER 1 — IDLE FRAME-BASED ANIMATO (loop reference-approved)
          Sempre montato, visibile quando NON è in attack/skill.

          FACING: i PNG idle sono esportati con direzione nativa DIFFERENTE
          dai PNG affondo/guardia (verificato empiricamente su Expo Go — 
          l'utente ha confermato che attack/skill sono orientati corretti
          col flip standard, mentre idle è specchiato). Compensiamo qui con
          un `scaleX: -1` locale applicato SOLO al layer idle, così l'output
          finale di tutti e 3 i layer è coerente.
         ═══════════════════════════════════════════════════════════════════ */}
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          { opacity: showIdle ? 1 : 0, transform: [{ scaleX: -1 }] },
        ]}
      >
        <HeroHopliteIdleLoop size={size} animated={showIdle && !paused} />
      </View>

      {/* ═══════════════════════════════════════════════════════════════════
          LAYER 2 — AFFONDO DI FALANGE (attack, 8 frame approvati)
          Sempre montato. Visibile + sequenza attiva solo se state==='attack'.
         ═══════════════════════════════════════════════════════════════════ */}
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          { opacity: attackActive ? 1 : 0 },
        ]}
      >
        <HeroHopliteAffondo size={size} active={attackActive && !paused} playKey={attackPlayKey} />
      </View>

      {/* ═══════════════════════════════════════════════════════════════════
          LAYER 3 — GUARDIA FERREA (skill, 6 frame approvati)
          Sempre montato. Visibile + sequenza attiva solo se state==='skill'.
         ═══════════════════════════════════════════════════════════════════ */}
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          { opacity: skillActive ? 1 : 0 },
        ]}
      >
        <HeroHopliteGuardiaFerrea size={size} active={skillActive && !paused} playKey={skillPlayKey} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },
});
