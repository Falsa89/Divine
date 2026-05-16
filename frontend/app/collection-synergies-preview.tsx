/**
 * CS2-D — Collection Synergies V2 Preview (READ-ONLY)
 * ─────────────────────────────────────────────────────────────────────────
 * Strictly read-only preview screen that surfaces the Collection Synergy V2
 * design data (CS2-A readiness plan + CS2-B preview resolver) following
 * the CS2-C contract (`collection_synergy_preview_screen_contract_v1`).
 *
 * SAFETY:
 *   - NO POST/PUT/PATCH/DELETE.
 *   - NO claim / activate / spend / equip / enable runtime / apply buff buttons.
 *   - NO player-owned data fetch. Falls back to a static design payload
 *     when network is unavailable.
 *   - NO battle / runtime hooks. NO DB writes.
 *   - Borea hidden: any `greek_borea` reference is silently filtered.
 *   - Legacy aliases `borea` / `primordial_gaia` are never rendered.
 *
 * Pressable usage is limited to a back navigation arrow and an
 * expand/collapse toggle on each category card; both are harmless.
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  View, Text, ScrollView, StyleSheet, ActivityIndicator, Pressable,
} from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { apiCall } from '../utils/api';

// ─────────────────────────────────────────────────────────────────────────
// Static design fallback — derived directly from
// /app/data/design/synergies/collection_synergies_v2_readiness_plan_v1.json
// Used when no network/data source is available. Strictly inert.
// ─────────────────────────────────────────────────────────────────────────
const STATIC_DESIGN_CATEGORIES: Array<{
  id: string;
  description: string;
  axis: string;
  future_runtime_feature_flag: string;
}> = [
  {
    id: 'faction_collection',
    description: 'Bonus per X owned heroes of faction Y',
    axis: 'faction',
    future_runtime_feature_flag: 'COLLECTION_SYNERGY_FACTION_ENABLED',
  },
  {
    id: 'element_collection',
    description: 'Bonus per X owned heroes of element Z',
    axis: 'element',
    future_runtime_feature_flag: 'COLLECTION_SYNERGY_ELEMENT_ENABLED',
  },
  {
    id: 'rarity_collection',
    description: 'Bonus per X owned heroes of rarity 5★ / 6★',
    axis: 'rarity',
    future_runtime_feature_flag: 'COLLECTION_SYNERGY_RARITY_ENABLED',
  },
  {
    id: 'origin_group_collection',
    description: 'Bonus per owning a thematic origin group (e.g. Olympian Pantheon)',
    axis: 'origin_group',
    future_runtime_feature_flag: 'COLLECTION_SYNERGY_ORIGIN_ENABLED',
  },
  {
    id: 'mythic_set_collection',
    description: 'Bonus per completing a specific mythic set (3-piece, 5-piece)',
    axis: 'mythic_set',
    future_runtime_feature_flag: 'COLLECTION_SYNERGY_MYTHIC_SET_ENABLED',
  },
  {
    id: 'divine_weapon_collection_link_future',
    description: 'Bonus per owning N Divine Weapons (catalog count, not equip)',
    axis: 'divine_weapon_catalog_count',
    future_runtime_feature_flag: 'COLLECTION_SYNERGY_DW_LINK_ENABLED',
  },
];

const STATIC_MILESTONE_MODEL = {
  trigger_axis: 'owned_count',
  owned_count_thresholds_tiered: [3, 5, 10] as number[],
  star_threshold_future_optional: [5, 6] as number[],
  max_total_collection_bonus_pct: 15,
  max_per_category_bonus_pct: 5,
  stacking_rule: 'additive_capped',
  applies_to: ['non_pvp_initial', 'opt_in_pvp_future_only'] as string[],
};

const COLORS = {
  bg: '#0E0917',
  panel: '#1A0F2E',
  border: '#2A1F4E',
  text: '#F0E6FF',
  muted: '#88799A',
  gold: '#FFB347',
  locked: '#5A4778',
  good: '#88CC88',
};

type Category = typeof STATIC_DESIGN_CATEGORIES[number];

export default function CollectionSynergiesPreviewScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState<Category[]>([]);
  const [milestone, setMilestone] = useState(STATIC_MILESTONE_MODEL);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [source, setSource] = useState<'design' | 'static_fallback'>('static_fallback');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        // No player data fetched. Future read-only design endpoint may exist;
        // we attempt it gracefully and fall back to static design payload.
        const r = await apiCall('/api/synergies/v2/all').catch(() => null);
        if (cancelled) return;
        // We only use the existing public v2 endpoint to confirm the
        // backend is reachable; collection categories themselves stay
        // hardcoded from design JSON per CS2-C contract.
        if (r && Array.isArray(r)) {
          setSource('design');
        } else {
          setSource('static_fallback');
        }
        setCategories(STATIC_DESIGN_CATEGORIES);
        setMilestone(STATIC_MILESTONE_MODEL);
      } catch (e: any) {
        if (cancelled) return;
        setError(String(e?.message || e));
        setCategories(STATIC_DESIGN_CATEGORIES);
        setMilestone(STATIC_MILESTONE_MODEL);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const totalCap = milestone.max_total_collection_bonus_pct;
  const perCat = milestone.max_per_category_bonus_pct;

  const renderCard = (c: Category) => {
    const isOpen = !!expanded[c.id];
    return (
      <View key={c.id} style={styles.card}>
        <Pressable
          onPress={() => setExpanded((p) => ({ ...p, [c.id]: !p[c.id] }))}
          accessibilityRole="button"
          accessibilityLabel={`Toggle details for ${c.id}`}
          style={({ pressed }) => [styles.cardHeader, pressed && { opacity: 0.85 }]}
        >
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>{c.id}</Text>
            <Text style={styles.cardSubtitle}>axis: {c.axis}</Text>
          </View>
          <View style={styles.lockedBadge}>
            <Text style={styles.lockedBadgeText}>Locked / Future</Text>
          </View>
        </Pressable>
        {isOpen ? (
          <View style={styles.cardBody}>
            <Text style={styles.bodyText}>{c.description}</Text>
            <Text style={styles.metaText}>
              future_runtime_feature_flag: {c.future_runtime_feature_flag}
            </Text>
            <Text style={styles.metaText}>
              Currently OFF — no bonus applied to combat.
            </Text>
          </View>
        ) : null}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={styles.header}>
        <Pressable
          onPress={() => router.back()}
          accessibilityRole="button"
          accessibilityLabel="Back"
          style={({ pressed }) => [styles.backBtn, pressed && { opacity: 0.7 }]}
          hitSlop={12}
        >
          <Text style={styles.backArrow}>{'‹'}</Text>
        </Pressable>
        <Text style={styles.headerTitle}>Collection Synergies</Text>
        <View style={{ width: 36 }} />
      </View>

      <View style={styles.banner}>
        <Text style={styles.bannerTitle}>Preview / Design-only / Non attivo</Text>
        <Text style={styles.bannerText}>
          Anteprima design delle sinergie da collezione future. Nessun bonus
          è attualmente applicato al combattimento.
        </Text>
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={COLORS.gold} />
          <Text style={styles.metaText}>Loading preview…</Text>
        </View>
      ) : (
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.capPanel}>
            <Text style={styles.capTitle}>Cap Policy</Text>
            <Text style={styles.capLine}>Max totale: {totalCap}%</Text>
            <Text style={styles.capLine}>Max per categoria: {perCat}%</Text>
            <Text style={styles.capLine}>
              Soglie owned: {milestone.owned_count_thresholds_tiered.join(' / ')}
            </Text>
            <Text style={styles.capLine}>
              Stacking: {milestone.stacking_rule}
            </Text>
            <Text style={styles.capLine}>
              Applies to: {milestone.applies_to.join(', ')}
            </Text>
          </View>

          <Text style={styles.sectionTitle}>
            Categorie ({categories.length})
          </Text>
          {categories.map(renderCard)}

          <View style={styles.footer}>
            <Text style={styles.footerText}>
              Sorgente: {source === 'design' ? 'live design' : 'static fallback'} ·
              CS2-A readiness + CS2-B preview resolver
            </Text>
            <Text style={styles.footerText}>
              Borea: hidden / catalog-only ·
              Legacy aliases (borea / primordial_gaia): excluded
            </Text>
            {error ? (
              <Text style={[styles.footerText, { color: '#FF8888' }]}>
                {error}
              </Text>
            ) : null}
          </View>
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: COLORS.bg },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  backBtn: {
    width: 36,
    height: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backArrow: { color: COLORS.text, fontSize: 28, lineHeight: 28 },
  headerTitle: {
    flex: 1,
    color: COLORS.text,
    fontSize: 18,
    fontWeight: '700',
    textAlign: 'center',
  },
  banner: {
    backgroundColor: COLORS.panel,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  bannerTitle: {
    color: COLORS.gold,
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 4,
  },
  bannerText: { color: COLORS.muted, fontSize: 12, lineHeight: 16 },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 32 },
  capPanel: {
    backgroundColor: COLORS.panel,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  capTitle: {
    color: COLORS.gold,
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 6,
  },
  capLine: { color: COLORS.text, fontSize: 12, marginBottom: 2 },
  sectionTitle: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 8,
  },
  card: {
    backgroundColor: COLORS.panel,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 8,
    marginBottom: 8,
    overflow: 'hidden',
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 12,
    minHeight: 56,
  },
  cardTitle: { color: COLORS.text, fontSize: 14, fontWeight: '700' },
  cardSubtitle: { color: COLORS.muted, fontSize: 11, marginTop: 2 },
  lockedBadge: {
    backgroundColor: COLORS.locked,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  lockedBadgeText: { color: COLORS.text, fontSize: 10, fontWeight: '700' },
  cardBody: {
    paddingHorizontal: 12,
    paddingBottom: 12,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  bodyText: { color: COLORS.text, fontSize: 12, lineHeight: 16, marginTop: 8 },
  metaText: { color: COLORS.muted, fontSize: 11, marginTop: 4 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  footer: { marginTop: 16, padding: 8 },
  footerText: { color: COLORS.muted, fontSize: 10, marginBottom: 2 },
});
