/**
 * RM1.23-C — Codex Sinergie (read-only)
 * ─────────────────────────────────────────────────────────────────────────
 * Schermata dedicata per studiare tutte le sinergie:
 *   • Sinergie Team V2 (10 active definitions, ID-based)
 *   • Formazione (V1 guide passthrough, placeholder)
 *   • Elementi (V1 guide passthrough)
 *   • Collezione (placeholder, future expansion)
 *
 * Data:
 *   GET /api/synergies/codex          → 10 V2 enrichite (status/owned/in_team)
 *   GET /api/synergies/v2/all         → fallback se codex non auth
 *   GET /api/synergies/guide          → V1 mythological/elemental/class
 *
 * Read-only. Nessuna mutazione DB. Nessun bottone di upgrade.
 * La forza delle sinergie cresce automaticamente con le stelle degli eroi.
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Pressable,
} from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { apiCall } from '../utils/api';
import SynergyHeroMiniCard, { SynergyHeroMember } from '../components/ui/SynergyHeroMiniCard';

const COLORS = {
  bg: '#0E0917',
  panel: '#1A0F2E',
  border: '#2A1F4E',
  text: '#F0E6FF',
  muted: '#88799A',
  gold: '#FFB347',
  mythic: '#FF44CC',
  legendary: '#FFB347',
  epic: '#9966FF',
  rare: '#44AAFF',
  common: '#88CC88',
};

type V2Effect = { stat: string; mode: string; value: number; target: string };
type Member = SynergyHeroMember;
type CodexSynergy = {
  id: string;
  display_name: string;
  description?: string;
  icon?: string;
  rarity_tier?: string;
  release_group?: string;
  required_hero_ids: string[];
  effects: V2Effect[];
  status: 'active' | 'available_not_in_team' | 'near_complete' | 'not_owned' | 'future';
  owned_count: number;
  in_team_count: number;
  required_count: number;
  completion_owned: number;
  completion_team: number;
  avg_owned_stars: number;
  members: Member[];
  min_required: number;
  max_members: number;
};

const STATUS_LABEL: Record<string, string> = {
  active: 'Attiva',
  available_not_in_team: 'Disponibile',
  near_complete: 'Quasi attiva',
  not_owned: 'Non posseduta',
  future: 'Futura',
};
const STATUS_COLOR: Record<string, string> = {
  active: '#44DD88',
  available_not_in_team: '#44AAFF',
  near_complete: '#FFB347',
  not_owned: '#666',
  future: '#88799A',
};

const FILTER_OPTIONS = [
  'Tutte', 'Attive', 'Disponibili', 'Quasi attive', 'Non possedute',
] as const;
type FilterOpt = typeof FILTER_OPTIONS[number];

const SECTIONS = [
  { id: 'team_synergies_v2', label: 'Sinergie Team' },
  { id: 'formation', label: 'Formazione' },
  { id: 'elements', label: 'Elementi' },
  { id: 'collection', label: 'Collezione' },
] as const;
type SectionId = typeof SECTIONS[number]['id'];

export default function SynergyCodexScreen() {
  const router = useRouter();
  const [section, setSection] = useState<SectionId>('team_synergies_v2');
  const [filter, setFilter] = useState<FilterOpt>('Tutte');
  const [synergies, setSynergies] = useState<CodexSynergy[]>([]);
  const [statusCounts, setStatusCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [v1Guide, setV1Guide] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [codex, guide] = await Promise.all([
          apiCall('/api/synergies/codex'),
          apiCall('/api/synergies/guide').catch(() => null),
        ]);
        setSynergies(codex?.team_synergies || []);
        setStatusCounts(codex?.status_counts || {});
        setV1Guide(guide);
      } catch (e: any) {
        // Fallback to public V2 list if codex auth fails
        try {
          const pub = await apiCall('/api/synergies/v2/all');
          const fallback = (pub?.team_synergies || []).map((s: any) => ({
            ...s,
            status: 'not_owned',
            owned_count: 0, in_team_count: 0, required_count: s.required_hero_ids?.length || 0,
            completion_owned: 0, completion_team: 0, avg_owned_stars: 0,
            members: (s.required_hero_ids || []).map((cid: string) => ({
              canonical_id: cid, display_name: cid, owned: false, in_team: false,
              best_stars: 0, max_stars: 5,
              hero_id: cid, image_url: null, rarity: 1,
              element: null, faction: null,
            })),
          }));
          setSynergies(fallback);
        } catch (e2: any) {
          setError(e2?.message || e?.message || 'Errore caricamento');
        }
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = useMemo(() => {
    if (filter === 'Attive') return synergies.filter((s) => s.status === 'active');
    if (filter === 'Disponibili') return synergies.filter((s) => s.status === 'available_not_in_team');
    if (filter === 'Quasi attive') return synergies.filter((s) => s.status === 'near_complete');
    if (filter === 'Non possedute') return synergies.filter((s) => s.status === 'not_owned');
    return synergies;
  }, [synergies, filter]);

  const renderTeamSection = () => (
    <View>
      {/* Status summary chips */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.summaryRow}>
        <View style={[s.summaryChip, { borderColor: STATUS_COLOR.active }]}>
          <Text style={[s.summaryNum, { color: STATUS_COLOR.active }]}>{statusCounts.active || 0}</Text>
          <Text style={s.summaryLbl}>Attive</Text>
        </View>
        <View style={[s.summaryChip, { borderColor: STATUS_COLOR.available_not_in_team }]}>
          <Text style={[s.summaryNum, { color: STATUS_COLOR.available_not_in_team }]}>
            {statusCounts.available_not_in_team || 0}
          </Text>
          <Text style={s.summaryLbl}>Disponibili</Text>
        </View>
        <View style={[s.summaryChip, { borderColor: STATUS_COLOR.near_complete }]}>
          <Text style={[s.summaryNum, { color: STATUS_COLOR.near_complete }]}>
            {statusCounts.near_complete || 0}
          </Text>
          <Text style={s.summaryLbl}>Quasi</Text>
        </View>
        <View style={[s.summaryChip, { borderColor: STATUS_COLOR.not_owned }]}>
          <Text style={[s.summaryNum, { color: STATUS_COLOR.not_owned }]}>
            {statusCounts.not_owned || 0}
          </Text>
          <Text style={s.summaryLbl}>Non possedute</Text>
        </View>
        <View style={s.summaryChipTot}>
          <Text style={s.summaryNumTot}>{synergies.length}</Text>
          <Text style={s.summaryLbl}>Totali</Text>
        </View>
      </ScrollView>

      {/* Filter chips */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.filterRow}>
        {FILTER_OPTIONS.map((opt) => (
          <TouchableOpacity
            key={opt}
            onPress={() => setFilter(opt)}
            style={[s.filterChip, filter === opt && s.filterChipActive]}
          >
            <Text style={[s.filterChipText, filter === opt && s.filterChipTextActive]}>{opt}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Synergy cards */}
      {filtered.length === 0 && (
        <Text style={s.emptyState}>Nessuna sinergia in questa categoria.</Text>
      )}
      {filtered.map((syn) => (
        <SynergyCard key={syn.id} syn={syn} />
      ))}

      <View style={s.upgradeNote}>
        <Text style={s.upgradeNoteText}>
          ✦ Le sinergie crescono automaticamente quando gli eroi coinvolti aumentano le stelle.
          Nessuna valuta o bottone di upgrade richiesto.
        </Text>
      </View>
    </View>
  );

  const renderFormationSection = () => (
    <View>
      <Text style={s.placeholderTitle}>Formazione</Text>
      <Text style={s.placeholderText}>
        Bonus compositivi basati su elementi/fazioni/ruoli/categorie nella formazione attiva.
        Foundation V2 in arrivo.
      </Text>
      {v1Guide?.class_synergies && (
        <View style={s.v1Wrap}>
          <Text style={s.v1Title}>Composizione di classe (V1)</Text>
          {v1Guide.class_synergies.map((c: any, i: number) => (
            <View key={i} style={s.v1Row}>
              <Text style={s.v1Icon}>{c.icon}</Text>
              <Text style={s.v1Name}>{c.name}</Text>
              <Text style={s.v1Desc}>{c.description}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );

  const renderElementsSection = () => (
    <View>
      <Text style={s.placeholderTitle}>Elementi</Text>
      <Text style={s.placeholderText}>
        Vantaggi elementali in battaglia (rock-paper-scissors).
      </Text>
      {v1Guide?.element_advantages && (
        <View style={s.v1Wrap}>
          <Text style={s.v1Title}>Vantaggi elementali</Text>
          {Object.entries(v1Guide.element_advantages).map(([atk, vs]: [string, any]) => (
            <Text key={atk} style={s.v1ElemRow}>
              <Text style={{ color: COLORS.gold }}>{atk}</Text>
              <Text>: forte vs </Text>
              <Text style={{ color: '#FF8888' }}>
                {Object.entries(vs as any)
                  .filter(([_, v]: [string, any]) => v > 1)
                  .map(([d]: [string, any]) => d)
                  .join(', ') || '—'}
              </Text>
            </Text>
          ))}
        </View>
      )}
    </View>
  );

  const renderCollectionSection = () => (
    <View>
      <Text style={s.placeholderTitle}>Collezione (Futura)</Text>
      <Text style={s.placeholderText}>
        Bonus basati sull'intera collezione (account-wide). Non richiedono che gli eroi siano in
        squadra attiva. Sezione foundation in attesa di prima ondata.
      </Text>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={s.root}>
        <Stack.Screen options={{ title: 'Codex Sinergie', headerShown: false }} />
        <View style={s.loaderWrap}>
          <ActivityIndicator color={COLORS.gold} />
          <Text style={s.loaderText}>Caricamento Codex…</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={s.root}>
      <Stack.Screen options={{ title: 'Codex Sinergie', headerShown: false }} />

      <View style={s.header}>
        <Pressable onPress={() => router.back()} style={s.backBtn}>
          <Text style={s.backBtnText}>← Indietro</Text>
        </Pressable>
        <Text style={s.title}>📖 Codex Sinergie</Text>
        <View style={{ width: 70 }} />
      </View>

      {/* Section tabs */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.sectionRow}>
        {SECTIONS.map((sec) => (
          <TouchableOpacity
            key={sec.id}
            onPress={() => setSection(sec.id as SectionId)}
            style={[s.sectionTab, section === sec.id && s.sectionTabActive]}
          >
            <Text style={[s.sectionTabText, section === sec.id && s.sectionTabTextActive]}>
              {sec.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView style={s.scroll} contentContainerStyle={s.scrollContent}>
        {error && (
          <View style={s.errorBox}>
            <Text style={s.errorText}>{error}</Text>
          </View>
        )}
        {section === 'team_synergies_v2' && renderTeamSection()}
        {section === 'formation' && renderFormationSection()}
        {section === 'elements' && renderElementsSection()}
        {section === 'collection' && renderCollectionSection()}
      </ScrollView>
    </SafeAreaView>
  );
}

function SynergyCard({ syn }: { syn: CodexSynergy }) {
  const tierColor =
    syn.rarity_tier === 'mythic' ? COLORS.mythic
    : syn.rarity_tier === 'legendary' ? COLORS.legendary
    : syn.rarity_tier === 'epic' ? COLORS.epic
    : syn.rarity_tier === 'rare' ? COLORS.rare
    : COLORS.common;
  const statusColor = STATUS_COLOR[syn.status] || COLORS.muted;
  const statusLabel = STATUS_LABEL[syn.status] || syn.status;
  return (
    <View style={[s.synCard, { borderColor: tierColor + '60' }]}>
      <View style={s.synCardHeader}>
        <Text style={s.synCardIcon}>{syn.icon || '✦'}</Text>
        <View style={{ flex: 1 }}>
          <Text style={[s.synCardName, { color: tierColor }]}>{syn.display_name}</Text>
          {!!syn.description && <Text style={s.synCardDesc}>{syn.description}</Text>}
        </View>
        <View style={[s.statusBadge, { backgroundColor: statusColor + '20', borderColor: statusColor }]}>
          <Text style={[s.statusBadgeText, { color: statusColor }]}>{statusLabel}</Text>
        </View>
      </View>

      <View style={s.synCardMeta}>
        <Text style={s.metaItem}>
          Posseduti: <Text style={{ color: COLORS.text }}>{syn.owned_count}/{syn.required_count}</Text>
        </Text>
        <Text style={s.metaItem}>
          In team: <Text style={{ color: COLORS.text }}>{syn.in_team_count}/{syn.required_count}</Text>
        </Text>
        {syn.avg_owned_stars > 0 && (
          <Text style={s.metaItem}>
            ⭐ avg: <Text style={{ color: COLORS.gold }}>{syn.avg_owned_stars.toFixed(1)}</Text>
          </Text>
        )}
      </View>

      <View style={s.membersRow}>
        {syn.members.map((m) => (
          <SynergyHeroMiniCard key={m.canonical_id} member={m} variant="tile" />
        ))}
      </View>

      {syn.effects && syn.effects.length > 0 && (
        <View style={s.effectsRow}>
          {syn.effects.map((e, i) => (
            <View key={i} style={s.effectPill}>
              <Text style={s.effectText}>
                {e.stat}{e.mode === 'percent' ? ` +${Math.round(e.value * 100)}%` : ` +${e.value}`}
                {e.target !== 'synergy_members' ? ` · ${e.target}` : ''}
              </Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: COLORS.bg },
  loaderWrap: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12 },
  loaderText: { color: COLORS.muted },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    padding: 12, borderBottomWidth: 1, borderBottomColor: COLORS.border,
  },
  backBtn: { paddingVertical: 6, paddingHorizontal: 8 },
  backBtnText: { color: COLORS.gold, fontSize: 13, fontWeight: '700' },
  title: { color: COLORS.gold, fontSize: 17, fontWeight: '900', letterSpacing: 0.5 },
  sectionRow: { flexGrow: 0, paddingHorizontal: 8, paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: COLORS.border },
  sectionTab: {
    paddingHorizontal: 12, paddingVertical: 6, borderRadius: 12,
    backgroundColor: COLORS.panel, marginRight: 6, borderWidth: 1, borderColor: COLORS.border,
  },
  sectionTabActive: { backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold },
  sectionTabText: { color: COLORS.muted, fontSize: 12, fontWeight: '700' },
  sectionTabTextActive: { color: COLORS.gold },
  scroll: { flex: 1 },
  scrollContent: { padding: 12, paddingBottom: 60 },
  errorBox: { backgroundColor: '#FF000020', borderColor: '#FF0000', borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 12 },
  errorText: { color: '#FF8888' },
  summaryRow: { flexGrow: 0, marginBottom: 8 },
  summaryChip: {
    backgroundColor: COLORS.panel, borderWidth: 1, borderRadius: 10,
    paddingHorizontal: 12, paddingVertical: 8, marginRight: 6, alignItems: 'center', minWidth: 70,
  },
  summaryChipTot: {
    backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold, borderWidth: 1, borderRadius: 10,
    paddingHorizontal: 12, paddingVertical: 8, marginRight: 6, alignItems: 'center', minWidth: 70,
  },
  summaryNum: { fontSize: 20, fontWeight: '900' },
  summaryNumTot: { fontSize: 20, fontWeight: '900', color: COLORS.gold },
  summaryLbl: { fontSize: 9, color: COLORS.muted, marginTop: 2 },
  filterRow: { flexGrow: 0, marginBottom: 10 },
  filterChip: {
    backgroundColor: COLORS.panel, borderWidth: 1, borderColor: COLORS.border,
    borderRadius: 14, paddingHorizontal: 12, paddingVertical: 6, marginRight: 5,
  },
  filterChipActive: { backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold },
  filterChipText: { color: COLORS.muted, fontSize: 11, fontWeight: '700' },
  filterChipTextActive: { color: COLORS.gold },
  emptyState: { color: COLORS.muted, textAlign: 'center', padding: 20, fontStyle: 'italic' },
  synCard: {
    backgroundColor: COLORS.panel, borderWidth: 1, borderRadius: 10,
    padding: 10, marginBottom: 10,
  },
  synCardHeader: { flexDirection: 'row', alignItems: 'flex-start', gap: 8 },
  synCardIcon: { fontSize: 22 },
  synCardName: { fontSize: 14, fontWeight: '900' },
  synCardDesc: { color: COLORS.muted, fontSize: 10, marginTop: 2 },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 3, borderWidth: 1, borderRadius: 8 },
  statusBadgeText: { fontSize: 9, fontWeight: '900', letterSpacing: 0.4 },
  synCardMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginTop: 8 },
  metaItem: { color: COLORS.muted, fontSize: 10 },
  membersRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 10 },
  memberPill: {
    paddingHorizontal: 8, paddingVertical: 4, borderWidth: 1, borderRadius: 6,
    flexDirection: 'row', alignItems: 'center', gap: 4, maxWidth: 220,
  },
  memberName: { fontSize: 10, fontWeight: '700' },
  memberStars: { fontSize: 9, color: COLORS.gold },
  effectsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 8 },
  effectPill: { backgroundColor: '#FFB34715', borderWidth: 1, borderColor: '#FFB34740', borderRadius: 5, paddingHorizontal: 6, paddingVertical: 2 },
  effectText: { color: COLORS.gold, fontSize: 9, fontWeight: '700' },
  upgradeNote: { backgroundColor: '#FFB34708', borderColor: '#FFB34730', borderWidth: 1, borderRadius: 8, padding: 10, marginTop: 8 },
  upgradeNoteText: { color: COLORS.muted, fontSize: 10, fontStyle: 'italic', lineHeight: 14 },
  placeholderTitle: { color: COLORS.gold, fontSize: 16, fontWeight: '900', marginBottom: 6 },
  placeholderText: { color: COLORS.muted, fontSize: 12, lineHeight: 18, marginBottom: 12 },
  v1Wrap: { backgroundColor: COLORS.panel, padding: 10, borderRadius: 8, borderWidth: 1, borderColor: COLORS.border },
  v1Title: { color: COLORS.text, fontWeight: '700', marginBottom: 6 },
  v1Row: { flexDirection: 'row', gap: 6, marginBottom: 6, alignItems: 'center' },
  v1Icon: { fontSize: 14 },
  v1Name: { color: COLORS.gold, fontSize: 11, fontWeight: '700' },
  v1Desc: { color: COLORS.muted, fontSize: 9, flex: 1 },
  v1ElemRow: { color: COLORS.muted, fontSize: 11, marginBottom: 3 },
});
