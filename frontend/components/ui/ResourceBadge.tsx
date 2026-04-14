import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS } from '../../constants/theme';

interface Props {
  icon: string;
  value: string | number;
  compact?: boolean;
}

export default function ResourceBadge({ icon, value, compact }: Props) {
  return (
    <View style={[s.badge, compact && s.compact]}>
      <Text style={[s.icon, compact && s.iconCompact]}>{icon}</Text>
      <Text style={[s.value, compact && s.valueCompact]}>{typeof value === 'number' ? value.toLocaleString() : value}</Text>
    </View>
  );
}

const s = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: 'rgba(255,255,255,0.06)',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  compact: {
    paddingHorizontal: 6,
    paddingVertical: 3,
  },
  icon: {
    fontSize: 14,
  },
  iconCompact: {
    fontSize: 11,
  },
  value: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '700',
  },
  valueCompact: {
    fontSize: 10,
  },
});
