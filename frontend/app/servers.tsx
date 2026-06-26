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

// Pre-QA Stabilization 115C — uso helper canonico condiviso con apiCall.
import { getCanonicalBackendUrl } from '../src/utils/backendUrl';
// HOTFIX C — uso ApiError + apiCallWithMeta (introdotti da HOTFIX B) per
// rendere il server-select fail-closed e diagnostico. PSP ensure / starter
// claim / roster verify non sono più best-effort: ogni step deve passare
// prima di salvare `v101_selected_server_id` e navigare in Home.
import { apiCallWithMeta, ApiError, ApiDiagnostics } from '../utils/api';
const BACKEND_URL = getCanonicalBackendUrl();

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

// HOTFIX C — diagnostic state per il flow server-select fail-closed.
// Ogni phase (psp_ensure, starter_claim, roster_verify) può produrre un
// diagError che blocca la navigazione e mostra una card diagnostica.
type DiagError = {
  phase:
    | 'no_auth_token'
    | 'psp_ensure'
    | 'starter_claim'
    | 'roster_verify'
    | 'network';
  code: string;
  status: number | null;
  detail: string | null;
  diagnostics: ApiDiagnostics | null;
  server_id: string;
  server_name: string;
};

export default function ServerSelectScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(true);
  const [servers, setServers] = useState<ServerProfile[]>([]);
  const [isFallback, setIsFallback] = useState<boolean>(true);
  const [entering, setEntering] = useState<string | null>(null);
  // HOTFIX C — diagError visibile come modal diagnostica con Riprova/Cambia server.
  const [diagError, setDiagError] = useState<DiagError | null>(null);

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

  // HOTFIX C — helper per costruire un DiagError da ApiError o eccezione generica.
  const apiErrorToDiag = (
    e: any,
    phase: DiagError['phase'],
    fallbackCode: string,
    s: ServerProfile,
  ): DiagError => {
    if (e instanceof ApiError) {
      return {
        phase,
        code: e.code || fallbackCode,
        status: e.status,
        detail: e.detail,
        diagnostics: e.diagnostics,
        server_id: s.server_id,
        server_name: s.server_name,
      };
    }
    return {
      phase: 'network',
      code: fallbackCode,
      status: null,
      detail: (e && (e.message as string)) || 'Errore di rete sconosciuto.',
      diagnostics: null,
      server_id: s.server_id,
      server_name: s.server_name,
    };
  };

  // HOTFIX C — server-select FAIL-CLOSED.
  // Step 1: token disponibile.
  // Step 2: POST /api/psp/ensure server-scoped, success solo se v110_psp_ensure=true.
  // Step 3: POST /api/psp/starter/claim server-scoped, success se v110_starter_claim=true
  //         (entrambi created:true e already_claimed:true sono idempotency-valid).
  // Step 4: GET /api/user/heroes?server_id=<sid> con apiCallWithMeta, roster_count > 0
  //         e nessun X-Blocker.
  // Step 5: solo dopo TUTTI gli step verde, salva v101_selected_server_id e naviga Home.
  // FAIL in qualunque step: resta su servers.tsx, popola diagError (card diagnostica).
  const onEnter = async (s: ServerProfile) => {
    if (!s.can_enter) return;
    setEntering(s.server_id);
    setDiagError(null);

    try {
      // ── Step 1: auth token (no token logging) ─────────────────────────
      const { getAuthTokenCompat } = await import('../src/utils/authTokenCompat');
      const _tokenLookup = await getAuthTokenCompat();
      const token = _tokenLookup.token;
      if (!token) {
        try {
          await AsyncStorage.setItem(
            'pack86_psp_ensure_last_mode',
            'no_auth_token_psp_ensure_deferred',
          );
        } catch (_e) { /* best-effort */ }
        setDiagError({
          phase: 'no_auth_token',
          code: 'NO_AUTH_TOKEN_SERVER_SELECT_BLOCKED',
          status: null,
          detail:
            'Token di autenticazione assente: impossibile preparare il server. Effettua nuovamente il login.',
          diagnostics: null,
          server_id: s.server_id,
          server_name: s.server_name,
        });
        setEntering(null);
        return;
      }

      // ── Step 2: PSP ensure (decisive, NON best-effort) ────────────────
      let ensureMeta;
      try {
        ensureMeta = await apiCallWithMeta<any>(
          `/api/psp/ensure?server_id=${encodeURIComponent(s.server_id)}`,
          {
            method: 'POST',
            headers: { 'X-Pack-86-Frontend-Ensure': 'true' },
          },
        );
      } catch (e: any) {
        setDiagError(apiErrorToDiag(e, 'psp_ensure', 'PSP_ENSURE_FAILED', s));
        setEntering(null);
        return;
      }
      const eData: any = ensureMeta.data || {};
      if (!eData.v110_psp_ensure) {
        setDiagError({
          phase: 'psp_ensure',
          code: (eData.blocker as string) || 'PSP_ENSURE_FAILED',
          status: ensureMeta.status,
          detail: (eData.hint as string) || (eData.detail as string) || null,
          diagnostics: ensureMeta.diagnostics,
          server_id: s.server_id,
          server_name: s.server_name,
        });
        setEntering(null);
        return;
      }
      // Telemetria locale post-success (idempotente). No PII, no token.
      try {
        await AsyncStorage.setItem(
          'pack86_psp_ensure_last_mode',
          eData.created ? 'fresh_start_created' : 'already_exists_no_write',
        );
        await AsyncStorage.setItem(
          'pack86_psp_ensure_last_server_id',
          s.server_id,
        );
      } catch (_e) { /* best-effort */ }

      // ── Step 3: Starter claim (decisive, idempotency-aware) ───────────
      // Idempotent-success path (already_claimed=true) è OK perché significa
      // che lo starter è stato già reclamato in passato: il roster deve
      // comunque esistere e verrà verificato allo step 4.
      let claimMeta;
      try {
        claimMeta = await apiCallWithMeta<any>(
          `/api/psp/starter/claim?server_id=${encodeURIComponent(s.server_id)}`,
          {
            method: 'POST',
            headers: { 'X-Pack-87-Frontend-Starter-Claim': 'true' },
          },
        );
      } catch (e: any) {
        setDiagError(apiErrorToDiag(e, 'starter_claim', 'STARTER_CLAIM_FAILED', s));
        setEntering(null);
        return;
      }
      const cData: any = claimMeta.data || {};
      if (!cData.v110_starter_claim) {
        setDiagError({
          phase: 'starter_claim',
          code: (cData.blocker as string) || 'STARTER_CLAIM_FAILED',
          status: claimMeta.status,
          detail: (cData.hint as string) || (cData.detail as string) || null,
          diagnostics: claimMeta.diagnostics,
          server_id: s.server_id,
          server_name: s.server_name,
        });
        setEntering(null);
        return;
      }
      try {
        await AsyncStorage.setItem(
          'pack87_starter_claim_last_mode',
          cData.created ? 'starter_claimed_first_time' : 'already_claimed_no_write',
        );
        await AsyncStorage.setItem(
          'pack87_starter_claim_last_server_id',
          s.server_id,
        );
        if (Array.isArray(cData.starter_user_hero_ids)) {
          await AsyncStorage.setItem(
            'pack87_starter_user_hero_ids',
            JSON.stringify(cData.starter_user_hero_ids),
          );
        }
      } catch (_e) { /* best-effort */ }

      // ── Step 4: Roster verify (GET /api/user/heroes server-scoped) ────
      let rosterMeta;
      try {
        rosterMeta = await apiCallWithMeta<any>(
          `/api/user/heroes?server_id=${encodeURIComponent(s.server_id)}`,
        );
      } catch (e: any) {
        setDiagError(apiErrorToDiag(e, 'roster_verify', 'ROSTER_FETCH_FAILED', s));
        setEntering(null);
        return;
      }
      const rosterData: any = rosterMeta.data;
      const heroes: any[] = Array.isArray(rosterData)
        ? rosterData
        : (rosterData && rosterData.heroes) || [];
      const blockerHeader = rosterMeta.diagnostics.blocker;
      const rosterCountHeader = rosterMeta.diagnostics.roster_count;
      const rosterEmpty =
        heroes.length === 0 ||
        rosterCountHeader === 0 ||
        !!blockerHeader;
      if (rosterEmpty) {
        setDiagError({
          phase: 'roster_verify',
          code: blockerHeader || 'ROSTER_EMPTY_AFTER_SERVER_PREP',
          status: rosterMeta.status,
          detail:
            heroes.length === 0
              ? 'Roster iniziale non creato su questo server.'
              : 'Roster bloccato da diagnostico server.',
          diagnostics: rosterMeta.diagnostics,
          server_id: s.server_id,
          server_name: s.server_name,
        });
        setEntering(null);
        return;
      }

      // ── Step 5: PASS — persisti selected_server_id e naviga ───────────
      // HOTFIX C — la persistenza avviene SOLO dopo tutti gli step verde.
      try {
        await AsyncStorage.setItem('v101_selected_server_id', s.server_id);
        await AsyncStorage.setItem('v102_selected_server_name', s.server_name);
        await AsyncStorage.setItem(
          'v102_selected_server_has_character',
          s.has_character ? 'true' : 'false',
        );
      } catch (_e) {
        // Se AsyncStorage fallisce, blocchiamo: lo state server-scoped a valle
        // diventa incoerente. Mostriamo diagError invece di navigare.
        setDiagError({
          phase: 'network',
          code: 'PERSIST_SELECTED_SERVER_FAILED',
          status: null,
          detail: 'Impossibile salvare la selezione server in locale.',
          diagnostics: null,
          server_id: s.server_id,
          server_name: s.server_name,
        });
        setEntering(null);
        return;
      }
      router.replace('/(tabs)/home');
    } catch (e: any) {
      // Catch generico (no silent): mai navigare in Home.
      setDiagError({
        phase: 'network',
        code: 'UNEXPECTED_SERVER_SELECT_ERROR',
        status: null,
        detail: (e && (e.message as string)) || 'Errore inatteso.',
        diagnostics: null,
        server_id: s.server_id,
        server_name: s.server_name,
      });
    } finally {
      setEntering(null);
    }
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

      {/* HOTFIX C — Card diagnostica modale: server-select fail-closed.
          Mostrata quando una qualunque phase (auth/ensure/claim/roster) fallisce.
          Bottoni: Riprova (stesso server) / Cambia server (chiude la card).
          Nessun retry automatico. Nessuna navigazione Home in failure. */}
      {diagError && (
        <View style={diagStyles.overlay} pointerEvents="auto">
          <View style={diagStyles.card}>
            <Text style={diagStyles.title}>Server non pronto</Text>
            <View style={diagStyles.row}>
              <Text style={diagStyles.label}>Codice</Text>
              <Text style={diagStyles.valueErr}>{diagError.code}</Text>
            </View>
            <View style={diagStyles.row}>
              <Text style={diagStyles.label}>Fase</Text>
              <Text style={diagStyles.value}>{diagError.phase}</Text>
            </View>
            {diagError.status !== null && (
              <View style={diagStyles.row}>
                <Text style={diagStyles.label}>HTTP</Text>
                <Text style={diagStyles.value}>{diagError.status}</Text>
              </View>
            )}
            <View style={diagStyles.row}>
              <Text style={diagStyles.label}>Server</Text>
              <Text style={diagStyles.value} numberOfLines={1}>
                {diagError.server_id}
              </Text>
            </View>
            {diagError.diagnostics?.roster_count !== null &&
              diagError.diagnostics?.roster_count !== undefined && (
                <View style={diagStyles.row}>
                  <Text style={diagStyles.label}>Roster count</Text>
                  <Text style={diagStyles.value}>
                    {diagError.diagnostics.roster_count}
                  </Text>
                </View>
              )}
            {diagError.diagnostics?.psp_lookup_mode && (
              <View style={diagStyles.row}>
                <Text style={diagStyles.label}>PSP lookup</Text>
                <Text style={diagStyles.value}>
                  {diagError.diagnostics.psp_lookup_mode}
                </Text>
              </View>
            )}
            {diagError.diagnostics?.server_scope && (
              <View style={diagStyles.row}>
                <Text style={diagStyles.label}>Scope</Text>
                <Text style={diagStyles.value}>
                  {diagError.diagnostics.server_scope}
                </Text>
              </View>
            )}
            {diagError.diagnostics?.blocker && (
              <View style={diagStyles.row}>
                <Text style={diagStyles.label}>X-Blocker</Text>
                <Text style={diagStyles.valueErr}>
                  {diagError.diagnostics.blocker}
                </Text>
              </View>
            )}
            {diagError.detail && (
              <View style={diagStyles.detailWrap}>
                <Text style={diagStyles.label}>Dettaglio</Text>
                <Text style={diagStyles.detailTxt}>{diagError.detail}</Text>
              </View>
            )}
            <View style={diagStyles.actionRow}>
              <TouchableOpacity
                style={[diagStyles.btn, diagStyles.btnSecondary]}
                onPress={() => setDiagError(null)}
                activeOpacity={0.8}
              >
                <Text style={diagStyles.btnSecondaryTxt}>Cambia server</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[diagStyles.btn, diagStyles.btnPrimary]}
                onPress={() => {
                  // HOTFIX C — Retry SOLO user-triggered, nessun loop automatico.
                  const target = servers.find(
                    (x) => x.server_id === diagError.server_id,
                  );
                  setDiagError(null);
                  if (target) onEnter(target);
                }}
                activeOpacity={0.8}
              >
                <Text style={diagStyles.btnPrimaryTxt}>Riprova</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      )}
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

