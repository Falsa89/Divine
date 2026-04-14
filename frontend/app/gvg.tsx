import React, { useState, useEffect, useCallback, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import Animated, { useSharedValue, useAnimatedStyle, withTiming, withRepeat, withSequence, FadeIn, FadeInDown, SlideInLeft, SlideInRight } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

function ScoreBar({ myScore, enemyScore, myColor, enemyColor }: { myScore: number, enemyScore: number, myColor: string, enemyColor: string }) {
  const total = Math.max(1, myScore + enemyScore);
  const myPct = (myScore / total) * 100;

  const myWidth = useSharedValue(50);
  useEffect(() => {
    myWidth.value = withTiming(myPct, { duration: 800 });
  }, [myPct]);

  const myStyle = useAnimatedStyle(() => ({
    width: `${myWidth.value}%`,
  }));

  return (
    <View style={styles.scoreBarContainer}>
      <View style={styles.scoreBarBg}>
        <Animated.View style={[styles.scoreBarFillLeft, { backgroundColor: myColor }, myStyle]} />
      </View>
      <View style={styles.scoreLabels}>
        <Text style={[styles.scoreNum, { color: myColor }]}>{myScore.toLocaleString()}</Text>
        <Text style={styles.vs}>VS</Text>
        <Text style={[styles.scoreNum, { color: enemyColor }]}>{enemyScore.toLocaleString()}</Text>
      </View>
    </View>
  );
}

function AttackRank({ attacks, title, color, isMyGuild }: any) {
  if (!attacks || attacks.length === 0) return null;
  return (
    <View style={styles.rankSection}>
      <Text style={[styles.rankTitle, { color }]}>{title}</Text>
      {attacks.slice(0, 5).map((a: any, i: number) => (
        <Animated.View
          key={a.user_id || i}
          entering={isMyGuild ? SlideInLeft.delay(i * 80).duration(300) : SlideInRight.delay(i * 80).duration(300)}
          style={[styles.rankRow, a.is_you && styles.rankRowYou]}
        >
          <Text style={styles.rankPos}>#{i + 1}</Text>
          <Text style={[styles.rankName, a.is_you && { color: '#ffd700' }]}>{a.username}{a.is_you ? ' (TU)' : ''}</Text>
          <Text style={[styles.rankDmg, { color }]}>{a.damage.toLocaleString()}</Text>
        </Animated.View>
      ))}
    </View>
  );
}

export default function GvGScreen() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState('');
  const pollRef = useRef<any>(null);

  const load = useCallback(async () => {
    try {
      const d = await apiCall('/api/gvg/wars');
      setData(d);
    } catch (e) {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    load();
    pollRef.current = setInterval(load, 10000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [load]);

  const matchmake = async () => {
    setActing('match');
    try {
      const r = await apiCall('/api/gvg/matchmake', { method: 'POST' });
      Alert.alert('\u2694\uFE0F Guerra Iniziata!', `Avversario: ${r.opponent}\nAttacca per accumulare punti!`);
      await load();
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setActing(''); }
  };

  const attack = async () => {
    setActing('attack');
    try {
      const r = await apiCall('/api/gvg/attack', { method: 'POST' });
      await refreshUser();
      await load();
      Alert.alert(
        '\u2694\uFE0F Attacco GvG!',
        `Danni inflitti: ${r.damage.toLocaleString()}${r.counter_damage > 0 ? `\nContrattacco nemico: ${r.counter_damage.toLocaleString()}` : ''}\n\nPunteggio: ${r.my_score.toLocaleString()} vs ${r.enemy_score.toLocaleString()}`
      );
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setActing(''); }
  };

  const endWar = async () => {
    Alert.alert('Termina Guerra', 'Vuoi terminare la guerra e assegnare le ricompense?', [
      { text: 'Annulla', style: 'cancel' },
      {
        text: 'Termina', style: 'destructive', onPress: async () => {
          setActing('end');
          try {
            const r = await apiCall('/api/gvg/end-war', { method: 'POST' });
            await refreshUser();
            await load();
            const msg = r.winner === 'Pareggio'
              ? `Pareggio! ${r.score_a.toLocaleString()} vs ${r.score_b.toLocaleString()}`
              : `Vincitore: ${r.winner}\n${r.guild_a_name}: ${r.score_a.toLocaleString()}\n${r.guild_b_name}: ${r.score_b.toLocaleString()}`;
            Alert.alert('\uD83C\uDFC6 Guerra Terminata!', msg);
          } catch (e: any) { Alert.alert('Errore', e.message); }
          finally { setActing(''); }
        }
      },
    ]);
  };

  // Sword animation (must be before conditional returns)
  const swordPulse = useSharedValue(1);
  useEffect(() => {
    swordPulse.value = withRepeat(withSequence(
      withTiming(1.1, { duration: 800 }),
      withTiming(1, { duration: 800 }),
    ), -1, true);
  }, []);
  const swordStyle = useAnimatedStyle(() => ({
    transform: [{ scale: swordPulse.value }],
  }));

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  const activeWar = data?.active_war;
  const recentWars = data?.recent_wars || [];
  const canMatch = data?.can_matchmake;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={styles.hdr}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.back}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={styles.title}>GUERRA TRA GILDE</Text>
        {activeWar && (
          <View style={styles.liveBadge}>
            <View style={styles.liveDot} />
            <Text style={styles.liveTxt}>IN CORSO</Text>
          </View>
        )}
      </View>

      <ScrollView contentContainerStyle={styles.body}>
        {/* No Guild */}
        {!user?.guild_id && (
          <Animated.View entering={FadeIn} style={styles.noGuild}>
            <Text style={styles.noGuildIcon}>{'\uD83C\uDFDB\uFE0F'}</Text>
            <Text style={styles.noGuildTxt}>Devi essere in una gilda per partecipare alle guerre GvG!</Text>
            <TouchableOpacity style={styles.goGuildBtn} onPress={() => router.push('/guild')}>
              <Text style={styles.goGuildTxt}>VAI ALLE GILDE</Text>
            </TouchableOpacity>
          </Animated.View>
        )}

        {/* Active War */}
        {activeWar && (
          <Animated.View entering={FadeInDown.duration(500)} style={styles.warCard}>
            <View style={styles.warHeader}>
              <View style={styles.warGuildCol}>
                <Text style={styles.warGuildName} numberOfLines={1}>{activeWar.my_guild}</Text>
                <Text style={styles.warGuildSub}>{activeWar.total_attacks_my} guerrieri</Text>
              </View>
              <Animated.View style={swordStyle}>
                <Text style={styles.warVsIcon}>{'\u2694\uFE0F'}</Text>
              </Animated.View>
              <View style={[styles.warGuildCol, { alignItems: 'flex-end' }]}>
                <Text style={[styles.warGuildName, { color: '#ff4444' }]} numberOfLines={1}>{activeWar.enemy_guild}</Text>
                <Text style={styles.warGuildSub}>{activeWar.total_attacks_enemy} guerrieri</Text>
              </View>
            </View>

            <ScoreBar
              myScore={activeWar.my_score}
              enemyScore={activeWar.enemy_score}
              myColor="#44cc44"
              enemyColor="#ff4444"
            />

            {/* Timer */}
            <View style={styles.timerRow}>
              <Text style={styles.timerLabel}>{'\u23F0'} Tempo:</Text>
              <Text style={[styles.timerVal, activeWar.time_remaining < 300 && { color: '#ff4444' }]}>
                {Math.floor(activeWar.time_remaining / 60)}:{(activeWar.time_remaining % 60).toString().padStart(2, '0')} restanti
              </Text>
            </View>

            {/* My contribution */}
            <View style={styles.contribRow}>
              <Text style={styles.contribLabel}>{'\uD83D\uDCAA'} I tuoi danni totali:</Text>
              <Text style={styles.contribVal}>{activeWar.my_damage.toLocaleString()}</Text>
            </View>

            {/* Attack Rankings */}
            <View style={styles.rankingsRow}>
              <AttackRank attacks={activeWar.my_attacks} title={`${activeWar.my_guild}`} color="#44cc44" isMyGuild={true} />
              <AttackRank attacks={activeWar.enemy_attacks} title={`${activeWar.enemy_guild}`} color="#ff4444" isMyGuild={false} />
            </View>

            {/* Action buttons */}
            <View style={styles.actionRow}>
              <TouchableOpacity
                style={[styles.atkBtn, acting === 'attack' && { opacity: 0.5 }]}
                onPress={attack}
                disabled={acting === 'attack'}
              >
                <Text style={styles.atkTxt}>{acting === 'attack' ? '\u2694\uFE0F ...' : '\u2694\uFE0F ATTACCA! (\u26A1 12)'}</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.endBtn, acting === 'end' && { opacity: 0.5 }]}
                onPress={endWar}
                disabled={acting === 'end'}
              >
                <Text style={styles.endTxt}>{'\uD83C\uDFC1'} TERMINA</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        )}

        {/* Matchmake Button */}
        {!activeWar && user?.guild_id && (
          <Animated.View entering={FadeIn} style={styles.matchSection}>
            <Text style={styles.matchIcon}>{'\u2694\uFE0F'}</Text>
            <Text style={styles.matchTitle}>Pronto per la guerra?</Text>
            <Text style={styles.matchDesc}>
              La tua gilda ({data?.guild_name}) con {data?.guild_members} membri{'\n'}
              verra abbinata a un avversario di livello simile.
            </Text>
            <TouchableOpacity
              style={[styles.matchBtn, !canMatch && { opacity: 0.4 }, acting === 'match' && { opacity: 0.5 }]}
              onPress={matchmake}
              disabled={!canMatch || acting === 'match'}
            >
              <Text style={styles.matchBtnTxt}>
                {acting === 'match' ? 'CERCANDO...' : !canMatch ? 'COOLDOWN ATTIVO' : '\u2694\uFE0F CERCA AVVERSARIO'}
              </Text>
            </TouchableOpacity>
            <Text style={styles.matchInfo}>{'\u26A1'} 12 stamina per attacco | {'\u23F0'} 30 min per guerra</Text>
          </Animated.View>
        )}

        {/* History */}
        {recentWars.length > 0 && (
          <View style={styles.historySection}>
            <Text style={styles.histTitle}>{'\uD83D\uDCDC'} Ultime Guerre</Text>
            {recentWars.map((w: any, i: number) => (
              <Animated.View key={w.id} entering={FadeInDown.delay(i * 80).duration(300)} style={[styles.histRow, w.won && styles.histRowWon, w.draw && styles.histRowDraw]}>
                <View style={[styles.histBadge, { backgroundColor: w.won ? '#44cc44' : w.draw ? '#888' : '#ff4444' }]}>
                  <Text style={styles.histBadgeTxt}>{w.won ? 'V' : w.draw ? 'P' : 'S'}</Text>
                </View>
                <View style={styles.histInfo}>
                  <Text style={styles.histEnemy}>vs {w.enemy_guild}</Text>
                  <Text style={styles.histScore}>{w.my_score.toLocaleString()} - {w.enemy_score.toLocaleString()}</Text>
                </View>
                <Text style={[styles.histResult, { color: w.won ? '#44cc44' : w.draw ? '#888' : '#ff4444' }]}>
                  {w.won ? 'VITTORIA' : w.draw ? 'PAREGGIO' : 'SCONFITTA'}
                </Text>
              </Animated.View>
            ))}
          </View>
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  c: { flex: 1, backgroundColor:'transparent' },
  hdr: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: 'rgba(255,107,53,0.3)' },
  backBtn: { padding: 4 },
  back: { color: '#ff6b35', fontSize: 20, fontWeight: '700' },
  title: { color: '#fff', fontSize: 14, fontWeight: '800', letterSpacing: 2, flex: 1, marginLeft: 8 },
  liveBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: 'rgba(255,68,68,0.15)', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10 },
  liveDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#ff4444' },
  liveTxt: { color: '#ff4444', fontSize: 8, fontWeight: '900', letterSpacing: 1 },
  body: { padding: 10, gap: 12 },

  // No Guild
  noGuild: { alignItems: 'center', padding: 30, gap: 10 },
  noGuildIcon: { fontSize: 48 },
  noGuildTxt: { color: '#888', fontSize: 13, textAlign: 'center' },
  goGuildBtn: { paddingHorizontal: 20, paddingVertical: 10, backgroundColor: '#6644ff', borderRadius: 10 },
  goGuildTxt: { color: '#fff', fontSize: 13, fontWeight: '800' },

  // War Card
  warCard: { padding: 12, borderRadius: 14, backgroundColor: 'rgba(255,255,255,0.03)', borderWidth: 1.5, borderColor: 'rgba(255,107,53,0.3)', gap: 8 },
  warHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  warGuildCol: { flex: 1 },
  warGuildName: { color: '#44cc44', fontSize: 14, fontWeight: '900' },
  warGuildSub: { color: '#888', fontSize: 9, marginTop: 1 },
  warVsIcon: { fontSize: 24, marginHorizontal: 10 },

  // Score Bar
  scoreBarContainer: { gap: 4 },
  scoreBarBg: { height: 12, backgroundColor: '#ff4444', borderRadius: 6, overflow: 'hidden' },
  scoreBarFillLeft: { height: '100%', borderRadius: 6 },
  scoreLabels: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  scoreNum: { fontSize: 16, fontWeight: '900' },
  vs: { color: '#555', fontSize: 10, fontWeight: '800', letterSpacing: 2 },

  // Timer
  timerRow: { flexDirection: 'row', justifyContent: 'center', gap: 6 },
  timerLabel: { color: '#888', fontSize: 10 },
  timerVal: { color: '#ffd700', fontSize: 10, fontWeight: '700' },

  // Contribution
  contribRow: { flexDirection: 'row', justifyContent: 'center', gap: 8, paddingVertical: 4, backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 6 },
  contribLabel: { color: '#888', fontSize: 10 },
  contribVal: { color: '#ffd700', fontSize: 10, fontWeight: '900' },

  // Rankings
  rankingsRow: { flexDirection: 'row', gap: 8 },
  rankSection: { flex: 1 },
  rankTitle: { fontSize: 10, fontWeight: '800', marginBottom: 4 },
  rankRow: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingVertical: 2, paddingHorizontal: 4, borderRadius: 4, marginBottom: 2 },
  rankRowYou: { backgroundColor: 'rgba(255,215,0,0.08)' },
  rankPos: { color: '#555', fontSize: 8, fontWeight: '700', width: 18 },
  rankName: { color: '#ccc', fontSize: 9, fontWeight: '600', flex: 1 },
  rankDmg: { fontSize: 9, fontWeight: '800' },

  // Action Row
  actionRow: { flexDirection: 'row', gap: 8 },
  atkBtn: { flex: 1, padding: 10, borderRadius: 8, backgroundColor: 'rgba(68,204,68,0.15)', borderWidth: 1.5, borderColor: '#44cc44', alignItems: 'center' },
  atkTxt: { color: '#44cc44', fontSize: 13, fontWeight: '900' },
  endBtn: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 8, backgroundColor: 'rgba(255,68,68,0.1)', borderWidth: 1, borderColor: '#ff4444' },
  endTxt: { color: '#ff4444', fontSize: 11, fontWeight: '700' },

  // Matchmake
  matchSection: { alignItems: 'center', padding: 20, gap: 8, borderRadius: 14, backgroundColor: 'rgba(255,255,255,0.03)', borderWidth: 1, borderColor: 'rgba(255,107,53,0.2)' },
  matchIcon: { fontSize: 40 },
  matchTitle: { color: '#fff', fontSize: 18, fontWeight: '900' },
  matchDesc: { color: '#888', fontSize: 11, textAlign: 'center', lineHeight: 16 },
  matchBtn: { paddingHorizontal: 30, paddingVertical: 12, backgroundColor: 'rgba(255,107,53,0.2)', borderWidth: 1.5, borderColor: '#ff6b35', borderRadius: 10, marginTop: 4 },
  matchBtnTxt: { color: '#ff6b35', fontSize: 14, fontWeight: '900', letterSpacing: 1 },
  matchInfo: { color: '#555', fontSize: 9, marginTop: 4 },

  // History
  historySection: { gap: 6 },
  histTitle: { color: '#fff', fontSize: 13, fontWeight: '800' },
  histRow: { flexDirection: 'row', alignItems: 'center', gap: 8, padding: 8, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.03)', borderLeftWidth: 3, borderLeftColor: '#ff4444' },
  histRowWon: { borderLeftColor: '#44cc44', backgroundColor: 'rgba(68,204,68,0.05)' },
  histRowDraw: { borderLeftColor: '#888' },
  histBadge: { width: 24, height: 24, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  histBadgeTxt: { color: '#fff', fontSize: 10, fontWeight: '900' },
  histInfo: { flex: 1 },
  histEnemy: { color: '#ccc', fontSize: 11, fontWeight: '600' },
  histScore: { color: '#888', fontSize: 9 },
  histResult: { fontSize: 10, fontWeight: '900', letterSpacing: 1 },
});
