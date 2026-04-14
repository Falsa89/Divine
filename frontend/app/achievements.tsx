import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import ScreenHeader from '../components/ui/ScreenHeader';
import { COLORS } from '../constants/theme';

const CAT_COLORS: Record<string, string> = { combat: '#FF5544', collection: '#FFD700', progression: '#44DD88', social: '#4499FF', economy: '#FF8844' };

export default function AchievementsScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [claiming, setClaiming] = useState('');

  useEffect(() => { load(); }, []);
  const load = async () => {
    try { const d = await apiCall('/api/achievements'); setData(d); }
    catch (e) {} finally { setLoading(false); }
  };

  const claim = async (achId: string, tierIdx: number, achName: string) => {
    setClaiming(`${achId}_${tierIdx}`);
    try {
      const r = await apiCall('/api/achievements/claim', { method: 'POST', body: JSON.stringify({ achievement_id: achId, tier_index: tierIdx }) });
      await refreshUser(); await load();
      const rewards = Object.entries(r.reward || {}).map(([k, v]) => `+${v} ${k}`).join('\n');
      Alert.alert('Achievement Riscosso!', `${r.achievement} - Tier ${r.tier}\n${rewards}${r.title_earned ? `\nTitolo: ${r.title_earned}` : ''}`);
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setClaiming(''); }
  };

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.c}>
      <ActivityIndicator size="large" color={COLORS.gold} />
    </LinearGradient>
  );

  const achievements = data?.achievements || [];
  const stats = data?.stats || {};
  const categories = data?.categories || {};
  const filtered = filter === 'all' ? achievements : achievements.filter((a: any) => a.category === filter);
  const claimable = achievements.filter((a: any) => a.tiers.some((t: any) => t.can_claim)).length;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.c}>
      <ScreenHeader
        title="Achievement"
        titleColor={COLORS.gold}
        showBack
        rightContent={
          <View style={s.hdrRight}>
            <Text style={s.hdrStat}>{stats.completed_tiers}/{stats.total_tiers}</Text>
            {claimable > 0 && (
              <LinearGradient colors={['#FF4444', '#CC2222']} style={s.claimBadge}>
                <Text style={s.claimBadgeTxt}>{claimable}</Text>
              </LinearGradient>
            )}
          </View>
        }
      />

      {/* Progress bar */}
      <View style={s.progWrap}>
        <View style={s.progBar}>
          <LinearGradient
            colors={[COLORS.gold, '#FF8C00']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={[s.progFill, { width: `${(stats.completion_pct || 0) * 100}%` }]}
          />
        </View>
        <Text style={s.progTxt}>{((stats.completion_pct || 0) * 100).toFixed(1)}% completato</Text>
      </View>

      {/* Category filter */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.filterWrap} contentContainerStyle={s.filterContent}>
        <TouchableOpacity
          style={[s.filterBtn, filter === 'all' && { borderColor: COLORS.gold, backgroundColor: COLORS.gold + '15' }]}
          onPress={() => setFilter('all')}
        >
          <Text style={[s.filterTxt, filter === 'all' && { color: COLORS.gold }]}>Tutti</Text>
        </TouchableOpacity>
        {Object.entries(categories).map(([cid, cat]: [string, any]) => (
          <TouchableOpacity
            key={cid}
            style={[s.filterBtn, filter === cid && { borderColor: cat.color, backgroundColor: cat.color + '15' }]}
            onPress={() => setFilter(cid)}
          >
            <Text style={[s.filterTxt, filter === cid && { color: cat.color }]}>{cat.icon} {cat.name}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView contentContainerStyle={s.body}>
        {filtered.map((ach: any, i: number) => {
          const catCol = CAT_COLORS[ach.category] || '#888';
          const hasClaimable = ach.tiers.some((t: any) => t.can_claim);
          return (
            <Animated.View key={ach.id} entering={FadeInDown.delay(i * 25).duration(250)}>
              <LinearGradient
                colors={hasClaimable ? ['rgba(255,215,0,0.06)', 'rgba(255,215,0,0.02)'] : ['rgba(255,255,255,0.03)', 'rgba(255,255,255,0.01)']}
                style={[s.achCard, hasClaimable && { borderColor: COLORS.gold + '60' }, { borderLeftColor: catCol }]}
              >
                <View style={s.achTop}>
                  <View style={[s.achIconWrap, { backgroundColor: catCol + '15' }]}>
                    <Text style={s.achIcon}>{ach.icon}</Text>
                  </View>
                  <View style={s.achInfo}>
                    <Text style={[s.achName, hasClaimable && { color: COLORS.gold }]}>{ach.name}</Text>
                    <Text style={s.achDesc}>{ach.description}</Text>
                  </View>
                  <Text style={[s.achVal, { color: catCol }]}>{ach.current_value.toLocaleString()}</Text>
                </View>
                {/* Progress */}
                <View style={s.achProgBar}>
                  <LinearGradient
                    colors={[catCol, catCol + 'AA']}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={[s.achProgFill, { width: `${ach.progress_pct * 100}%` }]}
                  />
                </View>
                {/* Tiers */}
                <View style={s.tiersRow}>
                  {ach.tiers.map((tier: any, ti: number) => (
                    <TouchableOpacity key={ti}
                      style={[
                        s.tierBtn,
                        tier.completed && s.tierDone,
                        tier.can_claim && s.tierClaim,
                        tier.claimed && s.tierClaimed,
                      ]}
                      onPress={() => tier.can_claim && claim(ach.id, ti, ach.name)}
                      disabled={!tier.can_claim || claiming === `${ach.id}_${ti}`}
                      activeOpacity={0.7}
                    >
                      <Text style={[s.tierTarget, tier.completed && { color: COLORS.success }, tier.can_claim && { color: COLORS.gold }]}>
                        {tier.target.toLocaleString()}
                      </Text>
                      <Text style={s.tierStatus}>
                        {tier.claimed ? '\u2705' : tier.can_claim ? '\uD83C\uDF81' : tier.completed ? '\u2714' : '\uD83D\uDD12'}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </LinearGradient>
            </Animated.View>
          );
        })}
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c: { flex: 1 },
  hdrRight: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  hdrStat: { color: COLORS.textMuted, fontSize: 11, fontWeight: '700' },
  claimBadge: { borderRadius: 10, paddingHorizontal: 7, paddingVertical: 2 },
  claimBadgeTxt: { color: '#fff', fontSize: 9, fontWeight: '900' },
  progWrap: { paddingHorizontal: 14, paddingVertical: 6 },
  progBar: { height: 6, backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 3, overflow: 'hidden' },
  progFill: { height: '100%', borderRadius: 3 },
  progTxt: { color: COLORS.textMuted, fontSize: 8, marginTop: 3, textAlign: 'center' },
  filterWrap: { maxHeight: 38 },
  filterContent: { paddingHorizontal: 10, gap: 6, alignItems: 'center' },
  filterBtn: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
    backgroundColor: 'rgba(255,255,255,0.03)',
  },
  filterTxt: { color: COLORS.textDim, fontSize: 9, fontWeight: '700' },
  body: { padding: 8, gap: 5, paddingBottom: 70 },
  achCard: {
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    borderLeftWidth: 3,
    gap: 5,
  },
  achTop: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  achIconWrap: { width: 32, height: 32, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  achIcon: { fontSize: 18 },
  achInfo: { flex: 1 },
  achName: { color: '#fff', fontSize: 11, fontWeight: '800' },
  achDesc: { color: COLORS.textDim, fontSize: 8, marginTop: 1 },
  achVal: { fontSize: 13, fontWeight: '900' },
  achProgBar: { height: 3, backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' },
  achProgFill: { height: '100%', borderRadius: 2 },
  tiersRow: { flexDirection: 'row', gap: 4 },
  tierBtn: {
    flex: 1,
    paddingVertical: 4,
    alignItems: 'center',
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  tierDone: { borderColor: 'rgba(68,221,136,0.3)' },
  tierClaim: { borderColor: COLORS.gold, backgroundColor: 'rgba(255,215,0,0.08)' },
  tierClaimed: { opacity: 0.35 },
  tierTarget: { color: COLORS.textMuted, fontSize: 8, fontWeight: '700' },
  tierStatus: { fontSize: 10 },
});
