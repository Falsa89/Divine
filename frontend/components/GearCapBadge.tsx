/**
 * frontend/components/GearCapBadge.tsx
 *
 * PROJECT_GEAR_CAP_PLUS_50_RUNTIME_PACK (v23)
 *
 * Badge read-only che mostra il +level corrente vs cap canonico (+50) con band color hint per stage.
 * NESSUNA mutation. NESSUNA chiamata backend. Usa solo constants locali.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import {
  GEAR_CAP_CANONICAL,
  GEAR_STAGED_CAPS,
  resolveGearStage,
  type GearStagedCap,
} from '../constants/gearCap';

export type GearCapBadgeProps = {
  level?: number;
  stage?: GearStagedCap;
  size?: 'sm' | 'md' | 'lg';
};

export default function GearCapBadge({ level, stage, size = 'md' }: GearCapBadgeProps) {
  const resolvedStage: GearStagedCap | null =
    stage ?? (typeof level === 'number' ? resolveGearStage(level) : GEAR_STAGED_CAPS[0]);
  const lvl = typeof level === 'number' ? Math.max(0, Math.min(level, GEAR_CAP_CANONICAL)) : null;
  const color = resolvedStage?.display_color_hint ?? '#9ea0c8';
  const labelIt = resolvedStage?.label_it ?? 'Avvio';
  const stageId = resolvedStage?.stage_id ?? 'early';

  const sizeStyle = size === 'lg' ? styles.lg : size === 'sm' ? styles.sm : styles.md;

  return (
    <View
      style={[styles.container, sizeStyle, { borderColor: color }]}
      accessibilityRole="text"
      accessibilityLabel={`Gear ${lvl ?? 0} su ${GEAR_CAP_CANONICAL}, stage ${labelIt}`}
    >
      <View style={[styles.colorBand, { backgroundColor: color }]} />
      <View style={styles.contentCol}>
        <Text style={styles.levelTxt}>
          {lvl !== null ? `+${lvl}` : '+0'} <Text style={styles.capTxt}>/ +{GEAR_CAP_CANONICAL}</Text>
        </Text>
        <Text style={[styles.stageTxt, { color }]}>{labelIt}</Text>
        <Text style={styles.stageIdTxt}>{stageId.toUpperCase()}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#141425',
    borderRadius: 8,
    borderWidth: 1,
    paddingRight: 12,
    overflow: 'hidden',
    minHeight: 44,
  },
  colorBand: { width: 6, alignSelf: 'stretch' },
  contentCol: { paddingLeft: 10, paddingVertical: 6, flex: 1 },
  levelTxt: { color: '#fff', fontSize: 16, fontWeight: '800', letterSpacing: 0.3 },
  capTxt: { color: '#9ea0c8', fontSize: 12, fontWeight: '600' },
  stageTxt: { fontSize: 12, fontWeight: '700', marginTop: 2 },
  stageIdTxt: { color: '#5a5c7a', fontSize: 9, fontWeight: '700', letterSpacing: 1 },
  sm: { minHeight: 36 },
  md: { minHeight: 44 },
  lg: { minHeight: 56 },
});
