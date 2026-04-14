import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, Dimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import Animated, { useSharedValue, useAnimatedStyle, withRepeat, withTiming, withSequence, withDelay, FadeIn, FadeInUp } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const { width: SW, height: SH } = Dimensions.get('window');
const MAP_W = Math.max(SW - 32, 600);
const MAP_H = Math.max(SH - 130, 260);

const EC: Record<string,string> = { fire:'#ff4444', water:'#4488ff', earth:'#88aa44', wind:'#44cc88', light:'#ffd700', dark:'#9944ff', neutral:'#ff6b35' };
const EI: Record<string,string> = { fire:'\uD83C\uDF0B', water:'\uD83C\uDF0A', earth:'\uD83C\uDFD4\uFE0F', wind:'\uD83C\uDF2C\uFE0F', light:'\u2728', dark:'\uD83C\uDF11', neutral:'\uD83C\uDFDB\uFE0F' };
const EN: Record<string,string> = { fire:'Fuoco', water:'Acqua', earth:'Terra', wind:'Vento', light:'Luce', dark:'Oscurita', neutral:'Neutro' };

// Map layout positions (relative to MAP_W/MAP_H)
const MAP_POSITIONS: Record<string, {x:number, y:number}> = {
  volcano:  { x: 0.12, y: 0.20 },
  ocean:    { x: 0.38, y: 0.65 },
  forest:   { x: 0.75, y: 0.15 },
  skylands: { x: 0.60, y: 0.48 },
  sanctum:  { x: 0.25, y: 0.42 },
  abyss:    { x: 0.85, y: 0.60 },
  olympus:  { x: 0.48, y: 0.18 },
};

// Connections between territories (visual lines)
const CONNECTIONS = [
  ['volcano', 'sanctum'], ['sanctum', 'olympus'], ['olympus', 'forest'],
  ['sanctum', 'ocean'], ['olympus', 'skylands'], ['skylands', 'abyss'],
  ['ocean', 'skylands'], ['forest', 'skylands'],
];

