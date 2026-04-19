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
// Canvas 520×400 con feet anchor a (260, 390) → piedi sempre in fondo-centro.
// Questo canvas include safe margin su TUTTI i lati → nessun clipping.
const FRAME_W = 520;
const FRAME_H = 400;
// Dove sono i piedi nel canvas del frame (usato per ground-align in render)
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;

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

  // =========================================================================
  // SCALE + POSITION per allineamento con HeroHopliteRig.
  // Obiettivo: feet del frame allineati ai feet del rig → ZERO scatto
  // quando BattleSprite passa da idle (rig) a attack (frame-based).
  //
  // Rig (1024×1024):
  //   - character body height in canvas ≈ 700 px
  //   - feet y in canvas ≈ 800 px → normalized 800/1024 = 0.781
  // Frame (520×400):
  //   - character body height in canvas ≈ 341 px (costante cross-frame)
  //   - feet pos (260, 390) → normalized 390/400 = 0.975
  // =========================================================================
  const RIG_FEET_Y_NORM = 800 / 1024;        // 0.781
  const RIG_BODY_H_NORM = 0.683;              // 700/1024 approx
  const FRAME_BODY_H_PX = 341;                // altezza corpo nativa nel frame

  // Scala il frame così che il corpo renda alla stessa altezza del rig
  const frameScale = (RIG_BODY_H_NORM * size) / FRAME_BODY_H_PX;
  const renderedH = FRAME_H * frameScale;
  const renderedW = FRAME_W * frameScale;

  // Posizionamento: piedi sul terreno alla stessa y del rig
  const rigFeetYInCell   = RIG_FEET_Y_NORM * size;
  const frameFeetYInBox  = FEET_CY_IN_FRAME * frameScale;
  const frameFeetXInBox  = FEET_CX_IN_FRAME * frameScale;

  const boxTop  = rigFeetYInCell - frameFeetYInBox;  // solitamente ~0
  const boxLeft = size / 2 - frameFeetXInBox;         // center feet on cell

  return (
    <View style={[styles.root, { width: size, height: size }]} pointerEvents="none">
      {/* Frame box posizionato con feet allineati al rig.
          overflow: visible → la punta della lancia può estendersi fuori
          dai bounds della cella senza venir tagliata (desired behavior). */}
      <View style={{
        position: 'absolute',
        top: boxTop,
        left: boxLeft,
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
  root: { overflow: 'visible' },  // spear tip può estendersi fuori dalla cella
});
