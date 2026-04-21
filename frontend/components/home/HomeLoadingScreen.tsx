/**
 * HomeLoadingScreen — schermata di caricamento premium mostrata DOPO il login,
 * PRIMA del primo render completo della home. Resta visibile finché il preload
 * degli asset core (background corrente, bottom nav, PLAY states, frame side,
 * 9 icone, hero home) non è completato.
 *
 * NESSUNA arte improvvisata: solo gradient blu notte + spinner gold + progress
 * bar sottile. Si dissolve via al completamento del preload.
 */
import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

const GOLD      = '#FFD700';
const GOLD_PALE = '#F7D563';
const NIGHT_0   = '#05091A';
const NIGHT_1   = '#0A1838';

type Props = {
  done: number;
  total: number;
  label?: string;
};

export default function HomeLoadingScreen({ done, total, label }: Props) {
  const pct = total > 0 ? Math.min(100, Math.round((done / total) * 100)) : 0;
  return (
    <LinearGradient colors={[NIGHT_0, NIGHT_1, NIGHT_0]} style={s.root}>
      <View style={s.center}>
        <ActivityIndicator size="large" color={GOLD} />
        <Text style={s.title}>{label || 'PREPARAZIONE HOMEPAGE'}</Text>
        <View style={s.barOuter}>
          <View style={[s.barInner, { width: `${pct}%` }]} />
        </View>
        <Text style={s.pct}>
          {total > 0 ? `${done} / ${total}  ·  ${pct}%` : '…'}
        </Text>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  center: { alignItems: 'center', paddingHorizontal: 24, gap: 16 },
  title: {
    color: GOLD, fontSize: 13, fontWeight: '900',
    letterSpacing: 2, marginTop: 16,
  },
  barOuter: {
    width: 260, height: 6,
    backgroundColor: 'rgba(255,215,0,0.15)',
    borderRadius: 3,
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.30)',
    overflow: 'hidden',
  },
  barInner: {
    height: '100%',
    backgroundColor: GOLD_PALE,
  },
  pct: { color: 'rgba(255,255,255,0.70)', fontSize: 10, fontWeight: '700', letterSpacing: 0.8 },
});
