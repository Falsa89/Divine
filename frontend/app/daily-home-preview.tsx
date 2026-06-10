/**
 * Pack 98 — Daily home reward preview (test-only).
 *
 * Mostra `DailyHomeRewardSection` con `forceVisible` ON, bypassando i flag
 * di default (che restano OFF in produzione).
 */
import React from 'react';
import { SafeAreaView, ScrollView, StyleSheet, Text } from 'react-native';
import DailyHomeRewardSection from '../src/components/DailyHomeRewardSection';

export default function DailyHomePreviewScreen() {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.h1}>Pack 98 — Daily Home Reward Preview</Text>
        <Text style={styles.meta}>
          Preview test-only. La sezione daily_login + daily_quest in produzione
          richiede AND di entrambi i flag:
          {'\n'}- EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED=true (Pack 97)
          {'\n'}- EXPO_PUBLIC_DAILY_HOME_UNLOCK=true (Pack 98)
          {'\n'}E server scope presente.
        </Text>
        <DailyHomeRewardSection forceVisible />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0d1117' },
  scroll: { padding: 16 },
  h1: { color: '#fff', fontSize: 20, fontWeight: '700', marginBottom: 8 },
  meta: { color: '#9ca3af', fontSize: 12, marginBottom: 16 },
});
