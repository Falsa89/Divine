/**
 * HeroHopliteIdleLoop — IDLE FRAME-BASED (RESUME-AWARE + COLOR MARKER)
 * =====================================================================
 *
 * DIAGNOSTICA POTENZIATA (Msg 516):
 *  - Timing uniforme 1200ms/frame → ciclo totale 6000ms, ogni frame
 *    è visibile per 1.2s garantiti.
 *  - Color marker a bordo del cell: 1=RED, 2=GREEN, 3=BLUE, 4=YELLOW,
 *    5=PURPLE. Se la posa non cambia ma il colore sì → problema asset
 *    cache. Se entrambi cambiano → tutto ok.
 *  - NIENTE badge testo dentro (era specchiato dal wrapper flippato).
 *    Il text badge viene renderizzato OUT-OF-FLIP da BattleSprite.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { HOPLITE_IDLE_ASSETS } from './hopliteAssetManifest';

export const HOPLITE_IDLE_DIAG = true;

const FRAMES = HOPLITE_IDLE_ASSETS;

// TIMING DIAGNOSTICO: 1200ms uniforme
const FRAME_DURATIONS_MS_DIAG = [1200, 1200, 1200, 1200, 1200];
const FRAME_DURATIONS_MS_PROD = [520, 280, 220, 320, 520];
const FRAME_DURATIONS_MS = HOPLITE_IDLE_DIAG
  ? FRAME_DURATIONS_MS_DIAG
  : FRAME_DURATIONS_MS_PROD;

// Color marker per frame (leggibile anche se posa non cambia)
const FRAME_COLORS = ['#FF2929', '#29FF5A', '#2980FF', '#FFD700', '#B829FF'];

const FRAME_W = 520;
const FRAME_H = 400;
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;

const RIG_FEET_Y_NORM = 800 / 1024;
const RIG_BODY_H_NORM = 0.683;
const FRAME_BODY_H_PX = 341;

let IDLE_MOUNT_COUNTER = 0;

type Props = {
  size: number;
  animated?: boolean;
  /** Callback opzionale: segnala al parent il frame index corrente (per HUD non-flippato) */
  onFrameChange?: (idx: number, cycles: number) => void;
};

export default function HeroHopliteIdleLoop({ size, animated = true, onFrameChange }: Props) {
  const [idx, setIdx] = useState(0);
  const idxRef = useRef(0);
  const cyclesRef = useRef(0);
  const frameStartAtRef = useRef<number>(Date.now());
  const elapsedInFrameRef = useRef<number>(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const instanceIdRef = useRef<number | null>(null);
  const onFrameChangeRef = useRef(onFrameChange);
  onFrameChangeRef.current = onFrameChange;

  if (instanceIdRef.current === null) {
    IDLE_MOUNT_COUNTER += 1;
    instanceIdRef.current = IDLE_MOUNT_COUNTER;
    if (HOPLITE_IDLE_DIAG) {
      console.log(`[IDLE_DIAG] MOUNT i#${instanceIdRef.current}`);
    }
  }

  useEffect(() => {
    if (!animated) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
        const now = Date.now();
        elapsedInFrameRef.current += now - frameStartAtRef.current;
      }
      return;
    }
    frameStartAtRef.current = Date.now();
    let cancelled = false;

    const advanceAndSchedule = () => {
      if (cancelled) return;
      const next = (idxRef.current + 1) % FRAMES.length;
      if (next === 0) cyclesRef.current += 1;
      idxRef.current = next;
      setIdx(next);
      onFrameChangeRef.current?.(next, cyclesRef.current);
      if (HOPLITE_IDLE_DIAG) {
        console.log(`[IDLE_DIAG] i#${instanceIdRef.current} → f${next + 1}/5 c${cyclesRef.current}`);
      }
      frameStartAtRef.current = Date.now();
      elapsedInFrameRef.current = 0;
      schedule();
    };

    const schedule = () => {
      if (cancelled || !animated) return;
      const holdMs = FRAME_DURATIONS_MS[idxRef.current];
      const remaining = Math.max(0, holdMs - elapsedInFrameRef.current);
      timeoutRef.current = setTimeout(advanceAndSchedule, remaining);
    };

    schedule();
    return () => {
      cancelled = true;
      if (timeoutRef.current) { clearTimeout(timeoutRef.current); timeoutRef.current = null; }
    };
  }, [animated]);

  useEffect(() => {
    return () => {
      if (HOPLITE_IDLE_DIAG) {
        console.log(`[IDLE_DIAG] UNMOUNT i#${instanceIdRef.current}`);
      }
    };
  }, []);

  // Geometria
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
      <View style={{
        position: 'absolute',
        top: boxTop,
        left: boxLeft,
        width: renderedW,
        height: renderedH,
      }}>
        <Image
          source={FRAMES[idx]}
          style={{ width: renderedW, height: renderedH }}
          resizeMode="contain"
          fadeDuration={0}
        />
      </View>
      {/* Color marker ring attorno al cell — visibile anche se pose non cambia.
          Se il colore cicla rosso→verde→blu→giallo→viola ma la posa no → bug asset. */}
      {HOPLITE_IDLE_DIAG && (
        <View
          pointerEvents="none"
          style={[
            StyleSheet.absoluteFillObject,
            {
              borderWidth: 4,
              borderColor: FRAME_COLORS[idx],
              borderRadius: 8,
            },
          ]}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },
});
