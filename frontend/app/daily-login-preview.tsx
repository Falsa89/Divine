/**
 * Pack 97 — Daily login claim preview page (test-only).
 *
 * Per ispezione manuale durante QA. NON linkata dalla home in produzione.
 * Visibile solo navigando esplicitamente a `/daily-login-preview`.
 *
 * Forza visibile il `DailyLoginClaimButton` indipendentemente dal feature flag
 * tramite la prop `forceVisible`. NON cambia il default produzione.
 */
import React from 'react';
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import DailyLoginClaimButton from '../src/components/DailyLoginClaimButton';

export default function DailyLoginPreviewScreen() {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.h1}>Pack 97 — Daily Login Claim Preview</Text>
        <Text style={styles.meta}>
          Questa pagina e' un preview di test per il componente DailyLoginClaimButton.
          NON e' linkata dalla home in produzione.
        </Text>
        <View style={styles.card}>
          <DailyLoginClaimButton forceVisible />
        </View>
        <Text style={styles.note}>
          Endpoint backend: POST /api/daily-login/claim?server_id=&lt;sid&gt;{'\n'}
          Health: GET /api/daily-login/claim/health{'\n'}
          Default UI: hidden (EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED=false){'\n'}
          Kill switches AND: REWARD_CLAIM_LEDGER_LIVE_ENABLED + DAILY_LOGIN_CLAIM_ENABLED
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0d1117' },
  scroll: { padding: 16 },
  h1: { color: '#fff', fontSize: 20, fontWeight: '700', marginBottom: 8 },
  meta: { color: '#9ca3af', fontSize: 12, marginBottom: 16 },
  card: { padding: 8, marginVertical: 8 },
  note: { color: '#6b7280', fontSize: 11, marginTop: 16 },
});
