/**
 * HeroHopliteAffondo
 * ===================
 * Frame-based player per l'attack "Affondo di Falange" di Greek Hoplite.
 * Usa gli 8 keyframe APPROVATI salvati in assets/heroes/greek_hoplite/affondo/.
 *
 * REFERENCE LOCKED: i frame sono la source of truth immutabile.
 * Questo player li swappa secondo il timing approvato. NON applica rotazioni
 * né trasformazioni al singolo frame → la silhouette resta esattamente
 * quella pittorica della reference.
 *
 * TIMING (totale ~800ms):
 *   #1 IDLE           0    → 0ms     (entry — snapshot, invisibile)
 *   #2 PRE-LOAD       0    → 90ms    (carica, spalla parte)
 *   #3 RITRAZIONE    90    → 200ms   (braccio si raccoglie indietro)
 *   #4 AFFONDO MID  200    → 300ms   (thrust parte, corpo avanti)
 *   #5 AFFONDO PEAK 300    → 420ms   (estensione massima)
 *   #6 IMPACT HOLD  420    → 560ms   (tenuta impatto, ~140ms)
 *   #7 RETURN MID   560    → 680ms   (rientro, corpo torna)
 *   #8 IDLE FINALE  680    → 800ms   (home, pronto per prossimo turno)
 *
 * Tutti i frame sono 384×900 RGBA con stesso ground baseline → nessuno
 * scatto verticale durante lo swap.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';

// Require statico dei 8 frame (bundling ahead-of-time)
const FRAMES = [
  require('../../assets/heroes/greek_hoplite/affondo/frame_1.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_2.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_3.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_4.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_5.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_6.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_7.png'),
  require('../../assets/heroes/greek_hoplite/affondo/frame_8.png'),
];

// Durata (ms) di ciascun frame nella sequenza — cumulativi NON, ognuno ha
// la propria "hold duration". Somma: 90+110+100+120+140+120+120 = 800ms.
const FRAME_DURATIONS_MS = [
  90,   // #1 IDLE      (kickoff — 90ms)
  110,  // #2 PRE-LOAD
  100,  // #3 RITRAZIONE
  120,  // #4 AFFONDO MID
  140,  // #5 AFFONDO PEAK
  120,  // #6 IMPACT HOLD
  120,  // #7 RETURN MID
  120,  // #8 IDLE FINALE (settle)
];

// Dimensioni native dei frame (tutti uguali per costruzione).
// Aspect ratio 384:640 = 0.6 (portrait), character anchored al bottom.
const FRAME_W = 384;
const FRAME_H = 640;

type Props = {
  /** Dimensione quadrata della cella in px (come HeroHopliteRig) */
  size: number;
  /** Callback opzionale a fine sequenza */
  onDone?: () => void;
};

export default function HeroHopliteAffondo({ size, onDone }: Props) {
  const [index, setIndex] = useState(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let cancelled = false;
    let i = 0;

    const advance = () => {
      if (cancelled) return;
      setIndex(i);
      if (i >= FRAMES.length - 1) {
        // Sequenza completa
        timeoutRef.current = setTimeout(() => {
          if (!cancelled) onDone?.();
        }, FRAME_DURATIONS_MS[i]);
        return;
      }
      timeoutRef.current = setTimeout(() => {
        i += 1;
        advance();
      }, FRAME_DURATIONS_MS[i]);
    };

    advance();

    return () => {
      cancelled = true;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  // Render: stesso box della cella (size×size) con il frame scaled per adattarsi
  // mantenendo aspect ratio. Il frame 384×900 è più alto che largo, quindi
  // limitiamo per altezza (fit contain) → il personaggio resta proporzionato.
  // Alignment: bottom center → i piedi stanno sulla linea del terreno.
  const frameScale = size / FRAME_H;
  const renderedW = FRAME_W * frameScale;
  const renderedH = FRAME_H * frameScale;

  return (
    <View style={[styles.root, { width: size, height: size }]} pointerEvents="none">
      {/* INNER scaleX=-1: le reference sono pre-renderizzate facing RIGHT,
          mentre il rig (e quindi il wrapper BattleSprite) si aspetta un
          asset che NATIVAMENTE guarda a LEFT. Mirroriamo internamente così
          questo componente combacia perfettamente con il flip che BattleSprite
          applica per team player (scaleX=-1) o lascia intatto per enemy. */}
      <View style={{
        position: 'absolute',
        bottom: 0,
        left: (size - renderedW) / 2,
        width: renderedW,
        height: renderedH,
        transform: [{ scaleX: -1 }],
      }}>
        <Image
          source={FRAMES[index]}
          style={{ width: renderedW, height: renderedH }}
          resizeMode="contain"
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },
});