function PulsingNode({ territory, onPress, attacking, isOwned, userGuild }: any) {
  const col = EC[territory.element] || '#888';
  const pulse = useSharedValue(1);
  const glow = useSharedValue(0);
  const isOlympus = territory.id === 'olympus';
  const nodeSize = isOlympus ? 68 : 54;

  useEffect(() => {
    if (isOwned) {
      pulse.value = withRepeat(withSequence(
        withTiming(1.08, { duration: 1200 }),
        withTiming(1, { duration: 1200 }),
      ), -1, true);
      glow.value = withRepeat(withSequence(
        withTiming(0.6, { duration: 1500 }),
        withTiming(0.2, { duration: 1500 }),
      ), -1, true);
    } else {
      pulse.value = withRepeat(withSequence(
        withTiming(1.03, { duration: 2000 }),
        withTiming(1, { duration: 2000 }),
      ), -1, true);
      glow.value = 0;
    }
  }, [isOwned]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulse.value }],
  }));

  const glowStyle = useAnimatedStyle(() => ({
    opacity: glow.value,
  }));

  const pos = MAP_POSITIONS[territory.id] || { x: 0.5, y: 0.5 };

  return (
    <Animated.View
      entering={FadeIn.delay(200).duration(600)}
      style={[
        styles.nodeWrapper,
        { left: pos.x * MAP_W - nodeSize/2, top: pos.y * MAP_H - nodeSize/2 },
      ]}
    >
      {/* Glow ring for owned */}
      {isOwned && (
        <Animated.View style={[styles.glowRing, glowStyle, {
          width: nodeSize + 16, height: nodeSize + 16, borderRadius: (nodeSize+16)/2,
          borderColor: col, left: -8, top: -8,
        }]} />
      )}
      <Animated.View style={animatedStyle}>
        <TouchableOpacity
          onPress={() => onPress(territory)}
          disabled={attacking === territory.id}
          activeOpacity={0.7}
          style={[
            styles.node,
            {
              width: nodeSize, height: nodeSize, borderRadius: nodeSize/2,
              borderColor: col, borderWidth: isOlympus ? 3 : 2,
              backgroundColor: isOwned ? col + '30' : 'rgba(20,20,40,0.9)',
            },
          ]}
        >
          <Text style={[styles.nodeIcon, { fontSize: isOlympus ? 24 : 20 }]}>{EI[territory.element]}</Text>
          {territory.controlled_by && (
            <View style={[styles.flagBadge, { backgroundColor: isOwned ? '#44cc44' : '#ff4444' }]}>
              <Text style={styles.flagText}>{territory.controlled_by.substring(0,3)}</Text>
            </View>
          )}
        </TouchableOpacity>
      </Animated.View>
      {/* Label - also clickable */}
      <TouchableOpacity onPress={() => onPress(territory)} style={[styles.nodeLabel, { top: nodeSize + 2 }]} activeOpacity={0.7}>
        <Text style={[styles.nodeName, { color: col }]} numberOfLines={1}>{territory.name.split(' ').slice(-1)[0]}</Text>
        {territory.defense_power > 0 && (
          <Text style={styles.nodeDefense}>{'\uD83D\uDEE1\uFE0F'} {territory.defense_power.toLocaleString()}</Text>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
}

function ConnectionLine({ from, to, territories }: { from: string, to: string, territories: any[] }) {
  const tFrom = territories.find((t:any) => t.id === from);
  const tTo = territories.find((t:any) => t.id === to);
  if (!tFrom || !tTo) return null;

  const pFrom = MAP_POSITIONS[from];
  const pTo = MAP_POSITIONS[to];
  if (!pFrom || !pTo) return null;

  const x1 = pFrom.x * MAP_W;
  const y1 = pFrom.y * MAP_H;
  const x2 = pTo.x * MAP_W;
  const y2 = pTo.y * MAP_H;

  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.sqrt(dx*dx + dy*dy);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);

  const sameOwner = tFrom.controlled_guild_id && tFrom.controlled_guild_id === tTo.controlled_guild_id;

  return (
    <View
      style={[
        styles.connectionLine,
        {
          left: x1,
          top: y1,
          width: len,
          transform: [{ rotate: `${angle}deg` }],
          backgroundColor: sameOwner ? 'rgba(68,204,68,0.3)' : 'rgba(255,255,255,0.08)',
          height: sameOwner ? 2 : 1,
        },
      ]}
    />
  );
}

export default function TerritoryScreen() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [attacking, setAttacking] = useState('');
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    try { const d = await apiCall('/api/territory/map'); setData(d); }
    catch(e) {}
    finally { setLoading(false); }
  };

  const attack = async (id: string) => {
    setAttacking(id);
    try {
      const r = await apiCall('/api/territory/attack', { method:'POST', body: JSON.stringify({territory_id:id}) });
      await refreshUser();
      await load();
      setSelected(null);
      if (r.action === 'reinforce') {
        Alert.alert('\uD83D\uDEE1\uFE0F Rinforzo!', `${r.territory} rinforzato!\n+${r.added_defense} difesa`);
      } else if (r.victory) {
        Alert.alert('\u2694\uFE0F Conquistato!', `${r.territory} conquistato!\n\uD83D\uDCB0 +${r.rewards?.gold} oro\n\uD83D\uDC8E +${r.rewards?.gems} gemme`);
      } else {
        Alert.alert('\uD83D\uDCA5 Sconfitta', `Non sei riuscito a conquistare ${r.territory}`);
      }
    } catch(e:any) { Alert.alert('Errore', e.message); }
    finally { setAttacking(''); }
  };

  const onNodePress = (territory: any) => {
    setSelected(territory);
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  const territories = data?.territories || [];
  const ownedCount = territories.filter((t:any) => t.controlled_guild_id && user?.guild_id === t.controlled_guild_id).length;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      {/* Header */}
      <View style={styles.hdr}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.back}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={styles.title}>MAPPA TERRITORI</Text>
        <View style={styles.hdrRight}>
          <Text style={styles.ownedBadge}>{'\uD83C\uDFF4'} {ownedCount}/{territories.length}</Text>
          <Text style={styles.costBadge}>{'\u26A1'} 15</Text>
        </View>
      </View>

      {/* Map Area */}
      <View style={styles.mapContainer}>
        <View style={[styles.mapArea, { width: MAP_W, height: MAP_H }]}>
          {/* Grid background */}
          <View style={styles.gridBg} />

          {/* Connection lines */}
          {CONNECTIONS.map(([a, b], i) => (
            <ConnectionLine key={i} from={a} to={b} territories={territories} />
          ))}

          {/* Territory Nodes */}
          {territories.map((t: any) => (
            <PulsingNode
              key={t.id}
              territory={t}
              onPress={onNodePress}
              attacking={attacking}
              isOwned={t.controlled_guild_id && user?.guild_id === t.controlled_guild_id}
              userGuild={user?.guild_id}
            />
          ))}
        </View>
      </View>

      {/* Selected Territory Panel */}
      {selected && (
        <Animated.View entering={FadeInUp.duration(300)} style={styles.panel}>
          <View style={styles.panelHeader}>
            <Text style={styles.panelIcon}>{EI[selected.element]}</Text>
            <View style={styles.panelInfo}>
              <Text style={[styles.panelName, { color: EC[selected.element] }]}>{selected.name}</Text>
              <Text style={styles.panelElem}>{EN[selected.element] || selected.element} | Difesa: {selected.defense_power.toLocaleString()}</Text>
            </View>
            <TouchableOpacity onPress={() => setSelected(null)} style={styles.closeBtn}>
              <Text style={styles.closeTxt}>{'\u2715'}</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.panelBody}>
            <View style={styles.panelRow}>
              <Text style={styles.panelLabel}>Controllato da:</Text>
              <Text style={[styles.panelValue, { color: selected.controlled_by ? '#44cc44' : '#888' }]}>
                {selected.controlled_by || 'Nessuno'}
              </Text>
            </View>
            <View style={styles.panelRow}>
              <Text style={styles.panelLabel}>Ricompense:</Text>
              <Text style={styles.panelReward}>{'\uD83D\uDCB0'} {selected.reward_gold.toLocaleString()} | {'\uD83D\uDC8E'} {selected.reward_gems}</Text>
            </View>
          </View>
          <TouchableOpacity
            style={[
              styles.panelBtn,
              { backgroundColor: EC[selected.element] + '25', borderColor: EC[selected.element] },
              attacking === selected.id && { opacity: 0.5 },
            ]}
            onPress={() => attack(selected.id)}
            disabled={attacking === selected.id}
          >
            <Text style={[styles.panelBtnTxt, { color: EC[selected.element] }]}>
              {selected.controlled_guild_id && user?.guild_id === selected.controlled_guild_id
                ? '\uD83D\uDEE1\uFE0F RINFORZA'
                : attacking === selected.id
                  ? 'ATTACCANDO...'
                  : '\u2694\uFE0F ATTACCA TERRITORIO'}
            </Text>
          </TouchableOpacity>
        </Animated.View>
      )}

      {/* Legend */}
      {!selected && (
        <View style={styles.legend}>
          {Object.entries(EC).slice(0, 6).map(([elem, col]) => (
            <View key={elem} style={styles.legendItem}>
              <View style={[styles.legendDot, { backgroundColor: col }]} />
              <Text style={styles.legendTxt}>{EN[elem]}</Text>
            </View>
          ))}
        </View>
      )}
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  c: { flex: 1, backgroundColor:'transparent' },
  hdr: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: 'rgba(255,107,53,0.2)' },
  backBtn: { padding: 4 },
  back: { color: '#ff6b35', fontSize: 20, fontWeight: '700' },
  title: { color: '#fff', fontSize: 14, fontWeight: '800', letterSpacing: 2, flex: 1, marginLeft: 8 },
  hdrRight: { flexDirection: 'row', gap: 8 },
  ownedBadge: { color: '#44cc44', fontSize: 11, fontWeight: '700' },
  costBadge: { color: '#ff8844', fontSize: 11, fontWeight: '700' },
  mapContainer: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  mapArea: { position: 'relative' },
  gridBg: { ...StyleSheet.absoluteFillObject, opacity: 0.03, backgroundColor: '#fff', borderRadius: 8 },
  connectionLine: { position: 'absolute', height: 1, transformOrigin: 'left center' },
  nodeWrapper: { position: 'absolute', alignItems: 'center', zIndex: 10 },
  glowRing: { position: 'absolute', borderWidth: 2, borderStyle: 'dashed' },
  node: { alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.5, shadowRadius: 4, elevation: 5 },
  nodeIcon: {},
  flagBadge: { position: 'absolute', bottom: -2, right: -4, paddingHorizontal: 3, paddingVertical: 1, borderRadius: 4 },
  flagText: { color: '#fff', fontSize: 6, fontWeight: '900' },
  nodeLabel: { position: 'absolute', alignItems: 'center', width: 80 },
  nodeName: { fontSize: 9, fontWeight: '800', textAlign: 'center' },
  nodeDefense: { fontSize: 7, color: '#aaa', textAlign: 'center' },
  panel: { position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(15,15,30,0.97)', borderTopWidth: 1, borderTopColor: 'rgba(255,107,53,0.3)', padding: 12 },
  panelHeader: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  panelIcon: { fontSize: 30 },
  panelInfo: { flex: 1 },
  panelName: { fontSize: 16, fontWeight: '900' },
  panelElem: { color: '#aaa', fontSize: 11, marginTop: 1 },
  closeBtn: { padding: 8 },
  closeTxt: { color: '#888', fontSize: 16 },
  panelBody: { marginTop: 8, gap: 4 },
  panelRow: { flexDirection: 'row', justifyContent: 'space-between' },
  panelLabel: { color: '#888', fontSize: 11 },
  panelValue: { fontSize: 11, fontWeight: '700' },
  panelReward: { color: '#ffd700', fontSize: 11, fontWeight: '700' },
  panelBtn: { marginTop: 8, padding: 10, borderRadius: 8, borderWidth: 1.5, alignItems: 'center' },
  panelBtnTxt: { fontSize: 13, fontWeight: '900', letterSpacing: 1 },
  legend: { flexDirection: 'row', justifyContent: 'center', gap: 12, paddingVertical: 6, paddingHorizontal: 12, flexWrap: 'wrap' },
  legendItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  legendDot: { width: 8, height: 8, borderRadius: 4 },
  legendTxt: { color: '#888', fontSize: 8 },
});
