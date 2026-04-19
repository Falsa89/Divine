/**
 * HeroHopliteIdleLoop — IDLE FRAME-BASED (RESUME-AWARE + DIAG)
 * =============================================================
 *
 * FIX CAUSA STRUTTURALE del problema "2 frame percepiti in battle":
 * quando il player era messo in pausa (animated=false) durante un
 * attack/skill e poi ripreso (animated=true), il vecchio codice
 * schedulava un setTimeout FRESCO con la FULL duration del frame
 * corrente → se gli attacchi interrompevano più velocemente della
 * durata del frame, l'idxRef non avanzava MAI.
 *
 * Fix applicato:
 * - Traccia `frameStartAt`: timestamp di quando il frame corrente è
 *   entrato in scena (come tempo "logico", pausa-aware).
 * - Al pause: accumula elapsed da frameStartAt nel frame corrente.
 * - Al resume: schedula solo il TEMPO RESIDUO (holdMs - elapsed).
 * - Se residuo ≤ 0 al resume, avanza subito al frame successivo.
 *
 * Così l'idle progredisce nel tempo logico anche se ripetutamente
 * interrotto da brevi pause di attack/skill.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet, Text } from 'react-native';
import { HOPLITE_IDLE_ASSETS } from './hopliteAssetManifest';

// ═════════════════════════════════════════════════════════════════════
// Flag diagnostica — true per abilitare log Metro + badge visivo.
// Set false per production.
// ═════════════════════════════════════════════════════════════════════
export const HOPLITE_IDLE_DIAG = true;

const FRAMES = HOPLITE_IDLE_ASSETS;

// TIMING DIAGNOSTICO TEMPORANEO: 1000ms uniforme per vedere chiaramente
// ciascun frame su Expo Go. Tornerà al timing production quando il bug
// sarà risolto e confermato.
const FRAME_DURATIONS_MS_DIAG = [1000, 1000, 1000, 1000, 1000];
const FRAME_DURATIONS_MS_PROD = [520, 280, 220, 320, 520];
const FRAME_DURATIONS_MS = HOPLITE_IDLE_DIAG
  ? FRAME_DURATIONS_MS_DIAG
  : FRAME_DURATIONS_MS_PROD;

// Canvas nativo dei frame (520×400, feet baseline comune)
const FRAME_W = 520;
const FRAME_H = 400;
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;

// Allineamento feet-to-ground
const RIG_FEET_Y_NORM = 800 / 1024;
const RIG_BODY_H_NORM = 0.683;
const FRAME_BODY_H_PX = 341;

let IDLE_MOUNT_COUNTER = 0;

type Props = {
  size: number;
  animated?: boolean;
};

export default function HeroHopliteIdleLoop({ size, animated = true }: Props) {
  const [idx, setIdx] = useState(0);
  const [cyclesCompleted, setCyclesCompleted] = useState(0);
  const idxRef = useRef(0);
  const cyclesRef = useRef(0);

  // Resume-aware timing state
  const frameStartAtRef = useRef<number>(Date.now());  // timestamp logico di inizio frame
  const elapsedInFrameRef = useRef<number>(0);         // ms accumulati nel frame corrente (paused → no accumulo)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const instanceIdRef = useRef<number | null>(null);
  if (instanceIdRef.current === null) {
    IDLE_MOUNT_COUNTER += 1;
    instanceIdRef.current = IDLE_MOUNT_COUNTER;
    if (HOPLITE_IDLE_DIAG) {
      console.log(`[IDLE_DIAG] MOUNT instance#${instanceIdRef.current}`);
    }
  }

  useEffect(() => {
    if (HOPLITE_IDLE_DIAG) {
      console.log(
        `[IDLE_DIAG] i#${instanceIdRef.current} effect animated=${animated} idx=${idxRef.current} elapsedInFrame=${elapsedInFrameRef.current}`
      );
    }

    // --- PAUSA ---
    if (!animated) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
        // Accumula elapsed del frame corrente (pausa-aware)
        const now = Date.now();
        elapsedInFrameRef.current += now - frameStartAtRef.current;
        if (HOPLITE_IDLE_DIAG) {
          console.log(
            `[IDLE_DIAG] i#${instanceIdRef.current} PAUSED on frame ${idxRef.current + 1}/5 (elapsed ${elapsedInFrameRef.current}/${FRAME_DURATIONS_MS[idxRef.current]}ms)`
          );
        }
      }
      return;
    }

    // --- RESUME / START ---
    frameStartAtRef.current = Date.now();
    let cancelled = false;

    const advanceAndSchedule = () => {
      if (cancelled) return;
      // Avanza frame
      const next = (idxRef.current + 1) % FRAMES.length;
      if (next === 0) {
        cyclesRef.current += 1;
        setCyclesCompleted(cyclesRef.current);
        if (HOPLITE_IDLE_DIAG) {
          console.log(`[IDLE_DIAG] i#${instanceIdRef.current} CYCLE DONE #${cyclesRef.current}`);
        }
      }
      idxRef.current = next;
      setIdx(next);
      // Reset counters per nuovo frame
      frameStartAtRef.current = Date.now();
      elapsedInFrameRef.current = 0;
      if (HOPLITE_IDLE_DIAG) {
        console.log(`[IDLE_DIAG] i#${instanceIdRef.current} → frame ${next + 1}/5`);
      }
      // Schedula il prossimo advance
      schedule();
    };

    const schedule = () => {
      if (cancelled || !animated) return;
      const holdMs = FRAME_DURATIONS_MS[idxRef.current];
      const remaining = Math.max(0, holdMs - elapsedInFrameRef.current);
      if (HOPLITE_IDLE_DIAG) {
        console.log(
          `[IDLE_DIAG] i#${instanceIdRef.current} schedule frame ${idxRef.current + 1}/5 remaining=${remaining}ms (full=${holdMs}, elapsed=${elapsedInFrameRef.current})`
        );
      }
      timeoutRef.current = setTimeout(advanceAndSchedule, remaining);
    };

    schedule();

    return () => {
      cancelled = true;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [animated]);

  // Unmount log
  useEffect(() => {
    return () => {
      if (HOPLITE_IDLE_DIAG) {
        console.log(
          `[IDLE_DIAG] UNMOUNT i#${instanceIdRef.current} (final idx=${idxRef.current}, cycles=${cyclesRef.current})`
        );
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
        transform: [{ scaleX: -1 }],
      }}>
        <Image
          source={FRAMES[idx]}
          style={{ width: renderedW, height: renderedH }}
          resizeMode="contain"
          fadeDuration={0}
        />
      </View>
      {HOPLITE_IDLE_DIAG && (
        <View style={styles.diagBadge} pointerEvents="none">
          <Text style={styles.diagText}>
            {`i#${instanceIdRef.current}·f${idx + 1}/5·c${cyclesCompleted}`}
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },
  diagBadge: {
    position: 'absolute',
    top: -22,
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 9999,
  },
  diagText: {
    backgroundColor: 'rgba(0,0,0,0.9)',
    color: '#FFD700',
    fontSize: 10,
    fontWeight: '900',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    fontFamily: 'monospace',
    borderWidth: 1,
    borderColor: '#FFD700',
  },
});
