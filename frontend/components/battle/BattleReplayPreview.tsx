/**
 * BattleReplayPreview.tsx — PROJECT_BATTLE_REPORT_REPLAY_SAVE_SHARE_FOUNDATION_PACK (v26)
 *
 * Overlay VISIVO-ONLY per replay battaglia.
 * NESSUNA chiamata al backend simulate (battle replay non e' una ri-simulazione).
 * NESSUN reward grant. NESSUN EXP grant. NESSUN RNG rerun.
 * Mostra timeline già calcolata e permette play/pause/step/restart/close.
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Modal } from 'react-native';
import type { BattleReplaySnapshotV1 } from './battleReplayTypes';

type Props = {
  visible: boolean;
  snapshot: BattleReplaySnapshotV1 | null;
  onClose: () => void;
};

const STEP_INTERVAL_MS = 900;

export default function BattleReplayPreview({ visible, snapshot, onClose }: Props) {
  const [stepIndex, setStepIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const total = snapshot?.timeline?.length || 0;

  useEffect(() => {
    if (!visible) {
      setStepIndex(0);
      setPlaying(false);
      if (timerRef.current) { clearTimeout(timerRef.current); timerRef.current = null; }
    }
  }, [visible]);

  useEffect(() => {
    if (!playing) {
      if (timerRef.current) { clearTimeout(timerRef.current); timerRef.current = null; }
      return;
    }
    if (stepIndex >= total) {
      setPlaying(false);
      return;
    }
    timerRef.current = setTimeout(() => setStepIndex((i) => Math.min(total, i + 1)), STEP_INTERVAL_MS);
    return () => {
      if (timerRef.current) { clearTimeout(timerRef.current); timerRef.current = null; }
    };
  }, [playing, stepIndex, total]);

  if (!snapshot) return null;

  const visibleEntries = (snapshot.timeline || []).slice(0, stepIndex);

  return (
    <Modal visible={visible} animationType="fade" transparent onRequestClose={onClose}>
      <View style={s.backdrop}>
        <View style={s.sheet}>
          <View style={s.headerRow}>
            <Text style={s.title}>{'▶︎'} REPLAY VISIVO</Text>
            <TouchableOpacity onPress={onClose} hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
              accessibilityRole="button" accessibilityLabel="Chiudi replay">
              <Text style={s.closeTxt}>{'✕'}</Text>
            </TouchableOpacity>
          </View>

          <View style={s.badgeRow}>
            <View style={[s.badge, s.badgeInfo]}><Text style={s.badgeTxt}>NESSUNA RICOMPENSA</Text></View>
            <View style={[s.badge, s.badgeInfo]}><Text style={s.badgeTxt}>NESSUN EXP</Text></View>
            <View style={[s.badge, s.badgeWarn]}><Text style={s.badgeTxt}>VISIVO-ONLY</Text></View>
          </View>

          <View style={s.statsRow}>
            <Text style={s.statTxt}>Esito: {snapshot.outcome === 'victory' ? 'Vittoria' : 'Sconfitta'}</Text>
            <Text style={s.statTxt}>Turni: {snapshot.turns}  ·  Durata: {Math.round(snapshot.duration_sec)}s</Text>
            {snapshot.mvp_ally_name && <Text style={s.statTxt}>MVP: {snapshot.mvp_ally_name}</Text>}
          </View>

          <ScrollView style={s.timelineScroll} contentContainerStyle={{ paddingBottom: 12 }}>
            {visibleEntries.length === 0 ? (
              <Text style={s.emptyTxt}>Premi {'▶︎'} per avviare il replay.</Text>
            ) : (
              visibleEntries.map((e) => (
                <View key={e.index} style={s.entryRow}>
                  <Text style={s.entryIdx}>#{e.index + 1}</Text>
                  <Text style={s.entryTxt}>{e.raw_label}</Text>
                </View>
              ))
            )}
            {stepIndex >= total && total > 0 && (
              <Text style={s.endTxt}>— Fine replay —</Text>
            )}
          </ScrollView>

          <View style={s.controlsRow}>
            <TouchableOpacity
              onPress={() => setPlaying((p) => !p)}
              disabled={stepIndex >= total && total > 0}
              style={[s.ctrlBtn, (stepIndex >= total && total > 0) && s.ctrlBtnDisabled]}
              accessibilityRole="button"
              accessibilityLabel={playing ? 'Pausa' : 'Play'}
            >
              <Text style={s.ctrlTxt}>{playing ? '⏸ Pausa' : '▶ Play'}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => { setPlaying(false); setStepIndex((i) => Math.min(total, i + 1)); }}
              disabled={stepIndex >= total}
              style={[s.ctrlBtn, stepIndex >= total && s.ctrlBtnDisabled]}
              accessibilityRole="button" accessibilityLabel="Avanza di un passo"
            >
              <Text style={s.ctrlTxt}>{'⇥'} Step</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => { setPlaying(false); setStepIndex(0); }}
              style={s.ctrlBtn}
              accessibilityRole="button" accessibilityLabel="Riavvia replay"
            >
              <Text style={s.ctrlTxt}>{'↻'} Riavvia</Text>
            </TouchableOpacity>
          </View>

          <Text style={s.footerTxt}>{`schema_v${snapshot.schema_version} · ${snapshot.replay_id}`}</Text>
        </View>
      </View>
    </Modal>
  );
}

const s = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.78)', justifyContent: 'center', padding: 16 },
  sheet: {
    backgroundColor: '#141425', borderRadius: 14, borderWidth: 1, borderColor: '#2a2a44',
    padding: 14, maxHeight: '90%',
  },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  title: { color: '#fff', fontSize: 16, fontWeight: '800', letterSpacing: 0.5 },
  closeTxt: { color: '#bcbcd8', fontSize: 18, fontWeight: '700' },
  badgeRow: { flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginBottom: 8 },
  badge: {
    paddingHorizontal: 8, paddingVertical: 3,
    backgroundColor: '#252540', borderRadius: 6, borderWidth: 1, borderColor: '#3a3a55',
  },
  badgeInfo: { backgroundColor: '#16243a', borderColor: '#1f4a6b' },
  badgeWarn: { backgroundColor: '#3a2a16', borderColor: '#6b4a1f' },
  badgeTxt: { color: '#d8d8f0', fontSize: 9, fontWeight: '700', letterSpacing: 0.5 },
  statsRow: { marginBottom: 10 },
  statTxt: { color: '#bcbcd8', fontSize: 12, lineHeight: 18 },
  timelineScroll: { backgroundColor: '#0f0f1e', borderRadius: 10, borderWidth: 1, borderColor: '#22223a', padding: 10, marginBottom: 10, maxHeight: 280 },
  emptyTxt: { color: '#9ea0c8', fontSize: 12, textAlign: 'center', paddingVertical: 16 },
  entryRow: { flexDirection: 'row', paddingVertical: 4, gap: 8 },
  entryIdx: { color: '#5a5c7a', fontSize: 11, fontWeight: '700', minWidth: 28 },
  entryTxt: { color: '#d8d8f0', fontSize: 12, flex: 1, lineHeight: 18 },
  endTxt: { color: '#7c7e9c', fontSize: 11, textAlign: 'center', marginTop: 10, fontStyle: 'italic' },
  controlsRow: { flexDirection: 'row', gap: 8, justifyContent: 'space-between' },
  ctrlBtn: {
    flex: 1, paddingVertical: 10, paddingHorizontal: 8,
    backgroundColor: '#1a1a2e', borderRadius: 8, borderWidth: 1, borderColor: '#2a2a44',
    alignItems: 'center', minHeight: 44, justifyContent: 'center',
  },
  ctrlBtnDisabled: { opacity: 0.4 },
  ctrlTxt: { color: '#fff', fontSize: 13, fontWeight: '700' },
  footerTxt: { color: '#5a5c7a', fontSize: 9, marginTop: 8, textAlign: 'center' },
});
