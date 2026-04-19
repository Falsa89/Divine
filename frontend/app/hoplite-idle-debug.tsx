/**
 * HOPLITE IDLE DEBUG — pagina temporanea per dimostrare che il loop
 * usa davvero tutti e 5 i frame, con badge index + timing live.
 *
 * Accesso: /hoplite-idle-debug
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, Image, ScrollView, StyleSheet } from 'react-native';
import { HOPLITE_IDLE_ASSETS } from '../components/ui/hopliteAssetManifest';

import HeroHopliteIdleLoop from '../components/ui/HeroHopliteIdleLoop';

const FRAMES = HOPLITE_IDLE_ASSETS;
const FRAME_DURATIONS_MS = [520, 280, 220, 320, 520];
const FRAME_LABELS = [
  '1 · IDLE BASE',
  '2 · BREATH IN START',
  '3 · GUARD TIGHT PEAK',
  '4 · SETTLE OPEN',
  '5 · LOOP RETURN',
];

export default function HopliteIdleDebug() {
  const [idx, setIdx] = useState(0);
  const [tick, setTick] = useState(0);  // contatore cicli completati
  const idxRef = useRef(0);
  const tickRef = useRef(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let cancelled = false;
    const scheduleNext = () => {
      if (cancelled) return;
      const holdMs = FRAME_DURATIONS_MS[idxRef.current];
      timeoutRef.current = setTimeout(() => {
        if (cancelled) return;
        const next = (idxRef.current + 1) % FRAMES.length;
        idxRef.current = next;
        if (next === 0) {
          tickRef.current += 1;
          setTick(tickRef.current);
        }
        setIdx(next);
        scheduleNext();
      }, holdMs);
    };
    scheduleNext();
    return () => {
      cancelled = true;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#0a0a0a' }} contentContainerStyle={{ padding: 16 }}>
      <Text style={styles.title}>HOPLITE IDLE — DEBUG 5-FRAME PROOF</Text>
      <Text style={styles.subtitle}>
        Timing: 520 / 280 / 220 / 320 / 520 ms · Cycle: 1860ms · Cycles completed: {tick}
      </Text>

      {/* Live loop con badge frame index */}
      <View style={styles.section}>
        <Text style={styles.h2}>LIVE LOOP</Text>
        <View style={styles.liveWrap}>
          <Image source={FRAMES[idx]} style={styles.liveImg} resizeMode="contain" fadeDuration={0} />
          <View style={styles.badgeBox}>
            <Text style={styles.badgeText}>{FRAME_LABELS[idx]}</Text>
            <Text style={styles.badgeSub}>hold = {FRAME_DURATIONS_MS[idx]}ms</Text>
          </View>
        </View>
      </View>

      {/* Contact sheet statico di tutti i 5 frame */}
      <View style={styles.section}>
        <Text style={styles.h2}>CONTACT SHEET (tutti e 5 i frame in parallelo)</Text>
        <View style={styles.row}>
          {FRAMES.map((src, i) => (
            <View key={i} style={[styles.cell, idx === i && styles.cellActive]}>
              <Image source={src} style={styles.cellImg} resizeMode="contain" fadeDuration={0} />
              <Text style={styles.cellLabel}>{FRAME_LABELS[i]}</Text>
              <Text style={styles.cellMs}>{FRAME_DURATIONS_MS[i]}ms</Text>
              {idx === i && <Text style={styles.cellNow}>▶ NOW</Text>}
            </View>
          ))}
        </View>
      </View>

      {/* Facing test: 2 HeroHopliteIdleLoop player (che hanno scaleX:-1 interno)
          wrappati con lo scaleX esterno che BattleSprite applica in battle.
          Simula ESATTAMENTE il render battle. */}
      <View style={styles.section}>
        <Text style={styles.h2}>FACING TEST — come apparirà in battle reale</Text>
        <Text style={styles.note}>
          Questi rendering usano lo stesso player e lo stesso outer wrapper di BattleSprite.
        </Text>
        <View style={styles.facingRow}>
          <View style={styles.facingCell}>
            <Text style={styles.facingLabel}>TEAM A (lato sinistro) → deve guardare DESTRA</Text>
            {/* Team A: outer scaleX = +1 (nessun flip, nativeFacing='right' == target='right') */}
            <View style={[styles.facingBox, { transform: [{ scaleX: 1 }] }]}>
              <HeroHopliteIdleLoop size={200} />
            </View>
          </View>
          <View style={styles.facingCell}>
            <Text style={styles.facingLabel}>TEAM B (lato destro) → deve guardare SINISTRA</Text>
            {/* Team B: outer scaleX = -1 (flip perché nativeFacing='right' != target='left') */}
            <View style={[styles.facingBox, { transform: [{ scaleX: -1 }] }]}>
              <HeroHopliteIdleLoop size={200} />
            </View>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  title: { color: '#FFD700', fontSize: 18, fontWeight: '900', marginBottom: 4 },
  subtitle: { color: '#BFE', fontSize: 12, marginBottom: 16, fontFamily: 'monospace' },
  section: { marginBottom: 20, backgroundColor: '#141414', padding: 12, borderRadius: 8 },
  h2: { color: '#FF9040', fontSize: 13, fontWeight: '800', marginBottom: 8 },
  liveWrap: { alignItems: 'center' },
  liveImg: { width: 300, height: 300, backgroundColor: '#000' },
  badgeBox: { marginTop: 8, backgroundColor: '#000', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 6, borderWidth: 1, borderColor: '#FFD700' },
  badgeText: { color: '#FFD700', fontSize: 16, fontWeight: '900', fontFamily: 'monospace' },
  badgeSub: { color: '#888', fontSize: 11, fontFamily: 'monospace', textAlign: 'center' },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, justifyContent: 'center' },
  cell: { width: 130, padding: 6, backgroundColor: '#000', borderRadius: 6, borderWidth: 1, borderColor: '#333', alignItems: 'center' },
  cellActive: { borderColor: '#FFD700', backgroundColor: '#1a1200' },
  cellImg: { width: 110, height: 110 },
  cellLabel: { color: '#CFC', fontSize: 10, fontWeight: '700', textAlign: 'center', marginTop: 4 },
  cellMs: { color: '#888', fontSize: 9, fontFamily: 'monospace' },
  cellNow: { color: '#FFD700', fontSize: 10, fontWeight: '900', marginTop: 2 },
  facingRow: { flexDirection: 'row', gap: 16, justifyContent: 'center' },
  facingCell: { alignItems: 'center', flex: 1 },
  facingLabel: { color: '#CFE', fontSize: 11, marginBottom: 6, fontWeight: '700' },
  facingBox: { width: 200, height: 200, backgroundColor: '#000', borderRadius: 6, borderWidth: 1, borderColor: '#444' },
  facingImg: { width: 180, height: 180 },
  note: { color: '#888', fontSize: 10, marginBottom: 6, fontStyle: 'italic' },
});
