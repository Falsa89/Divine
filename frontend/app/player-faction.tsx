/**
 * RM1.24-A — Player Faction V2 Selection UI Foundation
 * ─────────────────────────────────────────────────────────────────────────
 * Schermata read-mostly per la scelta dell'identità account (Player Faction
 * V2). Separata da V1 `users.faction`. Foundation: nessun bonus battle.
 *
 * Stati UI:
 *   • not_selected  → CTA "Scegli fazione" + nota "1 cambio gratuito".
 *   • selected      → fazione corrente in evidenza + CTA secondaria "Cambia
 *                     fazione" (solo se token>=1).
 *   • locked        → 5 fazioni internal mostrate locked/grigie, non
 *                     selezionabili.
 *
 * Carte fazione (tile responsive):
 *   • crest emoji + display_name
 *   • description + recommended_playstyle
 *   • buff_preview (preview only, non applicato in battle)
 *   • visual_theme (primary_color border + accent gradient)
 *   • status badge selected/available/locked
 *
 * Read-only per default; il select POST è chiamato SOLO via tap esplicito.
 */
import React, { useEffect, useState, useMemo, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Pressable,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { apiCall } from '../utils/api';

const COLORS = {
  bg: '#0A0918',
  panel: '#16102E',
  border: '#2A1F4E',
  text: '#F0E6FF',
  textMuted: '#88799A',
  gold: '#FFD700',
  goldDark: '#CC9900',
  blue: '#3D5AFE',
  blueDark: '#1A237E',
  green: '#44DD88',
  red: '#FF4466',
  locked: '#5A4A6A',
};

type VisualTheme = {
  crest: string;
  primary_color: string;
  accent_color: string;
};

type FactionCard = {
  id: string;
  display_name: string;
  description: string;
  identity_theme: string;
  allowed_at_onboarding: boolean;
  is_enabled: boolean;
  buff_preview: Record<string, number> | null;
  future_event_hooks: string[];
  change_token_id: string | null;
  notes: string | null;
  visual_theme: VisualTheme;
  recommended_playstyle: string | null;
  category: 'onboarding' | 'internal_or_future';
};

type FactionStatus = {
  version: number;
  user_id: string;
  player_faction_v2: string | null;
  player_faction_v2_selected_at: string | null;
  player_faction_v2_changed_at: string | null;
  change_tokens: number;
  ui_state: 'selected' | 'not_selected';
  can_select_initial: boolean;
  can_change: boolean;
  selected_card: FactionCard | null;
  v1_faction_legacy: string | null;
  battle_bonus_active: boolean;
};

type FactionListResponse = {
  total: number;
  onboarding_count: number;
  internal_count: number;
  onboarding: FactionCard[];
  internal_or_future: FactionCard[];
  free_change_concept: { default_tokens_on_first_select: number; monetized: boolean };
};

const STAT_LABELS: Record<string, string> = {
  attack: 'ATK',
  magic_damage: 'MAG',
  physical_damage: 'PHYS',
  speed: 'VEL',
  crit_damage: 'CRIT DMG',
  crit_chance: 'CRIT%',
  combo_rate: 'COMBO%',
  physical_defense: 'DEF FIS',
  magic_defense: 'DEF MAG',
  dodge: 'SCHIV',
  healing: 'CURE',
  penetration: 'PEN',
  lifesteal: 'LIFESTEAL',
  control_resistance: 'CC RES',
};

function fmtBuff(stat: string, val: number): string {
  const lbl = STAT_LABELS[stat] || stat.toUpperCase();
  return `${lbl} +${Math.round(val * 100)}%`;
}

export default function PlayerFactionScreen() {
  const router = useRouter();
  const [list, setList] = useState<FactionListResponse | null>(null);
  const [status, setStatus] = useState<FactionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<'onboarding' | 'locked'>('onboarding');
  const [pendingId, setPendingId] = useState<string | null>(null); // selezione UI
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const [pub, st] = await Promise.all([
        apiCall('/api/player-factions/v2/all'),
        apiCall('/api/user/faction-v2/status').catch(() => null),
      ]);
      setList(pub);
      setStatus(st);
    } catch (e: any) {
      setError(e?.message || 'Errore caricamento');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const onboardingCards = list?.onboarding || [];
  const lockedCards = list?.internal_or_future || [];

  const currentId = status?.player_faction_v2 || null;
  const canChange = !!status?.can_change;
  const canSelectInitial = !!status?.can_select_initial;

  const handleConfirmSelect = useCallback(
    async (faction: FactionCard) => {
      if (!faction.allowed_at_onboarding) {
        Alert.alert('Non disponibile', 'Questa fazione non è selezionabile al lancio.');
        return;
      }
      if (currentId === faction.id) {
        Alert.alert('Già selezionata', 'Hai già questa fazione.');
        return;
      }
      const isInitial = !currentId;
      const title = isInitial ? 'Conferma fazione' : 'Cambia fazione';
      const msg = isInitial
        ? `Vuoi scegliere "${faction.display_name}" come tua fazione?\n\nAvrai 1 cambio gratuito disponibile.`
        : `Vuoi cambiare a "${faction.display_name}"?\n\nUserai il tuo unico cambio gratuito (rimasti: ${status?.change_tokens || 0} → ${Math.max(0, (status?.change_tokens || 0) - 1)}).`;
      Alert.alert(title, msg, [
        { text: 'Annulla', style: 'cancel' },
        {
          text: 'Conferma',
          style: 'default',
          onPress: async () => {
            try {
              setSubmitting(true);
              const res = await apiCall('/api/user/faction-v2/select', {
                method: 'POST',
                body: JSON.stringify({ faction_id: faction.id, confirm: true }),
              });
              const after = res?.after || {};
              Alert.alert(
                'Successo',
                `Fazione ora: ${after.player_faction_v2 || faction.id}.\nToken cambio rimasti: ${after.change_tokens ?? 0}.\nNessun bonus battle attivo (foundation).`,
              );
              await load();
              setPendingId(null);
            } catch (e: any) {
              Alert.alert('Errore', e?.message || 'Impossibile salvare la selezione');
            } finally {
              setSubmitting(false);
            }
          },
        },
      ]);
    },
    [currentId, status, load],
  );

  if (loading) {
    return (
      <SafeAreaView style={s.root}>
        <Stack.Screen options={{ title: 'Fazione del Giocatore', headerShown: false }} />
        <View style={s.loaderWrap}>
          <ActivityIndicator color={COLORS.gold} />
          <Text style={s.loaderText}>Caricamento fazioni…</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={s.root}>
      <Stack.Screen options={{ title: 'Fazione del Giocatore', headerShown: false }} />

      {/* Header */}
      <View style={s.header}>
        <Pressable onPress={() => router.back()} style={s.backBtn}>
          <Text style={s.backTxt}>← Indietro</Text>
        </Pressable>
        <Text style={s.title}>⚔️ Fazione del Giocatore</Text>
        <View style={{ width: 70 }} />
      </View>

      <ScrollView style={s.scroll} contentContainerStyle={s.scrollContent}>
        {error && (
          <View style={s.errorBox}>
            <Text style={s.errorTxt}>{error}</Text>
          </View>
        )}

        <Text style={s.subtitle}>
          Scegli l'identità mitologica del tuo account.
        </Text>

        {/* Status banner */}
        <StatusBanner status={status} />

        {/* Tab switch onboarding / locked */}
        <View style={s.tabRow}>
          <TouchableOpacity
            onPress={() => setSelectedTab('onboarding')}
            style={[s.tab, selectedTab === 'onboarding' && s.tabActive]}
          >
            <Text
              style={[s.tabText, selectedTab === 'onboarding' && s.tabTextActive]}
            >
              Disponibili ({onboardingCards.length})
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => setSelectedTab('locked')}
            style={[s.tab, selectedTab === 'locked' && s.tabActive]}
          >
            <Text style={[s.tabText, selectedTab === 'locked' && s.tabTextActive]}>
              Future ({lockedCards.length})
            </Text>
          </TouchableOpacity>
        </View>

        {/* List */}
        {selectedTab === 'onboarding' ? (
          onboardingCards.map((f) => (
            <FactionTile
              key={f.id}
              faction={f}
              isCurrent={currentId === f.id}
              isPending={pendingId === f.id}
              canSelect={canSelectInitial || canChange}
              onPress={() => setPendingId((prev) => (prev === f.id ? null : f.id))}
              onConfirm={() => handleConfirmSelect(f)}
              submitting={submitting}
              currentId={currentId}
            />
          ))
        ) : (
          lockedCards.map((f) => (
            <FactionTile
              key={f.id}
              faction={f}
              isCurrent={false}
              isPending={false}
              canSelect={false}
              locked
              onPress={() => {}}
              onConfirm={() => {}}
              submitting={false}
              currentId={currentId}
            />
          ))
        )}

        <View style={s.foundationNote}>
          <Text style={s.foundationTxt}>
            ✦ Foundation read-only: la fazione è identità/community.
            Bonus combat e integrazione eventi arriveranno in patch
            successive (no pay-to-win).
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Status banner
// ──────────────────────────────────────────────────────────────────────
function StatusBanner({ status }: { status: FactionStatus | null }) {
  if (!status) return null;
  if (status.ui_state === 'not_selected') {
    return (
      <LinearGradient
        colors={['rgba(255,215,0,0.12)', 'rgba(61,90,254,0.10)']}
        style={s.banner}
      >
        <Text style={s.bannerTitle}>Nessuna fazione selezionata</Text>
        <Text style={s.bannerText}>
          La tua identità mitologica non è ancora scelta. Scegli la fazione
          tappando una carta qui sotto.
        </Text>
        <Text style={s.bannerHint}>
          ✦ Avrai <Text style={{ color: COLORS.gold, fontWeight: '900' }}>
            1 cambio fazione gratuito
          </Text> dopo il primo select.
        </Text>
      </LinearGradient>
    );
  }
  // selected
  const card = status.selected_card;
  return (
    <LinearGradient
      colors={[
        (card?.visual_theme.primary_color || COLORS.gold) + '33',
        (card?.visual_theme.accent_color || COLORS.blue) + '22',
      ]}
      style={s.banner}
    >
      <Text style={s.bannerTitle}>
        {card?.visual_theme.crest || '✦'}  Fazione attuale: {card?.display_name || status.player_faction_v2}
      </Text>
      {!!card?.description && (
        <Text style={s.bannerText}>{card.description}</Text>
      )}
      <View style={s.bannerRow}>
        <Text style={s.bannerHint}>
          Token cambio: <Text style={{ color: COLORS.gold, fontWeight: '900' }}>
            {status.change_tokens}
          </Text>
        </Text>
        <Text style={s.bannerHint}>
          Bonus battle: <Text style={{ color: status.battle_bonus_active ? COLORS.green : COLORS.textMuted }}>
            {status.battle_bonus_active ? 'attivo' : 'foundation (off)'}
          </Text>
        </Text>
      </View>
      {!!status.v1_faction_legacy && (
        <Text style={s.bannerLegacy}>
          (Legacy V1 fazione: {status.v1_faction_legacy} — sistema separato)
        </Text>
      )}
    </LinearGradient>
  );
}

// ──────────────────────────────────────────────────────────────────────
// Faction tile
// ──────────────────────────────────────────────────────────────────────
function FactionTile({
  faction,
  isCurrent,
  isPending,
  canSelect,
  onPress,
  onConfirm,
  submitting,
  locked,
  currentId,
}: {
  faction: FactionCard;
  isCurrent: boolean;
  isPending: boolean;
  canSelect: boolean;
  onPress: () => void;
  onConfirm: () => void;
  submitting: boolean;
  locked?: boolean;
  currentId: string | null;
}) {
  const primary = faction.visual_theme.primary_color;
  const accent = faction.visual_theme.accent_color;
  const borderColor = locked
    ? COLORS.locked
    : isCurrent
    ? COLORS.gold
    : isPending
    ? primary
    : COLORS.border;

  const statusBadge = locked
    ? { label: 'Futura', color: COLORS.locked }
    : isCurrent
    ? { label: 'Selezionata', color: COLORS.green }
    : { label: 'Disponibile', color: COLORS.blue };

  const buffEntries: [string, number][] = useMemo(() => {
    if (!faction.buff_preview) return [];
    return Object.entries(faction.buff_preview);
  }, [faction.buff_preview]);

  return (
    <Pressable
      onPress={locked ? undefined : onPress}
      disabled={locked}
      style={({ pressed }) => [
        s.tile,
        { borderColor, opacity: locked ? 0.55 : pressed ? 0.85 : 1 },
      ]}
    >
      {/* Header row */}
      <View style={s.tileHeader}>
        <LinearGradient
          colors={[primary + '55', accent + '55']}
          style={s.crestBox}
        >
          <Text style={s.crestEmoji}>{faction.visual_theme.crest}</Text>
        </LinearGradient>
        <View style={{ flex: 1 }}>
          <Text style={[s.tileName, { color: primary }]}>
            {faction.display_name}
          </Text>
          {!!faction.recommended_playstyle && (
            <Text style={s.tilePlaystyle}>{faction.recommended_playstyle}</Text>
          )}
        </View>
        <View style={[s.statusBadge, { backgroundColor: statusBadge.color + '22', borderColor: statusBadge.color }]}>
          <Text style={[s.statusBadgeTxt, { color: statusBadge.color }]}>
            {statusBadge.label}
          </Text>
        </View>
      </View>

      {/* Description */}
      <Text style={s.tileDesc}>{faction.description}</Text>

      {/* Buff preview */}
      {buffEntries.length > 0 && (
        <View style={s.buffRow}>
          <Text style={s.buffLabel}>Bonus futuro (preview, non attivo):</Text>
          <View style={s.buffPills}>
            {buffEntries.map(([stat, val]) => (
              <View key={stat} style={s.buffPill}>
                <Text style={s.buffPillTxt}>{fmtBuff(stat, val)}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Future events */}
      {faction.future_event_hooks.length > 0 && !locked && (
        <Text style={s.eventHint}>
          Eventi futuri: {faction.future_event_hooks.join(' · ')}
        </Text>
      )}

      {/* Locked notes */}
      {locked && !!faction.notes && (
        <Text style={s.lockedNote} numberOfLines={3}>
          {faction.notes}
        </Text>
      )}

      {/* Confirmation row when pending */}
      {isPending && !locked && canSelect && !isCurrent && (
        <View style={s.confirmRow}>
          <TouchableOpacity
            disabled={submitting}
            onPress={onConfirm}
            style={[s.confirmBtn, { borderColor: COLORS.green, backgroundColor: COLORS.green + '22' }]}
          >
            <Text style={[s.confirmBtnTxt, { color: COLORS.green }]}>
              {submitting ? 'Salvataggio…' : (currentId ? 'Conferma cambio' : 'Conferma scelta')}
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Selected = no actions */}
      {isCurrent && (
        <View style={s.confirmRow}>
          <View style={[s.confirmBtn, { borderColor: COLORS.gold, backgroundColor: COLORS.gold + '15' }]}>
            <Text style={[s.confirmBtnTxt, { color: COLORS.gold }]}>
              ✦ Fazione attuale
            </Text>
          </View>
        </View>
      )}

      {/* Cannot select hint */}
      {!locked && !isCurrent && !canSelect && (
        <Text style={s.cannotHint}>
          Cambio non disponibile: token esauriti.
        </Text>
      )}
    </Pressable>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: COLORS.bg },
  loaderWrap: { flex: 1, justifyContent: 'center', alignItems: 'center', gap: 12 },
  loaderText: { color: COLORS.textMuted },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  backBtn: { paddingVertical: 6, paddingHorizontal: 8 },
  backTxt: { color: COLORS.gold, fontSize: 13, fontWeight: '700' },
  title: { color: COLORS.gold, fontSize: 16, fontWeight: '900', letterSpacing: 0.5 },
  scroll: { flex: 1 },
  scrollContent: { padding: 12, paddingBottom: 60 },
  errorBox: {
    backgroundColor: '#FF000020',
    borderColor: '#FF0000',
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
  },
  errorTxt: { color: '#FF8888' },
  subtitle: {
    color: COLORS.textMuted,
    fontSize: 12,
    fontStyle: 'italic',
    marginBottom: 10,
    textAlign: 'center',
  },

  // Banner
  banner: {
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  bannerTitle: { color: COLORS.text, fontSize: 14, fontWeight: '900', marginBottom: 6 },
  bannerText: { color: COLORS.textMuted, fontSize: 12, lineHeight: 16 },
  bannerHint: { color: COLORS.textMuted, fontSize: 11, marginTop: 6 },
  bannerRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8, gap: 8, flexWrap: 'wrap' },
  bannerLegacy: { color: COLORS.textMuted, fontSize: 9, marginTop: 6, fontStyle: 'italic' },

  // Tabs
  tabRow: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  tab: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 10,
    backgroundColor: COLORS.panel,
    borderWidth: 1,
    borderColor: COLORS.border,
    alignItems: 'center',
  },
  tabActive: { backgroundColor: COLORS.gold + '22', borderColor: COLORS.gold },
  tabText: { color: COLORS.textMuted, fontSize: 12, fontWeight: '700' },
  tabTextActive: { color: COLORS.gold },

  // Tile
  tile: {
    backgroundColor: COLORS.panel,
    borderWidth: 1.5,
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
  },
  tileHeader: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  crestBox: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.15)',
  },
  crestEmoji: { fontSize: 26 },
  tileName: { fontSize: 15, fontWeight: '900' },
  tilePlaystyle: { color: COLORS.textMuted, fontSize: 10, marginTop: 2 },
  statusBadge: { borderWidth: 1, borderRadius: 8, paddingHorizontal: 8, paddingVertical: 4 },
  statusBadgeTxt: { fontSize: 9, fontWeight: '900', letterSpacing: 0.4 },
  tileDesc: { color: COLORS.text, fontSize: 12, lineHeight: 16, marginTop: 8 },
  buffRow: { marginTop: 10 },
  buffLabel: { color: COLORS.textMuted, fontSize: 10, marginBottom: 4 },
  buffPills: { flexDirection: 'row', flexWrap: 'wrap', gap: 5 },
  buffPill: {
    backgroundColor: '#FFD70015',
    borderColor: '#FFD70040',
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  buffPillTxt: { color: COLORS.gold, fontSize: 10, fontWeight: '700' },
  eventHint: { color: COLORS.textMuted, fontSize: 9, marginTop: 8, fontStyle: 'italic' },
  lockedNote: { color: COLORS.textMuted, fontSize: 10, marginTop: 8, fontStyle: 'italic' },
  confirmRow: { marginTop: 10, flexDirection: 'row', gap: 8 },
  confirmBtn: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    flex: 1,
    alignItems: 'center',
  },
  confirmBtnTxt: { fontSize: 12, fontWeight: '800' },
  cannotHint: { color: COLORS.textMuted, fontSize: 10, marginTop: 8, fontStyle: 'italic' },

  // Foundation note
  foundationNote: {
    backgroundColor: '#FFD70008',
    borderColor: '#FFD70030',
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginTop: 12,
  },
  foundationTxt: { color: COLORS.textMuted, fontSize: 11, lineHeight: 15, fontStyle: 'italic' },
});
