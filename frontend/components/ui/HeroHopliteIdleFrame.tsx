/**
 * HeroHopliteIdleFrame
 * =====================
 * Player IDLE frame-based per Greek Hoplite.
 *
 * REFERENCE LOCKED: idle usa il frame #1 dell'Affondo di Falange
 * (frame_1.png = "IDLE (entry snapshot)") come source-of-truth. Questo
 * frame è l'hoplite in guardia neutra, coerente con la silhouette e la
 * baseline della sequenza attack — quindi idle→attack è una transizione
 * SEAMLESS perché frame 1 è comune a entrambi.
 *
 * Scelta progettuale — "Disciplina tank estrema":
 *   L'idle è STATICO. Niente breathing, niente sway, niente pulse aura.
 *   L'eroe è fermo, pronto a colpire. Coerente con la policy "solo stati
 *   approvati animati, se non c'è un'animazione specifica resta statico".
 *
 * ─────────────────────────────────────────────────────────────────────────
 * NON È UN RIG. NON HA LAYER FRAZIONATI. NON HA TRANSFORM.
 * È il frame PNG completo, allineato feet-to-ground come gli altri player.
 * ─────────────────────────────────────────────────────────────────────────
 *
 * Allineamento identico a HeroHopliteAffondo e HeroHopliteGuardiaFerrea:
 *   - stesso FRAME_W / FRAME_H canvas
 *   - stessa feet anchor (FEET_CX, FEET_CY)
 *   - stesso frameScale/boxTop/boxLeft math
 *   → idle → attack → skill → idle sono transizioni senza salto.
 */
import React from 'react';
import { View, Image, StyleSheet } from 'react-native';
import { HOPLITE_AFFONDO_ASSETS } from './hopliteAssetManifest';

// Usiamo il frame 1 dell'Affondo (= idle entry snapshot) come frame idle.
// È già approvato e garantisce continuità di silhouette con l'attack.
const IDLE_FRAME = HOPLITE_AFFONDO_ASSETS[0];

// Stesso canvas nativo dei frame Affondo (520×400 con feet a 260,390)
const FRAME_W = 520;
const FRAME_H = 400;
const FEET_CX_IN_FRAME = 260;
const FEET_CY_IN_FRAME = 390;

// Costanti di allineamento — stesse di Affondo/GuardiaFerrea
const RIG_FEET_Y_NORM = 800 / 1024;
const RIG_BODY_H_NORM = 0.683;
const FRAME_BODY_H_PX = 341;

type Props = {
  size: number;
};

export default function HeroHopliteIdleFrame({ size }: Props) {
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
        transform: [{ scaleX: -1 }],  // coerente con Affondo/GuardiaFerrea
      }}>
        <Image
          source={IDLE_FRAME}
          style={{ width: renderedW, height: renderedH }}
          resizeMode="contain"
          fadeDuration={0}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { overflow: 'visible' },
});
