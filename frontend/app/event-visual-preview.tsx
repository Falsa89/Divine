/**
 * frontend/app/event-visual-preview.tsx
 *
 * v58 MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH — Track B (mode: event)
 * Deeplink-only static preview shell. NO backend. NO battle_engine. NO claim. NO reward.
 * NO mutation. NO Reanimated. NO import from frontend/app/story.tsx or frontend/app/combat.tsx.
 */
import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';

type Params = {
  event_id?: string;
  event_node_id?: string;
  event_display_name?: string;
  event_theme_hint?: string;
  enemy_family_preview?: string;
  bonus_rule_hint_preview?: string;
  background_hint?: string;
  music_hint?: string;
  battle_seed_preview?: string;
  team_power?: string;
  recommended_power?: string;
};

function asString(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'string') return v[0] as string;
  return undefined;
}

const DEFAULT_SEED = 'event-alpha-v58';
const DEFAULTS: Record<string, string> = {
  'event_id': 'event_preview_1',
  'event_node_id': 'event_node_preview_1',
  'event_display_name': 'Event Battle Preview',
  'battle_seed_preview': 'event-alpha-v58',
  'enemy_family_preview': 'event_enemy_preview',
  'event_theme_hint': 'limited_time_preview',
  'bonus_rule_hint_preview': 'bonus_drop_preview',
  'background_hint': 'event_bg',
  'music_hint': 'event_theme',
};

