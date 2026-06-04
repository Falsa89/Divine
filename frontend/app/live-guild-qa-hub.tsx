/**
 * MEGA_RELEASE_ACCELERATION_41_v92 — Live & Guild QA Hub
 *
 * Schermata QA accessibile da menu reale (NON nascosta) per testare:
 * - eventi live (Crepuscolo dei Titani, Assalto del Ragnarok, eventi generici)
 * - guild modes (Guerra tra Gilde, Raid di Gilda)
 * - server/world boss
 * - faction boss
 * - territory/fronti
 * - war/event avatar modes
 *
 * Ogni card mostra:
 * - TEST / QA label
 * - gate status (REAL OPEN | QA OVERRIDE | LIVE FORZATO APERTO)
 * - source type (encounter source canonica)
 * - avatar placeholder status (se richiesto)
 * - reward/ranking disabled labels
 * - bottoni: "Simula apertura QA" | "Apri lobby test"
 *
 * Garanzie:
 * - reward_live = false (universale)
 * - ranking_live = false (universale)
 * - event_currency_live = false
 * - guild_score_mutation = 0
 * - random_opponents_allowed = false (eredita policy v91)
 * - db_writes = 0
 * - production_enabled = false (qa_override_only = true)
 * - production_ui_exposure = false (UI marcata "QA HUB")
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';

type ModeCard = {
  mode_id: string;
  label: string;
  time_gated: boolean;
  real_schedule?: string;
  guild_required: boolean;
  avatar_required: boolean;
  avatar_id?: string;
  battle_required: boolean;
  encounter_source_type: string;
  source_id: string;
};

// Mirror deterministico del catalogo
// /app/data/design/live_mode_testability/live_guild_special_mode_encounter_source_catalog_v1.json
const MODE_CARDS: ModeCard[] = [
  {
    mode_id: 'event',
    label: 'Eventi Live (generico)',
    time_gated: true,
    real_schedule: 'per-event scheduled window',
    guild_required: false,
    avatar_required: false,
    battle_required: true,
    encounter_source_type: 'event_schedule_encounter',
    source_id: 'event_summer_invasion_stage_01',
  },
  {
    mode_id: 'crepuscolo_dei_titani',
    label: 'Crepuscolo dei Titani',
    time_gated: true,
    real_schedule: 'lun/mer/ven 20:30-21:30',
    guild_required: false,
    avatar_required: false,
    battle_required: true,
    encounter_source_type: 'event_schedule_encounter',
    source_id: 'event_crepuscolo_titani_wave_01',
  },
  {
    mode_id: 'assalto_del_ragnarok',
    label: 'Assalto del Ragnarök',
    time_gated: true,
    real_schedule: 'daily 11-12 + 19-20',
    guild_required: false,
    avatar_required: false,
    battle_required: true,
    encounter_source_type: 'event_schedule_encounter',
    source_id: 'event_assalto_ragnarok_wave_01',
  },
  {
    mode_id: 'guild_war',
    label: 'Guerra tra Gilde',
    time_gated: true,
    real_schedule: 'scheduled per stagione',
    guild_required: true,
    avatar_required: true,
    avatar_id: 'guild_war_avatar_base_dev',
    battle_required: true,
    encounter_source_type: 'guild_defense_team',
    source_id: 'gw_defense_team_design_v1',
  },
  {
    mode_id: 'guild_raid',
    label: 'Raid di Gilda',
    time_gated: true,
    real_schedule: 'weekly reset',
    guild_required: true,
    avatar_required: false,
    battle_required: true,
    encounter_source_type: 'raid_boss_catalog',
    source_id: 'guild_raid_boss_design_v1',
  },
  {
    mode_id: 'server_boss',
    label: 'Boss del Server',
    time_gated: true,
    real_schedule: 'weekly reset Monday UTC',
    guild_required: false,
    avatar_required: false,
    battle_required: true,
    encounter_source_type: 'server_boss_catalog',
    source_id: 'server_boss_weekly_design_v1',
  },
  {
    mode_id: 'faction_boss',
    label: 'Boss di Fazione',
    time_gated: true,
    real_schedule: 'daily window',
    guild_required: false,
    avatar_required: true,
    avatar_id: 'faction_boss_avatar_placeholder_dev',
    battle_required: true,
    encounter_source_type: 'faction_boss_catalog',
    source_id: 'faction_boss_design_v1',
  },
  {
    mode_id: 'territory',
    label: 'Conquista Territori',
    time_gated: true,
    real_schedule: 'scheduled wave + guild season',
    guild_required: true,
    avatar_required: true,
    avatar_id: 'player_war_avatar_mini_base_dev',
    battle_required: true,
    encounter_source_type: 'authored_encounter_catalog',
    source_id: 'territory_wave_design_v1',
  },
  {
    mode_id: 'war_avatar_mode',
    label: 'Modalità War Avatar (layout-only)',
    time_gated: false,
    guild_required: false,
    avatar_required: true,
    avatar_id: 'player_war_avatar_mini_base_dev',
    battle_required: false,
    encounter_source_type: 'avatar_layout_only',
    source_id: 'war_avatar_layout_design_v1',
  },
  {
    mode_id: 'event_avatar_mode',
    label: 'Modalità Event Avatar (layout-only)',
    time_gated: true,
    real_schedule: 'per-event scheduled window',
    guild_required: false,
    avatar_required: true,
    avatar_id: 'event_avatar_base_dev',
    battle_required: false,
    encounter_source_type: 'event_layout_only',
    source_id: 'event_avatar_layout_design_v1',
  },
];

function ModeCardView({
  card,
  qaOpen,
  onSimulate,
  onOpenLobby,
}: {
  card: ModeCard;
  qaOpen: boolean;
  onSimulate: () => void;
  onOpenLobby: () => void;
}) {
  const gateLabel = !card.time_gated
    ? 'NESSUN GATE'
    : qaOpen
    ? 'QA OVERRIDE · FORZATO APERTO'
    : 'GATE CHIUSO (real schedule)';
  const gateColor = !card.time_gated ? '#44DD99' : qaOpen ? '#FFD700' : '#666';

  return (
    <View style={s.card}>
      <View style={s.cardHeader}>
        <Text style={s.cardLabel}>{card.label}</Text>
        <View style={s.qaBadge}>
          <Text style={s.qaBadgeTxt}>TEST · QA</Text>
        </View>
      </View>

      <View style={[s.gateRow, { borderColor: gateColor }]}>
        <Text style={[s.gateTxt, { color: gateColor }]}>{gateLabel}</Text>
        {card.real_schedule && (
          <Text style={s.scheduleTxt}>Real: {card.real_schedule}</Text>
        )}
      </View>

      <View style={s.kvBlock}>
        <View style={s.kvRow}>
          <Text style={s.kvKey}>source_type:</Text>
          <Text style={s.kvVal}>{card.encounter_source_type}</Text>
        </View>
        <View style={s.kvRow}>
          <Text style={s.kvKey}>source_id:</Text>
          <Text style={s.kvVal}>{card.source_id}</Text>
        </View>
        <View style={s.kvRow}>
          <Text style={s.kvKey}>is_random:</Text>
          <Text style={[s.kvVal, s.kvFalse]}>false</Text>
        </View>
        {card.guild_required && (
          <View style={s.kvRow}>
            <Text style={s.kvKey}>guild_required:</Text>
            <Text style={[s.kvVal, s.kvWarn]}>YES (QA bypass)</Text>
          </View>
        )}
        {card.avatar_required && (
          <View style={s.kvRow}>
            <Text style={s.kvKey}>avatar:</Text>
            <Text style={[s.kvVal, s.kvWarn]}>
              {card.avatar_id} (placeholder dev)
            </Text>
          </View>
        )}
        {!card.battle_required && (
          <View style={s.kvRow}>
            <Text style={s.kvKey}>battle_required:</Text>
            <Text style={s.kvVal}>false (layout only)</Text>
          </View>
        )}
      </View>

      <View style={s.disabledFlags}>
        <Text style={s.disabledFlagTxt}>NO LIVE REWARD</Text>
        <Text style={s.disabledFlagTxt}>NO RANKING APPLIED</Text>
        <Text style={s.disabledFlagTxt}>NO CURRENCY</Text>
        <Text style={s.disabledFlagTxt}>NO SCORE MUT</Text>
      </View>

      <View style={s.cardActions}>
        {card.time_gated && (
          <TouchableOpacity
            style={[s.btn, s.btnSim, qaOpen && s.btnSimOn]}
            onPress={onSimulate}
            activeOpacity={0.85}
          >
            <Text style={s.btnTxt}>
              {qaOpen ? '✓ QA Window Open' : '⏱ Simula apertura QA'}
            </Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={[
            s.btn,
            s.btnLobby,
            card.time_gated && !qaOpen && s.btnLobbyDisabled,
          ]}
          onPress={onOpenLobby}
          disabled={card.time_gated && !qaOpen}
          activeOpacity={0.85}
        >
          <Text style={s.btnTxt}>▶ Apri lobby test</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

export default function LiveGuildQaHubScreen() {
  const router = useRouter();
  const [qaOpenSet, setQaOpenSet] = useState<Record<string, boolean>>({});

  const toggleSimulate = (mode_id: string) => {
    setQaOpenSet((prev) => ({ ...prev, [mode_id]: !prev[mode_id] }));
  };

  const openLobby = (card: ModeCard) => {
    const qaOpen = !!qaOpenSet[card.mode_id] || !card.time_gated;
    const path = `/live-mode-pre-entry-lobby?mode=${encodeURIComponent(
      card.mode_id,
    )}&source_id=${encodeURIComponent(card.source_id)}&qa_open=${qaOpen ? '1' : '0'}`;
    router.push(path as any);
  };

  const goBack = () => {
    if (router.canGoBack()) router.back();
    else router.push('/(tabs)/menu' as any);
  };

  return (
    <SafeAreaView style={s.safe}>
      <LinearGradient colors={['#10081A', '#2A1240']} style={s.bg}>
        <ScrollView contentContainerStyle={s.scroll}>
          <View style={s.header}>
            <TouchableOpacity onPress={goBack} style={s.backBtn}>
              <Text style={s.backTxt}>← Indietro</Text>
            </TouchableOpacity>
            <Text style={s.title}>Modalità Live & Guild QA</Text>
            <Text style={s.subtitle}>v92 · QA Hub · NO LIVE MUTATION</Text>
          </View>

          <View style={s.banner}>
            <Text style={s.bannerTitle}>⚠ TEST MODE · QA TIME OVERRIDE</Text>
            <Text style={s.bannerTxt}>
              Questa schermata è solo per QA. Nessuna ricompensa, classifica,
              valuta evento, punteggio gilda o progresso viene applicato. Le
              modalità time-gated possono essere simulate aperte localmente.
              Tutti gli avversari sono deterministici (no random).
            </Text>
          </View>

          {MODE_CARDS.map((card) => (
            <ModeCardView
              key={card.mode_id}
              card={card}
              qaOpen={!!qaOpenSet[card.mode_id]}
              onSimulate={() => toggleSimulate(card.mode_id)}
              onOpenLobby={() => openLobby(card)}
            />
          ))}

          <View style={s.footer}>
            <Text style={s.footerTxt}>
              v92 · db_writes=0 · reward_live=false · ranking_live=false ·
              event_currency_live=false · guild_score_mutation=0 ·
              random_opponents_allowed=false · production_enabled=false ·
              qa_override_only=true
            </Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#10081A' },
  bg: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 48 },
  header: { marginBottom: 12 },
  backBtn: { alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, marginBottom: 8 },
  backTxt: { color: '#AA88FF', fontSize: 14 },
  title: { color: '#FFD700', fontSize: 22, fontWeight: '800', textAlign: 'center' },
  subtitle: { color: '#AABBDD', fontSize: 12, textAlign: 'center', marginTop: 4 },

  banner: {
    backgroundColor: 'rgba(80,20,0,0.4)',
    borderColor: '#FF6644',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  bannerTitle: { color: '#FF6644', fontWeight: '800', fontSize: 12, marginBottom: 6 },
  bannerTxt: { color: '#FFDDCC', fontSize: 12, lineHeight: 18 },

  card: {
    backgroundColor: 'rgba(30,15,55,0.85)',
    borderColor: '#5544AA',
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 12,
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  cardLabel: { color: '#FFFFFF', fontSize: 15, fontWeight: '700', flex: 1, marginRight: 8 },
  qaBadge: { backgroundColor: '#FF6644', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  qaBadgeTxt: { color: '#000', fontSize: 9, fontWeight: '800' },

  gateRow: { borderWidth: 1, borderRadius: 6, padding: 8, marginBottom: 8 },
  gateTxt: { fontSize: 12, fontWeight: '700' },
  scheduleTxt: { color: '#AABBDD', fontSize: 10, marginTop: 2 },

  kvBlock: { marginBottom: 8 },
  kvRow: { flexDirection: 'row', justifyContent: 'space-between', marginVertical: 1 },
  kvKey: { color: '#AABBDD', fontSize: 10 },
  kvVal: { color: '#FFFFFF', fontSize: 10, flex: 1, textAlign: 'right' },
  kvFalse: { color: '#FF6644' },
  kvWarn: { color: '#FFAA44' },

  disabledFlags: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginBottom: 8 },
  disabledFlagTxt: {
    color: '#FFFFFF',
    backgroundColor: '#774444',
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 3,
    fontSize: 9,
    fontWeight: '700',
  },

  cardActions: { flexDirection: 'row', gap: 8 },
  btn: { flex: 1, paddingVertical: 10, borderRadius: 6, alignItems: 'center', minHeight: 44 },
  btnSim: { backgroundColor: '#666688' },
  btnSimOn: { backgroundColor: '#FFAA22' },
  btnLobby: { backgroundColor: '#22AA66' },
  btnLobbyDisabled: { backgroundColor: '#444444', opacity: 0.5 },
  btnTxt: { color: '#FFFFFF', fontWeight: '700', fontSize: 13 },

  footer: { marginTop: 12, padding: 8, backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: 6 },
  footerTxt: { color: '#88AAAA', fontSize: 9, textAlign: 'center' },
});
