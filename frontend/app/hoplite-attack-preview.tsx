/**
 * /hoplite-attack-preview — preview deterministica del rig Hoplite.
 *
 * v3: ora emula anche il WRAPPER (transY sink, spriteScale, aura pulse,
 *     hitFlash) che in battle viene applicato da BattleSprite. Così la
 *     contact sheet generata dal preview rispecchia ESATTAMENTE quello che
 *     si vedrà in combat reale. La logica delle animazioni viene riusata
 *     direttamente da `heroBattleAnimations.ts` (single source of truth).
 *
 * Parametri URL opzionali:
 *   ?state=attack|skill|idle → forza uno stato (default: auto-toggle)
 *   ?size=400                → dimensione rig in px (default 400)
 *   ?facing=right|left       → direzione (default right, come player team)
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming,
} from 'react-native-reanimated';
import { useLocalSearchParams } from 'expo-router';
import HeroHopliteRig, { HopliteRigState } from '../components/ui/HeroHopliteRig';
import {
  HOPLITE_PROFILE,
  type AnimHandles,
} from '../components/battle/heroBattleAnimations';

export default function HoplitePreview() {
  const params = useLocalSearchParams<{
    state?: string; size?: string; facing?: string; safe?: string;
  }>();
  const forcedState = (params.state as HopliteRigState) || null;
  const size = parseInt(params.size as string, 10) || 400;
  const facing = (params.facing as string) || 'right';
  const facingScaleX = facing === 'right' ? -1 : 1;
  // safe defaults to true; ?safe=false disables the safe helpers for A/B.
  const safeFill = params.safe !== 'false';

  const [state, setState] = useState<HopliteRigState>(forcedState || 'idle');

  // =========================================================================
  // WRAPPER HANDLES — stessi shared values che usa BattleSprite in battaglia.
  // In questo modo HOPLITE_PROFILE.skill() applica transY/scale/aura come in
  // combat reale e il preview diventa una rappresentazione fedele.
  // =========================================================================
  const transX      = useSharedValue(0);
  const transY      = useSharedValue(0);
  const bodyRot     = useSharedValue(0);
  const spriteScale = useSharedValue(1);
  const spriteOp    = useSharedValue(1);
  const auraOp      = useSharedValue(0);
  const auraSc      = useSharedValue(1);
  const hitFlash    = useSharedValue(0);
  const idleY       = useSharedValue(0);

  const handles: AnimHandles = {
    transX, transY, bodyRot, spriteScale, spriteOp,
    auraOp, auraSc, hitFlash, idleY,
  };

  // Auto-toggle idle ↔ attack se nessuno stato forzato via URL (solo se non
  // è la skill quello che vogliamo validare).
  useEffect(() => {
    if (forcedState) return;
    const loop = setInterval(() => {
      setState(s => (s === 'idle' ? 'attack' : 'idle'));
    }, 1400);
    return () => clearInterval(loop);
  }, [forcedState]);

  // Ogni volta che cambia lo state, triggera la corrispondente anim del
  // profilo Hoplite sui nostri handles locali (così il wrapper si anima).
  useEffect(() => {
    const ctx = { size, isEnemy: false, dir: 1 };
    if (state === 'attack') {
      HOPLITE_PROFILE.attack(handles, ctx);
    } else if (state === 'skill') {
      HOPLITE_PROFILE.skill(handles, ctx);
    } else {
      // ritorno a home (idle)
      transX.value = withTiming(0, { duration: 180 });
      transY.value = withTiming(0, { duration: 180 });
      spriteScale.value = withTiming(1, { duration: 180 });
      auraOp.value = withTiming(0, { duration: 180 });
      auraSc.value = withTiming(1, { duration: 180 });
      hitFlash.value = withTiming(0, { duration: 120 });
    }
  }, [state]);

  // Animated styles applicate sul wrapper del rig (replica BattleSprite)
  const bodyStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: transX.value },
      { translateY: transY.value },
      { scale: spriteScale.value },
    ],
    opacity: spriteOp.value,
  }));

  const auraStyle = useAnimatedStyle(() => ({
    opacity: auraOp.value,
    transform: [{ scale: auraSc.value }],
  }));

  const flashStyle = useAnimatedStyle(() => ({
    opacity: hitFlash.value,
  }));

  const trigger = (s: HopliteRigState) => setState(s);

  const stageW = size;
  const stageH = Math.round(size * 1.25);

  return (
    <View style={styles.root}>
      <View style={styles.stage}>
        <View style={{
          width: stageW,
          height: stageH,
          justifyContent: 'flex-end',
          alignItems: 'center',
        }}>
          {/* Aura layer — dietro al personaggio, come in BattleSprite.
              Volutamente piccola e senza shadow (shadow esplode in CSS web).
              Proporzionata ~60% del body, centrata sulla massa del torso. */}
          <Animated.View
            pointerEvents="none"
            style={[
              styles.auraLayer,
              {
                width: Math.round(size * 0.55),
                height: Math.round(size * 0.55),
                bottom: Math.round(size * 0.25),
              },
              auraStyle,
            ]}
          />

          {/* Body wrapper — applica transX/transY/scale come BattleSprite */}
          <Animated.View style={[styles.body, { width: size, height: size }, bodyStyle]}>
            <View style={{ transform: [{ scaleX: facingScaleX }] }}>
              <HeroHopliteRig size={size} state={state} safeFill={safeFill} />
            </View>
            {/* Hit flash overlay — sovrapposto al rig, come in BattleSprite */}
            <Animated.View
              pointerEvents="none"
              style={[styles.flashLayer, flashStyle]}
            />
          </Animated.View>
        </View>
      </View>
      <Text style={styles.label}>
        state: {state} · size: {size} · safe: {safeFill ? 'ON' : 'OFF'}
      </Text>
      <View style={styles.btns}>
        <Pressable style={styles.btn} onPress={() => trigger('idle')}>
          <Text style={styles.btnTxt}>IDLE</Text>
        </Pressable>
        <Pressable style={[styles.btn, styles.btnRed]} onPress={() => trigger('attack')}>
          <Text style={styles.btnTxt}>AFFONDO DI FALANGE</Text>
        </Pressable>
        <Pressable style={[styles.btn, styles.btnBlue]} onPress={() => trigger('skill')}>
          <Text style={styles.btnTxt}>GUARDIA FERREA</Text>
        </Pressable>
        <Pressable style={[styles.btn, styles.btnViolet]} onPress={() => trigger('stress' as HopliteRigState)}>
          <Text style={styles.btnTxt}>STRESS</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#111',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
  },
  stage: {
    backgroundColor: '#1a1a1a',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    padding: 10,
  },
  // Aura pulse — cerchio dorato morbido dietro al personaggio.
  // Niente shadow (shadow su RN-Web esplode visualmente).
  auraLayer: {
    position: 'absolute',
    borderRadius: 9999,
    backgroundColor: 'rgba(255, 200, 80, 0.45)',
    alignSelf: 'center',
  },
  body: {
    position: 'absolute',
    bottom: 0,
  },
  // Hit flash — overlay bianco/oro sul personaggio
  flashLayer: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 235, 180, 0.9)',
    borderRadius: 12,
  },
  label: {
    color: '#FFD700',
    fontFamily: 'monospace',
    fontSize: 14,
    marginTop: 10,
  },
  btns: { flexDirection: 'row', gap: 10, marginTop: 14 },
  btn: {
    backgroundColor: '#333',
    paddingHorizontal: 14, paddingVertical: 10,
    borderRadius: 6,
  },
  btnRed: { backgroundColor: '#FF4444' },
  btnBlue: { backgroundColor: '#3b82c7' },
  btnViolet: { backgroundColor: '#8844CC' },
  btnTxt: { color: '#fff', fontWeight: '900', fontSize: 13, letterSpacing: 1 },
});
