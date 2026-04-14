import React, { useState, useEffect } from 'react';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView,
  ActivityIndicator, Dimensions,
} from 'react-native';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import Animated, { FadeInDown } from 'react-native-reanimated';

const { width: W, height: H } = Dimensions.get('window');

const FRAME_COLORS: Record<string,string> = {
  bronze:'#cd7f32', silver:'#c0c0c0', gold:'#ffd700', diamond:'#44ddff', legendary:'#ff4444', divine:'#ffd700',
};

const TABS = [
  { id:'arena', label:'Arena', icon:'\uD83C\uDFC6', endpoint:'/api/rankings/arena' },
  { id:'power', label:'Potenza', icon:'\u2694\uFE0F', endpoint:'/api/rankings/power' },
  { id:'tower', label:'Torre', icon:'\uD83C\uDFF0', endpoint:'/api/rankings/tower' },
  { id:'level', label:'Livello', icon:'\u2B50', endpoint:'/api/rankings/level' },
  { id:'guild', label:'Gilda', icon:'\uD83C\uDFDB\uFE0F', endpoint:'/api/rankings/guild' },
];

const PODIUM_COLORS = ['#ffd700', '#c0c0c0', '#cd7f32'];
const PODIUM_SIZES = [56, 48, 44];

export default function RankingsScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('arena');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, [activeTab]);

  const load = async () => {
    setLoading(true);
    try {
      const tab = TABS.find(t => t.id === activeTab);
      if (tab) {
        const d = await apiCall(tab.endpoint);
        setData(d);
      }
    } catch (e) {} finally { setLoading(false); }
  };

  const isGuild = activeTab === 'guild';
  const ranking = isGuild ? data?.ranking : data?.ranking;
  const myRank = isGuild ? data?.my_guild : data?.my_rank;
  const top3 = ranking?.slice(0, 3) || [];
  const rest = ranking?.slice(3) || [];

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      {/* Header */}
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={s.back}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={s.title}>CLASSIFICHE</Text>
        {myRank && (
          <View style={s.myRankBadge}>
            <Text style={s.myRankTxt}>Tu: #{myRank.rank}</Text>
          </View>
        )}
      </View>

      {/* Tabs */}
      <View style={s.tabs}>
        {TABS.map(tab => (
          <TouchableOpacity
            key={tab.id}
            style={[s.tab, activeTab === tab.id && s.tabActive]}
            onPress={() => setActiveTab(tab.id)}
          >
            <Text style={s.tabIcon}>{tab.icon}</Text>
            <Text style={[s.tabLabel, activeTab === tab.id && s.tabLabelActive]}>{tab.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading ? (
        <View style={s.loadC}><ActivityIndicator size="large" color="#ffd700" /></View>
      ) : (
        <View style={s.body}>
          {/* Top 3 Podium */}
          {top3.length >= 3 && (
            <View style={s.podium}>
              {/* 2nd place */}
              <View style={s.podiumSlot}>
                <View style={[s.podiumAvatar, { width: PODIUM_SIZES[1], height: PODIUM_SIZES[1], borderColor: PODIUM_COLORS[1] }]}>
                  <Text style={[s.podiumLetter, { fontSize: PODIUM_SIZES[1] * 0.4 }]}>{(isGuild ? top3[1].name : top3[1].username)?.[0]?.toUpperCase()}</Text>
                </View>
                <View style={[s.podiumBadge, { backgroundColor: PODIUM_COLORS[1] + '25', borderColor: PODIUM_COLORS[1] }]}>
                  <Text style={[s.podiumRank, { color: PODIUM_COLORS[1] }]}>2</Text>
                </View>
                <Text style={s.podiumName} numberOfLines={1}>{isGuild ? top3[1].name : top3[1].username}</Text>
                <Text style={[s.podiumScore, { color: PODIUM_COLORS[1] }]}>{top3[1].score?.toLocaleString()}</Text>
                <View style={[s.podiumBar, { height: 40, backgroundColor: PODIUM_COLORS[1] + '30' }]} />
              </View>

              {/* 1st place */}
              <View style={s.podiumSlot}>
                <Text style={s.crown}>{'\uD83D\uDC51'}</Text>
                <View style={[s.podiumAvatar, { width: PODIUM_SIZES[0], height: PODIUM_SIZES[0], borderColor: PODIUM_COLORS[0] }]}>
                  <Text style={[s.podiumLetter, { fontSize: PODIUM_SIZES[0] * 0.4, color: PODIUM_COLORS[0] }]}>{(isGuild ? top3[0].name : top3[0].username)?.[0]?.toUpperCase()}</Text>
                </View>
                <View style={[s.podiumBadge, { backgroundColor: PODIUM_COLORS[0] + '25', borderColor: PODIUM_COLORS[0] }]}>
                  <Text style={[s.podiumRank, { color: PODIUM_COLORS[0] }]}>1</Text>
                </View>
                <Text style={[s.podiumName, { color: PODIUM_COLORS[0] }]} numberOfLines={1}>{isGuild ? top3[0].name : top3[0].username}</Text>
                <Text style={[s.podiumScore, { color: PODIUM_COLORS[0] }]}>{top3[0].score?.toLocaleString()}</Text>
                <View style={[s.podiumBar, { height: 56, backgroundColor: PODIUM_COLORS[0] + '30' }]} />
              </View>

              {/* 3rd place */}
              <View style={s.podiumSlot}>
                <View style={[s.podiumAvatar, { width: PODIUM_SIZES[2], height: PODIUM_SIZES[2], borderColor: PODIUM_COLORS[2] }]}>
                  <Text style={[s.podiumLetter, { fontSize: PODIUM_SIZES[2] * 0.4 }]}>{(isGuild ? top3[2].name : top3[2].username)?.[0]?.toUpperCase()}</Text>
                </View>
                <View style={[s.podiumBadge, { backgroundColor: PODIUM_COLORS[2] + '25', borderColor: PODIUM_COLORS[2] }]}>
                  <Text style={[s.podiumRank, { color: PODIUM_COLORS[2] }]}>3</Text>
                </View>
                <Text style={s.podiumName} numberOfLines={1}>{isGuild ? top3[2].name : top3[2].username}</Text>
                <Text style={[s.podiumScore, { color: PODIUM_COLORS[2] }]}>{top3[2].score?.toLocaleString()}</Text>
                <View style={[s.podiumBar, { height: 28, backgroundColor: PODIUM_COLORS[2] + '30' }]} />
              </View>
            </View>
          )}

          {/* Ranking List */}
          <ScrollView style={s.list}>
            {rest.map((entry: any, idx: number) => {
              const isYou = entry.is_you || entry.is_yours;
              const frameCol = FRAME_COLORS[entry.frame] || '#888';
              return (
                <Animated.View
                  key={entry.user_id || entry.guild_id || idx}
                  entering={FadeInDown.delay(idx * 30).duration(200)}
                  style={[s.row, isYou && s.rowYou]}
                >
                  {/* Rank Number */}
                  <View style={s.rankCol}>
                    <Text style={[s.rankNum, idx < 7 && { color: '#ffd700' }]}>#{entry.rank}</Text>
                  </View>

                  {/* Avatar */}
                  <View style={[s.rowAvatar, { borderColor: isGuild ? '#6644ff' : (entry.tier_color || frameCol) }]}>
                    <Text style={[s.rowLetter, { color: isGuild ? '#6644ff' : (entry.tier_color || '#fff') }]}>
                      {(isGuild ? entry.name : entry.username)?.[0]?.toUpperCase()}
                    </Text>
                  </View>

                  {/* Info */}
                  <View style={s.rowInfo}>
                    <View style={s.nameRow}>
                      <Text style={[s.rowName, isYou && { color: '#ff6b35' }]} numberOfLines={1}>
                        {isGuild ? entry.name : entry.username}
                      </Text>
                      {entry.tier_icon ? <Text style={s.tierIcon}>{entry.tier_icon}</Text> : null}
                    </View>
                    <Text style={s.rowSub}>
                      {isGuild
                        ? `Lv.${entry.level} \u2022 ${entry.members} membri \u2022 ${entry.territories} territori`
                        : `Lv.${entry.level}${entry.title ? ' \u2022 ' + entry.title : ''}${entry.faction ? ' \u2022 ' + entry.faction : ''}`
                      }
                    </Text>
                  </View>

                  {/* Score */}
                  <View style={s.scoreCol}>
                    {entry.tier_name ? (
                      <Text style={[s.tierLabel, { color: entry.tier_color || '#888' }]}>{entry.tier_name}</Text>
                    ) : null}
                    <Text style={s.rowScore}>{entry.score?.toLocaleString()}</Text>
                  </View>
                </Animated.View>
              );
            })}

            {(!ranking || ranking.length === 0) && (
              <Text style={s.emptyTxt}>Nessun dato disponibile</Text>
            )}
          </ScrollView>

          {/* My Rank Footer */}
          {myRank && (
            <View style={s.myRankBar}>
              <Text style={s.myRankLabel}>LA TUA POSIZIONE</Text>
              <Text style={s.myRankPos}>#{myRank.rank}</Text>
              <Text style={s.myRankName}>{isGuild ? myRank.name : myRank.username}</Text>
              <Text style={s.myRankScore}>{myRank.score?.toLocaleString()}</Text>
            </View>
          )}
        </View>
      )}
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c: { flex: 1, backgroundColor:'transparent' },
  loadC: { flex: 1, alignItems: 'center', justifyContent: 'center' },

  // Header
  hdr: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 16, paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: 'rgba(255,215,0,0.2)' },
  back: { color: '#ffd700', fontSize: 20, fontWeight: '700' },
  title: { color: '#ffd700', fontSize: 16, fontWeight: '900', letterSpacing: 2, flex: 1 },
  myRankBadge: { backgroundColor: 'rgba(255,107,53,0.2)', paddingHorizontal: 10, paddingVertical: 3, borderRadius: 8, borderWidth: 1, borderColor: 'rgba(255,107,53,0.4)' },
  myRankTxt: { color: '#ff6b35', fontSize: 11, fontWeight: '800' },

  // Tabs
  tabs: { flexDirection: 'row', paddingHorizontal: 8, paddingVertical: 4, gap: 3 },
  tab: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 3, paddingVertical: 5, borderRadius: 6, backgroundColor: 'rgba(255,255,255,0.03)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)' },
  tabActive: { backgroundColor: 'rgba(255,215,0,0.12)', borderColor: '#ffd700' },
  tabIcon: { fontSize: 12 },
  tabLabel: { color: '#666', fontSize: 9, fontWeight: '700' },
  tabLabelActive: { color: '#ffd700' },

  body: { flex: 1, flexDirection: 'row', padding: 6, gap: 6 },

  // Podium
  podium: { width: 200, flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'center', gap: 4, paddingBottom: 8 },
  podiumSlot: { flex: 1, alignItems: 'center' },
  crown: { fontSize: 16, marginBottom: 2 },
  podiumAvatar: { borderRadius: 30, borderWidth: 3, backgroundColor: 'rgba(255,255,255,0.06)', alignItems: 'center', justifyContent: 'center' },
  podiumLetter: { color: '#fff', fontWeight: '900' },
  podiumBadge: { marginTop: 3, paddingHorizontal: 6, paddingVertical: 1, borderRadius: 8, borderWidth: 1 },
  podiumRank: { fontSize: 11, fontWeight: '900' },
  podiumName: { color: '#ccc', fontSize: 8, fontWeight: '700', marginTop: 2, textAlign: 'center' },
  podiumScore: { fontSize: 9, fontWeight: '800', marginTop: 1 },
  podiumBar: { width: '80%', borderRadius: 4, marginTop: 4 },

  // List
  list: { flex: 1 },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 5, paddingHorizontal: 6, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.02)', marginBottom: 2, gap: 6 },
  rowYou: { backgroundColor: 'rgba(255,107,53,0.1)', borderWidth: 1, borderColor: 'rgba(255,107,53,0.3)' },

  rankCol: { width: 32 },
  rankNum: { color: '#888', fontSize: 12, fontWeight: '900', textAlign: 'center' },

  rowAvatar: { width: 30, height: 30, borderRadius: 8, borderWidth: 2, backgroundColor: 'rgba(255,255,255,0.05)', alignItems: 'center', justifyContent: 'center' },
  rowLetter: { fontSize: 13, fontWeight: '900' },

  rowInfo: { flex: 1 },
  nameRow: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  rowName: { color: '#fff', fontSize: 11, fontWeight: '700' },
  tierIcon: { fontSize: 10 },
  rowSub: { color: '#666', fontSize: 8, marginTop: 1 },

  scoreCol: { alignItems: 'flex-end', minWidth: 55 },
  tierLabel: { fontSize: 7, fontWeight: '700', letterSpacing: 0.5 },
  rowScore: { color: '#ffd700', fontSize: 12, fontWeight: '800' },

  emptyTxt: { color: '#555', fontSize: 12, textAlign: 'center', marginTop: 40 },

  // My Rank Bar
  myRankBar: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 12, paddingVertical: 6, backgroundColor: 'rgba(255,107,53,0.08)', borderTopWidth: 1, borderTopColor: 'rgba(255,107,53,0.2)' },
  myRankLabel: { color: '#888', fontSize: 8, fontWeight: '700', letterSpacing: 1 },
  myRankPos: { color: '#ff6b35', fontSize: 16, fontWeight: '900' },
  myRankName: { color: '#fff', fontSize: 12, fontWeight: '700', flex: 1 },
  myRankScore: { color: '#ffd700', fontSize: 14, fontWeight: '800' },
});