export default function EventVisualPreviewScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();
  const [event_id, setEventId] = useState<string>(asString(raw.event_id) || DEFAULTS['event_id']);
  const [event_node_id, setEventNodeId] = useState<string>(asString(raw.event_node_id) || DEFAULTS['event_node_id']);
  const [event_display_name, setEventDisplayName] = useState<string>(asString(raw.event_display_name) || DEFAULTS['event_display_name']);
  const [event_theme_hint, setEventThemeHint] = useState<string>(asString(raw.event_theme_hint) || DEFAULTS['event_theme_hint']);
  const [enemy_family_preview, setEnemyFamilyPreview] = useState<string>(asString(raw.enemy_family_preview) || DEFAULTS['enemy_family_preview']);
  const [bonus_rule_hint_preview, setBonusRuleHintPreview] = useState<string>(asString(raw.bonus_rule_hint_preview) || DEFAULTS['bonus_rule_hint_preview']);
  const [background_hint, setBackgroundHint] = useState<string>(asString(raw.background_hint) || DEFAULTS['background_hint']);
  const [music_hint, setMusicHint] = useState<string>(asString(raw.music_hint) || DEFAULTS['music_hint']);
  const [seed, setSeed] = useState<string>(asString(raw.battle_seed_preview) || DEFAULT_SEED);
  const teamPower = asString(raw.team_power);
  const recommendedPower = asString(raw.recommended_power);

  const onResetPreview = () => {
    setEventId(DEFAULTS['event_id'] || '');
    setEventNodeId(DEFAULTS['event_node_id'] || '');
    setEventDisplayName(DEFAULTS['event_display_name'] || '');
    setEventThemeHint(DEFAULTS['event_theme_hint'] || '');
    setEnemyFamilyPreview(DEFAULTS['enemy_family_preview'] || '');
    setBonusRuleHintPreview(DEFAULTS['bonus_rule_hint_preview'] || '');
    setBackgroundHint(DEFAULTS['background_hint'] || '');
    setMusicHint(DEFAULTS['music_hint'] || '');
    setSeed(DEFAULT_SEED);
  };

  const openRouter = () => {
    const url = `/visual-battle-preview-router?mode=event&source_route=event_visual_preview&battle_seed_preview=${encodeURIComponent(seed)}`;
    try { router.push(url); } catch { /* noop */ }
  };

  const onBack = () => { try { router.back(); } catch { /* noop */ } };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Event Visual Preview</Text>
          <Text style={styles.subtitle}>v58 · preview shell · deeplink-only · static</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
        </View>

        <View style={styles.modeCard}>
          <Text style={styles.sectionTitle}>Event Visual Preview · Mode Card</Text>
          <Text style={styles.line}>event_id: {event_id}</Text>
          <Text style={styles.line}>event_node_id: {event_node_id}</Text>
          <Text style={styles.line}>event_display_name: {event_display_name}</Text>
          <Text style={styles.line}>event_theme_hint: {event_theme_hint}</Text>
          <Text style={styles.line}>enemy_family_preview: {enemy_family_preview}</Text>
          <Text style={styles.line}>bonus_rule_hint_preview: {bonus_rule_hint_preview}</Text>
          <Text style={styles.line}>background_hint: {background_hint}</Text>
          <Text style={styles.line}>music_hint: {music_hint}</Text>
          <Text style={styles.line}>Seed: {seed}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Potere</Text>
          <Text style={styles.line}>Potere squadra: {teamPower || '—'}</Text>
          <Text style={styles.line}>Potere consigliato: {recommendedPower || '—'}</Text>
        </View>

        <View style={styles.guardsBox}>
          <Text style={styles.guardLine}>result_authoritative = false</Text>
          <Text style={styles.guardLine}>db_writes = 0</Text>
          <Text style={styles.guardLine}>battle_engine_runtime_used = false</Text>
          <Text style={styles.guardLine}>backend_used = false</Text>
          <Text style={styles.guardLine}>runtime_used = false</Text>
          <Text style={styles.guardLine}>reward_claim_enabled = false</Text>
        </View>

        <TouchableOpacity style={styles.primaryBtn} onPress={openRouter}>
          <Text style={styles.primaryBtnText}>Apri Visual Battle Preview Router</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryBtn} onPress={onResetPreview}>
          <Text style={styles.secondaryBtnText}>Reset preview</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryBtn} onPress={onBack}>
          <Text style={styles.secondaryBtnText}>Indietro</Text>
        </TouchableOpacity>

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>v58 MEGA_RELEASE_ACCELERATION_7 · event preview shell · no claim · deeplink-only</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0c0f14' },
  scrollContent: { padding: 16, paddingBottom: 48 },
  headerCard: { backgroundColor: '#141a22', borderRadius: 12, padding: 16, marginBottom: 16, borderWidth: 1, borderColor: '#222b36' },
  title: { color: '#fff', fontSize: 20, fontWeight: '700' },
  subtitle: { color: '#9aa4b2', fontSize: 12, marginTop: 4 },
  warningBox: { backgroundColor: '#3a2a14', borderRadius: 8, padding: 12, marginTop: 12, borderWidth: 1, borderColor: '#a07020' },
  warningText: { color: '#e8c884', fontSize: 12 },
  modeCard: { backgroundColor: '#1a212b', borderRadius: 12, padding: 14, marginBottom: 12, borderWidth: 1, borderColor: '#3b2a40' },
  card: { backgroundColor: '#141a22', borderRadius: 12, padding: 14, marginBottom: 12, borderWidth: 1, borderColor: '#222b36' },
  sectionTitle: { color: '#fff', fontSize: 15, fontWeight: '700', marginBottom: 8 },
  line: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  guardsBox: { backgroundColor: '#1a212b', borderRadius: 8, padding: 10, marginBottom: 12, borderWidth: 1, borderColor: '#2a3340' },
  guardLine: { color: '#9aa4b2', fontSize: 12, marginBottom: 2 },
  primaryBtn: { backgroundColor: '#3b6db5', paddingVertical: 14, borderRadius: 10, alignItems: 'center', marginTop: 4, minHeight: 48 },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  secondaryBtn: { backgroundColor: '#222b36', paddingVertical: 12, borderRadius: 10, alignItems: 'center', marginTop: 10, minHeight: 44 },
  secondaryBtnText: { color: '#cdd6e0', fontSize: 14, fontWeight: '600' },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});
