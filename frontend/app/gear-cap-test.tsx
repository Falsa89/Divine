/**
 * frontend/app/gear-cap-test.tsx
 *
 * PROJECT_GEAR_CAP_PLUS_50_RUNTIME_PACK (v23)
 *
 * Sandbox/test screen read-only per visualizzare lo staging del Gear Cap (+50).
 * NESSUNA mutation, NESSUNA chiamata backend obbligatoria in default-disabled state.
 * Route: /gear-cap-test (deeplink only, NON wirata nel menu in questo pack).
 *
 * Vincoli:
 *  - read-only: usa solo constants locali (frontend/constants/gearCap.ts)
 *  - safe area aware
 *  - NO toccare _layout.tsx (route auto-rilevata da expo-router file-based)
 *  - NO toccare home/menu in questo pack
 *  - NO Hero Elevation / Gemme / Rune / Artifact / Divine Weapon runtime
 */
import React, { useMemo, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import GearCapBadge from '../components/GearCapBadge';
import {
  GEAR_CAP_CANONICAL,
  GEAR_CAP_LEGACY_TO_REPLACE,
  GEAR_STAGED_CAPS,
  GEAR_SLOTS,
  resolveGearStage,
} from '../constants/gearCap';

const SCREEN_TAG = 'PROJECT_GEAR_CAP_PLUS_50_RUNTIME/v23';
const SAMPLE_LEVELS = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50];

export default function GearCapTestScreen() {
  const insets = useSafeAreaInsets();
  const [selectedLevel, setSelectedLevel] = useState<number>(0);
  const currentStage = useMemo(() => resolveGearStage(selectedLevel), [selectedLevel]);

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
        <Text style={styles.title}>Gear Cap +50 (TEST)</Text>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.badgeRow}>
        <View style={styles.badge}><Text style={styles.badgeText}>CONTENUTO DI TEST</Text></View>
        <View style={[styles.badge, styles.badgeWarn]}><Text style={styles.badgeText}>PREVIEW-ONLY</Text></View>
        <View style={[styles.badge, styles.badgeInfo]}><Text style={styles.badgeText}>NO MUTATION</Text></View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.intro}>
          Cap canonico: +{GEAR_CAP_CANONICAL} (legacy +{GEAR_CAP_LEGACY_TO_REPLACE} marcato come debt){'\n'}
          Stage: Avvio (0-10), Intermedio (11-20), Avanzato (21-35), Endgame (36-50).{'\n'}
          Separato da Hero Elevation, Gemme, Rune, Artifact, Divine Weapon, BP Delta.
        </Text>

        <Text style={styles.sectionTitle}>Stage canonici</Text>
        {GEAR_STAGED_CAPS.map((s) => (
          <View key={s.stage_id} style={styles.stageCard}>
            <View style={[styles.stageColorDot, { backgroundColor: s.display_color_hint }]} />
            <View style={styles.stageInfoCol}>
              <Text style={styles.stageInfoTitle}>{s.label_it} ({s.stage_id})</Text>
              <Text style={styles.stageInfoRange}>+{s.min} → +{s.max}</Text>
              <Text style={styles.stageInfoUnlock}>{s.unlock_via}</Text>
            </View>
          </View>
        ))}

        <Text style={styles.sectionTitle}>Slot disponibili</Text>
        <View style={styles.slotRow}>
          {GEAR_SLOTS.map((sl) => (
            <View key={sl.slot_id} style={styles.slotPill}>
              <Text style={styles.slotPillTxt}>{sl.label_it}</Text>
            </View>
          ))}
        </View>

        <Text style={styles.sectionTitle}>Anteprima badge per livello</Text>
        <Text style={styles.helperTxt}>Tocca un livello per vedere come si presenta il badge:</Text>
        <View style={styles.sampleRow}>
          {SAMPLE_LEVELS.map((lv) => {
            const active = lv === selectedLevel;
            return (
              <TouchableOpacity
                key={lv}
                onPress={() => setSelectedLevel(lv)}
                style={[styles.samplePill, active && styles.samplePillActive]}
                accessibilityRole="button"
                accessibilityLabel={`Seleziona livello ${lv}`}
                hitSlop={{ top: 8, bottom: 8, left: 6, right: 6 }}
              >
                <Text style={[styles.samplePillTxt, active && styles.samplePillTxtActive]}>+{lv}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
        <View style={{ marginTop: 12 }}>
          <GearCapBadge level={selectedLevel} size="lg" />
        </View>
        {currentStage && (
          <Text style={styles.previewMeta}>
            Stage attivo: {currentStage.label_it} ({currentStage.stage_id}){'\n'}
            Sblocco: {currentStage.unlock_via}
          </Text>
        )}

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
  stageCard: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#141425', borderRadius: 10, borderWidth: 1, borderColor: '#22223a',
    padding: 12, marginBottom: 8, gap: 12,
  },
  stageColorDot: { width: 14, height: 14, borderRadius: 7 },
  stageInfoCol: { flex: 1 },
  stageInfoTitle: { color: '#fff', fontSize: 14, fontWeight: '700' },
  stageInfoRange: { color: '#9ea0c8', fontSize: 12, fontWeight: '600', marginTop: 2 },
  stageInfoUnlock: { color: '#6f7196', fontSize: 11, marginTop: 2 },
  slotRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  slotPill: {
    paddingHorizontal: 12, paddingVertical: 6,
    backgroundColor: '#1a1a2e', borderRadius: 16, borderWidth: 1, borderColor: '#2a2a44',
  },
  slotPillTxt: { color: '#d8d8f0', fontSize: 12, fontWeight: '600' },
  helperTxt: { color: '#9ea0c8', fontSize: 12, marginBottom: 8 },
  sampleRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  samplePill: {
    paddingHorizontal: 10, paddingVertical: 6,
    backgroundColor: '#1a1a2e', borderRadius: 8, borderWidth: 1, borderColor: '#2a2a44',
    minHeight: 36, minWidth: 44, justifyContent: 'center', alignItems: 'center',
  },
  samplePillActive: { backgroundColor: '#2a3a55', borderColor: '#4a90e2' },
  samplePillTxt: { color: '#bcbcd8', fontSize: 12, fontWeight: '700' },
  samplePillTxtActive: { color: '#fff' },
  previewMeta: { color: '#9ea0c8', fontSize: 12, marginTop: 10, lineHeight: 18 },
  footerText: { color: '#5a5c7a', fontSize: 10, marginTop: 20 },
});
