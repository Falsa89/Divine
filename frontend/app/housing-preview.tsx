// housing-preview.tsx — PROJECT_Y Track D
// Anteprima Dimora Divina: locked / read-only. Tenta GET /api/housing/preview
// e gestisce 503 graziosamente con copy lock. Nessun bonus, potenziamento, spend o
// resident assignment esposto.
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity, ActivityIndicator, StatusBar } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Constants from 'expo-constants';
import { COLORS } from '../constants/theme';
import { SafeFeatureCard } from '../components/SafeFeatureCard';

type EndpointState = 'loading' | 'preview_503' | 'unavailable' | 'live';

const BACKEND_URL =
  (process.env.EXPO_BACKEND_URL as string | undefined) ||
  (Constants?.expoConfig?.extra as any)?.backendUrl ||
  '';

export default function HousingPreviewScreen() {
  const router = useRouter();
  const [state, setState] = useState<EndpointState>('loading');

  useEffect(() => {
    let alive = true;
    const url = BACKEND_URL ? `${BACKEND_URL}/api/housing/preview` : '/api/housing/preview';
    fetch(url)
      .then((r) => {
        if (!alive) return;
        if (r.status === 503) setState('preview_503');
        else if (r.status === 200) setState('live');
        else setState('unavailable');
      })
      .catch(() => {
        if (alive) setState('unavailable');
      });
    return () => { alive = false; };
  }, []);

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
        <Text style={styles.headerTitle}>Dimora Divina</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.banner}>
          <Text style={styles.bannerIcon}>🏛️</Text>
          <Text style={styles.bannerTitle}>Dimora Divina in preparazione</Text>
          <Text style={styles.bannerSubtitle}>
            Bonus, residenti e potenziamenti non sono ancora attivi.
          </Text>
        </View>

        <Text style={styles.sectionTitle}>Stato endpoint</Text>
        {state === 'loading' && (
          <View style={styles.loadingWrap}>
            <ActivityIndicator color={COLORS.accent} />
            <Text style={styles.loadingText}>Verifica disponibilità…</Text>
          </View>
        )}
        {state === 'preview_503' && (
          <SafeFeatureCard
            title="Endpoint /api/housing/preview"
            subtitle="Servizio temporaneamente disabilitato."
            visibility="player_visible_locked"
            endpointStatus="preview_503"
            lockReason="Il servizio anteprima Dimora è attualmente disabilitato (HTTP 503). In attesa di firme HOUSING_LIVE_BONUS_*."
            icon="⚠️"
            statusBadge="503"
          />
        )}
        {state === 'live' && (
          <SafeFeatureCard
            title="Endpoint /api/housing/preview"
            subtitle="Anteprima dati disponibile. Bonus live restano comunque disattivati in UI."
            visibility="player_visible_active_read_only"
            endpointStatus="live"
            icon="🔗"
            statusBadge="Online"
          />
        )}
        {state === 'unavailable' && (
          <SafeFeatureCard
            title="Endpoint /api/housing/preview"
            subtitle="Non raggiungibile in questo momento."
            visibility="player_visible_locked"
            lockReason="Errore di rete o servizio temporaneamente non disponibile."
            icon="🌐"
            statusBadge="Offline"
          />
        )}

        <Text style={styles.sectionTitle}>Feature future (anteprima)</Text>
        <SafeFeatureCard
          title="Stanze & Arredamento"
          subtitle="Personalizza la tua Dimora con stanze tematiche."
          visibility="player_visible_locked"
          lockReason="In attesa di firme HOUSING_LIVE_BONUS_USER_APPROVAL."
          icon="🛋️"
          statusBadge="In arrivo"
        />
        <SafeFeatureCard
          title="Residenti Eroi"
          subtitle="Assegna eroi come residenti per ottenere bonus passivi."
          visibility="player_visible_locked"
          lockReason="In attesa di firme HOUSING_LIVE_BONUS_BALANCE_APPROVAL."
          icon="👪"
          statusBadge="In arrivo"
        />
        <SafeFeatureCard
          title="Bonus Passivi Giornalieri"
          subtitle="Genera risorse passive in base alla configurazione."
          visibility="player_visible_locked"
          lockReason="In attesa di firme HOUSING_LIVE_BONUS_ECONOMY_APPROVAL."
          icon="💎"
          statusBadge="In arrivo"
        />

        <View style={styles.footerNote}>
          <Text style={styles.footerNoteText}>
            Nessuna azione live disponibile. Tutte le interazioni sono in modalità anteprima statica.
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
  headerTitle: { color: COLORS.textPrimary, fontSize: 18, fontWeight: '800', letterSpacing: 0.5 },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 80 },
  banner: {
    alignItems: 'center',
    padding: 20,
    borderRadius: 16,
    backgroundColor: 'rgba(255,170,68,0.10)',
    borderWidth: 1,
    borderColor: 'rgba(255,170,68,0.35)',
    marginBottom: 20,
  },
  bannerIcon: { fontSize: 36 },
  bannerTitle: { color: COLORS.textPrimary, fontSize: 20, fontWeight: '800', marginTop: 8 },
  bannerSubtitle: { color: COLORS.textSecondary, fontSize: 13, marginTop: 6, textAlign: 'center', lineHeight: 18 },
  sectionTitle: {
    color: COLORS.gold, fontSize: 14, fontWeight: '800',
    letterSpacing: 1, textTransform: 'uppercase',
    marginTop: 16, marginBottom: 10,
  },
  loadingWrap: {
    padding: 16,
    alignItems: 'center',
    backgroundColor: COLORS.bgGlass,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.borderLight,
  },
  loadingText: { color: COLORS.textMuted, marginTop: 8, fontSize: 13 },
  footerNote: {
    marginTop: 16, padding: 14, borderRadius: 12,
    backgroundColor: COLORS.bgGlass,
    borderWidth: 1, borderColor: COLORS.borderLight,
  },
  footerNoteText: { color: COLORS.textMuted, fontSize: 12, fontStyle: 'italic', lineHeight: 16 },
});
