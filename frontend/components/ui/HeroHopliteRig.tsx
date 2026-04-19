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
import HeroHopliteIdleFrame from './HeroHopliteIdleFrame';
import HeroHopliteAffondo from './HeroHopliteAffondo';
import HeroHopliteGuardiaFerrea from './HeroHopliteGuardiaFerrea';

export type HopliteRigState =
  | 'idle' | 'attack' | 'skill' | 'hit' | 'dead' | 'heal' | 'dodge' | 'stress';

type Props = {
  size: number;
  state?: HopliteRigState;
  /** LEGACY: non più usato (il rig anatomico è stato rimosso). */
  animated?: boolean;
  /** LEGACY: non più usato. */
  safeFill?: boolean;
};

export default function HeroHopliteRig({ size, state = 'idle' }: Props) {
  // ───────────────────────────────────────────────────────────────────────
  // VISIBILITY MAP
  //   - idle/hit/dead/heal/dodge/stress → mostra frame statico idle
  //   - attack                          → mostra Affondo player attivo
  //   - skill                           → mostra Guardia Ferrea player attivo
  // ───────────────────────────────────────────────────────────────────────
  const attackActive = state === 'attack';
  const skillActive = state === 'skill';
  const showIdle = !attackActive && !skillActive;

  // ═══════════════════════════════════════════════════════════════════════
  // PLAY KEYS — hardening anti "doppio trigger".
  //
  //   Un solo playback per ogni invocazione logica. Il key viene
  //   incrementato SOLO alla transizione non-attack → attack (o
  //   non-skill → skill). Confrontiamo via prevStateRef per evitare
  //   re-render spuri che non cambiano veramente lo state.
  //
  //   Il player interno ha un secondo livello di protezione
  //   (`lastPlayedKeyRef`): anche se React rieseguisse l'effect senza
  //   motivo, la guard impedisce un doppio playback dello stesso key.
  // ═══════════════════════════════════════════════════════════════════════
  const [attackPlayKey, setAttackPlayKey] = React.useState(0);
  const [skillPlayKey, setSkillPlayKey] = React.useState(0);
  const prevStateRef = React.useRef<HopliteRigState>(state);
  React.useEffect(() => {
    const prev = prevStateRef.current;
    if (state === 'attack' && prev !== 'attack') {
      setAttackPlayKey(k => k + 1);
    }
    if (state === 'skill' && prev !== 'skill') {
      setSkillPlayKey(k => k + 1);
    }
    prevStateRef.current = state;
  }, [state]);

  return (
    <View style={[styles.root, { width: size, height: size }]}>

      {/* ═══════════════════════════════════════════════════════════════════
          LAYER 1 — IDLE FRAME (statico, reference-approved)
          Sempre montato, visibile quando NON è in attack/skill.
          Nessun breathing, nessun transform, zero rig frazionato.
         ═══════════════════════════════════════════════════════════════════ */}
      <View
        pointerEvents="none"
        style={[
          StyleSheet.absoluteFillObject,
          { opacity: showIdle ? 1 : 0 },
        ]}
      >
        <HeroHopliteIdleFrame size={size} />
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
        <HeroHopliteAffondo size={size} active={attackActive} playKey={attackPlayKey} />
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
        <HeroHopliteGuardiaFerrea size={size} active={skillActive} playKey={skillPlayKey} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },
});
