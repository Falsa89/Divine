/**
 * frontend/app/material-raid-test.tsx
 *
 * PROJECT_MATERIAL_RAID_RUNTIME_PACK (v25)
 *
 * Sandbox/test screen read-only per visualizzare i 5 track e i 5 stage di Material Raid.
 * NESSUNA mutation, NESSUNA chiamata backend obbligatoria in default-disabled state.
 * Route: /material-raid-test (deeplink only, NON wirata nel menu in questo pack).
 *
 * Vincoli:
 *  - read-only: usa solo constants locali (frontend/constants/materialRaid.ts)
 *  - safe area aware
 *  - NO toccare _layout.tsx (route auto-rilevata da expo-router file-based)
 *  - NO toccare home/menu/forge/equipment/soul-forge in questo pack
 *  - NO Gemme / Rune / Artifact / Divine Weapon / Hero Elevation runtime
 *  - NO stamina / tickets / paid attempts
 */
import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import {
  MATERIAL_RAID_TRACKS,
  MATERIAL_RAID_STAGE_IDS,
  MATERIAL_RAID_RECOMMENDED_POWER,
  MATERIAL_RAID_REWARD_FAMILIES,
  describeRuntimeState,
} from '../constants/materialRaid';

const SCREEN_TAG = 'PROJECT_MATERIAL_RAID_RUNTIME/v25';

export default function MaterialRaidTestScreen() {
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
        <Text style={styles.title}>Material Raid (TEST)</Text>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.badgeRow}>
        <View style={styles.badge}><Text style={styles.badgeText}>CONTENUTO DI TEST</Text></View>
        <View style={[styles.badge, styles.badgeWarn]}><Text style={styles.badgeText}>PREVIEW-ONLY</Text></View>
        <View style={[styles.badge, styles.badgeInfo]}><Text style={styles.badgeText}>NO MUTATION</Text></View>
        <View style={[styles.badge, styles.badgeWarn]}><Text style={styles.badgeText}>REWARD CLAIM DISABLED</Text></View>
        <View style={[styles.badge, styles.badgeInfo]}><Text style={styles.badgeText}>NO STAMINA</Text></View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.intro}>
          Modalita PvE per material farm. 5 track totali (2 aperti in preview, 3 bloccati futuri){'\n'}
          5 stage di difficolta I-V con recommended_power crescente. NESSUNA stamina, NESSUN ticket.
        </Text>

        <Text style={styles.sectionTitle}>Tracks</Text>
        {MATERIAL_RAID_TRACKS.map((t) => (
          <View key={t.track_id} style={[styles.card, t.runtime_state === 'locked_deferred' && styles.cardLocked]}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>{t.label_it}</Text>
              <View style={[styles.statePill, t.runtime_state === 'locked_deferred' && styles.statePillLocked]}>
                <Text style={styles.statePillTxt}>{describeRuntimeState(t.runtime_state)}</Text>
              </View>
            </View>
            <Text style={styles.cardBody}>{t.description_it}</Text>
            <Text style={styles.cardMeta}>track_id: {t.track_id}</Text>
          </View>
        ))}

        <Text style={styles.sectionTitle}>Stage I-V (recommended_power)</Text>
        <View style={styles.stagesRow}>
          {MATERIAL_RAID_STAGE_IDS.map((sid) => (
            <View key={sid} style={styles.stagePill}>
              <Text style={styles.stagePillId}>{sid}</Text>
              <Text style={styles.stagePillPwr}>~{(MATERIAL_RAID_RECOMMENDED_POWER[sid] / 1000).toFixed(0)}k</Text>
            </View>
          ))}
        </View>

        <Text style={styles.sectionTitle}>Reward families canoniche</Text>
        {Object.entries(MATERIAL_RAID_REWARD_FAMILIES).map(([fam, ids]) => (
          <View key={fam} style={styles.famCard}>
            <Text style={styles.famTitle}>{fam}</Text>
            <Text style={styles.famBody}>{(ids as readonly string[]).join(', ')}</Text>
          </View>
        ))}

        <Text style={styles.sectionTitle}>Stato runtime</Text>
        <View style={styles.infoBox}>
          <Text style={styles.infoLine}>• Endpoint: /api/material-raid/*  (gated da MATERIAL_RAID_RUNTIME_PREVIEW_ENABLED)</Text>
          <Text style={styles.infoLine}>• Default: HTTP 503 inert envelope</Text>
          <Text style={styles.infoLine}>• Reward claim: DISABLED in questo pack (inventory safety pending)</Text>
          <Text style={styles.infoLine}>• Legacy /raids/*, /inventory: NON modificati</Text>
          <Text style={styles.infoLine}>• DB writes: 0</Text>
          <Text style={styles.infoLine}>• Materiali grant: 0</Text>
          <Text style={styles.infoLine}>• Stamina/tickets/paid: 0</Text>
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
  cardLocked: { opacity: 0.7, borderColor: '#3a2a16' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  cardTitle: { color: '#fff', fontSize: 14, fontWeight: '700', flex: 1, marginRight: 8 },
  cardBody: { color: '#bcbcd8', fontSize: 12, lineHeight: 18, marginBottom: 4 },
  cardMeta: { color: '#5a5c7a', fontSize: 10, fontWeight: '600' },
  statePill: {
    paddingHorizontal: 8, paddingVertical: 3,
    backgroundColor: '#16243a', borderRadius: 6, borderWidth: 1, borderColor: '#1f4a6b',
  },
  statePillLocked: { backgroundColor: '#3a2a16', borderColor: '#6b4a1f' },
  statePillTxt: { color: '#d8d8f0', fontSize: 9, fontWeight: '700', letterSpacing: 0.4 },
  stagesRow: { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
  stagePill: {
    paddingHorizontal: 14, paddingVertical: 8, backgroundColor: '#1a1a2e',
    borderRadius: 10, borderWidth: 1, borderColor: '#2a2a44', alignItems: 'center', minWidth: 64,
  },
  stagePillId: { color: '#fff', fontSize: 16, fontWeight: '800' },
  stagePillPwr: { color: '#9ea0c8', fontSize: 11, fontWeight: '600', marginTop: 2 },
  famCard: {
    backgroundColor: '#141425', borderRadius: 8, borderWidth: 1, borderColor: '#22223a',
    padding: 10, marginBottom: 6,
  },
  famTitle: { color: '#fff', fontSize: 12, fontWeight: '700', marginBottom: 4 },
  famBody: { color: '#9ea0c8', fontSize: 11, lineHeight: 16 },
  infoBox: {
    backgroundColor: '#0f0f1e', borderRadius: 10, borderWidth: 1, borderColor: '#22223a', padding: 12,
  },
  infoLine: { color: '#bcbcd8', fontSize: 12, lineHeight: 19 },
  footerText: { color: '#5a5c7a', fontSize: 10, marginTop: 20 },
});
