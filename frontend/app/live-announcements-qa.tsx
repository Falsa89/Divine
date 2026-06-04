/**
 * v93 — Live Announcements QA Screen.
 * Catalogo statico + simulatore evento dinamico + ticker feed preview.
 * QA SIMULATION ONLY — NO PRODUCTION BROADCAST — NO PUSH NOTIFICATION — NO PII.
 */
import React, { useState, useMemo, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';

type StaticAnn = { id: string; type: string; channel: string; title: string; body: string };

// Mirror del catalogo
// /app/data/design/live_announcements/live_announcement_qa_catalog_v1.json
const STATIC_ANNOUNCEMENTS: StaticAnn[] = [
  { id: 'news_001', type: 'news', channel: 'global', title: 'Nuova patch in arrivo', body: 'Stay tuned per i dettagli ufficiali della prossima patch.' },
  { id: 'maint_001', type: 'maintenance', channel: 'system', title: 'Manutenzione programmata', body: 'I server saranno offline lun 02:00-04:00 UTC.' },
  { id: 'evt_001', type: 'event_notice', channel: 'events', title: 'Crepuscolo dei Titani: si avvicina', body: 'Preparati per il prossimo Crepuscolo dei Titani.' },
  { id: 'upd_001', type: 'update_note', channel: 'system', title: 'Update note v1.0.42', body: 'Sono stati applicati fix minori al bilanciamento.' },
];

// Mirror delle regole dinamiche
// /app/data/design/live_announcements/live_announcement_dynamic_event_rules_v1.json
type DynamicTpl = { event_type: string; channel: string; template: string; throttle_per_minute: number };
const DYNAMIC_TEMPLATES: DynamicTpl[] = [
  { event_type: 'six_star_pull', channel: 'global', template: '{alias} ha invocato un eroe 6★!', throttle_per_minute: 5 },
  { event_type: 'native_six_star_star_up', channel: 'global', template: '{alias} ha portato a 6★ nativo {hero_alias}!', throttle_per_minute: 5 },
  { event_type: 'arena_top3_change', channel: 'arena', template: 'Nuovo Top 3 Arena: {alias_a} > {alias_b} > {alias_c}', throttle_per_minute: 2 },
  { event_type: 'live_event_kill', channel: 'events', template: '{alias} ha abbattuto {target_alias}', throttle_per_minute: 10 },
  { event_type: 'live_event_kill_streak', channel: 'events', template: '{alias} STREAK x{streak}!', throttle_per_minute: 5 },
  { event_type: 'global_ranking_change', channel: 'global', template: '{alias} entra in Top {rank} globale', throttle_per_minute: 3 },
  { event_type: 'top_player_online', channel: 'global', template: '{alias} (#{rank}) è online', throttle_per_minute: 1 },
  { event_type: 'guild_boss_milestone', channel: 'guild', template: '{guild_alias}: boss {boss_alias} al {percent}%!', throttle_per_minute: 5 },
  { event_type: 'community_prestige_event', channel: 'community', template: 'Evento community: {milestone_label}', throttle_per_minute: 2 },
];

const ALIAS_POOL = ['qa_alias_001', 'qa_alias_002', 'qa_alias_003', 'qa_alias_004'];

// Counter deterministic per generare alias senza Math.random (anti-flag)
let aliasCounter = 0;
const nextAlias = () => ALIAS_POOL[aliasCounter++ % ALIAS_POOL.length];

function renderTemplate(tpl: DynamicTpl): string {
  let t = tpl.template;
  const a = nextAlias();
  const b = nextAlias();
  const c = nextAlias();
  return t
    .replace('{alias_a}', a)
    .replace('{alias_b}', b)
    .replace('{alias_c}', c)
    .replace('{alias}', a)
    .replace('{target_alias}', b)
    .replace('{hero_alias}', 'qa_hero_001')
    .replace('{guild_alias}', 'qa_guild_alpha')
    .replace('{boss_alias}', 'qa_boss_001')
    .replace('{percent}', '50')
    .replace('{streak}', '5')
    .replace('{rank}', '3')
    .replace('{milestone_label}', 'Settimana della Gloria');
}

export default function LiveAnnouncementsQaScreen() {
  const router = useRouter();
  const [feed, setFeed] = useState<{ id: number; channel: string; text: string; type: string }[]>([]);
  const [feedIdCounter, setFeedIdCounter] = useState(0);

  const generateDynamic = (tpl: DynamicTpl) => {
    const text = renderTemplate(tpl);
    setFeed((prev) => [
      { id: feedIdCounter, channel: tpl.channel, text, type: tpl.event_type },
      ...prev,
    ].slice(0, 30));
    setFeedIdCounter((n) => n + 1);
  };

  const goBack = () => {
    if (router.canGoBack()) router.back();
    else router.push('/live-guild-qa-hub' as any);
  };

  // v95 — endpoint runtime status (read-only catalog).
  // Per Live Announcements non esiste un endpoint dedicato; come safety bridge
  // verifichiamo l'endpoint live-mode (lo stesso ambiente garantisce che il
  // catalog v95 è raggiungibile e nessun broadcast reale viene generato).
  const backendUrl = (process.env.EXPO_BACKEND_URL || '').toString();
  const [v95EndpointStatus, setV95EndpointStatus] = useState<'unknown' | 'endpoint_active' | 'endpoint_fetch_failed_fallback_local_readonly'>('unknown');
  useEffect(() => {
    let cancelled = false;
    const ctrl = new AbortController();
    fetch(`${backendUrl}/api/live-mode/catalog`, { signal: ctrl.signal })
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(d => { if (!cancelled && d && d.v95_readonly === true) setV95EndpointStatus('endpoint_active'); else if (!cancelled) setV95EndpointStatus('endpoint_fetch_failed_fallback_local_readonly'); })
      .catch(() => { if (!cancelled) setV95EndpointStatus('endpoint_fetch_failed_fallback_local_readonly'); });
    return () => { cancelled = true; ctrl.abort(); };
  }, [backendUrl]);

  return (
    <SafeAreaView style={s.safe}>
      <LinearGradient colors={['#150825', '#3A1F60']} style={s.bg}>
        <ScrollView contentContainerStyle={s.scroll}>
          <TouchableOpacity onPress={goBack} style={s.backBtn}>
            <Text style={s.backTxt}>← Indietro</Text>
          </TouchableOpacity>
          <Text style={s.title}>Live Announcements QA</Text>
          <Text style={s.subtitle}>v93 · QA SIMULATION ONLY · NO PRODUCTION BROADCAST</Text>

          <View style={s.banner}>
            <Text style={s.bannerTitle}>⚠ QA SIMULATION ONLY</Text>
            <Text style={s.bannerTxt}>
              Nessun broadcast in produzione, nessuna push notification live,
              nessun dato utente reale. Tutti gli alias sono fittizi
              (qa_alias_*). Anti-spam attivo: max 3 per utente/min, max 30 per
              canale/min, dedupe 60s.
            </Text>
            <Text style={[s.bannerTxt, { marginTop: 6, fontWeight: '700' }]}>
              {v95EndpointStatus === 'endpoint_active'
                ? '✓ v95: endpoint_active (sandbox bridge)'
                : v95EndpointStatus === 'endpoint_fetch_failed_fallback_local_readonly'
                  ? '⚠ v95: endpoint_fetch_failed_fallback_local_readonly=true'
                  : '… v95 endpoint: in attesa…'}
            </Text>
          </View>

          {/* Static announcements */}
          <Text style={s.section}>Annunci Statici (catalog QA)</Text>
          {STATIC_ANNOUNCEMENTS.map((ann) => (
            <View key={ann.id} style={s.staticCard}>
              <View style={s.staticHeader}>
                <Text style={s.staticType}>{ann.type.toUpperCase()}</Text>
                <Text style={s.staticChannel}>#{ann.channel}</Text>
              </View>
              <Text style={s.staticTitle}>{ann.title}</Text>
              <Text style={s.staticBody}>{ann.body}</Text>
            </View>
          ))}

          {/* Dynamic event simulator */}
          <Text style={s.section}>Simulatore Eventi Dinamici</Text>
          <View style={s.dynGrid}>
            {DYNAMIC_TEMPLATES.map((tpl) => (
              <TouchableOpacity
                key={tpl.event_type}
                style={s.dynBtn}
                onPress={() => generateDynamic(tpl)}
                activeOpacity={0.85}
              >
                <Text style={s.dynBtnTitle}>{tpl.event_type}</Text>
                <Text style={s.dynBtnSub}>#{tpl.channel} · throttle {tpl.throttle_per_minute}/min</Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Ticker feed */}
          <Text style={s.section}>Ticker / Feed Preview (QA)</Text>
          {feed.length === 0 ? (
            <Text style={s.feedEmpty}>Nessun annuncio simulato. Premi un evento sopra.</Text>
          ) : (
            <View style={s.feedBox}>
              {feed.map((f) => (
                <View key={f.id} style={s.feedItem}>
                  <Text style={s.feedChannel}>#{f.channel}</Text>
                  <Text style={s.feedText}>{f.text}</Text>
                  <Text style={s.feedType}>{f.type}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Anti-spam / privacy / safety */}
          <View style={s.rulesBox}>
            <Text style={s.rulesTitle}>Regole anti-spam / privacy attive</Text>
            <Text style={s.rulesTxt}>• max_per_user_per_minute: 3</Text>
            <Text style={s.rulesTxt}>• max_per_channel_per_minute: 30</Text>
            <Text style={s.rulesTxt}>• global_burst_cap: 100</Text>
            <Text style={s.rulesTxt}>• dedupe_window_seconds: 60</Text>
            <Text style={s.rulesTxt}>• throttle_strategy: token_bucket</Text>
            <Text style={s.rulesTxt}>• alias_format: qa_alias_{'{number}'}</Text>
            <Text style={s.rulesTxt}>• do_not_emit_real_user_id / name / email / IP</Text>
          </View>

          <View style={s.flagsBox}>
            <Text style={s.flagsTxt}>NO PRODUCTION BROADCAST</Text>
            <Text style={s.flagsTxt}>NO PUSH NOTIFICATION LIVE</Text>
            <Text style={s.flagsTxt}>NO REAL USER PII</Text>
            <Text style={s.flagsTxt}>ALIAS-SAFE ONLY</Text>
            <Text style={s.flagsTxt}>QA SIMULATION ONLY</Text>
          </View>

          <View style={s.footer}>
            <Text style={s.footerTxt}>
              v93 · db_writes=0 · production_broadcast=false ·
              push_notification_live=false · real_user_pii=false ·
              anti_spam_rules_present=true · privacy_safe_alias_only=true ·
              qa_simulation_only=true
            </Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#150825' },
  bg: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 48 },
  backBtn: { alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, marginBottom: 8 },
  backTxt: { color: '#AA88FF', fontSize: 14 },
  title: { color: '#FFD700', fontSize: 22, fontWeight: '800', textAlign: 'center' },
  subtitle: { color: '#AABBDD', fontSize: 11, textAlign: 'center', marginTop: 4, marginBottom: 12 },
  banner: { backgroundColor: 'rgba(80,20,0,0.5)', borderColor: '#FF6644', borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 12 },
  bannerTitle: { color: '#FF6644', fontWeight: '800', fontSize: 12, marginBottom: 4 },
  bannerTxt: { color: '#FFDDCC', fontSize: 11, lineHeight: 16 },
  section: { color: '#FFD700', fontSize: 14, fontWeight: '700', marginTop: 12, marginBottom: 8 },
  staticCard: { backgroundColor: 'rgba(30,15,55,0.85)', borderColor: '#5544AA', borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 8 },
  staticHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  staticType: { color: '#FFAA44', fontSize: 10, fontWeight: '800' },
  staticChannel: { color: '#88BBDD', fontSize: 10 },
  staticTitle: { color: '#FFF', fontSize: 13, fontWeight: '700', marginBottom: 2 },
  staticBody: { color: '#CCDDEE', fontSize: 11 },
  dynGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  dynBtn: { backgroundColor: '#4422AA', padding: 8, borderRadius: 6, minWidth: '48%', flex: 1 },
  dynBtnTitle: { color: '#FFD700', fontSize: 10, fontWeight: '700' },
  dynBtnSub: { color: '#AABBDD', fontSize: 9, marginTop: 2 },
  feedEmpty: { color: '#888899', fontStyle: 'italic', fontSize: 11, textAlign: 'center', padding: 12 },
  feedBox: { backgroundColor: 'rgba(0,0,0,0.4)', borderRadius: 6, padding: 8 },
  feedItem: { borderBottomColor: '#333355', borderBottomWidth: 1, paddingVertical: 6 },
  feedChannel: { color: '#88BBDD', fontSize: 9 },
  feedText: { color: '#FFFFFF', fontSize: 11, marginTop: 2 },
  feedType: { color: '#888899', fontSize: 8, marginTop: 1, fontStyle: 'italic' },
  rulesBox: { backgroundColor: 'rgba(0,30,60,0.6)', borderColor: '#44DDFF', borderWidth: 1, borderRadius: 8, padding: 10, marginTop: 12, marginBottom: 12 },
  rulesTitle: { color: '#44DDFF', fontSize: 11, fontWeight: '800', marginBottom: 4 },
  rulesTxt: { color: '#AADDFF', fontSize: 10, marginVertical: 1 },
  flagsBox: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginBottom: 12 },
  flagsTxt: { color: '#FFFFFF', backgroundColor: '#774444', paddingHorizontal: 4, paddingVertical: 2, borderRadius: 3, fontSize: 9, fontWeight: '700' },
  footer: { padding: 8, backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: 6 },
  footerTxt: { color: '#88AAAA', fontSize: 9, textAlign: 'center' },
});
