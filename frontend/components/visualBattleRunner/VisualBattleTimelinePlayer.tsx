/*
 * VisualBattleTimelinePlayer.tsx
 *
 * Deterministic timeline stepper. Plays the supplied playback_timeline using
 * setInterval for visual cue only. No battle simulation. No winner recomputation.
 * No random numbers. No reward UI.
 */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';

type TimelineEvent = {
  t?: number;
  event?: string;
};

type LogEntry = {
  turn?: number;
  actor?: string;
  action?: string;
  target?: string;
  damage?: number;
};

export function VisualBattleTimelinePlayer(props: {
  timeline: TimelineEvent[];
  log: LogEntry[];
  onActiveTurnChange?: (turnIndex: number) => void;
}) {
  const { timeline, log, onActiveTurnChange } = props;
  const safeTimeline = useMemo(() => (Array.isArray(timeline) ? timeline : []), [timeline]);
  const [activeIdx, setActiveIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [shake, setShake] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Map a timeline event index to a "turn" index (1-based in log; we expose 0..N).
  const indexToTurn = (idx: number): number => {
    const evt = safeTimeline[idx];
    if (!evt) return 0;
    const ev = String(evt.event || '');
    const m = ev.match(/turn_(\d+)_animation/);
    if (m) return Number(m[1]);
    if (ev === 'battle_start') return 0;
    if (ev === 'battle_end_winner_team' || ev === 'battle_end_winner_enemy' || ev === 'battle_end_draw') {
      // at end: all damage applied
      return safeTimeline.length;
    }
    return 0;
  };

  useEffect(() => {
    if (onActiveTurnChange) onActiveTurnChange(indexToTurn(activeIdx));
    // simple hit-marker flash when a damage event is on screen
    const ev = safeTimeline[activeIdx]?.event || '';
    if (/turn_\d+_animation/.test(ev)) {
      setShake(true);
      const tid = setTimeout(() => setShake(false), 220);
      return () => clearTimeout(tid);
    }
    return undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeIdx, safeTimeline.length]);

  useEffect(() => {
    if (!playing) {
      if (timerRef.current) clearInterval(timerRef.current);
      timerRef.current = null;
      return;
    }
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setActiveIdx((prev) => {
        if (prev >= safeTimeline.length - 1) {
          setPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 700);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      timerRef.current = null;
    };
  }, [playing, safeTimeline.length]);

  const reset = () => {
    setPlaying(false);
    setActiveIdx(0);
  };
  const step = () => {
    setActiveIdx((p) => Math.min(p + 1, Math.max(0, safeTimeline.length - 1)));
  };

  const activeEvent = safeTimeline[activeIdx];
  const activeLogEntry = useMemo<LogEntry | null>(() => {
    const turn = indexToTurn(activeIdx);
    const found = (log || []).find((l) => l?.turn === turn);
    return found || null;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeIdx, log]);

  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>Timeline Player</Text>
      <View style={[styles.activeBox, shake && styles.shake]}>
        <Text style={styles.activeT}>t = {activeEvent?.t ?? 0}</Text>
        <Text style={styles.activeEvt}>{activeEvent?.event ?? '—'}</Text>
        {activeLogEntry ? (
          <Text style={styles.hitMarker}>
            💥 {activeLogEntry.actor} → {activeLogEntry.target}  (−{activeLogEntry.damage} HP, {activeLogEntry.action})
          </Text>
        ) : (
          <Text style={styles.hitMarkerMuted}>(camera cue / no damage)</Text>
        )}
      </View>

      <View style={styles.controlsRow}>
        <TouchableOpacity style={styles.btn} onPress={reset}>
          <Text style={styles.btnText}>Reset</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.btn} onPress={() => setPlaying((p) => !p)}>
          <Text style={styles.btnText}>{playing ? 'Pause' : 'Play'}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.btn} onPress={step}>
          <Text style={styles.btnText}>Step</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.list} contentContainerStyle={{ paddingBottom: 4 }}>
        {safeTimeline.map((evt, idx) => (
          <View
            key={`${idx}_${evt?.event}`}
            style={[styles.listRow, idx === activeIdx && styles.listRowActive]}
          >
            <Text style={styles.listT}>t={evt?.t ?? 0}</Text>
            <Text style={styles.listEvt}>{evt?.event}</Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1a1e26',
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: '#272c36',
    marginBottom: 10,
  },
  cardTitle: { color: '#f4eccd', fontSize: 14, fontWeight: '700', marginBottom: 8 },
  activeBox: {
    backgroundColor: '#0e1116',
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#3a3f4a',
    marginBottom: 8,
  },
  shake: { borderColor: '#cbb064' },
  activeT: { color: '#cbb064', fontSize: 12, marginBottom: 2 },
  activeEvt: { color: '#e6e8ec', fontSize: 14, fontWeight: '700' },
  hitMarker: { color: '#f4cccc', fontSize: 12, marginTop: 4 },
  hitMarkerMuted: { color: '#8d9099', fontSize: 12, marginTop: 4 },
  controlsRow: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  btn: {
    backgroundColor: '#2a3142',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
  },
  btnText: { color: '#f4eccd', fontWeight: '700', fontSize: 12 },
  list: { maxHeight: 160 },
  listRow: {
    flexDirection: 'row',
    paddingVertical: 4,
    paddingHorizontal: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#272c36',
    gap: 10,
  },
  listRowActive: { backgroundColor: '#2a3142' },
  listT: { color: '#cbb064', fontSize: 11, width: 50 },
  listEvt: { color: '#e6e8ec', fontSize: 11, flex: 1 },
});

export default VisualBattleTimelinePlayer;