// HOTFIX C — Stili della card diagnostica fail-closed.
const diagStyles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.65)',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 18,
  },
  card: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: '#13133A',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,180,80,0.5)',
    padding: 16,
  },
  title: {
    color: '#FFB347',
    fontSize: 16,
    fontWeight: '900',
    letterSpacing: 1,
    marginBottom: 10,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 4,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: 'rgba(255,255,255,0.08)',
  },
  label: { color: 'rgba(255,255,255,0.65)', fontSize: 11, fontWeight: '700' },
  value: { color: '#fff', fontSize: 11, fontWeight: '700', maxWidth: 220, textAlign: 'right' },
  valueErr: { color: '#FFB347', fontSize: 11, fontWeight: '900', maxWidth: 220, textAlign: 'right' },
  detailWrap: { marginTop: 10 },
  detailTxt: { color: 'rgba(255,255,255,0.85)', fontSize: 11, marginTop: 4, lineHeight: 16 },
  actionRow: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 16,
  },
  btn: {
    flex: 1,
    height: 44,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnPrimary: { backgroundColor: '#FF6B35' },
  btnPrimaryTxt: { color: '#fff', fontSize: 12, fontWeight: '900', letterSpacing: 2 },
  btnSecondary: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.25)',
  },
  btnSecondaryTxt: { color: '#fff', fontSize: 12, fontWeight: '800', letterSpacing: 2 },
});
