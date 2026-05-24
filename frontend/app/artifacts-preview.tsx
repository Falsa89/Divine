// artifacts-preview.tsx — PROJECT_Y Track C
// Anteprima Collezione Artefatti: read-only, locked. Nessuna evocazione,
// import, potenziamento o bonus live. Mostra categorie/rarita' come placeholder statici.
import React from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity, StatusBar } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '../constants/theme';
import { SafeFeatureCard } from '../components/SafeFeatureCard';

const RARITY_DATA = [
  { stars: 6, color: '#ffd700', label: 'Mitici', count: '—' },
  { stars: 5, color: '#ff8844', label: 'Leggendari', count: '—' },
  { stars: 4, color: '#aa44ff', label: 'Epici', count: '—' },
  { stars: 3, color: '#4488ff', label: 'Rari', count: '—' },
];

const CATEGORIES = [
  { id: 'offensive', label: 'Offensivi', icon: '⚔️' },
  { id: 'defensive', label: 'Difensivi', icon: '🛡️' },
  { id: 'support', label: 'Supporto', icon: '✨' },
  { id: 'special', label: 'Speciali', icon: '💎' },
];

export default function ArtifactsPreviewScreen() {
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
        <Text style={styles.headerTitle}>Anteprima Artefatti</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.banner}>
          <Text style={styles.bannerIcon}>💎</Text>
          <Text style={styles.bannerTitle}>Collezione Artefatti</Text>
          <Text style={styles.bannerSubtitle}>
            Artefatti in anteprima — evocazione, import e bonus non ancora attivi.
          </Text>
        </View>

        <Text style={styles.sectionTitle}>Stato</Text>
        <SafeFeatureCard
          title="Sistema Artefatti"
          subtitle="In attesa di firme di approvazione live import."
          visibility="player_visible_locked"
          lockReason="Richieste 5 firme: ARTIFACT_USER_APPROVAL, _DATA_, _BALANCE_, _ECONOMY_, _RELEASE_"
          icon="🔒"
          statusBadge="In arrivo"
        />

        <Text style={styles.sectionTitle}>Raretà (anteprima)</Text>
        <View style={styles.rarityGrid}>
          {RARITY_DATA.map((r) => (
            <View key={r.stars} style={[styles.rarityCard, { borderColor: r.color + '55' }]}>
              <Text style={[styles.rarityStars, { color: r.color }]}>{'★'.repeat(r.stars)}</Text>
              <Text style={styles.rarityLabel}>{r.label}</Text>
              <Text style={styles.rarityCount}>{r.count}</Text>
            </View>
          ))}
        </View>

        <Text style={styles.sectionTitle}>Categorie (anteprima)</Text>
        {CATEGORIES.map((c) => (
          <SafeFeatureCard
            key={c.id}
            title={c.label}
            subtitle="Categoria in anteprima. Nessuna interazione live disponibile."
            visibility="player_visible_locked"
            lockReason="Bonus ed evocazioni non ancora attivi."
            icon={c.icon}
            statusBadge="Locked"
          />
        ))}

        <View style={styles.footerNote}>
          <Text style={styles.footerNoteText}>
            Nessuna azione live disponibile in questa schermata. Per la pagina interattiva attuale,
            usa la voce “Artefatti & Costellazioni” nel Menu principale.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bgPrimary },
  headerBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    paddingTop: 8,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderLight,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.bgGlass,
  },
  backIcon: { color: COLORS.textPrimary, fontSize: 22, fontWeight: '700' },
  headerTitle: { color: COLORS.textPrimary, fontSize: 18, fontWeight: '800', letterSpacing: 0.5 },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 80 },
  banner: {
    alignItems: 'center',
    padding: 20,
    borderRadius: 16,
    backgroundColor: 'rgba(170,68,255,0.12)',
    borderWidth: 1,
    borderColor: 'rgba(170,68,255,0.35)',
    marginBottom: 20,
  },
  bannerIcon: { fontSize: 36 },
  bannerTitle: {
    color: COLORS.textPrimary,
    fontSize: 20,
    fontWeight: '800',
    marginTop: 8,
  },
  bannerSubtitle: {
    color: COLORS.textSecondary,
    fontSize: 13,
    marginTop: 6,
    textAlign: 'center',
    lineHeight: 18,
  },
  sectionTitle: {
    color: COLORS.gold,
    fontSize: 14,
    fontWeight: '800',
    letterSpacing: 1,
    textTransform: 'uppercase',
    marginTop: 16,
    marginBottom: 10,
  },
  rarityGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  rarityCard: {
    width: '48%',
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    backgroundColor: COLORS.bgGlass,
    marginBottom: 10,
    alignItems: 'center',
  },
  rarityStars: { fontSize: 16, fontWeight: '800' },
  rarityLabel: { color: COLORS.textPrimary, fontSize: 14, fontWeight: '700', marginTop: 4 },
  rarityCount: { color: COLORS.textMuted, fontSize: 12, marginTop: 2 },
  footerNote: {
    marginTop: 16,
    padding: 14,
    borderRadius: 12,
    backgroundColor: COLORS.bgGlass,
    borderWidth: 1,
    borderColor: COLORS.borderLight,
  },
  footerNoteText: {
    color: COLORS.textMuted,
    fontSize: 12,
    fontStyle: 'italic',
    lineHeight: 16,
  },
});
