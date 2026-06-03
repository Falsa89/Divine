/**
 * frontend/app/boss-visual-preview.tsx
 *
 * v57 MEGA_RELEASE_ACCELERATION_6_BOSS_VISUAL_PREVIEW_ROUTE — Track B
 * Boss Visual Preview deeplink shell (STATIC + DEEPLINK-ONLY).
 *
 * NO home menu wiring. NO backend. NO battle_engine.
 * NO /api/battle/simulate. NO /api/story/battle.
 * NO claim button. NO reward. NO mutation. NO Reanimated. NO combat.tsx import.
 *
 * Default seed: boss-alpha-v57.
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';

type Params = {
  boss_family_id?: string;
  boss_display_name?: string;
  boss_phase_preview?: string;
  battle_seed_preview?: string;
  team_power?: string;
  recommended_power?: string;
};

function asString(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'string') return v[0] as string;
  return undefined;
}

const DEFAULT_BOSS_FAMILY = 'training_boss_preview';
const DEFAULT_BOSS_NAME = 'Boss Preview';
const DEFAULT_PHASE = 'phase_1';
const DEFAULT_SEED = 'boss-alpha-v57';

// Static hint table — fully local, no backend.
const HINTS: Record<string, { weakness: string; enrage: string; background: string; music: string }> = {
  training_boss_preview: {
    weakness: 'attacchi fisici base',
    enrage: 'enrage_at_50pct_hp',
    background: 'training_arena_bg',
    music: 'training_boss_theme',
  },
};

export default function BossVisualPreviewScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();

  const initialFamily = asString(raw.boss_family_id) || DEFAULT_BOSS_FAMILY;
  const initialName = asString(raw.boss_display_name) || DEFAULT_BOSS_NAME;
  const initialPhase = asString(raw.boss_phase_preview) || DEFAULT_PHASE;
  const initialSeed = asString(raw.battle_seed_preview) || DEFAULT_SEED;
  const teamPower = asString(raw.team_power);
  const recommendedPower = asString(raw.recommended_power);

  const [bossFamily, setBossFamily] = useState<string>(initialFamily);
  const [bossName, setBossName] = useState<string>(initialName);
  const [phase, setPhase] = useState<string>(initialPhase);
  const [seed, setSeed] = useState<string>(initialSeed);

  const hints = HINTS[bossFamily] || HINTS[DEFAULT_BOSS_FAMILY];

  const onResetPreview = () => {
    setBossFamily(DEFAULT_BOSS_FAMILY);
    setBossName(DEFAULT_BOSS_NAME);
    setPhase(DEFAULT_PHASE);
    setSeed(DEFAULT_SEED);
  };

  const openRouter = () => {
    const url = `/visual-battle-preview-router?mode=boss&source_route=boss_visual_preview&boss_family_id=${encodeURIComponent(
      bossFamily,
    )}&boss_display_name=${encodeURIComponent(bossName)}&boss_phase_preview=${encodeURIComponent(
      phase,
    )}&battle_seed_preview=${encodeURIComponent(seed)}`;
    try {
      router.push(url);
    } catch {
      // noop fallback
    }
  };

  const onBack = () => {
    try {
      router.back();
    } catch {
      // noop fallback
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Boss Visual Preview</Text>
          <Text style={styles.subtitle}>
            v57 · preview shell · deeplink-only · static
          </Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale boss non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
        </View>

        <View style={styles.bossCard}>
          <Text style={styles.sectionTitle}>Boss Card</Text>
          <Text style={styles.bossName}>{bossName}</Text>
          <Text style={styles.line}>Family: {bossFamily}</Text>
          <Text style={styles.line}>Phase preview: {phase}</Text>
          <Text style={styles.line}>Seed: {seed}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Hint preview</Text>
          <Text style={styles.line}>Weakness hint: {hints.weakness}</Text>
          <Text style={styles.line}>Enrage hint: {hints.enrage}</Text>
          <Text style={styles.helper}>
            Background: {hints.background} · Music: {hints.music}
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Potere</Text>
          <Text style={styles.line}>
            Potere squadra: {teamPower || '—'}
          </Text>
          <Text style={styles.line}>
            Potere consigliato: {recommendedPower || '—'}
          </Text>
        </View>

        <View style={styles.guardsBox}>
          <Text style={styles.guardLine}>result_authoritative = false</Text>
          <Text style={styles.guardLine}>db_writes = 0</Text>
          <Text style={styles.guardLine}>battle_engine_runtime_used = false</Text>
          <Text style={styles.guardLine}>backend_used = false</Text>
          <Text style={styles.guardLine}>reward_claim_enabled = false</Text>
          <Text style={styles.guardLine}>reward_grant_enabled = false</Text>
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
          <Text style={styles.footerText}>
            v57 MEGA_RELEASE_ACCELERATION_6 · boss preview shell · no claim · deeplink-only
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0c0f14' },
  scrollContent: { padding: 16, paddingBottom: 48 },
  headerCard: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  title: { color: '#fff', fontSize: 20, fontWeight: '700' },
  subtitle: { color: '#9aa4b2', fontSize: 12, marginTop: 4 },
  warningBox: {
    backgroundColor: '#3a2a14',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#a07020',
  },
  warningText: { color: '#e8c884', fontSize: 12 },
  bossCard: {
    backgroundColor: '#1a212b',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#3b2a40',
  },
  card: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  sectionTitle: { color: '#fff', fontSize: 15, fontWeight: '700', marginBottom: 8 },
  bossName: { color: '#e8c884', fontSize: 18, fontWeight: '700', marginBottom: 6 },
  line: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  helper: { color: '#9aa4b2', fontSize: 12, marginTop: 6 },
  guardsBox: {
    backgroundColor: '#1a212b',
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#2a3340',
  },
  guardLine: { color: '#9aa4b2', fontSize: 12, marginBottom: 2 },
  primaryBtn: {
    backgroundColor: '#3b6db5',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 4,
    minHeight: 48,
  },
  primaryBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  secondaryBtn: {
    backgroundColor: '#222b36',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
    minHeight: 44,
  },
  secondaryBtnText: { color: '#cdd6e0', fontSize: 14, fontWeight: '600' },
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});
