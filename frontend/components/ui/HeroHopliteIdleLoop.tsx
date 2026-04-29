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
import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { HOPLITE_IDLE_ASSETS } from './hopliteAssetManifest';

export const HOPLITE_IDLE_DIAG = false;

const FRAMES = HOPLITE_IDLE_ASSETS;
// TIMING production (Msg 426): step ulteriore — ciclo ~595ms
// Frame 3 peak sempre il più corto. Prudente: -16% ma non frenetico.
const FRAME_DURATIONS_MS_DIAG = [1200, 1200, 1200, 1200, 1200];
const FRAME_DURATIONS_MS_PROD = [160, 100, 75, 100, 160];  // cycle ~595ms
const FRAME_DURATIONS_MS = HOPLITE_IDLE_DIAG ? FRAME_DURATIONS_MS_DIAG : FRAME_DURATIONS_MS_PROD;
const FRAME_COLORS = ['#FF2929', '#29FF5A', '#2980FF', '#FFD700', '#B829FF'];

// ═══════════════════════════════════════════════════════════════════════
// GLOBAL TICKER — module-level. Avanza SEMPRE, indipendente da React.
// Tick ogni 150ms (più fine granularità del frame più corto 220ms).
// Mantiene `currentFrameIdx` globale. Notifica sottoscrittori su cambio.
// v16.9 — PAUSE GATE: quando >=1 IdleLoop è montato con paused=true,
// il tick è gated → frame counter freezato. Quando ZERO IdleLoop sono
// paused, il tick riprende. Implementa un counter di componenti paused
// (semplice e robusto agli unmount). Single-source-of-truth: quando
// `pausedConsumerCount > 0` → tick non avanza.
// v16.10 — STAGGER PHASE: ogni IdleLoop instance assegna un offset
// deterministico (counter incrementale modulo numero frame). Quando
// il global counter avanza, i subscriber computano localmente
// `(currentFrameIdx + offset) % FRAMES.length` invece di usare lo stesso
// idx → le transizioni dei multipli Hoplite si SFASANO → no più
// "lampo collettivo" sincrono percepito a x1/x2. A x3 il battle-pacing
// nasconde idle quindi nessun side-effect.
// ═══════════════════════════════════════════════════════════════════════
let currentFrameIdx = 0;
let elapsedInCurrentFrame = 0;
let lastTickAt = Date.now();
const subscribers = new Set<(idx: number) => void>();
let pausedConsumerCount = 0;
let nextPhaseOffset = 0;

function tick() {
  const now = Date.now();
  const delta = now - lastTickAt;
  lastTickAt = now;
  // v16.9 — gate globale: se almeno un consumer è in pause, NON avanzare.
  if (pausedConsumerCount > 0) return;
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
// MISURA REALE (Msg 422): body_h=341 su tutti i 5 frame idle (bbox alpha).
// Uguale a Affondo peak (342). L'idle appare visivamente piu' piccolo perche'
// attack/skill si muovono dinamicamente (feet_cx si sposta 40px + arco del salto)
// mentre idle e' statico => meno "spazio scenico". Compenso alzando RIG_BODY_H_NORM
// di +8% solo qui => parita' visiva senza falsificare il FRAME_BODY_H_PX.
const RIG_BODY_H_NORM = 0.74;           // era 0.683 (compensazione staticita')
const FRAME_BODY_H_PX = 341;            // valore REALE misurato con PIL su PNG

type Props = {
  size: number;
  /** v16.9 — Quando false, freeze del frame counter via gate globale. */
  animated?: boolean;
};

export default function HeroHopliteIdleLoop({ size, animated = true }: Props) {
  // v16.10 — STAGGER PHASE per-istanza: ogni IdleLoop riceve un offset
  // deterministico (counter incrementale modulo numero frame). Quando il
  // global counter avanza, il display index locale è
  //   (currentFrameIdx + phaseOffset) % FRAMES.length
  // → le transizioni dei multipli Hoplite si SFASANO → addio "lampo
  // collettivo" sincrono percepito a x1/x2. L'offset è stabilizzato in
  // un ref per istanza, così non cambia tra render. Su unmount/remount
  // il counter NON viene decrementato: gli offset si distribuiscono
  // comunque in modo bilanciato e non sincrono.
  const phaseOffsetRef = useRef<number | null>(null);
  if (phaseOffsetRef.current === null) {
    phaseOffsetRef.current = nextPhaseOffset % FRAMES.length;
    nextPhaseOffset += 1;
  }
  const phaseOffset = phaseOffsetRef.current;

  const [globalIdx, setGlobalIdx] = useState(currentFrameIdx);
  const idx = (globalIdx + phaseOffset) % FRAMES.length;

  useEffect(() => {
    const handler = (i: number) => setGlobalIdx(i);
    subscribers.add(handler);
    // sync immediately to current global idx
    setGlobalIdx(currentFrameIdx);
    return () => { subscribers.delete(handler); };
  }, []);

  // v16.9 — Pause propagation: `animated=false` (passato dal HeroHopliteRig
  // come `showIdle && !paused`) registra questo consumer come "paused" sul
  // global ticker → quando count > 0, il tick globale freeza il frame
  // counter → tutti gli IdleLoop sub vedono lo stesso `currentFrameIdx`
  // congelato → idle visualmente FERMO.
  useEffect(() => {
    if (!animated) {
      pausedConsumerCount += 1;
      return () => {
        pausedConsumerCount = Math.max(0, pausedConsumerCount - 1);
      };
    }
    return undefined;
  }, [animated]);

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
        {/* v16.12 — RIMOSSA `key` dinamica per-frame.
            Era: key={`hoplite-idle-${idx}`} → cambiava ad OGNI frame del global
            ticker (~ogni 100-160ms). React, vedendo una nuova key in stessa
            posizione albero, UNMOUNTAVA la <Image> precedente e MONTAVA una
            nuova istanza → su device reale (iOS/Android) ogni unmount/mount
            comporta release + re-allocazione della native texture/view via
            bridge → nel singolo frame di reconciliation lo schermo mostrava
            un attimo "vuoto" → percezione di FLICKER/appear-disappear breve.
            Soluzione: lasciare l'<Image> stabile e cambiare SOLO il source.
            React Native swappa la texture in-place senza distruggere il view
            → transizione di frame atomica, zero flash. */}
        <Image
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
