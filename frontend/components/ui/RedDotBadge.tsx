/**
 * Pre-QA Stabilization 116C — RedDotBadge (visual-only component).
 *
 * Render: dot semplice o count capped (`9+` / `99+`).
 * NESSUNA logica di claim/mutation/spend.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

type Severity = 'none' | 'info' | 'warning';

interface Props {
  hasDot: boolean;
  count?: number;
  severity?: Severity;
  cap?: 9 | 99;
  size?: number;
}

export default function RedDotBadge({ hasDot, count = 0, severity = 'info', cap = 99, size = 8 }: Props) {
  if (!hasDot) return null;
  const showCount = count > 0;
  const color = severity === 'warning' ? '#FFB700' : '#E53935';
  const text = showCount ? (count > cap ? `${cap}+` : String(count)) : '';
  const minWidth = showCount ? size * 2 : size;
  return (
    <View style={[s.badge, { backgroundColor: color, minWidth, height: showCount ? size * 1.8 : size, borderRadius: size }]}>
      {showCount ? <Text style={[s.txt, { fontSize: size * 0.9 }]}>{text}</Text> : null}
    </View>
  );
}

const s = StyleSheet.create({
  badge: {
    paddingHorizontal: 3,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.4)',
  },
  txt: { color: '#FFFFFF', fontWeight: '800' },
});
