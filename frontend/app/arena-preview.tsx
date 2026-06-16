/**
 * Pack 122 Track E — Arena Opponent Selection Preview Hub.
 *
 * STRICT CONSTRAINTS (preview-only):
 *   - No matchmaking live.
 *   - No MMR / ranking mutation.
 *   - No reward grant.
 *   - No DB write.
 *   - Deterministic preview opponents only.
 *   - Tap opponent → pre-battle-lobby con opponent_id query param.
 *
 * Player-facing copy chiara: "Arena Preview - nessuna classifica reale".
 */
import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
// Pack 123 — Preview lobby URL builder (no-write, no-DB, no-grant).
import { buildPreviewLobbyUrl } from '../src/utils/previewBattleTeam';

const PREVIEW_OPPONENTS = [
  { id: 'preview_arena_001', name: 'Guerriero Preview A', power: 12500, rank: 'Bronzo (preview)' },
  { id: 'preview_arena_002', name: 'Mago Preview B', power: 18200, rank: 'Argento (preview)' },
  { id: 'preview_arena_003', name: 'Custode Preview C', power: 24100, rank: 'Oro (preview)' },
];

export default function ArenaPreviewScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  // Pack 124 — Back button con fallback safe a /(tabs)/home.
  const handleBack = React.useCallback(() => {
    try {
      if (router.canGoBack?.()) router.back();
      else router.replace('/(tabs)/home' as any);
    } catch (_e) {
      router.replace('/(tabs)/home' as any);
    }
  }, [router]);
  return (
    <View style={[s.root, { paddingTop: insets.top + 16 }]}>
      {/* Pack 124 — Top bar con back button (era assente: fix device QA). */}
      <View style={s.topBar}>
        <TouchableOpacity
          accessibilityRole="button"
          accessibilityLabel="Torna indietro"
          onPress={handleBack}
          activeOpacity={0.7}
          style={s.backBtn}
        >
          <Text style={s.backBtnTxt}>{'\u2190  Indietro'}</Text>
        </TouchableOpacity>
        <Text style={s.title}>Arena PvP — Preview</Text>
        <View style={{ width: 80 }} />
      </View>
      <View style={s.banner}>
        <Text style={s.bannerText}>
          Anteprima preview-only. Nessun matchmaking live, nessuna classifica reale,
          nessuna ricompensa. La battaglia sara' avviata in modalita' preview.
        </Text>
      </View>
      <ScrollView contentContainerStyle={{ paddingBottom: insets.bottom + 96, gap: 12 }}>
        {PREVIEW_OPPONENTS.map((o) => (
          <TouchableOpacity
            key={o.id}
            style={s.card}
            onPress={() => router.push(buildPreviewLobbyUrl({
              mode: 'arena',
              encounter_id: `enc_arena_preview_${o.id}`,
              enemy_source_id: o.id,
              enemy_source_type: 'authored',
              opponent_id: o.id,
            }) as any)}
          >
            <Text style={s.cardName}>{o.name}</Text>
            <Text style={s.cardMeta}>{o.rank} · Power {o.power}</Text>
            <Text style={s.cardCta}>Avvia preview →</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0a0a1a', paddingHorizontal: 16 },
  topBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 },
  backBtn: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 6, borderWidth: 1, borderColor: '#3D5AFE', backgroundColor: 'rgba(61,90,254,0.18)' },
  backBtnTxt: { color: '#9FA8DA', fontSize: 11, fontWeight: '900', letterSpacing: 1 },
  title: { color: '#FFD700', fontSize: 18, fontWeight: '900', marginBottom: 4, letterSpacing: 1 },
  banner: { backgroundColor: '#1f1f3a', padding: 12, borderRadius: 8, marginBottom: 16, borderWidth: 1, borderColor: '#3D5AFE' },
  bannerText: { color: '#cfd8dc', fontSize: 12, lineHeight: 18 },
  card: { backgroundColor: '#16162e', padding: 16, borderRadius: 10, borderWidth: 1, borderColor: '#2a2a4a' },
  cardName: { color: '#fff', fontSize: 16, fontWeight: '800' },
  cardMeta: { color: '#aabbcc', fontSize: 12, marginTop: 4 },
  cardCta: { color: '#88CCFF', fontSize: 12, marginTop: 8, fontWeight: '700' },
});
