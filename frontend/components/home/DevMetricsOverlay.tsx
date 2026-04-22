/**
 * DevMetricsOverlay — overlay flottante che mostra i valori runtime reali
 * del layout responsive della home. Usato durante le pass di debug layout
 * per verificare che i numeri teorici coincidano con il rendering reale.
 *
 * Posizionato in alto a destra sotto la currency bar, piccolo ma leggibile.
 * Si disattiva via flag `SHOW_DEV_METRICS` nel parent.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

type Row = { k: string; v: string | number };

export function DevMetricsOverlay({ rows }: { rows: Row[] }) {
  return (
    <View style={s.wrap} pointerEvents="none">
      <Text style={s.title}>DEV · METRICS</Text>
      {rows.map((r, i) => (
        <View key={i} style={s.row}>
          <Text style={s.k}>{r.k}</Text>
          <Text style={s.v}>{typeof r.v === 'number' ? Number(r.v).toFixed(1) : r.v}</Text>
        </View>
      ))}
    </View>
  );
}

const s = StyleSheet.create({
  wrap: {
    position: 'absolute',
    bottom: 140,
    left: 6,
    backgroundColor: 'rgba(0,0,0,0.82)',
    borderWidth: 1,
    borderColor: '#FFD700',
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 4,
    zIndex: 9000,
    minWidth: 148,
  },
  title: {
    color: '#FFD700',
    fontSize: 8,
    fontWeight: '900',
    letterSpacing: 0.5,
    marginBottom: 2,
    textAlign: 'center',
  },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  k: { color: '#F0E8D8', fontSize: 8, fontWeight: '700' },
  v: { color: '#6EC8FF', fontSize: 8, fontWeight: '900' },
});
