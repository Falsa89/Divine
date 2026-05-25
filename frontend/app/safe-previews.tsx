// safe-previews.tsx — PROJECT_Z Track B
// Hub centralizzato per le anteprime sicure (Pack Y). Read-only, nessuna live
// action. Espone navigazione verso /artifacts-preview, /housing-preview, /status-codex.
import React from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity, StatusBar } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { COLORS } from '../constants/theme';
import { SafeFeatureCard } from '../components/SafeFeatureCard';

type Entry = {
  route: string;
  title: string;
  subtitle: string;
  icon: string;
  badge: string;
  locked: boolean;
};

const ENTRIES: Entry[] = [
  {
    route: '/status-codex',
    title: 'Codex Status Effects',
    subtitle: 'Catalogo famiglie first-slice e second-slice in sola lettura.',
    icon: '\uD83D\uDCD8',
    badge: 'Anteprima',
    locked: false, // read-only attivo
  },
  {
    route: '/artifacts-preview',
    title: 'Anteprima Artefatti',
    subtitle: 'Evocazione, import e bonus non ancora attivi. Solo consultazione.',
    icon: '\uD83D\uDC8E',
    badge: 'In arrivo',
    locked: false,
  },
  {
    route: '/housing-preview',
    title: 'Dimora Divina',
    subtitle: 'Sistema in preparazione. Endpoint preview attualmente 503.',
    icon: '\uD83C\uDFDB\uFE0F',
    badge: 'In arrivo',
    locked: false,
  },
];

export default function SafePreviewsScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <LinearGradient
        colors={[COLORS.bgPrimary, COLORS.bgSecondary]}
        style={StyleSheet.absoluteFill}
      />
      <View style={styles.headerBar}>
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.backBtn}
          accessibilityLabel="Indietro"
          accessibilityRole="button"
        >
          <Text style={styles.backIcon}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Sistemi in preparazione</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.banner}>
          <Text style={styles.bannerIcon}>{'\u2728'}</Text>
          <Text style={styles.bannerTitle}>Anteprime sicure</Text>
          <Text style={styles.bannerSubtitle}>
            Esplora i sistemi in preparazione. Nessuna azione live, solo consultazione.
          </Text>
        </View>

        {ENTRIES.map((e) => (
          // PROJECT_PLAYER_FACING_LEGACY_SURFACES_LOCK_AND_AUDIT — Track B
          // BUG FIX: il wrapper esterno TouchableOpacity intercettava il tap su
          // mobile ma la SafeFeatureCard interna (non locked) era a sua volta
          // TouchableOpacity senza onPress: il press veniva consumato dal child
          // e l'onPress del wrapper non scattava. Soluzione safe navigation-only:
          // passare onPress direttamente alla SafeFeatureCard. Nessuna azione live.
          <SafeFeatureCard
            key={e.route}
            title={e.title}
            subtitle={e.subtitle}
            visibility="player_visible_active_read_only"
            statusBadge={e.badge}
            icon={e.icon}
            onPress={() => router.push(e.route as any)}
            accessibilityRole="link"
            accessibilityHint="Apre la pagina in sola lettura"
            testID={`safe-preview-card-${e.route.replace('/', '')}`}
          />
        ))}

        <View style={styles.footerNote}>
          <Text style={styles.footerNoteText}>
            Tutte le pagine in questa sezione sono in sola lettura. Nessun bottone qui esegue
            azioni produttive: nessuna evocazione, nessun acquisto, nessun cambio server.
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
    width: 40, height: 40, borderRadius: 20,
    alignItems: 'center', justifyContent: 'center',
    backgroundColor: COLORS.bgGlass,
  },
  backIcon: { color: COLORS.textPrimary, fontSize: 22, fontWeight: '700' },
  headerTitle: {
    color: COLORS.textPrimary,
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 80 },
  banner: {
    alignItems: 'center',
    padding: 20,
    borderRadius: 16,
    backgroundColor: 'rgba(255,107,53,0.10)',
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.35)',
    marginBottom: 16,
  },
  bannerIcon: { fontSize: 36 },
  bannerTitle: { color: COLORS.textPrimary, fontSize: 20, fontWeight: '800', marginTop: 8 },
  bannerSubtitle: {
    color: COLORS.textSecondary,
    fontSize: 13,
    marginTop: 6,
    textAlign: 'center',
    lineHeight: 18,
  },
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
