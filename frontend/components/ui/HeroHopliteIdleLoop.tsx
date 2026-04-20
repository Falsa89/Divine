/**
 * HeroHopliteIdleLoop — GLOBAL TICKER (bulletproof)
 * ===================================================
 *
 * Approccio RADICALE: timer a livello MODULE che tick ogni ~250ms e aggiorna
 * un counter globale. I componenti IdleLoop si sottoscrivono via useSyncExternalStore-like
 * pattern. Zero dipendenza da useEffect lifecycle. Zero problemi di remount.
 *
 * IL TIMER GIRA SEMPRE (module-level), quindi anche se il componente React
 * viene rimontato N volte, il counter globale continua ad avanzare.
 */
import React, { useEffect, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { HOPLITE_IDLE_ASSETS } from './hopliteAssetManifest';

export const HOPLITE_IDLE_DIAG = false;

const FRAMES = HOPLITE_IDLE_ASSETS;
// TIMING production (Msg 420): ulteriormente velocizzato — ciclo ~795ms totale
// Frame 3 (peak breath) più corto, 1/5 stabili. Non deve sembrare nervoso.
const FRAME_DURATIONS_MS_DIAG = [1200, 1200, 1200, 1200, 1200];
const FRAME_DURATIONS_MS_PROD = [220, 130, 95, 130, 220];  // cycle ~795ms
const FRAME_DURATIONS_MS = HOPLITE_IDLE_DIAG ? FRAME_DURATIONS_MS_DIAG : FRAME_DURATIONS_MS_PROD;
const FRAME_COLORS = ['#FF2929', '#29FF5A', '#2980FF', '#FFD700', '#B829FF'];

// ═══════════════════════════════════════════════════════════════════════
// GLOBAL TICKER — module-level. Avanza SEMPRE, indipendente da React.
// Tick ogni 150ms (più fine granularità del frame più corto 220ms).
// Mantiene `currentFrameIdx` globale. Notifica sottoscrittori su cambio.
// ═══════════════════════════════════════════════════════════════════════
let currentFrameIdx = 0;
let elapsedInCurrentFrame = 0;
let lastTickAt = Date.now();
const subscribers = new Set<(idx: number) => void>();

function tick() {
  const now = Date.now();
  const delta = now - lastTickAt;
  lastTickAt = now;
  elapsedInCurrentFrame += delta;
  const holdMs = FRAME_DURATIONS_MS[currentFrameIdx];
  if (elapsedInCurrentFrame >= holdMs) {
    elapsedInCurrentFrame = 0;
    currentFrameIdx = (currentFrameIdx + 1) % FRAMES.length;
    if (HOPLITE_IDLE_DIAG) {
      console.log(`[IDLE_GLOBAL] → f${currentFrameIdx + 1}/5 (subs=${subscribers.size})`);
    }
    subscribers.forEach(fn => fn(currentFrameIdx));
  }
}
// Avvia il ticker una volta — tick 40ms per onorare anche il frame più corto (~110ms)
setInterval(tick, 40);

// ═══════════════════════════════════════════════════════════════════════

const FRAME_W = 520;
const FRAME_H = 400;
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;
const RIG_FEET_Y_NORM = 800 / 1024;
const RIG_BODY_H_NORM = 0.683;
// FRAME_BODY_H_PX — altezza corpo NATIVA nei PNG idle (misurata dai 5 frame).
// I frame idle hanno bordi trasparenti più ampi dell'Affondo, quindi il body
// reale è ~300px invece dei 341 dell'Affondo. Scalare sul body REALE garantisce
// parità scenica: idle e attack/skill appaiono della stessa altezza visiva.
const FRAME_BODY_H_PX = 300;

type Props = {
  size: number;
  animated?: boolean;  // retained for API, ignored by implementation
};

export default function HeroHopliteIdleLoop({ size }: Props) {
  const [idx, setIdx] = useState(currentFrameIdx);

  useEffect(() => {
    const handler = (i: number) => setIdx(i);
    subscribers.add(handler);
    // sync immediately to current global idx
    setIdx(currentFrameIdx);
    return () => { subscribers.delete(handler); };
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
          key={`hoplite-idle-${idx}`}
          source={FRAMES[idx]}
          style={{ width: renderedW, height: renderedH }}
          resizeMode="contain"
          fadeDuration={0}
        />
      </View>
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
