/*
 * VisualBattlePreviewShell.tsx
 *
 * Top-level preview-only visual shell. Renders the playback envelope returned by
 * /api/generic-visual-battle-runner-preview/playback-preview as a battle-like UI:
 *  - title + debug line (battle_instance_id / viewer_kind / runner_mode)
 *  - Team / Enemy HP bars (deterministic from snapshots + log)
 *  - Timeline stepper with hit markers / camera cues
 *  - Result summary panel
 *  - Safety footer
 *
 * Hard invariants (also enforced by validator track A):
 *  - No /api/battle/simulate or /api/story/battle call.
 *  - No reward / claim / commit button.
 *  - No AsyncStorage write.
 *  - No battle simulation (rendering is data-driven).
 *  - PREVIEW ONLY / NO REWARDS label always visible.
 */
import React, { useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { VisualBattlePreviewHpBars } from './VisualBattlePreviewHpBars';
import { VisualBattleTimelinePlayer } from './VisualBattleTimelinePlayer';
import { VisualBattleSafetyPanel } from './VisualBattleSafetyPanel';

type PlaybackEnvelope = {
  status?: string;
  runner_mode?: string;
  viewer_kind?: string;
  battle_instance_id?: string;
  timeline?: Array<{ t?: number; event?: string }>;
  result_summary?: Record<string, any>;
  validation?: { valid?: boolean; missing_fields?: string[] };
  safety_flags?: Record<string, unknown>;
  notes?: string[];
};

type Payload = Record<string, any>;

export function VisualBattlePreviewShell(props: {
  payload: Payload | null;
  playback: PlaybackEnvelope | null;
}) {
  const { payload, playback } = props;
  const [activeTurn, setActiveTurn] = useState(0);

  if (!payload || !playback || playback.status !== 'preview_ok') {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>Nessun playback envelope disponibile.</Text>
      </View>
    );
  }

  const team = (payload?.team_snapshot?.heroes || []) as any[];
  const enemies = (payload?.enemy_snapshot?.enemies || []) as any[];
  const log = ((payload?.battle_seed_or_precomputed_battle_log?.precomputed_battle_log || []) as any[]);
  const timeline = (playback.timeline || []) as any[];

  return (
    <View>
      <View style={styles.headerCard}>
        <Text style={styles.titleCenter}>Generic Visual Battle Runner Preview</Text>
        <Text style={styles.subtitleCenter}>PREVIEW ONLY · NO REWARDS</Text>
        <View style={styles.debugRow}>
          <Text style={styles.debugText} numberOfLines={1}>
            bi_id: {playback.battle_instance_id}
          </Text>
          <Text style={styles.debugText}>
            viewer: {playback.viewer_kind} · mode: {playback.runner_mode}
          </Text>
        </View>
      </View>

      <View style={styles.battleRow}>
        <View style={styles.battleCol}>
          <VisualBattlePreviewHpBars
            title="Team"
            side="team"
            combatants={team}
            log={log}
            activeTurn={activeTurn}
          />
        </View>
        <View style={styles.battleCol}>
          <VisualBattlePreviewHpBars
            title="Enemy"
            side="enemy"
            combatants={enemies}
            log={log}
            activeTurn={activeTurn}
          />
        </View>
      </View>

      <VisualBattleTimelinePlayer
        timeline={timeline}
        log={log}
        onActiveTurnChange={setActiveTurn}
      />

      <View style={styles.resultCard}>
        <Text style={styles.resultTitle}>Result Summary (display-only)</Text>
        <Row label="winner" value={String((playback.result_summary as any)?.winner || '—')} />
        <Row label="mvp_hero_id" value={String((playback.result_summary as any)?.mvp_hero_id || '—')} />
        <Row label="stars" value={String((playback.result_summary as any)?.stars || '—')} />
        <Row
          label="duration_seconds"
          value={String((playback.result_summary as any)?.duration_seconds || '—')}
        />
      </View>

      <VisualBattleSafetyPanel />
    </View>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  empty: { padding: 24, alignItems: 'center' },
  emptyText: { color: '#8d9099', fontSize: 12 },
  headerCard: {
    backgroundColor: '#1a1e26',
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: '#272c36',
    marginBottom: 10,
    alignItems: 'center',
  },
  titleCenter: { color: '#f4eccd', fontSize: 16, fontWeight: '700' },
  subtitleCenter: { color: '#cbb064', fontSize: 11, marginTop: 4, letterSpacing: 1 },
  debugRow: { width: '100%', marginTop: 8, gap: 2 },
  debugText: { color: '#8d9099', fontSize: 11, textAlign: 'center' },
  battleRow: { flexDirection: 'row', gap: 8 },
  battleCol: { flex: 1 },
  resultCard: {
    backgroundColor: '#1a1e26',
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: '#272c36',
    marginBottom: 10,
  },
  resultTitle: { color: '#f4eccd', fontSize: 14, fontWeight: '700', marginBottom: 6 },
  row: { flexDirection: 'row', paddingVertical: 3 },
  rowLabel: { color: '#aab0ba', fontSize: 12, flex: 1 },
  rowValue: { color: '#e6e8ec', fontSize: 12, flex: 1, textAlign: 'right' },
});

export default VisualBattlePreviewShell;
