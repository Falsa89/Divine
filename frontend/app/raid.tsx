import React, { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import Animated, { useSharedValue, useAnimatedStyle, withTiming, withSequence, withRepeat, FadeIn, FadeInDown, SlideInRight } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const EC: Record<string,string> = { fire:'#ff4444', water:'#4488ff', earth:'#88aa44', wind:'#44cc88', light:'#ffd700', dark:'#9944ff', neutral:'#888' };
const BOSS_EMOJI: Record<string,string> = { dark:'\uD83D\uDC32', fire:'\uD83D\uDD25', water:'\uD83C\uDF0A', neutral:'\uD83D\uDCA0' };
const WEAKNESS: Record<string,string> = { dark:'Luce', fire:'Acqua', water:'Terra', earth:'Vento', wind:'Fuoco', light:'Oscurita' };

interface DamageEntry {
  id: string;
  damage: number;
  bossName: string;
  hpRemaining: number;
  victory: boolean;
  timestamp: number;
}

function AnimatedHpBar({ current, max, color }: { current: number, max: number, color: string }) {
  const progress = useSharedValue(1);
  const pct = Math.max(0, current / max);

  useEffect(() => {
    progress.value = withTiming(pct, { duration: 600 });
  }, [pct]);

  const barStyle = useAnimatedStyle(() => ({
    width: `${progress.value * 100}%`,
    backgroundColor: progress.value > 0.5 ? color : progress.value > 0.2 ? '#ff8844' : '#ff2222',
  }));

  return (
    <View style={styles.hpBarBg}>
      <Animated.View style={[styles.hpBarFill, barStyle]} />
    </View>
  );
}

function BossCard({ boss, activeRaid, onJoin, onAttack, acting, damageLog }: any) {
  const col = EC[boss.element] || '#888';
  const isParticipant = activeRaid?.is_participant;
  const hpCurrent = activeRaid?.current_hp ?? boss.hp;
  const hpPct = Math.round((hpCurrent / boss.hp) * 100);
  const isEnraged = hpPct < 25;
  const weakness = WEAKNESS[boss.element] || '???';

  // Boss shake when enraged
  const shake = useSharedValue(0);
  useEffect(() => {
    if (isEnraged && activeRaid) {
      shake.value = withRepeat(withSequence(
        withTiming(-2, { duration: 80 }),
        withTiming(2, { duration: 80 }),
        withTiming(0, { duration: 80 }),
      ), -1, true);
    } else {
      shake.value = 0;
    }
  }, [isEnraged, activeRaid]);

  const shakeStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: shake.value }],
  }));

  // Relevant damage entries
  const bossLogs = (damageLog || []).filter((d: DamageEntry) => d.bossName === boss.name).slice(0, 5);

  return (
    <Animated.View entering={FadeIn.duration(500)} style={[styles.card, { borderColor: col }]}>
      {/* Boss Header */}
      <View style={styles.cardTop}>
        <Animated.View style={[styles.bossIconContainer, { backgroundColor: col + '15', borderColor: col }, shakeStyle]}>
          <Text style={styles.bossEmoji}>{BOSS_EMOJI[boss.element] || '\uD83D\uDCA0'}</Text>
          {isEnraged && <Text style={styles.enragedBadge}>{'\uD83D\uDCA2'}</Text>}
        </Animated.View>
        <View style={styles.bossInfo}>
          <View style={styles.bossNameRow}>
            <Text style={[styles.bossName, { color: col }]}>{boss.name}</Text>
            {isEnraged && <Text style={styles.enragedTxt}>INFURIATO!</Text>}
          </View>
          <Text style={styles.bossDesc}>{boss.description}</Text>
          <View style={styles.bossStatsRow}>
            <Text style={styles.statBadge}>{'\u2764\uFE0F'} {boss.hp.toLocaleString()}</Text>
            <Text style={styles.statBadge}>{'\u2694\uFE0F'} {boss.attack.toLocaleString()}</Text>
            <Text style={styles.statBadge}>{'\uD83D\uDEE1\uFE0F'} {boss.defense.toLocaleString()}</Text>
            <Text style={[styles.statBadge, { color: '#ff8844' }]}>{'\u26A0\uFE0F'} {weakness}</Text>
          </View>
        </View>
      </View>

      {/* Active Raid Status */}
      {activeRaid && (
        <Animated.View entering={FadeInDown.duration(400)} style={styles.raidActive}>
          <View style={styles.hpSection}>
            <View style={styles.hpHeader}>
              <Text style={styles.hpLabel}>HP BOSS</Text>
              <Text style={[styles.hpPct, { color: hpPct > 50 ? col : hpPct > 20 ? '#ff8844' : '#ff2222' }]}>{hpPct}%</Text>
            </View>
            <AnimatedHpBar current={hpCurrent} max={boss.hp} color={col} />
            <Text style={styles.hpNumbers}>{hpCurrent.toLocaleString()} / {boss.hp.toLocaleString()}</Text>
          </View>

          {/* Participants */}
          <View style={styles.participants}>
            <Text style={styles.partLabel}>{'\uD83D\uDC65'} Partecipanti ({activeRaid.participant_names?.length || 0}/{boss.max_players})</Text>
            <View style={styles.partList}>
              {activeRaid.participant_names?.map((name: string, i: number) => (
                <View key={i} style={[styles.partChip, { borderColor: col + '60' }]}>
                  <Text style={styles.partName}>{name}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Contribution */}
          {activeRaid.total_damage > 0 && (
            <View style={styles.contribSection}>
              <Text style={styles.contribLabel}>Danno totale inflitto: {activeRaid.total_damage.toLocaleString()}</Text>
              <View style={styles.contribBar}>
                <View style={[styles.contribFill, { width: `${Math.min(100, (activeRaid.total_damage / boss.hp) * 100)}%`, backgroundColor: col + '60' }]} />
              </View>
            </View>
          )}
        </Animated.View>
      )}

      {/* Damage Log */}
      {bossLogs.length > 0 && (
        <View style={styles.logSection}>
          <Text style={styles.logTitle}>{'\uD83D\uDCDC'} Log Attacchi</Text>
          {bossLogs.map((entry: DamageEntry, i: number) => (
            <Animated.View key={entry.id} entering={SlideInRight.delay(i * 100).duration(300)} style={styles.logEntry}>
              <Text style={styles.logDmg}>{entry.victory ? '\uD83C\uDFC6' : '\u2694\uFE0F'} -{entry.damage.toLocaleString()}</Text>
              <Text style={styles.logHp}>HP: {entry.hpRemaining.toLocaleString()}</Text>
            </Animated.View>
          ))}
        </View>
      )}

      {/* Rewards */}
      <View style={styles.rewardRow}>
        <Text style={styles.rewardLabel}>Ricompense:</Text>
        <Text style={styles.rewardVal}>{'\uD83D\uDCB0'} {boss.reward_gold.toLocaleString()}</Text>
        <Text style={styles.rewardVal}>{'\uD83D\uDC8E'} {boss.reward_gems}</Text>
        <Text style={styles.rewardVal}>{'\u2728'} {boss.reward_exp.toLocaleString()}</Text>
      </View>

      {/* Action Buttons */}
      <View style={styles.btns}>
        {!isParticipant && (
          <TouchableOpacity
            style={[styles.joinBtn, { borderColor: col }, acting === boss.id && { opacity: 0.5 }]}
            onPress={() => onJoin(boss.id)}
            disabled={acting === boss.id}
          >
            <Text style={[styles.joinTxt, { color: col }]}>
              {acting === boss.id ? '...' : activeRaid ? '\uD83D\uDC65 UNISCITI AL RAID' : '\uD83D\uDE80 CREA RAID'}
            </Text>
          </TouchableOpacity>
        )}
        {isParticipant && (
          <TouchableOpacity
            style={[styles.atkBtn, { backgroundColor: col + '20', borderColor: col }, acting === 'atk_' + boss.id && { opacity: 0.5 }]}
            onPress={() => onAttack(boss.id)}
            disabled={acting === 'atk_' + boss.id}
          >
            <Text style={[styles.atkTxt, { color: col }]}>
              {acting === 'atk_' + boss.id ? '\u2694\uFE0F ATTACCANDO...' : '\u2694\uFE0F ATTACCA! (\u26A1 10)'}
            </Text>
          </TouchableOpacity>
        )}
      </View>
    </Animated.View>
  );
}

export default function RaidScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState('');
  const [damageLog, setDamageLog] = useState<DamageEntry[]>([]);
  const pollRef = useRef<any>(null);

  const load = useCallback(async () => {
    try { const d = await apiCall('/api/raids'); setData(d); }
    catch(e) {}
    finally { setLoading(false); }
  }, []);

  // Initial load + auto-polling every 8 seconds
  useEffect(() => {
    load();
    pollRef.current = setInterval(() => {
      load();
    }, 8000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [load]);

  const joinOrCreate = async (bossId: string) => {
    setActing(bossId);
    try {
      const r = await apiCall('/api/raid/create', { method: 'POST', body: JSON.stringify({ boss_id: bossId }) });
      Alert.alert(
        r.action === 'joined' ? '\uD83D\uDC65 Unito al Raid!' : '\uD83D\uDE80 Raid Creato!',
        'Ora puoi attaccare il boss! Coordina con gli altri giocatori.'
      );
      await load();
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setActing(''); }
  };

  const attack = async (bossId: string) => {
    setActing('atk_' + bossId);
    try {
      const r = await apiCall(`/api/raid/attack/${bossId}`, { method: 'POST' });
      await refreshUser();

      // Add to damage log
      const newEntry: DamageEntry = {
        id: Date.now().toString(),
        damage: r.damage_dealt,
        bossName: r.boss_name,
        hpRemaining: r.boss_hp_remaining,
        victory: r.victory,
        timestamp: Date.now(),
      };
      setDamageLog(prev => [newEntry, ...prev].slice(0, 20));

      await load();

      if (r.victory) {
        Alert.alert(
          '\uD83C\uDFC6 BOSS SCONFITTO!',
          `Danni totali tuoi: ${r.your_total_damage.toLocaleString()}\nRicompense distribuite a tutti i partecipanti!`
        );
      }
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setActing(''); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff4444" /></LinearGradient>;

  const hasActiveRaids = data?.active_raids?.length > 0;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={styles.hdr}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.back}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={styles.title}>RAID COOPERATIVI</Text>
        <View style={styles.hdrRight}>
          {hasActiveRaids && (
            <View style={styles.liveBadge}>
              <View style={styles.liveDot} />
              <Text style={styles.liveTxt}>LIVE</Text>
            </View>
          )}
          <Text style={styles.costTxt}>{'\u26A1'} 10</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.list}>
        {data?.bosses?.map((boss: any) => {
          const activeRaid = data?.active_raids?.find((r: any) => r.boss_id === boss.id);
          return (
            <BossCard
              key={boss.id}
              boss={boss}
              activeRaid={activeRaid}
              onJoin={joinOrCreate}
              onAttack={attack}
              acting={acting}
              damageLog={damageLog}
            />
          );
        })}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  c: { flex: 1, backgroundColor:'transparent' },
  hdr: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: 'rgba(255,68,68,0.3)' },
  backBtn: { padding: 4 },
  back: { color: '#ff4444', fontSize: 20, fontWeight: '700' },
  title: { color: '#ff4444', fontSize: 14, fontWeight: '800', letterSpacing: 2, flex: 1, marginLeft: 8 },
  hdrRight: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  liveBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: 'rgba(68,204,68,0.15)', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10 },
  liveDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#44cc44' },
  liveTxt: { color: '#44cc44', fontSize: 9, fontWeight: '900', letterSpacing: 1 },
  costTxt: { color: '#ff8844', fontSize: 11, fontWeight: '700' },
  list: { padding: 8, gap: 10 },

  // Boss Card
  card: { padding: 10, borderRadius: 12, backgroundColor: 'rgba(255,255,255,0.03)', borderWidth: 1.5, gap: 8 },
  cardTop: { flexDirection: 'row', gap: 10 },
  bossIconContainer: { width: 56, height: 56, borderRadius: 14, alignItems: 'center', justifyContent: 'center', borderWidth: 1.5 },
  bossEmoji: { fontSize: 30 },
  enragedBadge: { position: 'absolute', top: -4, right: -4, fontSize: 12 },
  bossInfo: { flex: 1 },
  bossNameRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  bossName: { fontSize: 14, fontWeight: '900' },
  enragedTxt: { color: '#ff2222', fontSize: 8, fontWeight: '900', backgroundColor: 'rgba(255,34,34,0.15)', paddingHorizontal: 4, paddingVertical: 1, borderRadius: 4 },
  bossDesc: { color: '#888', fontSize: 9, marginTop: 2 },
  bossStatsRow: { flexDirection: 'row', gap: 8, marginTop: 4 },
  statBadge: { color: '#aaa', fontSize: 8, fontWeight: '600' },

  // Active Raid
  raidActive: { gap: 6, paddingTop: 4, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)' },
  hpSection: {},
  hpHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 3 },
  hpLabel: { color: '#888', fontSize: 9, fontWeight: '700', letterSpacing: 1 },
  hpPct: { fontSize: 11, fontWeight: '900' },
  hpBarBg: { height: 10, backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 5, overflow: 'hidden' },
  hpBarFill: { height: '100%', borderRadius: 5 },
  hpNumbers: { color: '#aaa', fontSize: 8, marginTop: 2, textAlign: 'center' },
  participants: {},
  partLabel: { color: '#888', fontSize: 9, fontWeight: '700' },
  partList: { flexDirection: 'row', gap: 4, marginTop: 3, flexWrap: 'wrap' },
  partChip: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8, borderWidth: 1, backgroundColor: 'rgba(255,255,255,0.04)' },
  partName: { color: '#ccc', fontSize: 9, fontWeight: '600' },
  contribSection: { marginTop: 2 },
  contribLabel: { color: '#888', fontSize: 8 },
  contribBar: { height: 4, backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 2, marginTop: 2, overflow: 'hidden' },
  contribFill: { height: '100%', borderRadius: 2 },

  // Damage Log
  logSection: { paddingTop: 4, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)' },
  logTitle: { color: '#888', fontSize: 9, fontWeight: '700', marginBottom: 3 },
  logEntry: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 2, paddingHorizontal: 4, backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: 4, marginBottom: 2 },
  logDmg: { color: '#ff6b35', fontSize: 9, fontWeight: '700' },
  logHp: { color: '#888', fontSize: 9 },

  // Rewards
  rewardRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  rewardLabel: { color: '#888', fontSize: 9 },
  rewardVal: { color: '#ffd700', fontSize: 9, fontWeight: '700' },

  // Buttons
  btns: { flexDirection: 'row', gap: 8 },
  joinBtn: { flex: 1, padding: 10, borderRadius: 8, borderWidth: 1.5, alignItems: 'center' },
  joinTxt: { fontSize: 12, fontWeight: '800' },
  atkBtn: { flex: 1, padding: 10, borderRadius: 8, borderWidth: 1.5, alignItems: 'center' },
  atkTxt: { fontSize: 12, fontWeight: '800' },
});
