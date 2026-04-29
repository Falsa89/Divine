/**
 * BattleReport — detailed post-battle report (v16.22 Foundation)
 * ───────────────────────────────────────────────────────────────
 * Mostra una tabella ALLEATI vs NEMICI con damage_dealt / received / heal
 * + MVP highlight per parte. In-tree overlay (no Modal — policy v16.5+).
 */
import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import type { BattleReport, BattleStat } from './postBattleTypes';
import { COLORS } from '../../constants/theme';

export interface BattleReportViewProps {
  visible: boolean;
  onClose: () => void;
  report: BattleReport;
}

export default function BattleReportView({ visible, onClose, report }: BattleReportViewProps) {
  if (!visible) return null;
  return (
    <View style={s.overlay} pointerEvents="auto">
      <TouchableOpacity
        style={StyleSheet.absoluteFill}
        activeOpacity={1}
        onPress={onClose}
      />
      <View style={s.cardWrap}>
        <LinearGradient
          colors={['rgba(11,23,60,0.98)', 'rgba(5,9,26,0.98)']}
          style={s.card}
        >
          <View style={s.header}>
            <Text style={s.title}>{'\uD83D\uDCCA'}  REPORT BATTAGLIA</Text>
            <TouchableOpacity onPress={onClose} hitSlop={{top:10,bottom:10,left:10,right:10}}>
              <Text style={s.close}>{'\u2715'}</Text>
            </TouchableOpacity>
          </View>
          <ScrollView
            style={{ flex: 1 }}
            contentContainerStyle={{ paddingBottom: 12 }}
            showsVerticalScrollIndicator={false}
          >
            <Section
              title="ALLEATI"
              accent="#5BC8FF"
              units={report.allies}
              mvpId={report.mvp_ally_id}
            />
            <View style={{ height: 12 }} />
            <Section
              title="NEMICI"
              accent="#FF6B6B"
              units={report.enemies}
              mvpId={report.mvp_enemy_id}
            />
          </ScrollView>
        </LinearGradient>
      </View>
    </View>
  );
}

function Section({
  title, accent, units, mvpId,
}: { title: string; accent: string; units: BattleStat[]; mvpId?: string }) {
  return (
    <View>
      <Text style={[s.sectionTitle, { color: accent }]}>
        {title} · <Text style={s.sectionCount}>{units.length}</Text>
      </Text>
      <View style={s.tableHead}>
        <Text style={[s.col, s.colName]}>Unità</Text>
        <Text style={[s.col, s.colNum]}>Danno</Text>
        <Text style={[s.col, s.colNum]}>Subito</Text>
        <Text style={[s.col, s.colNum]}>Cura</Text>
      </View>
      {units.map(u => {
        const isMvp = u.unit_id === mvpId;
        return (
          <View key={u.unit_id} style={[s.row, isMvp && s.rowMvp]}>
            <View style={[s.col, s.colName, { flexDirection: 'row', alignItems: 'center', gap: 6 }]}>
              {isMvp && <Text style={s.mvpTag}>MVP</Text>}
              <Text style={[s.unitName, !u.survived && s.unitNameDead]} numberOfLines={1}>
                {u.name || '?'}
              </Text>
              {!u.survived && <Text style={s.deadTag}>{'\uD83D\uDC80'}</Text>}
            </View>
            <Text style={[s.col, s.colNum, s.numTxt]}>{format(u.damage_dealt)}</Text>
            <Text style={[s.col, s.colNum, s.numTxtDim]}>{format(u.damage_received)}</Text>
            <Text style={[s.col, s.colNum, s.numTxtHeal]}>{format(u.healing_done)}</Text>
          </View>
        );
      })}
      {units.length === 0 && (
        <Text style={s.emptyHint}>Nessun dato disponibile</Text>
      )}
    </View>
  );
}

function format(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 10_000)    return `${(n / 1000).toFixed(1)}k`;
  return Math.round(n).toLocaleString();
}

const s = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0, bottom: 0, left: 0, right: 0,
    backgroundColor: 'rgba(0,0,0,0.72)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9700,
    elevation: 9700,
    padding: 16,
  },
  cardWrap: {
    width: '94%',
    maxWidth: 720,
    height: '88%',
    maxHeight: 480,
  },
  card: {
    flex: 1,
    borderRadius: 14,
    borderWidth: 1.5,
    borderColor: 'rgba(255,107,53,0.42)',
    padding: 14,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.08)',
    marginBottom: 10,
  },
  title: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '900',
    letterSpacing: 1,
  },
  close: { color: '#FFD7A8', fontSize: 18, fontWeight: '900' },

  sectionTitle: {
    fontSize: 12,
    fontWeight: '900',
    letterSpacing: 0.8,
    marginBottom: 6,
    paddingLeft: 4,
  },
  sectionCount: { color: 'rgba(255,255,255,0.5)', fontWeight: '600' },

  tableHead: {
    flexDirection: 'row',
    paddingHorizontal: 6,
    paddingVertical: 4,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.08)',
    marginBottom: 4,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 6,
    paddingVertical: 6,
    borderRadius: 6,
    marginBottom: 2,
  },
  rowMvp: {
    backgroundColor: 'rgba(255,215,0,0.10)',
    borderWidth: 1,
    borderColor: 'rgba(255,215,0,0.32)',
  },
  col: { fontSize: 11, color: 'rgba(255,255,255,0.66)', fontWeight: '700' },
  colName: { flex: 1.6 },
  colNum: { flex: 1, textAlign: 'right' },

  unitName: { color: '#fff', fontSize: 11, fontWeight: '700', flexShrink: 1 },
  unitNameDead: { color: 'rgba(255,255,255,0.42)', textDecorationLine: 'line-through' },
  deadTag: { fontSize: 10, marginLeft: 2 },

  mvpTag: {
    color: '#000',
    backgroundColor: '#FFD700',
    fontSize: 8,
    fontWeight: '900',
    paddingHorizontal: 4,
    paddingVertical: 1,
    borderRadius: 3,
    letterSpacing: 0.5,
  },

  numTxt:     { color: '#fff' },
  numTxtDim:  { color: 'rgba(255,107,53,0.85)' },
  numTxtHeal: { color: '#5BFF8A' },

  emptyHint: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 11,
    fontStyle: 'italic',
    textAlign: 'center',
    paddingVertical: 8,
  },
});
