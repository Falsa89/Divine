/*
 * VisualBattleSafetyPanel.tsx
 *
 * Always-visible footer panel that surfaces the runner safety guarantees.
 * Pure-presentational; never renders claim/commit buttons.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export function VisualBattleSafetyPanel() {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>Safety guarantees · PREVIEW ONLY · NO REWARDS</Text>
      <SafetyRow label="db_writes" value="0" />
      <SafetyRow label="reward_grant_enabled" value="false" />
      <SafetyRow label="exp_grant_enabled" value="false" />
      <SafetyRow label="progress_enabled" value="false" />
      <SafetyRow label="story_progress_enabled" value="false" />
      <SafetyRow label="daily_progress_enabled" value="false" />
      <SafetyRow label="quest_progress_enabled" value="false" />
      <SafetyRow label="achievement_progress_enabled" value="false" />
      <SafetyRow label="battle_simulation_enabled" value="false" />
      <SafetyRow label="calls_battle_engine" value="false" />
      <SafetyRow label="calls_api_battle_simulate" value="false" />
      <SafetyRow label="calls_api_story_battle" value="false" />
      <SafetyRow label="claim_button_enabled" value="false" />
      <SafetyRow label="commit_button_enabled" value="false" />
      <Text style={styles.muted}>
        Deeplink-only sandbox · non collegato da Home/menu/Story/combat.
      </Text>
    </View>
  );
}

function SafetyRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#0f2415',
    borderRadius: 10,
    padding: 14,
    borderWidth: 1,
    borderColor: '#1f4a30',
    marginTop: 4,
  },
  title: { color: '#9fdca7', fontSize: 13, fontWeight: '700', marginBottom: 8 },
  row: { flexDirection: 'row', paddingVertical: 3, gap: 8 },
  rowLabel: { color: '#aab0ba', fontSize: 12, flex: 1 },
  rowValue: { color: '#e6e8ec', fontSize: 12, flex: 1, textAlign: 'right' },
  muted: { color: '#8d9099', fontSize: 11, marginTop: 8 },
});

export default VisualBattleSafetyPanel;
