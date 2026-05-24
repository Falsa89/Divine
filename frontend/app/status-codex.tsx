// status-codex.tsx — PROJECT_Y Track E
// Codex Status Effects: read-only. Mostra famiglie first-slice e second-slice
// con stato di readiness. Nessun toggle, nessuna attivazione, nessun bottone live.
import React from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity, StatusBar } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '../constants/theme';
import { SafeFeatureCard } from '../components/SafeFeatureCard';

type Family = {
  id: string;
  label: string;
  icon: string;
  description: string;
  slice: 'first' | 'second';
};

const FIRST_SLICE: Family[] = [
  { id: 'attack_buff', label: 'Buff Offensivi', icon: '⚔️', description: 'Aumenti percentuali del danno inflitto (con caps di aggregazione).', slice: 'first' },
  { id: 'defense_buff', label: 'Buff Difensivi', icon: '🛡️', description: 'Riduzioni del danno subito o aumenti della resistenza.', slice: 'first' },
  { id: 'heal_over_time', label: 'Heal-over-Time', icon: '💚', description: 'Rigenerazione progressiva degli HP nel corso del round.', slice: 'first' },
  { id: 'crit_buff', label: 'Crit Buff', icon: '✨', description: 'Aumento di probabilità di colpo critico (cap fisso).', slice: 'first' },
];

const SECOND_SLICE: Family[] = [
  { id: 'debuff_offensive', label: 'Debuff Offensivi', icon: '🔻', description: 'Riduzioni del danno inflitto dal bersaglio.', slice: 'second' },
  { id: 'debuff_defensive', label: 'Debuff Difensivi', icon: '🔺', description: 'Riduzioni della resistenza del bersaglio.', slice: 'second' },
  { id: 'speed_up', label: 'Speed Up', icon: '⚡', description: 'Aumento di velocità / iniziativa del bersaglio.', slice: 'second' },
  { id: 'speed_down', label: 'Speed Down', icon: '🔴', description: 'Riduzione di velocità / iniziativa del bersaglio.', slice: 'second' },
];

export default function StatusCodexScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <LinearGradient
        colors={[COLORS.bgPrimary, COLORS.bgSecondary]}
        style={StyleSheet.absoluteFill}
      />
      <View style={styles.headerBar}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn} accessibilityLabel="Indietro">
          <Text style={styles.backIcon}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Codex Status</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
        <View style={styles.banner}>
          <Text style={styles.bannerIcon}>📘</Text>
          <Text style={styles.bannerTitle}>Codex degli Status Effect</Text>
          <Text style={styles.bannerSubtitle}>
            Consultazione delle famiglie di status. Sola lettura.
          </Text>
        </View>

        <View style={styles.legendBox}>
          <View style={styles.legendRow}>
            <View style={[styles.dot, { backgroundColor: COLORS.success }]} />
            <Text style={styles.legendText}>First-slice — disponibile a livello backend</Text>
          </View>
          <View style={styles.legendRow}>
            <View style={[styles.dot, { backgroundColor: COLORS.warning }]} />
            <Text style={styles.legendText}>Second-slice — in attesa di prod rollout</Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>First-Slice (gated, non-prod ready)</Text>
        {FIRST_SLICE.map((f) => (
          <SafeFeatureCard
            key={f.id}
            title={f.label}
            subtitle={f.description}
            visibility="player_visible_active_read_only"
            icon={f.icon}
            statusBadge="First-Slice"
          />
        ))}

        <Text style={styles.sectionTitle}>Second-Slice (in attesa firme prod)</Text>
        {SECOND_SLICE.map((f) => (
          <SafeFeatureCard
            key={f.id}
            title={f.label}
            subtitle={f.description}
            visibility="player_visible_locked"
            lockReason="In attesa di firme PROD_ROLLOUT_* e STATUS_SECOND_SLICE_PROD_STAGE_*_APPROVAL."
            icon={f.icon}
            statusBadge="Second-Slice"
          />
        ))}

        <View style={styles.footerNote}>
          <Text style={styles.footerNoteText}>
            Questo codex è in sola lettura. Nessun toggle runtime, nessuna attivazione,
            nessun pulsante di rollout esposto.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bgPrimary },
  headerBar: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 12, paddingTop: 8, paddingBottom: 12,
    borderBottomWidth: 1, borderBottomColor: COLORS.borderLight,
  },
  backBtn: {
    width: 40, height: 40, borderRadius: 20,
    alignItems: 'center', justifyContent: 'center',
    backgroundColor: COLORS.bgGlass,
  },
  backIcon: { color: COLORS.textPrimary, fontSize: 22, fontWeight: '700' },
  headerTitle: { color: COLORS.textPrimary, fontSize: 18, fontWeight: '800', letterSpacing: 0.5 },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 80 },
  banner: {
    alignItems: 'center', padding: 20, borderRadius: 16,
    backgroundColor: 'rgba(68,170,255,0.10)',
    borderWidth: 1, borderColor: 'rgba(68,170,255,0.35)',
    marginBottom: 16,
  },
  bannerIcon: { fontSize: 36 },
  bannerTitle: { color: COLORS.textPrimary, fontSize: 20, fontWeight: '800', marginTop: 8 },
  bannerSubtitle: { color: COLORS.textSecondary, fontSize: 13, marginTop: 6, textAlign: 'center' },
  legendBox: {
    padding: 12, borderRadius: 10,
    backgroundColor: COLORS.bgGlass,
    borderWidth: 1, borderColor: COLORS.borderLight,
    marginBottom: 12,
  },
  legendRow: { flexDirection: 'row', alignItems: 'center', marginVertical: 2 },
  dot: { width: 10, height: 10, borderRadius: 5, marginRight: 8 },
  legendText: { color: COLORS.textSecondary, fontSize: 12 },
  sectionTitle: {
    color: COLORS.gold, fontSize: 14, fontWeight: '800',
    letterSpacing: 1, textTransform: 'uppercase',
    marginTop: 16, marginBottom: 10,
  },
  footerNote: {
    marginTop: 16, padding: 14, borderRadius: 12,
    backgroundColor: COLORS.bgGlass,
    borderWidth: 1, borderColor: COLORS.borderLight,
  },
  footerNoteText: { color: COLORS.textMuted, fontSize: 12, fontStyle: 'italic', lineHeight: 16 },
});
