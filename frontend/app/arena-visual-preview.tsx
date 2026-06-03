/**
 * frontend/app/arena-visual-preview.tsx
 *
 * v58 MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH — Track B (mode: arena)
 * Deeplink-only static preview shell. NO backend. NO battle_engine. NO claim. NO reward.
 * NO mutation. NO Reanimated. NO import from frontend/app/story.tsx or frontend/app/combat.tsx.
 */
import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';

type Params = {
  arena_bracket_preview?: string;
  opponent_name_preview?: string;
  opponent_power_preview?: string;
  enemy_family_preview?: string;
  ruleset_hint_preview?: string;
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

const DEFAULT_SEED = 'arena-alpha-v58';
const DEFAULTS: Record<string, string> = {
  'arena_bracket_preview': 'bronze_preview',
  'opponent_name_preview': 'Training Rival Preview',
  'opponent_power_preview': '45000',
  'battle_seed_preview': 'arena-alpha-v58',
  'enemy_family_preview': 'arena_rival_preview',
  'ruleset_hint_preview': 'standard_ruleset_preview',
  'background_hint': 'arena_bg',
  'music_hint': 'arena_theme',
};

export default function ArenaVisualPreviewScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();
  const [arena_bracket_preview, setArenaBracketPreview] = useState<string>(asString(raw.arena_bracket_preview) || DEFAULTS['arena_bracket_preview']);
  const [opponent_name_preview, setOpponentNamePreview] = useState<string>(asString(raw.opponent_name_preview) || DEFAULTS['opponent_name_preview']);
  const [opponent_power_preview, setOpponentPowerPreview] = useState<string>(asString(raw.opponent_power_preview) || DEFAULTS['opponent_power_preview']);
  const [enemy_family_preview, setEnemyFamilyPreview] = useState<string>(asString(raw.enemy_family_preview) || DEFAULTS['enemy_family_preview']);
  const [ruleset_hint_preview, setRulesetHintPreview] = useState<string>(asString(raw.ruleset_hint_preview) || DEFAULTS['ruleset_hint_preview']);
  const [background_hint, setBackgroundHint] = useState<string>(asString(raw.background_hint) || DEFAULTS['background_hint']);
  const [music_hint, setMusicHint] = useState<string>(asString(raw.music_hint) || DEFAULTS['music_hint']);
  const [seed, setSeed] = useState<string>(asString(raw.battle_seed_preview) || DEFAULT_SEED);
  const teamPower = asString(raw.team_power);
  const recommendedPower = asString(raw.recommended_power);

  const onResetPreview = () => {
    setArenaBracketPreview(DEFAULTS['arena_bracket_preview'] || '');
    setOpponentNamePreview(DEFAULTS['opponent_name_preview'] || '');
    setOpponentPowerPreview(DEFAULTS['opponent_power_preview'] || '');
    setEnemyFamilyPreview(DEFAULTS['enemy_family_preview'] || '');
    setRulesetHintPreview(DEFAULTS['ruleset_hint_preview'] || '');
    setBackgroundHint(DEFAULTS['background_hint'] || '');
    setMusicHint(DEFAULTS['music_hint'] || '');
    setSeed(DEFAULT_SEED);
  };

  const openRouter = () => {
    const url = `/visual-battle-preview-router?mode=arena&source_route=arena_visual_preview&battle_seed_preview=${encodeURIComponent(seed)}`;
    try { router.push(url); } catch { /* noop */ }
  };

  const onBack = () => { try { router.back(); } catch { /* noop */ } };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Arena Visual Preview</Text>
          <Text style={styles.subtitle}>v58 · preview shell · deeplink-only · static</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
        </View>

        <View style={styles.modeCard}>
          <Text style={styles.sectionTitle}>Arena Visual Preview · Mode Card</Text>
          <Text style={styles.line}>arena_bracket_preview: {arena_bracket_preview}</Text>
          <Text style={styles.line}>opponent_name_preview: {opponent_name_preview}</Text>
          <Text style={styles.line}>opponent_power_preview: {opponent_power_preview}</Text>
          <Text style={styles.line}>enemy_family_preview: {enemy_family_preview}</Text>
          <Text style={styles.line}>ruleset_hint_preview: {ruleset_hint_preview}</Text>
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
          <Text style={styles.footerText}>v58 MEGA_RELEASE_ACCELERATION_7 · arena preview shell · no claim · deeplink-only</Text>
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
