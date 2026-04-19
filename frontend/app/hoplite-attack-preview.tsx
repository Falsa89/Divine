/**
 * /hoplite-attack-preview — preview deterministica del rig Hoplite in attack.
 *
 * Uso: navigare a /hoplite-attack-preview per vedere il rig montato in scala
 * grande che alterna idle → attack ogni 2 secondi. Utile per catturare frame
 * esatti dell'animazione "Affondo di Falange" senza dipendere dalla casualità
 * del battle engine.
 *
 * Parametri URL opzionali:
 *   ?state=attack|idle   → forza uno stato (default: auto-toggle)
 *   ?size=400            → dimensione rig in px (default 400)
 *   ?facing=right|left   → direzione (default right, come player team)
 */
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import HeroHopliteRig, { HopliteRigState } from '../components/ui/HeroHopliteRig';

export default function HoplitePreview() {
  const params = useLocalSearchParams<{ state?: string; size?: string; facing?: string }>();
  const forcedState = (params.state as HopliteRigState) || null;
  const size = parseInt(params.size as string, 10) || 400;
  const facing = (params.facing as string) || 'right';
  const facingScaleX = facing === 'right' ? -1 : 1;

  const [state, setState] = useState<HopliteRigState>(forcedState || 'idle');

  // Auto-toggle idle ↔ attack se nessuno stato forzato via URL
  useEffect(() => {
    if (forcedState) return;
    const loop = setInterval(() => {
      setState(s => (s === 'idle' ? 'attack' : 'idle'));
    }, 1400);
    return () => clearInterval(loop);
  }, [forcedState]);

  const trigger = (s: HopliteRigState) => setState(s);

  return (
    <View style={styles.root}>
      <View style={styles.stage}>
        <View style={{
          width: size,
          height: Math.round(size * 1.25),
          justifyContent: 'flex-end',
          alignItems: 'center',
        }}>
          <View style={{ transform: [{ scaleX: facingScaleX }] }}>
            <HeroHopliteRig size={size} state={state} />
          </View>
        </View>
      </View>
      <Text style={styles.label}>state: {state} · size: {size}</Text>
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
  btnTxt: { color: '#fff', fontWeight: '900', fontSize: 13, letterSpacing: 1 },
});
