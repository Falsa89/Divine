/**
 * frontend/app/hero-elevation-test.tsx
 *
 * PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME_PACK (v22)
 *
 * Sandbox/test screen read-only per visualizzare tutti i 15 tier dell'Hero Elevation.
 * NESSUNA mutation, NESSUNA chiamata backend in questo screen (uses local constants only).
 * Route: /hero-elevation-test (deeplink only, NON wirata nel menu in questo pack).
 *
 * Vincoli:
 *  - read-only: usa solo constants locali (frontend/constants/heroElevation.ts)
 *  - safe area aware
 *  - NO toccare _layout.tsx (route auto-rilevata da expo-router file-based)
 *  - NO toccare home/menu in questo pack
 */
import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import HeroElevationBadge from '../components/HeroElevationBadge';
import { HERO_ELEVATION_TIERS } from '../constants/heroElevation';

const SCREEN_TAG = 'PROJECT_HERO_ELEVATION_QUALITY_FRAME_RUNTIME/v22';

export default function HeroElevationTestScreen() {
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
        <Text style={styles.title}>Hero Elevation (TEST)</Text>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.badgeRow}>
        <View style={styles.badge}><Text style={styles.badgeText}>CONTENUTO DI TEST</Text></View>
        <View style={[styles.badge, styles.badgeWarn]}><Text style={styles.badgeText}>PREVIEW-ONLY</Text></View>
        <View style={[styles.badge, styles.badgeInfo]}><Text style={styles.badgeText}>NO MUTATION</Text></View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.intro}>
          Visualizzazione di tutti i {HERO_ELEVATION_TIERS.length} tier canonici. {'\n'}
          Separato da: Hero Level, Star Up, Ascensione, Skill, Costellazioni, Reincarnation, Gear, Gemme, Rune, Artifact, Divine Weapon.
        </Text>
        {HERO_ELEVATION_TIERS.map((t) => (
          <View key={t.tier_id} style={styles.tierCard}>
            <HeroElevationBadge tierId={t.tier_id} size="md" />
          </View>
        ))}
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
  tierCard: {
    backgroundColor: '#141425', borderRadius: 10, borderWidth: 1, borderColor: '#22223a',
    padding: 12, marginBottom: 8,
  },
  footerText: { color: '#5a5c7a', fontSize: 10, marginTop: 16 },
});
