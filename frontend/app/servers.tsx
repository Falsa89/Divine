// servers.tsx — v102 — Server Select runtime wiring (functional UI).
//
// v102 sostituisce la precedente read-only locked preview con una UI selezionabile reale.
// Quando il backend /api/server-profiles/select e' 503 (PROJECT_B Track A skeleton),
// l'UI dichiara apertamente SERVER PROFILE FALLBACK e usa una lista server locale safe.
// NESSUNA chiamata mutativa lato server. La selezione persiste in AsyncStorage
// sotto la chiave canonica v101_selected_server_id (compat v101).
//
// Acceptance v102:
// - lista server selezionabile
// - card con dettagli + pulsante Entra
// - tap salva v101_selected_server_id
// - route a /(tabs)/home
// - se backend non disponibile -> label fallback visibile
// - nessun token raw log, nessun secret in repo
import React, { useEffect, useMemo, useState } from 'react';
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
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';
import { COLORS } from '../constants/theme';

type ServerStatus = 'online' | 'busy' | 'full' | 'maintenance' | 'locked';

type ServerProfile = {
  server_id: string;
  server_name: string;
  region: string;
  status: ServerStatus;
  recommended?: boolean;
  is_last_played?: boolean;
  has_character?: boolean;
  character_name?: string | null;
  character_level?: number | null;
  power?: number | null;
  created_at?: string | null;
  can_enter: boolean;
  reason_if_locked?: string | null;
  is_new?: boolean;
};

const BACKEND_URL =
  (process.env.EXPO_BACKEND_URL as string | undefined) ||
  (Constants?.expoConfig?.extra as any)?.backendUrl ||
  '';

// SERVER PROFILE FALLBACK — dichiarato. Lista safe locale, marcata [QA] esplicito.
// I server NON sono di produzione. has_character=false ovunque perche'
// la server data isolation reale (account/inventory/team per server_id)
// e' PENDING (deferred a v104+).
const FALLBACK_SERVERS: ServerProfile[] = [
  {
    server_id: 'qa-eu-01',
    server_name: '[QA] Aurora · EU-01',
    region: 'EU',
    status: 'online',
    recommended: true,
    is_last_played: false,
    has_character: false,
    can_enter: true,
    is_new: true,
  },
  {
    server_id: 'qa-eu-02',
    server_name: '[QA] Crepuscolo · EU-02',
    region: 'EU',
    status: 'online',
    has_character: false,
    can_enter: true,
  },
  {
    server_id: 'qa-na-01',
    server_name: '[QA] Eclissi · NA-01',
    region: 'NA',
    status: 'busy',
    has_character: false,
    can_enter: true,
  },
  {
    server_id: 'qa-asia-01',
    server_name: '[QA] Alba · ASIA-01',
    region: 'ASIA',
    status: 'online',
    has_character: false,
    can_enter: true,
  },
  {
    server_id: 'qa-eu-99',
    server_name: '[QA] Nebbia · EU-99 (Manutenzione)',
    region: 'EU',
    status: 'maintenance',
    has_character: false,
    can_enter: false,
    reason_if_locked: 'In manutenzione programmata',
  },
];

const STATUS_LABEL: Record<ServerStatus, string> = {
  online: 'Online',
  busy: 'Affollato',
  full: 'Pieno',
  maintenance: 'Manutenzione',
  locked: 'Bloccato',
};

const STATUS_COLOR: Record<ServerStatus, string> = {
  online: '#5DD89A',
  busy: '#F4B854',
  full: '#FF6B6B',
  maintenance: '#7A7AC4',
  locked: '#888',
};

