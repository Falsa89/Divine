/**
 * frontend/app/visual-battle-preview-router.tsx
 *
 * v55 MEGA_RELEASE_ACCELERATION_4_VISUAL_BATTLE_ROUTING_EXPANSION_PREVIEW — Track B
 * Generic Visual Battle Preview Router Shell (DEEPLINK-ONLY).
 *
 * NO home menu wiring. NO backend fetch. NO claim button. NO mutation.
 * NO battle_engine. NO /api/battle/simulate. NO /api/story/battle.
 * Result NON-AUTHORITATIVE. Reward NOT granted.
 */
import React from 'react';
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
  mode?: string;
  source_route?: string;
  track_id?: string;
  stage_id?: string;
  chapter_id?: string;
  battle_seed_preview?: string;
  team_power?: string;
  recommended_power?: string;
  enemy_family_preview?: string;
};

function asString(v: unknown): string | undefined {
  if (typeof v === 'string') return v;
  if (Array.isArray(v) && v.length > 0 && typeof v[0] === 'string') return v[0] as string;
  return undefined;
}

export default function VisualBattlePreviewRouterScreen() {
  const router = useRouter();
  const raw = useLocalSearchParams<Params>();

  const mode = asString(raw.mode) || 'unknown';
  const sourceRoute = asString(raw.source_route);
  const trackId = asString(raw.track_id);
  const stageId = asString(raw.stage_id);
  const chapterId = asString(raw.chapter_id);
  const seed = asString(raw.battle_seed_preview);
  const teamPower = asString(raw.team_power);
  const recommendedPower = asString(raw.recommended_power);
  const enemyFamily = asString(raw.enemy_family_preview);

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
          <Text style={styles.title}>Visual Battle Preview Router</Text>
          <Text style={styles.subtitle}>v55 · deeplink-only · shell preview multi-mode</Text>
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>Preview visuale non autoritativa.</Text>
            <Text style={styles.warningText}>Nessun reward verrà assegnato.</Text>
            <Text style={styles.warningText}>Routing preview only.</Text>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Parametri ricevuti</Text>
          <Text style={styles.line}>Modalità: {mode}</Text>
          {sourceRoute ? <Text style={styles.line}>Source route: {sourceRoute}</Text> : null}
          {trackId ? <Text style={styles.line}>Track ID: {trackId}</Text> : null}
          {stageId ? <Text style={styles.line}>Stage ID: {stageId}</Text> : null}
          {chapterId ? <Text style={styles.line}>Chapter ID: {chapterId}</Text> : null}
          {seed ? <Text style={styles.line}>Seed preview: {seed}</Text> : null}
          {teamPower ? <Text style={styles.line}>Potere squadra: {teamPower}</Text> : null}
          {recommendedPower ? (
            <Text style={styles.line}>Potere consigliato: {recommendedPower}</Text>
          ) : null}
          {enemyFamily ? (
            <Text style={styles.line}>Famiglia nemica (preview): {enemyFamily}</Text>
          ) : null}
          {!sourceRoute && !trackId && !stageId && !chapterId && !seed ? (
            <Text style={styles.helper}>
              Nessun parametro fornito. La schermata non crasha: usa il deeplink con i query
              param previsti dal contratto v1.
            </Text>
          ) : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Placeholder griglia 3x3</Text>
          <View style={styles.grid}>
            {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <View key={i} style={styles.gridCell}>
                <Text style={styles.gridCellText}>{i + 1}</Text>
              </View>
            ))}
          </View>
          <Text style={styles.helper}>
            Layout placeholder: nessun asset reale, nessuna chiamata backend.
          </Text>
        </View>

        <View style={styles.guardsBox}>
          <Text style={styles.guardLine}>result_authoritative = false</Text>
          <Text style={styles.guardLine}>reward_claim_enabled = false</Text>
          <Text style={styles.guardLine}>reward_grant_enabled = false</Text>
          <Text style={styles.guardLine}>battle_engine_runtime_used = false</Text>
          <Text style={styles.guardLine}>db_writes = 0</Text>
          <Text style={styles.guardLine}>home_menu_mandatory_routing = false</Text>
        </View>

        <TouchableOpacity style={styles.primaryBtn} onPress={onBack}>
          <Text style={styles.primaryBtnText}>Indietro</Text>
        </TouchableOpacity>

        <View style={styles.footerBox}>
          <Text style={styles.footerText}>
            v55 MEGA_RELEASE_ACCELERATION_4 · deeplink-only · no claim · preview shell
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
  card: {
    backgroundColor: '#141a22',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222b36',
  },
  sectionTitle: { color: '#fff', fontSize: 15, fontWeight: '700', marginBottom: 8 },
  line: { color: '#cdd6e0', fontSize: 13, marginBottom: 4 },
  helper: { color: '#9aa4b2', fontSize: 12, marginTop: 8 },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  gridCell: {
    width: '31%',
    aspectRatio: 1,
    backgroundColor: '#1a212b',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2a3340',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  gridCellText: { color: '#5a6473', fontSize: 16 },
  guardsBox: {
    backgroundColor: '#1a212b',
    borderRadius: 8,
    padding: 10,
    marginTop: 4,
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
  footerBox: { marginTop: 24, alignItems: 'center' },
  footerText: { color: '#5a6473', fontSize: 11 },
});
