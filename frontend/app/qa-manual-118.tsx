// Pre-QA Stabilization 118B — Web QA Access Harness page.
//
// QA-ONLY READ-ONLY DEEPLINK-ONLY surface.
// - Non e' linkata da nessuna tab, menu o home: accessibile solo via deeplink
//   diretto /qa-manual-118.
// - Gated da EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=true (preQaDevQaVisible()).
// - Esegue solo chiamate GET read-only verso gli 8 endpoint autorizzati.
// - Nessun bottone claim/buy/spend/upgrade. Nessuna mutation. Nessun POST.
// - Nessun resolver actionable. Nessuna push. Nessun chat live.
// - Banner QA permanente in alto.
//
// NOTA: questa NON e' una superficie player. NON deve essere mai esposta
// in produzione senza il flag dev/QA esplicito.

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { preQaDevQaVisible } from '../src/utils/preQaNavGuard';

// Endpoint canonical (read-only) autorizzati Pack 118B.
const ALLOWED_GET_ENDPOINTS: ReadonlyArray<{
  id: string;
  label: string;
  path: string;
  requires_server_id: boolean;
  requires_auth: boolean;
}> = [
  { id: 'bp_metadata', label: 'Battle Power · metadata',
    path: '/api/battle-power/metadata', requires_server_id: false, requires_auth: false },
  { id: 'bp_summary', label: 'Battle Power · summary',
    path: '/api/battle-power/summary', requires_server_id: true, requires_auth: true },
  { id: 'bp_breakdown', label: 'Battle Power · breakdown (metadata-only)',
    path: '/api/battle-power/breakdown', requires_server_id: false, requires_auth: false },
  { id: 'rd_metadata', label: 'Red Dot · metadata',
    path: '/api/red-dot/metadata', requires_server_id: false, requires_auth: false },
  { id: 'rd_summary', label: 'Red Dot · summary',
    path: '/api/red-dot/summary', requires_server_id: true, requires_auth: true },
  { id: 'hu_metadata', label: 'Hero Upgrade · metadata',
    path: '/api/hero-upgrade/metadata', requires_server_id: false, requires_auth: false },
  { id: 'hu_readiness', label: 'Hero Upgrade · readiness',
    path: '/api/hero-upgrade/readiness', requires_server_id: true, requires_auth: true },
  { id: 'user_heroes', label: 'User Heroes',
    path: '/api/user/heroes', requires_server_id: true, requires_auth: true },
];

type ProbeResult = {
  status?: number;
  ok?: boolean;
  body_text?: string;
  body_pretty?: string;
  ms?: number;
  error?: string;
};

const QA_HARNESS_VERSION = 'pre_qa_118b_web_qa_access_harness_v1';

