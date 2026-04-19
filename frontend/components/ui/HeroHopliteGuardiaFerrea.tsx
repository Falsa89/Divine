/**
 * HeroHopliteGuardiaFerrea
 * =========================
 * Frame-based player per la SKILL "Guardia Ferrea" di Greek Hoplite.
 * Usa i 6 keyframe APPROVATI in assets/heroes/greek_hoplite/guardia_ferrea/.
 *
 * REFERENCE LOCKED:
 *   1. IDLE           2. ANCHOR        3. SHIELD FORWARD
 *   4. PULSE PEAK     5. HOLD END      6. RETURN
 *
 * Timing (totale ~1060ms):
 *   #1 IDLE            0 →  80ms   (entry snapshot)
 *   #2 ANCHOR         80 → 230ms   (raccolta, scudo su)
 *   #3 SHIELD FORWARD 230 → 380ms  (parata leggibile)
 *   #4 PULSE PEAK     380 → 660ms  (hold 280ms sul glow — key frame)
 *   #5 HOLD END       660 → 910ms  (stance difensiva tenuta)
 *   #6 RETURN         910 → 1060ms (rientro morbido)
 *
 * Canvas 420×420 uniforme, piedi ancorati a (210, 390) — no clipping,
 * glow intero, scudo e silhouette complete in tutti i frame.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';

const FRAMES = [
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_1.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_2.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_3.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_4.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_5.png'),
  require('../../assets/heroes/greek_hoplite/guardia_ferrea/frame_6.png'),
];

const FRAME_DURATIONS_MS = [
  80,   // 1. IDLE
  150,  // 2. ANCHOR
  150,  // 3. SHIELD FORWARD
  280,  // 4. PULSE PEAK (key — pulse readability)
  250,  // 5. HOLD END
  150,  // 6. RETURN
];

// Canvas nativo dei frame (tutti uguali, feet-anchored)
const FRAME_W = 420;
const FRAME_H = 420;
const FEET_CX_IN_FRAME = 210;
const FEET_CY_IN_FRAME = 390;

// Costanti di allineamento con HeroHopliteRig (stesse di HeroHopliteAffondo).
// Guardiscono che idle (rig) e skill (frame) abbiano i piedi alla stessa y.
const RIG_FEET_Y_NORM = 800 / 1024;  // 0.781
const RIG_BODY_H_NORM = 0.683;
const FRAME_BODY_H_PX = 288;          // altezza corpo media (audit 278..301 ex. glow)

type Props = {
  size: number;
  onDone?: () => void;
};

export default function HeroHopliteGuardiaFerrea({ size, onDone }: Props) {
  const [index, setIndex] = useState(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let cancelled = false;
    let i = 0;
    const advance = () => {
      if (cancelled) return;
      setIndex(i);
      if (i >= FRAMES.length - 1) {
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

  // Scale & position: stesso schema del Affondo player → zero salto feet
  const frameScale = (RIG_BODY_H_NORM * size) / FRAME_BODY_H_PX;
  const renderedH = FRAME_H * frameScale;
  const renderedW = FRAME_W * frameScale;

  const rigFeetYInCell  = RIG_FEET_Y_NORM * size;
  const frameFeetYInBox = FEET_CY_IN_FRAME * frameScale;
  const frameFeetXInBox = FEET_CX_IN_FRAME * frameScale;

  const boxTop  = rigFeetYInCell - frameFeetYInBox;
  const boxLeft = size / 2 - frameFeetXInBox;

  return (
    <View style={[styles.root, { width: size, height: size }]} pointerEvents="none">
      {/* scaleX=-1 interno per cancellare il flip applicato da BattleSprite
          (team player). Coerente con HeroHopliteAffondo. */}
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
  root: { overflow: 'visible' },
});
