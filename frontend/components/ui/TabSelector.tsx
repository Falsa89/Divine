import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS, SPACING } from '../../constants/theme';

interface TabItem {
  key: string;
  label: string;
  icon?: string;
}

interface Props {
  tabs: TabItem[];
  active: string;
  onChange: (key: string) => void;
  accentColor?: string;
}

export default function TabSelector({ tabs, active, onChange, accentColor }: Props) {
  const color = accentColor || COLORS.gold;
  return (
    <View style={s.container}>
      {tabs.map((tab) => {
        const isActive = tab.key === active;
        return (
          <TouchableOpacity
            key={tab.key}
            style={s.tabWrapper}
            onPress={() => onChange(tab.key)}
            activeOpacity={0.7}
          >
            <View style={[s.tab, isActive && { backgroundColor: color + '15' }]}>
              {tab.icon && <Text style={[s.icon, isActive && { color }]}>{tab.icon}</Text>}
              <Text style={[s.label, isActive && { color }]}>{tab.label}</Text>
            </View>
            {isActive && (
              <LinearGradient
                colors={[color, color + '00']}
                start={{ x: 0.5, y: 0 }}
                end={{ x: 0.5, y: 1 }}
                style={s.indicator}
              />
            )}
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const s = StyleSheet.create({
  container: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  tabWrapper: {
    flex: 1,
    alignItems: 'center',
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
    borderRadius: 6,
    marginHorizontal: 2,
  },
  icon: {
    fontSize: 12,
    color: COLORS.textMuted,
  },
  label: {
    fontSize: 11,
    fontWeight: '800',
    color: COLORS.textMuted,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  indicator: {
    height: 2,
    width: '60%',
    borderRadius: 1,
    marginTop: 2,
  },
});