export default function ServerSelectScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(true);
  const [servers, setServers] = useState<ServerProfile[]>([]);
  const [isFallback, setIsFallback] = useState<boolean>(true);
  const [entering, setEntering] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    const url = BACKEND_URL
      ? `${BACKEND_URL}/api/server-profiles/list`
      : '/api/server-profiles/list';
    fetch(url, { method: 'GET' })
      .then(async (r) => {
        if (!alive) return;
        if (r.status === 200) {
          try {
            const j = await r.json();
            if (j && Array.isArray(j.servers) && j.servers.length > 0) {
              setServers(j.servers as ServerProfile[]);
              setIsFallback(!!j.is_fallback);
            } else {
              setServers(FALLBACK_SERVERS);
              setIsFallback(true);
            }
          } catch {
            setServers(FALLBACK_SERVERS);
            setIsFallback(true);
          }
        } else {
          // 503/404/other -> fallback dichiarato
          setServers(FALLBACK_SERVERS);
          setIsFallback(true);
        }
      })
      .catch(() => {
        if (alive) {
          setServers(FALLBACK_SERVERS);
          setIsFallback(true);
        }
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  const sections = useMemo(() => {
    const recommended = servers.filter((s) => s.recommended);
    const lastPlayed = servers.filter((s) => s.is_last_played);
    const withCharacter = servers.filter((s) => s.has_character && !s.is_last_played);
    const others = servers.filter(
      (s) => !s.recommended && !s.is_last_played && !s.has_character,
    );
    return { recommended, lastPlayed, withCharacter, others };
  }, [servers]);

  const onEnter = async (s: ServerProfile) => {
    if (!s.can_enter) return;
    setEntering(s.server_id);
    try {
      await AsyncStorage.setItem('v101_selected_server_id', s.server_id);
      await AsyncStorage.setItem('v102_selected_server_name', s.server_name);
      await AsyncStorage.setItem(
        'v102_selected_server_has_character',
        s.has_character ? 'true' : 'false',
      );
    } catch (_e) {
      // non logghiamo dettagli sensibili
    }

    // Pack 86 — UI -> POST /api/psp/ensure?server_id=<sid>
    // Quando l'utente entra in un server, il frontend chiama il backend
    // ensure idempotente (Pack 85) per garantire che esista un PSP
    // fresh-start (player_level=1, player_exp=0, roster vuoto, NESSUNA
    // copia S1->S2). Bearer token reale da SecureStore (v96_auth_token).
    // Se ensure fallisce/no-auth, NON facciamo fallback global roster:
    // semplicemente proseguiamo e il lobby downstream mostrera' blocker
    // onesti (PLAYER_SERVER_PROFILE_REQUIRED / SELECTED_SERVER_REQUIRED).
    // Nessun silent 's1', nessuna mutation oltre PSP fresh-start.
    //
    // Pack 87 — Subito dopo ensure, chiamiamo idempotentemente
    // POST /api/psp/starter/claim?server_id=<sid> per assegnare lo starter
    // roster server-scoped (3 heroes low-rarity non-premium) se non ancora
    // reclamato. Idempotente (claim_once_per_server). NO global fallback.
    // NO premium currency. NO inventory/equipment/story reward.
    try {
      const SecureStore = await import('expo-secure-store');
      const token = await SecureStore.getItemAsync('v96_auth_token').catch(() => null);
      if (token && BACKEND_URL) {
        const ensureUrl = `${BACKEND_URL}/api/psp/ensure?server_id=${encodeURIComponent(s.server_id)}`;
        await fetch(ensureUrl, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Pack-86-Frontend-Ensure': 'true',
          },
        }).then(async (r) => {
          // Best-effort: salva flag onboarding stato per UI
          if (r.ok) {
            try {
              const j = await r.json();
              if (j && j.v110_psp_ensure === true) {
                await AsyncStorage.setItem(
                  'pack86_psp_ensure_last_mode',
                  j.created ? 'fresh_start_created' : 'already_exists_no_write',
                );
                await AsyncStorage.setItem(
                  'pack86_psp_ensure_last_server_id',
                  s.server_id,
                );
              }
            } catch (_e) { /* best-effort */ }
          }
        }).catch(() => { /* tolerated: lobby blocker honest downstream */ });

        // Pack 87 — Starter claim post-ensure (idempotente, server-scoped).
        const claimUrl = `${BACKEND_URL}/api/psp/starter/claim?server_id=${encodeURIComponent(s.server_id)}`;
        await fetch(claimUrl, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Pack-87-Frontend-Starter-Claim': 'true',
          },
        }).then(async (r) => {
          if (r.ok) {
            try {
              const j = await r.json();
              if (j && j.v110_starter_claim === true) {
                await AsyncStorage.setItem(
                  'pack87_starter_claim_last_mode',
                  j.created ? 'starter_claimed_first_time' : 'already_claimed_no_write',
                );
                await AsyncStorage.setItem(
                  'pack87_starter_claim_last_server_id',
                  s.server_id,
                );
                if (Array.isArray(j.starter_user_hero_ids)) {
                  await AsyncStorage.setItem(
                    'pack87_starter_user_hero_ids',
                    JSON.stringify(j.starter_user_hero_ids),
                  );
                }
              }
            } catch (_e) { /* best-effort */ }
          }
        }).catch(() => { /* tolerated: lobby blocker honest downstream, no global fallback */ });
      }
    } catch (_e) { /* best-effort, no global fallback */ }

    router.replace('/(tabs)/home');
  };

  const renderCard = (s: ServerProfile, key: string) => {
    const statusColor = STATUS_COLOR[s.status];
    const disabled = !s.can_enter;
    return (
      <View key={key} style={cardStyles.outer}>
        <LinearGradient
          colors={[statusColor + '22', 'rgba(15,15,45,0.95)']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={[cardStyles.card, { borderColor: statusColor + '55' }]}
        >
          <View style={cardStyles.headerRow}>
            <View style={{ flex: 1 }}>
              <Text style={cardStyles.serverName}>{s.server_name}</Text>
              <Text style={cardStyles.serverMeta}>
                {s.region} · <Text style={{ color: statusColor }}>{STATUS_LABEL[s.status]}</Text>
              </Text>
            </View>
            <View style={cardStyles.badges}>
              {s.recommended ? (
                <View style={[cardStyles.badge, { backgroundColor: '#FF6B3522' }]}>
                  <Text style={[cardStyles.badgeTxt, { color: '#FF6B35' }]}>CONSIGLIATO</Text>
                </View>
              ) : null}
              {s.is_new ? (
                <View style={[cardStyles.badge, { backgroundColor: '#5DD89A22' }]}>
                  <Text style={[cardStyles.badgeTxt, { color: '#5DD89A' }]}>NUOVO</Text>
                </View>
              ) : null}
              {s.is_last_played ? (
                <View style={[cardStyles.badge, { backgroundColor: '#7A7AC422' }]}>
                  <Text style={[cardStyles.badgeTxt, { color: '#7A7AC4' }]}>ULTIMO</Text>
                </View>
              ) : null}
              {s.status === 'maintenance' ? (
                <View style={[cardStyles.badge, { backgroundColor: '#7A7AC422' }]}>
                  <Text style={[cardStyles.badgeTxt, { color: '#7A7AC4' }]}>MANUT.</Text>
                </View>
              ) : null}
            </View>
          </View>

          {s.has_character ? (
            <View style={cardStyles.characterRow}>
              <Text style={cardStyles.characterIcon}>{'\u2694\uFE0F'}</Text>
              <View style={{ flex: 1 }}>
                <Text style={cardStyles.characterName}>{s.character_name || 'Personaggio'}</Text>
                <Text style={cardStyles.characterMeta}>
                  {s.character_level ? `Lv.${s.character_level}` : '\u2014'}
                  {s.power ? ` · Potere ${s.power}` : ''}
                </Text>
              </View>
            </View>
          ) : null}

          {disabled && s.reason_if_locked ? (
            <Text style={cardStyles.lockedReason}>{s.reason_if_locked}</Text>
          ) : null}

          <TouchableOpacity
            disabled={disabled || entering === s.server_id}
            onPress={() => onEnter(s)}
            activeOpacity={0.8}
            style={[
              cardStyles.enterBtn,
              {
                backgroundColor: disabled ? '#3a3a55' : '#FF6B35',
                opacity: entering === s.server_id ? 0.6 : 1,
              },
            ]}
          >
            <Text style={cardStyles.enterBtnTxt}>
              {entering === s.server_id ? 'Entrata...' : disabled ? 'Non disponibile' : 'ENTRA'}
            </Text>
          </TouchableOpacity>
        </LinearGradient>
      </View>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" />
        <LinearGradient
          colors={[COLORS.bgPrimary, COLORS.bgSecondary]}
          style={StyleSheet.absoluteFill}
        />
        <View style={styles.loadingWrap}>
          <ActivityIndicator color={COLORS.accent} size="large" />
          <Text style={styles.loadingTxt}>Caricamento server...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <LinearGradient
        colors={[COLORS.bgPrimary, COLORS.bgSecondary]}
        style={StyleSheet.absoluteFill}
      />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>SELEZIONE SERVER</Text>
        <Text style={styles.subtitle}>Scegli il server su cui vuoi giocare.</Text>

        {isFallback ? (
          <View style={styles.fallbackBanner}>
            <Text style={styles.fallbackTxt}>
              {'\u26A0\uFE0F'} LISTA SERVER QA/FALLBACK \u00b7 DATI NON DI PRODUZIONE
            </Text>
            <Text style={styles.fallbackSubTxt}>
              Pack 85-87 attivi: account identity condivisa tra server; profilo
              giocatore, roster e progressione sono server-scoped. Entrare in un
              nuovo server crea un PSP fresh-start (livello 1, exp 0) senza copia
              da altri server. Inventario, valute, story e equipment restano
              ancora deferred. Nessuna finzione di separazione.
            </Text>
          </View>
        ) : null}

        {sections.recommended.length > 0 ? (
          <>
            <Text style={styles.sectionTitle}>SERVER CONSIGLIATO</Text>
            {sections.recommended.map((s, i) => renderCard(s, `rec-${i}`))}
          </>
        ) : null}

        {sections.lastPlayed.length > 0 ? (
          <>
            <Text style={styles.sectionTitle}>ULTIMO SERVER</Text>
            {sections.lastPlayed.map((s, i) => renderCard(s, `last-${i}`))}
          </>
        ) : null}

        {sections.withCharacter.length > 0 ? (
          <>
            <Text style={styles.sectionTitle}>SERVER CON PERSONAGGI</Text>
            {sections.withCharacter.map((s, i) => renderCard(s, `ch-${i}`))}
          </>
        ) : null}

        {sections.others.length > 0 ? (
          <>
            <Text style={styles.sectionTitle}>TUTTI I SERVER</Text>
            {sections.others.map((s, i) => renderCard(s, `all-${i}`))}
          </>
        ) : null}

        <View style={{ height: 32 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bgPrimary },
  loadingWrap: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12 },
  loadingTxt: { color: COLORS.text, opacity: 0.7, fontSize: 14 },
  scroll: { padding: 16, paddingTop: 24 },
  title: {
    color: COLORS.text,
    fontSize: 22,
    fontWeight: '900',
    letterSpacing: 3,
    marginBottom: 4,
  },
  subtitle: { color: COLORS.text, opacity: 0.7, fontSize: 13, marginBottom: 14 },
  fallbackBanner: {
    backgroundColor: 'rgba(244,184,84,0.12)',
    borderColor: 'rgba(244,184,84,0.4)',
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
    marginBottom: 16,
  },
  fallbackTxt: { color: '#F4B854', fontSize: 11, fontWeight: '800' },
  fallbackSubTxt: { color: '#F4B854', fontSize: 10, marginTop: 4, opacity: 0.85 },
  sectionTitle: {
    color: COLORS.accent,
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 2,
    marginTop: 18,
    marginBottom: 8,
  },
});

const cardStyles = StyleSheet.create({
  outer: { marginBottom: 12, borderRadius: 12, overflow: 'hidden' },
  card: { borderWidth: 1, borderRadius: 12, padding: 14 },
  headerRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 8 },
  serverName: { color: COLORS.text, fontSize: 16, fontWeight: '800' },
  serverMeta: { color: COLORS.text, opacity: 0.75, fontSize: 12, marginTop: 2 },
  badges: { flexDirection: 'row', gap: 4, flexWrap: 'wrap', maxWidth: 130, justifyContent: 'flex-end' },
  badge: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  badgeTxt: { fontSize: 9, fontWeight: '900', letterSpacing: 1 },
  characterRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: 'rgba(255,255,255,0.08)',
  },
  characterIcon: { fontSize: 20 },
  characterName: { color: COLORS.text, fontSize: 13, fontWeight: '700' },
  characterMeta: { color: COLORS.text, opacity: 0.7, fontSize: 11 },
  lockedReason: { color: '#F4B854', fontSize: 11, marginTop: 8 },
  enterBtn: {
    marginTop: 12,
    height: 44, // >= 44pt iOS / 44dp Android touch target
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  enterBtnTxt: { color: '#fff', fontSize: 13, fontWeight: '900', letterSpacing: 3 },
});
