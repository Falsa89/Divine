import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import Animated, { FadeIn, FadeInDown, useSharedValue, useAnimatedStyle, withRepeat, withSequence, withTiming } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const RARITY_COLORS: Record<number, string> = { 1: '#888', 2: '#44aa44', 3: '#4488ff', 4: '#aa44ff', 5: '#ff8844', 6: '#ffd700' };
const STAR = '\u2B50';

type TabType = 'artifacts' | 'constellations';

function StarRow({ count }: { count: number }) {
  return <Text style={styles.stars}>{STAR.repeat(count)}</Text>;
}

export default function ArtifactsScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [tab, setTab] = useState<TabType>('artifacts');
  const [artData, setArtData] = useState<any>(null);
  const [constData, setConstData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [pulling, setPulling] = useState('');

  // Animation for constellation glow
  const glow = useSharedValue(0.3);
  useEffect(() => {
    glow.value = withRepeat(withSequence(
      withTiming(0.8, { duration: 1500 }),
      withTiming(0.3, { duration: 1500 }),
    ), -1, true);
  }, []);
  const glowStyle = useAnimatedStyle(() => ({ opacity: glow.value }));

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    try {
      const [a, c] = await Promise.all([
        apiCall('/api/artifacts'),
        apiCall('/api/constellations'),
      ]);
      setArtData(a);
      setConstData(c);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const pullArtifact = async (multi: boolean) => {
    setPulling(multi ? 'art10' : 'art1');
    try {
      const endpoint = multi ? '/api/artifacts/pull10' : '/api/artifacts/pull';
      const r = await apiCall(endpoint, { method: 'POST' });
      await refreshUser();
      await loadAll();
      if (multi) {
        const names = r.results.map((x: any) => `${x.artifact.icon} ${x.artifact.name} (${x.artifact.rarity}${STAR})${x.is_duplicate ? ' DUP' : ' NUOVO!'}`).join('\n');
        Alert.alert('\uD83C\uDFB0 10 Artefatti!', names);
      } else {
        Alert.alert(
          r.is_duplicate ? '\uD83D\uDD04 Duplicato!' : '\u2728 Nuovo Artefatto!',
          `${r.artifact.icon} ${r.artifact.name} (${r.artifact.rarity}${STAR})\n${r.is_duplicate ? 'Aggiunto come materiale di fusione' : r.artifact.description}`
        );
      }
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setPulling(''); }
  };

  const pullConstellation = async (multi: boolean) => {
    setPulling(multi ? 'const10' : 'const1');
    try {
      const endpoint = multi ? '/api/constellations/pull10' : '/api/constellations/pull';
      const r = await apiCall(endpoint, { method: 'POST' });
      await refreshUser();
      await loadAll();
      if (multi) {
        const names = r.results.map((x: any) => `${x.constellation.icon} ${x.constellation.name} (${x.constellation.rarity}${STAR})${x.is_duplicate ? ' DUP' : ' NUOVA!'}`).join('\n');
        Alert.alert('\u2728 10 Costellazioni!', names);
      } else {
        Alert.alert(
          r.is_duplicate ? '\uD83D\uDD04 Duplicato!' : '\u2728 Nuova Costellazione!',
          `${r.constellation.icon} ${r.constellation.name} (${r.constellation.rarity}${STAR})\n${r.is_duplicate ? 'Aggiunto come materiale di fusione' : r.constellation.description}`
        );
      }
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setPulling(''); }
  };

  const fuseArtifact = async (id: string) => {
    try {
      const r = await apiCall('/api/artifacts/fuse', { method: 'POST', body: JSON.stringify({ artifact_id: id }) });
      await loadAll();
      Alert.alert('\uD83D\uDD25 Potenziato!', `Livello ${r.new_level}!\nNuovi buff: ${Object.entries(r.new_buff).map(([k, v]) => `+${(Number(v) * 100).toFixed(1)}% ${k}`).join(', ')}`);
    } catch (e: any) { Alert.alert('Errore', e.message); }
  };

  const fuseConstellation = async (id: string) => {
    try {
      const r = await apiCall('/api/constellations/fuse', { method: 'POST', body: JSON.stringify({ constellation_id: id }) });
      await loadAll();
      Alert.alert('\u2B50 Potenziata!', `Livello ${r.new_level}!\nNuovi buff: ${Object.entries(r.new_buff).map(([k, v]) => `+${(Number(v) * 100).toFixed(1)}% ${k}`).join(', ')}`);
    } catch (e: any) { Alert.alert('Errore', e.message); }
  };

  const equipConstellation = async (id: string) => {
    try {
      const r = await apiCall('/api/constellations/equip', { method: 'POST', body: JSON.stringify({ constellation_id: id }) });
      await loadAll();
      Alert.alert('\u264C Equipaggiata!', `Costellazione ${r.constellation} attiva sul team!`);
    } catch (e: any) { Alert.alert('Errore', e.message); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ffd700" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      {/* Header */}
      <View style={styles.hdr}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.back}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={styles.title}>{tab === 'artifacts' ? 'ARTEFATTI' : 'COSTELLAZIONI'}</Text>
        {tab === 'artifacts' && artData && (
          <Text style={styles.countBadge}>{artData.owned_count}/{artData.total_count}</Text>
        )}
      </View>

      {/* Tab switcher */}
      <View style={styles.tabs}>
        <TouchableOpacity style={[styles.tab, tab === 'artifacts' && styles.tabActive]} onPress={() => setTab('artifacts')}>
          <Text style={[styles.tabTxt, tab === 'artifacts' && styles.tabTxtActive]}>{'\uD83D\uDC8E'} Artefatti</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tab, tab === 'constellations' && styles.tabActiveConst]} onPress={() => setTab('constellations')}>
          <Text style={[styles.tabTxt, tab === 'constellations' && styles.tabTxtActive]}>{'\u2728'} Costellazioni</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.body}>
        {/* ========== ARTIFACTS TAB ========== */}
        {tab === 'artifacts' && (
          <>
            {/* Pull buttons */}
            <View style={styles.pullRow}>
              <TouchableOpacity style={[styles.pullBtn, pulling === 'art1' && { opacity: 0.5 }]} onPress={() => pullArtifact(false)} disabled={!!pulling}>
                <Text style={styles.pullTxt}>{pulling === 'art1' ? '...' : '\uD83C\uDFB0 Evoca x1'}</Text>
                <Text style={styles.pullCost}>{'\uD83D\uDC8E'} 120</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.pullBtn, styles.pullBtn10, pulling === 'art10' && { opacity: 0.5 }]} onPress={() => pullArtifact(true)} disabled={!!pulling}>
                <Text style={styles.pullTxt}>{pulling === 'art10' ? '...' : '\uD83C\uDFB0 Evoca x10'}</Text>
                <Text style={styles.pullCost}>{'\uD83D\uDC8E'} 1,000</Text>
              </TouchableOpacity>
            </View>

            {/* Total buffs */}
            {artData && Object.keys(artData.total_buffs).length > 0 && (
              <Animated.View entering={FadeIn} style={styles.totalBuffs}>
                <Text style={styles.totalTitle}>{'\uD83D\uDCAA'} Buff Totali Team</Text>
                <View style={styles.buffGrid}>
                  {Object.entries(artData.total_buffs).map(([stat, val]) => (
                    <View key={stat} style={styles.buffChip}>
                      <Text style={styles.buffStat}>{stat.toUpperCase()}</Text>
                      <Text style={styles.buffVal}>+{(Number(val) * 100).toFixed(1)}%</Text>
                    </View>
                  ))}
                </View>
              </Animated.View>
            )}

            {/* Artifact list */}
            <View style={styles.grid}>
              {artData?.artifacts?.map((art: any, i: number) => {
                const col = RARITY_COLORS[art.rarity] || '#888';
                return (
                  <Animated.View key={art.id} entering={FadeInDown.delay(i * 40).duration(300)} style={[styles.artCard, { borderColor: art.owned ? col : '#333', opacity: art.owned ? 1 : 0.5 }]}>
                    <View style={styles.artTop}>
                      <Text style={styles.artIcon}>{art.icon}</Text>
                      <View style={styles.artInfo}>
                        <Text style={[styles.artName, { color: col }]} numberOfLines={1}>{art.name}</Text>
                        <StarRow count={art.rarity} />
                      </View>
                      {art.owned && <Text style={styles.artLevel}>Lv.{art.level}</Text>}
                    </View>
                    {art.owned && (
                      <View style={styles.artBuffs}>
                        {Object.entries(art.effective_buff).map(([k, v]) => (
                          <Text key={k} style={styles.artBuffTxt}>+{(Number(v) * 100).toFixed(1)}% {k}</Text>
                        ))}
                        {art.duplicates > 0 && (
                          <TouchableOpacity style={[styles.fuseBtn, { borderColor: col }]} onPress={() => fuseArtifact(art.id)}>
                            <Text style={[styles.fuseTxt, { color: col }]}>{'\uD83D\uDD25'} POTENZIA ({art.duplicates})</Text>
                          </TouchableOpacity>
                        )}
                      </View>
                    )}
                    {!art.owned && <Text style={styles.artLocked}>{'\uD83D\uDD12'} Non posseduto</Text>}
                  </Animated.View>
                );
              })}
            </View>
          </>
        )}

        {/* ========== CONSTELLATIONS TAB ========== */}
        {tab === 'constellations' && (
          <>
            {/* Pull buttons */}
            <View style={styles.pullRow}>
              <TouchableOpacity style={[styles.pullBtnConst, pulling === 'const1' && { opacity: 0.5 }]} onPress={() => pullConstellation(false)} disabled={!!pulling}>
                <Text style={styles.pullTxt}>{pulling === 'const1' ? '...' : '\u2728 Evoca x1'}</Text>
                <Text style={styles.pullCost}>{'\uD83D\uDC8E'} 200</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.pullBtnConst, styles.pullBtn10Const, pulling === 'const10' && { opacity: 0.5 }]} onPress={() => pullConstellation(true)} disabled={!!pulling}>
                <Text style={styles.pullTxt}>{pulling === 'const10' ? '...' : '\u2728 Evoca x10'}</Text>
                <Text style={styles.pullCost}>{'\uD83D\uDC8E'} 1,800</Text>
              </TouchableOpacity>
            </View>

            {/* Equipped constellation */}
            {constData?.equipped_id && constData.equipped_buff && (
              <Animated.View entering={FadeIn} style={styles.equippedCard}>
                <Animated.View style={[styles.equippedGlow, glowStyle]} />
                <Text style={styles.equippedLabel}>{'\u264C'} COSTELLAZIONE ATTIVA</Text>
                <View style={styles.equippedBuffs}>
                  {Object.entries(constData.equipped_buff).map(([k, v]) => (
                    <Text key={k} style={styles.equippedBuff}>+{(Number(v) * 100).toFixed(1)}% {k}</Text>
                  ))}
                </View>
                {constData.equipped_skill && (
                  <View style={styles.skillRow}>
                    <Text style={styles.skillLabel}>{'\u2694\uFE0F'} Skill (ogni 3 turni):</Text>
                    <Text style={styles.skillName}>{constData.equipped_skill.name}</Text>
                    <Text style={styles.skillDesc}>{constData.equipped_skill.description}</Text>
                  </View>
                )}
              </Animated.View>
            )}

            {/* Constellation list */}
            {constData?.constellations?.map((c: any, i: number) => {
              const col = c.color || '#888';
              return (
                <Animated.View key={c.id} entering={FadeInDown.delay(i * 50).duration(300)} style={[styles.constCard, { borderColor: c.owned ? col : '#333', opacity: c.owned ? 1 : 0.5 }]}>
                  <View style={styles.constTop}>
                    <View style={[styles.constIconBg, { backgroundColor: col + '20', borderColor: col }]}>
                      <Text style={styles.constIcon}>{c.icon}</Text>
                    </View>
                    <View style={styles.constInfo}>
                      <View style={styles.constNameRow}>
                        <Text style={[styles.constName, { color: col }]}>{c.name}</Text>
                        <Text style={styles.constRank}>#{c.rank}</Text>
                        {c.equipped && <Text style={styles.equippedBadge}>{'\u2705'} ATTIVA</Text>}
                      </View>
                      <StarRow count={c.rarity} />
                      <Text style={styles.constDesc} numberOfLines={1}>{c.description}</Text>
                    </View>
                    {c.owned && <Text style={styles.constLevel}>Lv.{c.level}</Text>}
                  </View>

                  {c.owned && (
                    <View style={styles.constDetails}>
                      <View style={styles.constBuffRow}>
                        <Text style={styles.constBuffLabel}>Buff Team:</Text>
                        {Object.entries(c.effective_buff).map(([k, v]) => (
                          <Text key={k} style={[styles.constBuffVal, { color: col }]}>+{(Number(v) * 100).toFixed(1)}% {k}</Text>
                        ))}
                      </View>
                      <View style={styles.constSkillRow}>
                        <Text style={styles.constSkillLabel}>{'\u2694\uFE0F'} {c.skill.name}</Text>
                        <Text style={styles.constSkillDesc}>{c.skill.description}</Text>
                      </View>
                      <View style={styles.constActions}>
                        {!c.equipped && (
                          <TouchableOpacity style={[styles.equipBtn, { borderColor: col }]} onPress={() => equipConstellation(c.id)}>
                            <Text style={[styles.equipTxt, { color: col }]}>EQUIPAGGIA</Text>
                          </TouchableOpacity>
                        )}
                        {c.duplicates > 0 && (
                          <TouchableOpacity style={[styles.fuseBtn, { borderColor: col }]} onPress={() => fuseConstellation(c.id)}>
                            <Text style={[styles.fuseTxt, { color: col }]}>{'\u2B50'} POTENZIA ({c.duplicates})</Text>
                          </TouchableOpacity>
                        )}
                      </View>
                    </View>
                  )}
                  {!c.owned && <Text style={styles.constLocked}>{'\uD83D\uDD12'} Evoca per sbloccare</Text>}
                </Animated.View>
              );
            })}
          </>
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  c: { flex: 1, backgroundColor:'transparent' },
  hdr: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: 'rgba(255,215,0,0.2)' },
  backBtn: { padding: 4 },
  back: { color: '#ffd700', fontSize: 20, fontWeight: '700' },
  title: { color: '#ffd700', fontSize: 14, fontWeight: '800', letterSpacing: 2, flex: 1, marginLeft: 8 },
  countBadge: { color: '#888', fontSize: 11 },
  tabs: { flexDirection: 'row', borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)' },
  tab: { flex: 1, paddingVertical: 8, alignItems: 'center', borderBottomWidth: 2, borderBottomColor: 'transparent' },
  tabActive: { borderBottomColor: '#ffd700' },
  tabActiveConst: { borderBottomColor: '#9944ff' },
  tabTxt: { color: '#888', fontSize: 12, fontWeight: '700' },
  tabTxtActive: { color: '#fff' },
  body: { padding: 8, gap: 8, paddingBottom: 20 },
  // Pull buttons
  pullRow: { flexDirection: 'row', gap: 8 },
  pullBtn: { flex: 1, padding: 10, borderRadius: 10, backgroundColor: 'rgba(255,215,0,0.1)', borderWidth: 1.5, borderColor: '#ffd700', alignItems: 'center' },
  pullBtn10: { backgroundColor: 'rgba(255,215,0,0.2)' },
  pullBtnConst: { flex: 1, padding: 10, borderRadius: 10, backgroundColor: 'rgba(153,68,255,0.1)', borderWidth: 1.5, borderColor: '#9944ff', alignItems: 'center' },
  pullBtn10Const: { backgroundColor: 'rgba(153,68,255,0.2)' },
  pullTxt: { color: '#fff', fontSize: 12, fontWeight: '800' },
  pullCost: { color: '#aaa', fontSize: 9, marginTop: 2 },
  // Total buffs
  totalBuffs: { padding: 10, borderRadius: 10, backgroundColor: 'rgba(255,215,0,0.05)', borderWidth: 1, borderColor: 'rgba(255,215,0,0.2)' },
  totalTitle: { color: '#ffd700', fontSize: 12, fontWeight: '800', marginBottom: 6 },
  buffGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  buffChip: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6, backgroundColor: 'rgba(255,215,0,0.1)' },
  buffStat: { color: '#ffd700', fontSize: 8, fontWeight: '700' },
  buffVal: { color: '#44cc44', fontSize: 10, fontWeight: '800' },
  // Artifact cards
  grid: { gap: 6 },
  artCard: { padding: 8, borderRadius: 10, backgroundColor: 'rgba(255,255,255,0.03)', borderWidth: 1.5 },
  artTop: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  artIcon: { fontSize: 24 },
  artInfo: { flex: 1 },
  artName: { fontSize: 12, fontWeight: '800' },
  stars: { fontSize: 8, color: '#ffd700' },
  artLevel: { color: '#ffd700', fontSize: 11, fontWeight: '900' },
  artBuffs: { marginTop: 4, paddingTop: 4, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)', gap: 2 },
  artBuffTxt: { color: '#44cc44', fontSize: 9, fontWeight: '600' },
  artLocked: { color: '#555', fontSize: 9, marginTop: 4 },
  fuseBtn: { marginTop: 4, paddingVertical: 4, paddingHorizontal: 10, borderRadius: 6, borderWidth: 1, alignSelf: 'flex-start' },
  fuseTxt: { fontSize: 9, fontWeight: '800' },
  // Equipped constellation
  equippedCard: { padding: 12, borderRadius: 12, backgroundColor: 'rgba(153,68,255,0.08)', borderWidth: 1.5, borderColor: '#9944ff', overflow: 'hidden' },
  equippedGlow: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(153,68,255,0.1)' },
  equippedLabel: { color: '#9944ff', fontSize: 12, fontWeight: '900', letterSpacing: 1 },
  equippedBuffs: { flexDirection: 'row', gap: 10, marginTop: 4 },
  equippedBuff: { color: '#44cc44', fontSize: 10, fontWeight: '700' },
  skillRow: { marginTop: 6, paddingTop: 6, borderTopWidth: 1, borderTopColor: 'rgba(153,68,255,0.2)' },
  skillLabel: { color: '#888', fontSize: 9 },
  skillName: { color: '#ffd700', fontSize: 12, fontWeight: '800' },
  skillDesc: { color: '#aaa', fontSize: 9, marginTop: 1 },
  // Constellation cards
  constCard: { padding: 10, borderRadius: 12, backgroundColor: 'rgba(255,255,255,0.03)', borderWidth: 1.5 },
  constTop: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  constIconBg: { width: 42, height: 42, borderRadius: 21, borderWidth: 1.5, alignItems: 'center', justifyContent: 'center' },
  constIcon: { fontSize: 22 },
  constInfo: { flex: 1 },
  constNameRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  constName: { fontSize: 13, fontWeight: '900' },
  constRank: { color: '#666', fontSize: 9, fontWeight: '700' },
  equippedBadge: { fontSize: 8, color: '#44cc44', fontWeight: '800' },
  constDesc: { color: '#666', fontSize: 8, marginTop: 1 },
  constLevel: { color: '#ffd700', fontSize: 12, fontWeight: '900' },
  constDetails: { marginTop: 6, paddingTop: 6, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)', gap: 4 },
  constBuffRow: { flexDirection: 'row', alignItems: 'center', gap: 6, flexWrap: 'wrap' },
  constBuffLabel: { color: '#888', fontSize: 9 },
  constBuffVal: { fontSize: 9, fontWeight: '800' },
  constSkillRow: {},
  constSkillLabel: { color: '#ffd700', fontSize: 10, fontWeight: '700' },
  constSkillDesc: { color: '#888', fontSize: 8, marginTop: 1 },
  constActions: { flexDirection: 'row', gap: 8, marginTop: 4 },
  equipBtn: { paddingVertical: 5, paddingHorizontal: 12, borderRadius: 6, borderWidth: 1 },
  equipTxt: { fontSize: 10, fontWeight: '800' },
  constLocked: { color: '#555', fontSize: 9, marginTop: 4, marginLeft: 50 },
});
