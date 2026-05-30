/**
 * frontend/app/gear-forge-test.tsx
 *
 * PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME_PACK (v24)
 *
 * Sandbox/test screen read-only per visualizzare i 4 subsystem Forge.
 * NESSUNA mutation, NESSUNA chiamata backend obbligatoria in default-disabled state.
 * Route: /gear-forge-test (deeplink only, NON wirata nel menu in questo pack).
 *
 * Vincoli:
 *  - read-only: usa solo constants locali (frontend/constants/gearForge.ts)
 *  - safe area aware
 *  - NO toccare _layout.tsx (route auto-rilevata da expo-router file-based)
 *  - NO toccare home/menu/forge/equipment/soul-forge in questo pack
 *  - NO Gemme / Rune / Artifact / Divine Weapon / Hero Elevation runtime
 */
import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import {
  FORGE_SUBSYSTEMS,
  FUSION_QUALITIES,
  FUSION_MIN_FODDER,
  describeSubsystemState,
} from '../constants/gearForge';

const SCREEN_TAG = 'PROJECT_GEAR_FORGE_FUSION_REFORGE_RUNTIME/v24';

export default function GearForgeTestScreen() {
  const insets = useSafeAreaInsets();
  return (
    <View style={[styles.container, { paddingTop: insets.top, paddingBottom: insets.bottom }]}>
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.backBtn}
          accessibilityRole="button"
          accessibilityLabel="Torna indietro"
          hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
        >
          <Text style={styles.backText}>‹ Indietro</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Forge Gear (TEST)</Text>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.badgeRow}>
        <View style={styles.badge}><Text style={styles.badgeText}>CONTENUTO DI TEST</Text></View>
        <View style={[styles.badge, styles.badgeWarn]}><Text style={styles.badgeText}>PREVIEW-ONLY</Text></View>
        <View style={[styles.badge, styles.badgeInfo]}><Text style={styles.badgeText}>NO MUTATION</Text></View>
        <View style={[styles.badge, styles.badgeWarn]}><Text style={styles.badgeText}>FUSION COMMIT DISABLED</Text></View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.intro}>
          La Forge gestisce 4 subsystem: Potenzia (+level fino a +50), Fondi (qualita su pezzi same-slot in eccesso),
          Riforgia (reroll sub-stat) e Incanta (proprieta magiche, futuro).{'\n'}
          Separato da: Gemme, Rune, Artifact, Divine Weapon, Hero Elevation, BP Delta, Combat.
        </Text>

        <Text style={styles.sectionTitle}>Subsystems Forge</Text>
        {FORGE_SUBSYSTEMS.map((s) => (
          <View key={s.id} style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>{s.label_it}</Text>
              <View style={styles.statePill}><Text style={styles.statePillTxt}>{describeSubsystemState(s.runtime_state)}</Text></View>
            </View>
            <Text style={styles.cardBody}>{s.description_it}</Text>
            <Text style={styles.cardMeta}>id: {s.id}</Text>
          </View>
        ))}

        <Text style={styles.sectionTitle}>Fusion: qualita canoniche</Text>
        <View style={styles.pillRow}>
          {FUSION_QUALITIES.map((q) => (
            <View key={q} style={styles.qualityPill}><Text style={styles.qualityPillTxt}>{q}</Text></View>
          ))}
        </View>
        <Text style={styles.helperTxt}>Minimo fodder per quality-up: {FUSION_MIN_FODDER}</Text>

        <Text style={styles.sectionTitle}>Stato runtime</Text>
        <View style={styles.infoBox}>
          <Text style={styles.infoLine}>• Endpoint: /api/gear-forge/*  (gated da GEAR_FORGE_RUNTIME_PREVIEW_ENABLED)</Text>
          <Text style={styles.infoLine}>• Default: HTTP 503 inert envelope</Text>
          <Text style={styles.infoLine}>• Fusion commit: DISABLED in questo pack (safety audit pending)</Text>
          <Text style={styles.infoLine}>• Legacy /forge/*: NON modificato</Text>
          <Text style={styles.infoLine}>• DB writes: 0</Text>
          <Text style={styles.infoLine}>• Materiali spesi: 0</Text>
        </View>

        <Text style={styles.footerText}>{`tag=${SCREEN_TAG}`}</Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#080816' },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 12,
    borderBottomWidth: 1, borderBottomColor: '#1f1f33',
  },
  backBtn: { minHeight: 44, minWidth: 88, justifyContent: 'center' },
  backText: { color: '#9ea0c8', fontSize: 16, fontWeight: '600' },
  title: { color: '#fff', fontSize: 18, fontWeight: '700' },
  headerSpacer: { width: 88 },
  badgeRow: { flexDirection: 'row', gap: 8, paddingHorizontal: 16, paddingTop: 10, flexWrap: 'wrap' },
  badge: {
    paddingHorizontal: 10, paddingVertical: 4,
    backgroundColor: '#252540', borderRadius: 6, borderWidth: 1, borderColor: '#3a3a55',
  },
  badgeWarn: { backgroundColor: '#3a2a16', borderColor: '#6b4a1f' },
  badgeInfo: { backgroundColor: '#16243a', borderColor: '#1f4a6b' },
  badgeText: { color: '#d8d8f0', fontSize: 10, fontWeight: '700', letterSpacing: 0.5 },
  scrollContent: { paddingHorizontal: 16, paddingTop: 12, paddingBottom: 32 },
  intro: { color: '#bcbcd8', fontSize: 13, lineHeight: 19, marginBottom: 16 },
  sectionTitle: { color: '#fff', fontSize: 14, fontWeight: '700', marginTop: 18, marginBottom: 8, letterSpacing: 0.3 },
  card: {
    backgroundColor: '#141425', borderRadius: 10, borderWidth: 1, borderColor: '#22223a',
    padding: 12, marginBottom: 8,
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  cardTitle: { color: '#fff', fontSize: 14, fontWeight: '700' },
  cardBody: { color: '#bcbcd8', fontSize: 12, lineHeight: 18, marginBottom: 4 },
  cardMeta: { color: '#5a5c7a', fontSize: 10, fontWeight: '600' },
  statePill: {
    paddingHorizontal: 8, paddingVertical: 3,
    backgroundColor: '#1a1a2e', borderRadius: 6, borderWidth: 1, borderColor: '#2a2a44',
  },
  statePillTxt: { color: '#d8d8f0', fontSize: 9, fontWeight: '700', letterSpacing: 0.4 },
  pillRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 8 },
  qualityPill: {
    paddingHorizontal: 12, paddingVertical: 6,
    backgroundColor: '#1a1a2e', borderRadius: 16, borderWidth: 1, borderColor: '#2a2a44',
  },
  qualityPillTxt: { color: '#d8d8f0', fontSize: 11, fontWeight: '700', textTransform: 'capitalize' },
  helperTxt: { color: '#9ea0c8', fontSize: 12, marginTop: 4 },
  infoBox: {
    backgroundColor: '#0f0f1e', borderRadius: 10, borderWidth: 1, borderColor: '#22223a', padding: 12,
  },
  infoLine: { color: '#bcbcd8', fontSize: 12, lineHeight: 19 },
  footerText: { color: '#5a5c7a', fontSize: 10, marginTop: 20 },
});
