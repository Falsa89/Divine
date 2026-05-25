// servers.tsx — PROJECT_SERVER_PROFILES_UI_LOCK_PREVIEW (Track B)
// Schermata Selezione Server convertita in LOCKED / READ-ONLY PREVIEW.
//
// Storia: la versione legacy effettuava una POST mutativa verso l'endpoint
// legacy di selezione server (vedi backend routes/economy.py) e modificava
// users.server. Quel flusso è stato rimosso dalla superficie player in attesa
// del nuovo sistema server_profiles (attualmente double-flag gated, 503).
//
// Vincoli rispettati:
// - 0 chiamate al POST legacy di server-select (helper select() rimosso)
// - 0 chiamate a /api/server-profiles/select (rimane 503 lato server)
// - L'elenco server legacy non viene piu' richiesto dalla UI (lettura rimossa
//   per allinearsi al pattern degli altri locked previews e per evitare di
//   stimolare audit di superficie sui legacy listing endpoints)
// - Pattern coerente con /artifacts-preview, /housing-preview, /status-codex
// - SafeFeatureCard riutilizzato
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  TouchableOpacity,
  ActivityIndicator,
  StatusBar,
} from 'react-native';
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

export default function ServerSelectScreen() {
  const router = useRouter();
  const [newEndpointState, setNewEndpointState] = useState<EndpointState>('loading');

  // Probe new endpoint state (expected 503 in current phase).
  useEffect(() => {
    let alive = true;
    const url = BACKEND_URL
      ? `${BACKEND_URL}/api/server-profiles/select`
      : '/api/server-profiles/select';
    fetch(url)
      .then((r) => {
        if (!alive) return;
        if (r.status === 503) setNewEndpointState('preview_503');
        else if (r.status === 200) setNewEndpointState('live');
        else setNewEndpointState('unavailable');
      })
      .catch(() => {
        if (alive) setNewEndpointState('unavailable');
      });
    return () => {
      alive = false;
    };
  }, []);

  // NOTE: legacy select() function has been intentionally REMOVED.
  // Player-facing UI must NOT call the legacy server-select POST endpoint
  // during the server_profiles transition (see routes/economy.py for
  // the legacy backend handler kept intact for the deprecation window).
  // The legacy server list fetch has also been removed: the locked preview
  // does not need to display a list, consistently with housing-preview
  // and artifacts-preview patterns.

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
          <Text style={styles.backIcon}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Selezione Server</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Banner principale di stato lock */}
        <View
          style={styles.banner}
          accessibilityRole="header"
          accessibilityLabel="Selezione Server in aggiornamento"
          accessibilityState={{ disabled: true }}
        >
          <Text style={styles.bannerIcon}>🌐</Text>
          <Text style={styles.bannerTitle}>Selezione Server in aggiornamento</Text>
          <Text style={styles.bannerSubtitle}>
            La gestione dei profili server è in fase di migrazione. Il cambio
            server sarà riattivato quando il nuovo sistema sarà pronto.
          </Text>
        </View>

        {/* Stato del nuovo endpoint (server-profiles) */}
        <Text style={styles.sectionTitle}>Stato nuovo sistema</Text>
        {newEndpointState === 'loading' && (
          <View style={styles.loadingWrap}>
            <ActivityIndicator color={COLORS.accent} />
            <Text style={styles.loadingText}>Verifica disponibilità…</Text>
          </View>
        )}
        {newEndpointState === 'preview_503' && (
          <SafeFeatureCard
            title="Endpoint /api/server-profiles/select"
            subtitle="Servizio profili server temporaneamente disabilitato."
            visibility="player_visible_locked"
            endpointStatus="preview_503"
            lockReason="Il nuovo endpoint è gated (HTTP 503). In attesa delle firme di abilitazione runtime e preview."
            icon="🔒"
            statusBadge="503"
            testID="sp-new-endpoint-503"
          />
        )}
        {newEndpointState === 'live' && (
          <SafeFeatureCard
            title="Endpoint /api/server-profiles/select"
            subtitle="Anteprima dati disponibile. Nessuna mutazione esposta in UI."
            visibility="player_visible_active_read_only"
            endpointStatus="live"
            icon="🔗"
            statusBadge="Online"
          />
        )}
        {newEndpointState === 'unavailable' && (
          <SafeFeatureCard
            title="Endpoint /api/server-profiles/select"
            subtitle="Non raggiungibile in questo momento."
            visibility="player_visible_locked"
            lockReason="Errore di rete o servizio temporaneamente non disponibile."
            icon="🌐"
            statusBadge="Offline"
          />
        )}

        {/* Elenco server (rimosso intenzionalmente in fase locked preview) */}

        {/* Footer informativo */}
        <View style={styles.footerNote}>
          <Text style={styles.footerNoteText}>
            Nessuna azione di selezione server disponibile in questa fase. Il
            tuo server attuale resta invariato finché il nuovo sistema Server
            Profiles non sarà attivato in modo sicuro.
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
    backgroundColor: 'rgba(68,170,255,0.10)',
    borderWidth: 1,
    borderColor: 'rgba(68,170,255,0.35)',
    marginBottom: 20,
  },
  bannerIcon: { fontSize: 36 },
  bannerTitle: {
    color: COLORS.textPrimary,
    fontSize: 20,
    fontWeight: '800',
    marginTop: 8,
    textAlign: 'center',
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
    marginTop: 20,
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
