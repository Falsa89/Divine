/**
 * RuntimeSheetSprite — RM1.17-N
 *
 * Renderizza uno sprite-sheet animato a frame, leggendo i metadati dal
 * contract dell'eroe (`useRuntimeSheets: true`). Supporta:
 *  - layout grid N cols × M rows (es. skill 5×2 con 10ª cella vuota)
 *  - loop true/false
 *  - fps per-state
 *  - reset frame a 0 su cambio di state
 *  - pause globale (stop del frame-tick)
 *
 * Geometria identica a BattleSprite: size × size*1.25, feet-anchored al bottom
 * del parent (justifyContent:'flex-end' già gestito dal wrapper).
 *
 * Perché NON usa reanimated shared values: gli sprite-sheet hanno bisogno di
 * un integer frame counter che triggeri re-render React per cambiare il
 * marginLeft/marginTop del tile. setState + setInterval è l'approccio più
 * semplice e robusto cross-platform.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Image } from 'react-native';
import { heroRuntimeSheet, type RuntimeSheetState } from './ui/hopliteAssets';

type Props = {
  heroId?: string | null;
  heroName?: string | null;
  state: RuntimeSheetState;
  /** Larghezza di rendering (il frame avrà width=size, height=size*1.25). */
  size: number;
  /** Scala facing (±1). Applicata come transform alla Image. */
  facingScaleX?: number;
  /** Pausa il frame-tick. */
  paused?: boolean;
  /** Instance id dell'azione: reset frame 0 su nuova invocazione. */
  actionInstanceId?: number;
};

export default function RuntimeSheetSprite({
  heroId,
  heroName,
  state,
  size,
  facingScaleX = 1,
  paused = false,
  actionInstanceId,
}: Props) {
  const info = heroRuntimeSheet(heroId, heroName, state);

  // Geometria cella display: preserva aspect della cella source (640×768).
  const frameW = size;
  const frameH = Math.round(size * 1.25);

  // Frame corrente (index 0..frames-1)
  const [frameIdx, setFrameIdx] = useState(0);
  const frameIdxRef = useRef(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Reset a 0 quando cambia state o actionInstanceId
  useEffect(() => {
    frameIdxRef.current = 0;
    setFrameIdx(0);
  }, [state, actionInstanceId]);

  // Frame tick via setInterval
  useEffect(() => {
    if (!info) return;
    if (paused) return;
    // periodo in ms
    const periodMs = Math.max(1, Math.round(1000 / Math.max(1, info.fps)));
    intervalRef.current = setInterval(() => {
      const next = frameIdxRef.current + 1;
      if (next >= info.frames) {
        if (info.loop) {
          frameIdxRef.current = 0;
          setFrameIdx(0);
        } else {
          // hold last frame
          frameIdxRef.current = info.frames - 1;
          setFrameIdx(info.frames - 1);
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        }
      } else {
        frameIdxRef.current = next;
        setFrameIdx(next);
      }
    }, periodMs);
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
    // ri-creiamo l'interval quando cambia state/paused/fps/frames
  }, [info?.fps, info?.frames, info?.loop, state, paused, actionInstanceId]);

  if (!info) return null;

  // RM1.17-O — SAFETY GUARD: clamp frameIdx in range [0, frames-1]. Previene
  // di mostrare la cella padding trasparente (es. skill 10ª cella) se per
  // una race il counter dovesse avanzare oltre info.frames-1.
  const safeFrameIdx = Math.max(0, Math.min(frameIdx, info.frames - 1));

  // Calcola colonna/riga per il frame corrente con safeFrameIdx
  const col = safeFrameIdx % info.columns;
  const row = Math.floor(safeFrameIdx / info.columns);

  // Dimensioni totali della Image (grid completo in coordinate display)
  const totalW = info.columns * frameW;
  const totalH = info.rows * frameH;

  // RM1.17-O — VISUAL SCALE a bottom-anchor
  // Alcuni eroi (Berserker) hanno il body nel source più piccolo di Hoplite
  // battlefield. Applichiamo una scala visiva UNIFORME per tutti gli stati
  // (letta dal contract) con compensazione translateY per mantenere feet
  // ancorati al bottom del wrapper layout box. Default 1.0 → no-op.
  //
  // Math: scale (origin = center) espande il contenuto ±(H*(S-1))/2 da center.
  // Per mantenere visual bottom = layout bottom, trasliamo UP di
  // (H*(S-1))/2. Il facingScaleX rimane nel wrapper esterno; combinando
  // scale uniforme interno + scaleX esterno, il flip orizzontale funziona
  // (scale uniforme è commutativo rispetto a scaleX=-1).
  const visualScale = typeof info.visualScale === 'number' && info.visualScale > 0
    ? info.visualScale
    : 1;
  const scaleTransform = visualScale !== 1
    ? [
        { translateY: -(frameH * (visualScale - 1)) / 2 },
        { scale: visualScale },
      ]
    : [];

  return (
    <View
      pointerEvents="none"
      style={{
        width: frameW,
        height: frameH,
        overflow: visualScale > 1 ? 'visible' : 'hidden',
        alignItems: 'flex-start',
        justifyContent: 'flex-start',
        transform: [{ scaleX: facingScaleX }, ...scaleTransform],
      }}
    >
      <Image
        source={info.source}
        style={{
          width: totalW,
          height: totalH,
          marginLeft: -col * frameW,
          marginTop: -row * frameH,
        }}
        resizeMode="stretch"
      />
    </View>
  );
}
