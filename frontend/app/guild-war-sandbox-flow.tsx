/**
 * v93 — Guild War Sandbox Flow (QA).
 * Mostra attaccante / difensore / defense team source / lane.
 * NO guild_score_mutation, NO leaderboard, NO season_progress, NO real_user_pii.
 */
import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { AvatarPlaceholderGuildWar } from '../components/avatarPlaceholders/AvatarPlaceholderDev';

const DEFENSE_TEAM = [
  { hero_id: 'alpha_arena_hero_01', role: 'dps', level: 30, stars: 4, power: 8000 },
  { hero_id: 'alpha_arena_hero_02', role: 'dps', level: 30, stars: 4, power: 8000 },
  { hero_id: 'alpha_arena_hero_03', role: 'healer', level: 30, stars: 4, power: 7500 },
];
const LANES = ['lane_north', 'lane_center', 'lane_south'];

export default function GuildWarSandboxFlowScreen() {
  const router = useRouter();
  const goBack = () => {
    if (router.canGoBack()) router.back();
    else router.push('/live-guild-qa-hub' as any);
  };
  const openBattle = () => {
    router.push('/live-mode-pre-entry-lobby?mode=guild_war&source_id=gw_defense_team_design_v1&qa_open=1' as any);
  };

  return (
    <SafeAreaView style={s.safe}>
      <LinearGradient colors={['#1A0830', '#3A1A60']} style={s.bg}>
        <ScrollView contentContainerStyle={s.scroll}>
          <TouchableOpacity onPress={goBack} style={s.backBtn}>
            <Text style={s.backTxt}>← Indietro</Text>
          </TouchableOpacity>
          <Text style={s.title}>Guild War Sandbox</Text>
          <Text style={s.subtitle}>v93 · QA · NO GUILD SCORE · NO LEADERBOARD · NO PII</Text>

          <View style={s.banner}>
            <Text style={s.bannerTxt}>
              Sandbox QA: gli alias sotto sono fittizi, nessun dato utente reale
              viene letto. Nessuna mutazione di guild score, leaderboard, season.
            </Text>
          </View>

          <Text style={s.section}>Schieramenti</Text>
          <View style={s.armiesRow}>
            <View style={s.armyBox}>
              <Text style={s.armyTitle}>Attaccante</Text>
              <AvatarPlaceholderGuildWar size={80} label="ATTACKER" />
              <Text style={s.armyAlias}>qa_alias_attacker_001</Text>
              <Text style={s.armyMeta}>Guild: qa_guild_alpha</Text>
            </View>
            <Text style={s.vs}>VS</Text>
            <View style={s.armyBox}>
              <Text style={s.armyTitle}>Difensore</Text>
              <AvatarPlaceholderGuildWar size={80} label="DEFENDER" />
              <Text style={s.armyAlias}>qa_alias_defender_001</Text>
              <Text style={s.armyMeta}>Guild: qa_guild_beta</Text>
            </View>
          </View>

          <Text style={s.section}>Defense Team Source (canonical)</Text>
          <View style={s.sourceBox}>
            <View style={s.kvRow}>
              <Text style={s.kvKey}>source_type:</Text>
              <Text style={s.kvVal}>guild_defense_team</Text>
            </View>
            <View style={s.kvRow}>
              <Text style={s.kvKey}>source_id:</Text>
              <Text style={s.kvVal}>gw_defense_team_design_v1</Text>
            </View>
            <View style={s.kvRow}>
              <Text style={s.kvKey}>is_random:</Text>
              <Text style={[s.kvVal, s.kvFalse]}>false</Text>
            </View>
          </View>

          <Text style={s.section}>Defense Team</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={s.teamRow}>
              {DEFENSE_TEAM.map((u, i) => (
                <View key={i} style={s.unit}>
                  <Text style={s.unitId}>{u.hero_id}</Text>
                  <Text style={s.unitMeta}>
                    {u.role.toUpperCase()} · Lv.{u.level} · ★{u.stars}
                  </Text>
                  <Text style={s.unitPwr}>PWR {u.power}</Text>
                </View>
              ))}
            </View>
          </ScrollView>

          <Text style={s.section}>Lane / Territory</Text>
          <View style={s.lanesRow}>
            {LANES.map((l) => (
              <View key={l} style={s.lane}>
                <Text style={s.laneTxt}>{l}</Text>
              </View>
            ))}
          </View>

          <View style={s.flagsBox}>
            <Text style={s.flagsTxt}>NO GUILD SCORE</Text>
            <Text style={s.flagsTxt}>NO LEADERBOARD</Text>
            <Text style={s.flagsTxt}>NO SEASON PROGRESS</Text>
            <Text style={s.flagsTxt}>NO PII</Text>
            <Text style={s.flagsTxt}>NO REWARD</Text>
            <Text style={s.flagsTxt}>NO RANKING</Text>
          </View>

          <TouchableOpacity style={s.btn} onPress={openBattle} activeOpacity={0.85}>
            <Text style={s.btnTxt}>▶ Apri lobby battaglia test</Text>
          </TouchableOpacity>

          <View style={s.footer}>
            <Text style={s.footerTxt}>
              v93 · db_writes=0 · guild_score_mutation=0 · ranking_live=false ·
              real_user_pii=false · random_opponents_allowed=false
            </Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#1A0830' },
  bg: { flex: 1 },
  scroll: { padding: 16, paddingBottom: 48 },
  backBtn: { alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, marginBottom: 8 },
  backTxt: { color: '#AA88FF', fontSize: 14 },
  title: { color: '#AA22FF', fontSize: 22, fontWeight: '800', textAlign: 'center' },
  subtitle: { color: '#AABBDD', fontSize: 11, textAlign: 'center', marginTop: 4, marginBottom: 12 },
  banner: { backgroundColor: 'rgba(40,0,60,0.6)', borderColor: '#AA22FF', borderWidth: 1, borderRadius: 8, padding: 10, marginBottom: 12 },
  bannerTxt: { color: '#DDCCFF', fontSize: 11, lineHeight: 16 },
  section: { color: '#FFD700', fontSize: 13, fontWeight: '700', marginTop: 12, marginBottom: 8 },
  armiesRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around', marginBottom: 12 },
  armyBox: { alignItems: 'center', flex: 1 },
  armyTitle: { color: '#FFFFFF', fontSize: 12, fontWeight: '700', marginBottom: 4 },
  armyAlias: { color: '#AABBDD', fontSize: 9, marginTop: 4 },
  armyMeta: { color: '#888899', fontSize: 9 },
  vs: { color: '#FF6644', fontSize: 22, fontWeight: '800', marginHorizontal: 8 },
  sourceBox: { backgroundColor: 'rgba(0,40,80,0.4)', borderColor: '#44DDFF', borderWidth: 1, borderRadius: 6, padding: 8, marginBottom: 8 },
  kvRow: { flexDirection: 'row', justifyContent: 'space-between' },
  kvKey: { color: '#AABBDD', fontSize: 10 },
  kvVal: { color: '#FFFFFF', fontSize: 10 },
  kvFalse: { color: '#FF6644' },
  teamRow: { flexDirection: 'row', gap: 8 },
  unit: { width: 110, backgroundColor: 'rgba(20,15,40,0.7)', borderColor: '#AA22FF', borderWidth: 1, borderRadius: 6, padding: 6, alignItems: 'center' },
  unitId: { color: '#FFF', fontSize: 9, fontWeight: '600', textAlign: 'center' },
  unitMeta: { color: '#AABBDD', fontSize: 9, marginTop: 2 },
  unitPwr: { color: '#FFD700', fontSize: 10, fontWeight: '700', marginTop: 2 },
  lanesRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  lane: { flex: 1, backgroundColor: 'rgba(40,30,80,0.5)', padding: 8, marginHorizontal: 2, borderRadius: 6, alignItems: 'center' },
  laneTxt: { color: '#DDCCFF', fontSize: 10, fontWeight: '600' },
  flagsBox: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginBottom: 12 },
  flagsTxt: { color: '#FFFFFF', backgroundColor: '#774444', paddingHorizontal: 4, paddingVertical: 2, borderRadius: 3, fontSize: 9, fontWeight: '700' },
  btn: { backgroundColor: '#22BB66', paddingVertical: 14, borderRadius: 10, alignItems: 'center', minHeight: 48, marginBottom: 12 },
  btnTxt: { color: '#FFFFFF', fontSize: 15, fontWeight: '800' },
  footer: { padding: 8, backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: 6 },
  footerTxt: { color: '#88AAAA', fontSize: 9, textAlign: 'center' },
});