export default function QaManual118Screen() {
  const insets = useSafeAreaInsets();
  const devQaVisible = preQaDevQaVisible();

  const [serverId, setServerId] = useState<string>('s1');
  const [bearerToken, setBearerToken] = useState<string>('');
  const [results, setResults] = useState<Record<string, ProbeResult>>({});
  const [busy, setBusy] = useState<boolean>(false);

  const baseUrl = useMemo(() => {
    // Read-only: usa env Expo. Nessun hardcoding.
    return (process.env.EXPO_BACKEND_URL as string | undefined) || '';
  }, []);

  const runProbe = useCallback(async (
    epId: string,
    path: string,
    requiresServerId: boolean,
    requiresAuth: boolean,
  ) => {
    if (!baseUrl) {
      setResults((r) => ({ ...r, [epId]: { error: 'EXPO_BACKEND_URL non configurato' } }));
      return;
    }
    const qp = requiresServerId && serverId ? `?server_id=${encodeURIComponent(serverId)}` : '';
    const url = `${baseUrl}${path}${qp}`;
    const headers: Record<string, string> = { Accept: 'application/json' };
    if (requiresAuth && bearerToken) headers['Authorization'] = `Bearer ${bearerToken}`;
    const t0 = Date.now();
    try {
      const resp = await fetch(url, { method: 'GET', headers });
      const text = await resp.text();
      let pretty = text;
      try {
        pretty = JSON.stringify(JSON.parse(text), null, 2);
      } catch {
        // mantieni text grezzo
      }
      setResults((r) => ({
        ...r,
        [epId]: {
          status: resp.status,
          ok: resp.ok,
          body_text: text.slice(0, 4000),
          body_pretty: pretty.slice(0, 4000),
          ms: Date.now() - t0,
        },
      }));
    } catch (e: any) {
      setResults((r) => ({ ...r, [epId]: { error: String(e?.message || e), ms: Date.now() - t0 } }));
    }
  }, [baseUrl, serverId, bearerToken]);

  const runAll = useCallback(async () => {
    setBusy(true);
    for (const ep of ALLOWED_GET_ENDPOINTS) {
      await runProbe(ep.id, ep.path, ep.requires_server_id, ep.requires_auth);
    }
    setBusy(false);
  }, [runProbe]);

  // Probe automatico all'apertura solo per metadata pubblici (no auth).
  useEffect(() => {
    if (!devQaVisible) return;
    (async () => {
      for (const ep of ALLOWED_GET_ENDPOINTS) {
        if (!ep.requires_auth) {
          await runProbe(ep.id, ep.path, false, false);
        }
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!devQaVisible) {
    return (
      <View style={[styles.root, { paddingTop: insets.top + 16 }]}>
        <View style={styles.banner}>
          <Text style={styles.bannerTitle}>QA-only · gated</Text>
          <Text style={styles.bannerSub}>
            Questa pagina e' una superficie QA read-only. Per accedervi imposta
            EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=true.
          </Text>
        </View>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={{ paddingTop: insets.top + 12, paddingBottom: insets.bottom + 64 }}
    >
      <View style={styles.banner}>
        <Text style={styles.bannerTitle}>QA · {QA_HARNESS_VERSION}</Text>
        <Text style={styles.bannerSub}>
          READ-ONLY · DEEPLINK-ONLY · DEV/QA-ONLY · NO CLAIMS · NO MUTATIONS · NO LIVE SYSTEMS
        </Text>
        <Text style={styles.bannerSub}>
          Questa pagina chiama solo endpoint GET autorizzati. Nessun bottone esegue mutazioni.
        </Text>
      </View>

      <View style={styles.controls}>
        <Text style={styles.label}>server_id (required per endpoint server-scoped)</Text>
        <TextInput
          style={styles.input}
          value={serverId}
          onChangeText={setServerId}
          autoCapitalize="none"
          autoCorrect={false}
          placeholder="s1"
          placeholderTextColor="#9aa0a6"
        />

        <Text style={styles.label}>bearer_token (opzionale, per endpoint auth)</Text>
        <TextInput
          style={[styles.input, { fontFamily: 'monospace' }]}
          value={bearerToken}
          onChangeText={setBearerToken}
          autoCapitalize="none"
          autoCorrect={false}
          multiline
          placeholder="<incolla access_token>"
          placeholderTextColor="#9aa0a6"
        />

        <TouchableOpacity
          style={[styles.btn, busy && { opacity: 0.5 }]}
          onPress={runAll}
          disabled={busy}
          accessibilityRole="button"
        >
          <Text style={styles.btnText}>
            {busy ? 'Probing...' : 'Run all read-only probes'}
          </Text>
        </TouchableOpacity>
      </View>

      {ALLOWED_GET_ENDPOINTS.map((ep) => {
        const r = results[ep.id];
        return (
          <View key={ep.id} style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>{ep.label}</Text>
              <Text style={styles.cardSub}>
                GET {ep.path}{ep.requires_server_id ? '?server_id=…' : ''}
                {ep.requires_auth ? '  · auth' : '  · no auth'}
              </Text>
            </View>

            <View style={styles.cardActions}>
              <TouchableOpacity
                style={styles.btnSm}
                onPress={() => runProbe(ep.id, ep.path, ep.requires_server_id, ep.requires_auth)}
                accessibilityRole="button"
              >
                <Text style={styles.btnSmText}>Probe</Text>
              </TouchableOpacity>
            </View>

            {!r ? (
              <Text style={styles.muted}>— non eseguito —</Text>
            ) : r.error ? (
              <Text style={styles.error}>error: {r.error}</Text>
            ) : (
              <>
                <Text style={[styles.statusLine, r.ok ? styles.statusOk : styles.statusKo]}>
                  HTTP {r.status}  ·  {r.ms} ms
                </Text>
                <ScrollView horizontal>
                  <Text style={styles.body}>{r.body_pretty || r.body_text || ''}</Text>
                </ScrollView>
              </>
            )}
          </View>
        );
      })}

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Harness version: {QA_HARNESS_VERSION}
        </Text>
        <Text style={styles.footerText}>
          Endpoints autorizzati: {ALLOWED_GET_ENDPOINTS.length}/8 (read-only)
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0f1115', paddingHorizontal: 16 },
  banner: {
    backgroundColor: '#3a1f1f',
    borderWidth: 1,
    borderColor: '#aa4444',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  bannerTitle: { color: '#ffd9d9', fontSize: 16, fontWeight: '800', marginBottom: 4 },
  bannerSub: { color: '#f6c9c9', fontSize: 12, marginTop: 2 },
  controls: { marginBottom: 16 },
  label: { color: '#cfd3dc', fontSize: 12, marginTop: 8, marginBottom: 4 },
  input: {
    backgroundColor: '#1b1f27',
    color: '#e8eaed',
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#2a2f3a',
    minHeight: 40,
  },
  btn: {
    backgroundColor: '#2a6df4',
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 12,
    alignItems: 'center',
  },
  btnText: { color: '#ffffff', fontWeight: '700' },
  card: {
    backgroundColor: '#161a22',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222733',
  },
  cardHeader: { marginBottom: 8 },
  cardTitle: { color: '#e8eaed', fontWeight: '700', fontSize: 14 },
  cardSub: { color: '#9aa0a6', fontSize: 12, marginTop: 2 },
  cardActions: { flexDirection: 'row', marginBottom: 8 },
  btnSm: {
    backgroundColor: '#2c3a52',
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 6,
  },
  btnSmText: { color: '#e8eaed', fontWeight: '600' },
  statusLine: { fontFamily: 'monospace', fontSize: 12, marginBottom: 6 },
  statusOk: { color: '#7bd07b' },
  statusKo: { color: '#e07b7b' },
  body: { color: '#cfd3dc', fontFamily: 'monospace', fontSize: 11 },
  muted: { color: '#9aa0a6', fontStyle: 'italic' },
  error: { color: '#e07b7b' },
  footer: { marginTop: 8, alignItems: 'center' },
  footerText: { color: '#666c75', fontSize: 11 },
});
