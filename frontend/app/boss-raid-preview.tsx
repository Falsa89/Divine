/**
 * Pack 122 Track F — Boss / Raid Selection Preview Hub.
 *
 * STRICT CONSTRAINTS (preview-only):
 *   - No drop / loot.
 *   - No entry consumption.
 *   - No raid reward live.
 *   - No DB write.
 *   - Deterministic preview bosses only.
 *   - Tap boss → pre-battle-lobby con boss_id query param.
 */
import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
// Pack 123 — Preview lobby URL builder (no-write, no-DB, no-grant).
import { buildPreviewLobbyUrl } from '../src/utils/previewBattleTeam';

const PREVIEW_BOSSES = [
  { id: 'preview_boss_001', name: 'Drago Preview', tier: 'Tier 1 (preview)', power: 32000 },
  { id: 'preview_boss_002', name: 'Titano Preview', tier: 'Tier 2 (preview)', power: 48000 },
  { id: 'preview_boss_003', name: 'Demone Preview', tier: 'Tier 3 (preview)', power: 65000 },
];

export default function BossRaidPreviewScreen() {
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
        <Text style={s.title}>Raid Cooperativi — Preview</Text>
        <View style={{ width: 80 }} />
      </View>
      <View style={s.banner}>
        <Text style={s.bannerText}>
          Anteprima preview-only. Nessun drop, nessun ingresso consumato, nessuna
          ricompensa raid live. La battaglia partira' in modalita' preview.
        </Text>
      </View>
      <ScrollView contentContainerStyle={{ paddingBottom: insets.bottom + 96, gap: 12 }}>
        {PREVIEW_BOSSES.map((b) => (
          <TouchableOpacity
            key={b.id}
            style={s.card}
            onPress={() => router.push(buildPreviewLobbyUrl({
              mode: 'boss',
              encounter_id: `enc_boss_preview_${b.id}`,
              enemy_source_id: b.id,
              enemy_source_type: 'boss',
              boss_id: b.id,
            }) as any)}
          >
            <Text style={s.cardName}>{b.name}</Text>
            <Text style={s.cardMeta}>{b.tier} · Power {b.power}</Text>
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
  backBtn: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 6, borderWidth: 1, borderColor: '#FF5544', backgroundColor: 'rgba(255,85,68,0.18)' },
  backBtnTxt: { color: '#FFAB91', fontSize: 11, fontWeight: '900', letterSpacing: 1 },
  title: { color: '#FFD700', fontSize: 18, fontWeight: '900', marginBottom: 4, letterSpacing: 1 },
  banner: { backgroundColor: '#1f1f3a', padding: 12, borderRadius: 8, marginBottom: 16, borderWidth: 1, borderColor: '#FF5544' },
  bannerText: { color: '#cfd8dc', fontSize: 12, lineHeight: 18 },
  card: { backgroundColor: '#16162e', padding: 16, borderRadius: 10, borderWidth: 1, borderColor: '#2a2a4a' },
  cardName: { color: '#fff', fontSize: 16, fontWeight: '800' },
  cardMeta: { color: '#ffaa44', fontSize: 12, marginTop: 4 },
  cardCta: { color: '#88CCFF', fontSize: 12, marginTop: 8, fontWeight: '700' },
});
