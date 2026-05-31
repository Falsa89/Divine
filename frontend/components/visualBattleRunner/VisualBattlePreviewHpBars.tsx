/*
 * VisualBattlePreviewHpBars.tsx
 *
 * Pure-presentational HP bars driven by deterministic playback data.
 * No animation lib dependency. No async storage. No reward UI.
 */
import React, { useMemo } from 'react';
import { View, Text, StyleSheet } from 'react-native';

type Combatant = {
  slot?: number;
  hero_id?: string;
  enemy_id?: string;
  name?: string;
  hp?: number;
  atk?: number;
};

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

export function VisualBattlePreviewHpBars(props: {
  title: string;
  side: 'team' | 'enemy';
  combatants: Combatant[];
  log: LogEntry[];
  activeTurn: number; // 0..N
}) {
  const { title, side, combatants, log, activeTurn } = props;

  // Compute deterministic remaining HP by replaying the log up to activeTurn.
  const hpRemaining = useMemo(() => {
    const idKey: 'hero_id' | 'enemy_id' = side === 'team' ? 'hero_id' : 'enemy_id';
    const initial: Record<string, number> = {};
    combatants.forEach((c) => {
      const id = (c[idKey] as string | undefined) ?? c.name ?? `slot_${c.slot ?? 0}`;
      initial[id] = Math.max(0, c.hp ?? 0);
    });
    const applied = { ...initial };
    for (const entry of log) {
      if ((entry?.turn ?? 0) > activeTurn) break;
      const tgt = entry?.target;
      if (tgt && tgt in applied) {
        applied[tgt] = Math.max(0, applied[tgt] - (entry?.damage ?? 0));
      }
    }
    return { initial, applied };
  }, [combatants, log, activeTurn, side]);

  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      {combatants.map((c, idx) => {
        const id =
          ((side === 'team' ? c.hero_id : c.enemy_id) as string | undefined) ?? c.name ?? `slot_${idx}`;
        const maxHp = hpRemaining.initial[id] || 1;
        const curHp = hpRemaining.applied[id] ?? maxHp;
        const pct = Math.max(0, Math.min(100, (curHp / maxHp) * 100));
        const dead = curHp <= 0;
        return (
          <View key={id + idx} style={styles.row}>
            <View style={styles.metaCol}>
              <Text style={styles.name} numberOfLines={1}>
                {c.name || id}
              </Text>
              <Text style={styles.hpText}>
                HP {curHp} / {maxHp}
              </Text>
            </View>
            <View style={styles.barTrack}>
              <View
                style={[
                  styles.barFill,
                  {
                    width: `${pct}%`,
                    backgroundColor: dead ? '#5a3a3a' : side === 'team' ? '#3a8a4f' : '#a8341c',
                  },
                ]}
              />
              {dead ? <Text style={styles.deadOverlay}>KO</Text> : null}
            </View>
          </View>
        );
      })}
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
  title: { color: '#f4eccd', fontSize: 14, fontWeight: '700', marginBottom: 8 },
  row: { paddingVertical: 4 },
  metaCol: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 3 },
  name: { color: '#e6e8ec', fontSize: 12, flex: 1 },
  hpText: { color: '#aab0ba', fontSize: 11 },
  barTrack: {
    height: 10,
    backgroundColor: '#0e1116',
    borderRadius: 5,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#272c36',
    justifyContent: 'center',
  },
  barFill: { height: '100%' },
  deadOverlay: {
    position: 'absolute',
    alignSelf: 'center',
    color: '#f4cccc',
    fontSize: 10,
    fontWeight: '700',
  },
});

export default VisualBattlePreviewHpBars;
