/**
 * gem-socket-test.tsx — PROJECT_GEM_SOCKET_RUNTIME_PACK (v27)
 *
 * Sandbox/test screen read-only per il sistema Gem Socket.
 * NESSUNA mutation. NESSUNA chiamata backend obbligatoria.
 * Deeplink only: /gem-socket-test.
 */
import React, { useMemo, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { router } from 'expo-router';
import {
  GEM_FAMILIES,
  GEM_TIERS,
  MAX_SOCKETS_BY_RARITY,
  SOCKET_LEVEL_UNLOCKS,
  SAFETY_BADGE_LABELS,
  maxSocketsForRarity,
  levelRequiredForSocket,
  type GemFamily,
} from '../constants/gemSocket';

const SCREEN_TAG = 'PROJECT_GEM_SOCKET_RUNTIME/v27';

const SAMPLE_GEAR = {
  gear_id: 'sample_weapon_001',
  slot: 'weapon' as const,
  rarity: 5,
  level: 25,
  base_stats: { attack: 1000 },
};

export default function GemSocketTestScreen() {
  const insets = useSafeAreaInsets();
  const [selectedFamily, setSelectedFamily] = useState<GemFamily>(GEM_FAMILIES[0]);
  const maxSlots = maxSocketsForRarity(SAMPLE_GEAR.rarity);
  const slotUnlocked = useMemo(
    () => [1,2,3].map((i) => ({
      index: i,
      withinRarity: i <= maxSlots,
      requiredLevel: levelRequiredForSocket(i),
      levelOk: (levelRequiredForSocket(i) ?? 0) <= SAMPLE_GEAR.level,
    })),
    [maxSlots]
  );

  return (
    <View style={[s.container, { paddingTop: insets.top, paddingBottom: insets.bottom }]}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}
          accessibilityRole="button" accessibilityLabel="Torna indietro"
          hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}>
          <Text style={s.backText}>{'‹'} Indietro</Text>
        </TouchableOpacity>
        <Text style={s.title}>Gem Socket (TEST)</Text>
        <View style={s.headerSpacer} />
      </View>

      <View style={s.badgeRow}>
        <View style={[s.badge, s.badgeWarn]}><Text style={s.badgeTxt}>{SAFETY_BADGE_LABELS.preview_only}</Text></View>
        <View style={[s.badge, s.badgeInfo]}><Text style={s.badgeTxt}>{SAFETY_BADGE_LABELS.no_db}</Text></View>
        <View style={[s.badge, s.badgeInfo]}><Text style={s.badgeTxt}>{SAFETY_BADGE_LABELS.no_premium}</Text></View>
        <View style={[s.badge, s.badgeWarn]}><Text style={s.badgeTxt}>{SAFETY_BADGE_LABELS.no_live_commit}</Text></View>
        <View style={[s.badge, s.badgeInfo]}><Text style={s.badgeTxt}>{SAFETY_BADGE_LABELS.no_rune_overlap}</Text></View>
      </View>

      <ScrollView contentContainerStyle={s.scrollContent}>
        <View style={s.explainBox}>
          <Text style={s.explainTitle}>Cosa sono le Gemme Socket</Text>
          <Text style={s.explainTxt}>
            • Gear = equip classico, cap +50.{'\n'}
            • Gemme = pietre incastonabili NEI gear (socket).{'\n'}
            • Rune = scroll/talismani/pergamene/sigilli, equipaggiati sull'eroe.{'\n'}
            • Artefatti = collezione globale roster/account.{'\n'}
            • Divine Weapon = arma personale dei 6★.{'\n'}
            • NESSUN consumo della valuta premium `gems`.{'\n'}
            • Nessun commit live in questo pack.
          </Text>
        </View>

        <Text style={s.sectionTitle}>Sample Gear</Text>
        <View style={s.card}>
          <Text style={s.cardTitle}>{SAMPLE_GEAR.slot.toUpperCase()} — R{SAMPLE_GEAR.rarity}★</Text>
          <Text style={s.cardBody}>Livello: +{SAMPLE_GEAR.level}  ·  Attack base: {SAMPLE_GEAR.base_stats.attack}</Text>
          <Text style={s.cardMeta}>gear_id: {SAMPLE_GEAR.gear_id}</Text>
        </View>

        <Text style={s.sectionTitle}>Socket slots (rarity {SAMPLE_GEAR.rarity}★, max {maxSlots})</Text>
        <View style={s.slotsRow}>
          {slotUnlocked.map((slot) => {
            const eligible = slot.withinRarity && slot.levelOk;
            return (
              <View key={slot.index} style={[s.slotPill, !eligible && s.slotPillLocked]}>
                <Text style={s.slotPillId}>Slot {slot.index}</Text>
                <Text style={s.slotPillStatus}>
                  {!slot.withinRarity ? 'rarità bassa' : !slot.levelOk ? `+${slot.requiredLevel}` : 'pronto'}
                </Text>
              </View>
            );
          })}
        </View>
        <Text style={s.helperTxt}>
          Soglie unlock: socket1=+{SOCKET_LEVEL_UNLOCKS[1]}, socket2=+{SOCKET_LEVEL_UNLOCKS[2]}, socket3=+{SOCKET_LEVEL_UNLOCKS[3]}.{'\n'}
          Max socket per rarità: {Object.entries(MAX_SOCKETS_BY_RARITY).map(([r, n]) => `R${r}=${n}`).join(' · ')}
        </Text>

        <Text style={s.sectionTitle}>Famiglie Gemme (6)</Text>
        <View style={s.famGrid}>
          {GEM_FAMILIES.map((fam) => {
            const active = fam.family_id === selectedFamily.family_id;
            return (
              <TouchableOpacity
                key={fam.family_id}
                onPress={() => setSelectedFamily(fam)}
                style={[s.famCard, active && { borderColor: fam.color, borderWidth: 2 }]}
                accessibilityRole="button"
                accessibilityLabel={`Seleziona ${fam.label_it}`}
              >
                <View style={[s.famDot, { backgroundColor: fam.color }]} />
                <Text style={s.famTitle}>{fam.label_it}</Text>
                <Text style={s.famMeta}>{fam.stat_family}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text style={s.sectionTitle}>Tier disponibili (preview non-final)</Text>
        <View style={s.tierRow}>
          {GEM_TIERS.map((t) => (
            <View key={t} style={s.tierPill}><Text style={s.tierPillTxt}>{t}</Text></View>
          ))}
        </View>

        <View style={s.previewBox}>
          <Text style={s.previewTitle}>Selezione corrente</Text>
          <Text style={s.previewLine}>Famiglia: {selectedFamily.label_it} ({selectedFamily.family_id})</Text>
          <Text style={s.previewLine}>Stat: {selectedFamily.stat_family}</Text>
          <Text style={s.previewLine}>Slot preferiti: {selectedFamily.preferred_slots.join(', ')}</Text>
          {selectedFamily.max_per_item_preview != null && (
            <Text style={s.previewLine}>Max per item (preview): {selectedFamily.max_per_item_preview}</Text>
          )}
          <Text style={s.previewHint}>
            Le combinazioni esatte di stat saranno definite nel pack di safety hardening.
            Endpoint preview: POST /api/gem-socket/socket-preview.
          </Text>
        </View>

        <Text style={s.footerText}>{`tag=${SCREEN_TAG}`}</Text>
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#080816' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#1f1f33' },
  backBtn: { minHeight: 44, minWidth: 88, justifyContent: 'center' },
  backText: { color: '#9ea0c8', fontSize: 16, fontWeight: '600' },
  title: { color: '#fff', fontSize: 18, fontWeight: '700' },
  headerSpacer: { width: 88 },
  badgeRow: { flexDirection: 'row', gap: 6, paddingHorizontal: 16, paddingTop: 10, flexWrap: 'wrap' },
  badge: { paddingHorizontal: 8, paddingVertical: 3, backgroundColor: '#252540',
    borderRadius: 6, borderWidth: 1, borderColor: '#3a3a55' },
  badgeWarn: { backgroundColor: '#3a2a16', borderColor: '#6b4a1f' },
  badgeInfo: { backgroundColor: '#16243a', borderColor: '#1f4a6b' },
  badgeTxt: { color: '#d8d8f0', fontSize: 9, fontWeight: '700', letterSpacing: 0.5 },
  scrollContent: { paddingHorizontal: 16, paddingTop: 12, paddingBottom: 32 },
  explainBox: { backgroundColor: '#0f0f1e', borderRadius: 10, borderWidth: 1, borderColor: '#22223a', padding: 12, marginBottom: 16 },
  explainTitle: { color: '#fff', fontSize: 13, fontWeight: '700', marginBottom: 6 },
  explainTxt: { color: '#bcbcd8', fontSize: 12, lineHeight: 19 },
  sectionTitle: { color: '#fff', fontSize: 14, fontWeight: '700', marginTop: 14, marginBottom: 8, letterSpacing: 0.3 },
  card: { backgroundColor: '#141425', borderRadius: 10, borderWidth: 1, borderColor: '#22223a', padding: 12, marginBottom: 8 },
  cardTitle: { color: '#fff', fontSize: 14, fontWeight: '700' },
  cardBody: { color: '#bcbcd8', fontSize: 12, lineHeight: 18, marginTop: 4 },
  cardMeta: { color: '#5a5c7a', fontSize: 10, fontWeight: '600', marginTop: 4 },
  slotsRow: { flexDirection: 'row', gap: 8, flexWrap: 'wrap' },
  slotPill: { paddingHorizontal: 14, paddingVertical: 8, backgroundColor: '#1a1a2e',
    borderRadius: 10, borderWidth: 1, borderColor: '#2a2a44', alignItems: 'center', minWidth: 78 },
  slotPillLocked: { opacity: 0.55, borderColor: '#3a2a16' },
  slotPillId: { color: '#fff', fontSize: 13, fontWeight: '800' },
  slotPillStatus: { color: '#9ea0c8', fontSize: 10, fontWeight: '600', marginTop: 2 },
  helperTxt: { color: '#9ea0c8', fontSize: 11, lineHeight: 16, marginTop: 8 },
  famGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  famCard: { backgroundColor: '#141425', borderRadius: 10, borderWidth: 1, borderColor: '#22223a',
    padding: 10, minWidth: '30%', flexGrow: 1, alignItems: 'center' },
  famDot: { width: 16, height: 16, borderRadius: 8, marginBottom: 6 },
  famTitle: { color: '#fff', fontSize: 12, fontWeight: '700' },
  famMeta: { color: '#9ea0c8', fontSize: 10, fontWeight: '600', marginTop: 2 },
  tierRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  tierPill: { paddingHorizontal: 10, paddingVertical: 5, backgroundColor: '#1a1a2e',
    borderRadius: 14, borderWidth: 1, borderColor: '#2a2a44' },
  tierPillTxt: { color: '#d8d8f0', fontSize: 11, fontWeight: '700', textTransform: 'capitalize' },
  previewBox: { backgroundColor: '#0f0f1e', borderRadius: 10, borderWidth: 1, borderColor: '#22223a', padding: 12, marginTop: 14 },
  previewTitle: { color: '#fff', fontSize: 13, fontWeight: '700', marginBottom: 6 },
  previewLine: { color: '#bcbcd8', fontSize: 12, lineHeight: 18 },
  previewHint: { color: '#7c7e9c', fontSize: 11, marginTop: 8, fontStyle: 'italic', lineHeight: 16 },
  footerText: { color: '#5a5c7a', fontSize: 10, marginTop: 20 },
});
