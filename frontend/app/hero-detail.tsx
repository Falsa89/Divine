import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Image, Dimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, useLocalSearchParams } from 'expo-router';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import ScreenHeader from '../components/ui/ScreenHeader';
import TabSelector from '../components/ui/TabSelector';
import GradientButton from '../components/ui/GradientButton';
import StarDisplay from '../components/ui/StarDisplay';
import TranscendenceStars from '../components/ui/TranscendenceStars';
import HeroIdleAnimation from '../components/ui/HeroIdleAnimation';
import { COLORS, RARITY, ELEMENTS, CLASSES } from '../constants/theme';

const STAT_LABELS: Record<string, string> = {
  hp: 'HP', speed: 'VEL', physical_damage: 'DMG FIS', magic_damage: 'DMG MAG',
  physical_defense: 'DEF FIS', magic_defense: 'DEF MAG', healing: 'CURE', healing_received: 'CURE RIC',
  damage_rate: 'DMG RATE', penetration: 'PEN', dodge: 'SCHIV', crit_chance: 'CRIT%',
  crit_damage: 'CRIT DMG', hit_rate: 'HIT%', combo_rate: 'COMBO%', block_rate: 'BLOCK%',
};

const TABS = [
  { key: 'stats', label: 'Stats', icon: '\u{1F4CA}' },
  { key: 'skills', label: 'Skill', icon: '\u2728' },
  { key: 'fusion', label: 'Fusione', icon: '\uD83D\uDD2E' },
  { key: 'equip', label: 'Equip', icon: '\uD83D\uDDE1\uFE0F' },
];

export default function HeroDetailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const { refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [fusionInfo, setFusionInfo] = useState<any>(null);
  const [equipInfo, setEquipInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('stats');
  const [acting, setActing] = useState(false);

  const heroId = params.id as string;

  useEffect(() => { if (heroId) load(); }, [heroId]);

  const load = async () => {
    try {
      const [detail, fusion, equip] = await Promise.all([
        apiCall(`/api/hero/full-detail/${heroId}`),
        apiCall(`/api/fusion/info/${heroId}`),
        apiCall(`/api/hero/equipment/${heroId}`),
      ]);
      setData(detail); setFusionInfo(fusion); setEquipInfo(equip);
    } catch (e) {} finally { setLoading(false); }
  };

  const doLevelUp = async () => {
    setActing(true);
    try {
      const r = await apiCall('/api/hero/gain-exp', {
        method: 'POST',
        body: JSON.stringify({ user_hero_id: heroId, exp_amount: 10000 }),
      });
      await refreshUser();
      await load();
      const leveled = r.leveled_up?.filter((h: any) => h.hero_name === data?.name);
      if (leveled?.length > 0) {
        Alert.alert('Livello Aumentato!', `${leveled[0].hero_name}: Lv.${leveled[0].old_level} \u2192 Lv.${leveled[0].new_level}\nEXP: +${r.exp_gained}`);
      } else {
        Alert.alert('EXP Guadagnata!', `+${r.exp_gained} EXP`);
      }
    } catch (e: any) { Alert.alert('Errore', e.message); }
    finally { setActing(false); }
  };

  const doStarFusion = async () => {
    Alert.alert(
      'Fusione Stelle',
      `Vuoi fondere ${data?.name} da ${fusionInfo?.current_stars}\u2B50 a ${fusionInfo?.target_stars}\u2B50?`,
      [
        { text: 'Annulla' },
        {
          text: 'FUSIONE!', style: 'default', onPress: async () => {
            setActing(true);
            try {
              const r = await apiCall('/api/fusion/star-up', {
                method: 'POST',
                body: JSON.stringify({ user_hero_id: heroId }),
              });
              await refreshUser();
              await load();
              Alert.alert('Fusione Riuscita!', `${r.hero_name}: ${r.old_stars}\u2B50 \u2192 ${r.new_stars}\u2B50\nNuova Potenza: ${r.new_power?.toLocaleString()}`);
            } catch (e: any) { Alert.alert('Errore Fusione', e.message); }
            finally { setActing(false); }
          }
        },
      ]
    );
  };

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.c}>
      <ActivityIndicator size="large" color={COLORS.gold} />
    </LinearGradient>
  );
  if (!data) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.c}>
      <Text style={s.err}>Eroe non trovato</Text>
    </LinearGradient>
  );

  const col = ELEMENTS.colors[data.element] || '#888';
  const rarCol = RARITY.colors[Math.min(data.stars || 1, 6)] || '#888';
  const stars = Math.min(data.stars, 15);
  const starText = stars <= 6 ? '\u2B50'.repeat(stars) : `${stars}\u2B50`;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={s.c}>
      <ScreenHeader
        title={data.name}
        titleColor={col}
        showBack
        rightContent={
          <View style={s.powerBadge}>
            <Text style={s.powerIcon}>{'\u26A1'}</Text>
            <Text style={s.powerVal}>{data.power?.toLocaleString()}</Text>
          </View>
        }
      />

      <ScrollView contentContainerStyle={s.body}>
        {/* Hero Header Card */}
        <Animated.View entering={FadeIn}>
          <LinearGradient
            colors={[col + '12', 'rgba(10,10,40,0.6)']}
            style={[s.heroCard, { borderColor: col + '40' }]}
          >
            <View style={s.heroTop}>
              <TouchableOpacity onPress={() => router.push({ pathname: '/hero-viewer', params: { heroId: params.id as string } })} activeOpacity={0.8}>
                {data.image ? (
                  <HeroIdleAnimation stars={stars} size={80} color={col}>
                    <View style={[s.heroImgWrap, { borderColor: rarCol }]}>
                      <Image source={{ uri: data.image }} style={s.heroImg} />
                      <LinearGradient colors={['transparent', col + '30']} style={s.heroImgGrad} />
                    </View>
                  </HeroIdleAnimation>
                ) : (
                  <HeroIdleAnimation stars={stars} size={80} color={col}>
                    <View style={[s.heroImgPh, { backgroundColor: col + '15', borderColor: rarCol }]}>
                      <Text style={[s.heroImgInit, { color: col }]}>{data.name?.[0]}</Text>
                    </View>
                  </HeroIdleAnimation>
                )}
              </TouchableOpacity>
              <View style={s.heroInfo}>
                <Text style={[s.heroName, { color: rarCol }]}>{data.name}</Text>
                <View style={s.heroStars}>
                  {stars <= 12 ? <StarDisplay stars={stars} size={12} /> : <TranscendenceStars stars={stars} size={12} />}
                </View>
                <Text style={s.heroMeta}>
                  {ELEMENTS.icons[data.element] || ''} {data.element} {'\u2022'} {CLASSES.icons[data.hero_class] || ''} {data.hero_class} {'\u2022'} Lv.{data.level}/{data.level_cap}
                </Text>
                {data.is_reincarnated && (
                  <View style={s.reincBadge}>
                    <Text style={s.reincText}>{'\uD83D\uDCAB'} REINCARNATO x{data.reincarnation_count}</Text>
                  </View>
                )}
                {/* EXP bar */}
                <View style={s.expBarBg}>
                  <LinearGradient
                    colors={[col, col + 'AA']}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={[s.expFill, { width: `${(data.exp_progress || 0) * 100}%` }]}
                  />
                </View>
                <Text style={s.expTxt}>EXP: {data.experience}/{data.exp_to_next}</Text>
                {/* Level Up Button */}
                <TouchableOpacity
                  onPress={doLevelUp}
                  disabled={acting}
                  activeOpacity={0.7}
                  style={s.levelUpBtnWrap}
                >
                  <LinearGradient
                    colors={[COLORS.success + 'DD', COLORS.success + '99']}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={s.levelUpBtn}
                  >
                    <Text style={s.levelUpTxt}>{acting ? '...' : '\u2B06 LIVELLA'}</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            </View>
          </LinearGradient>
        </Animated.View>

        {/* Tab selector */}
        <TabSelector tabs={TABS} active={tab} onChange={setTab} accentColor={col} />

        {/* STATS TAB */}
        {tab === 'stats' && data.effective_stats && (
          <Animated.View entering={FadeIn} style={s.statsGrid}>
            {Object.entries(data.effective_stats).map(([stat, val]: [string, any], i) => (
              <Animated.View key={stat} entering={FadeInDown.delay(i * 15)}>
                <LinearGradient
                  colors={['rgba(255,255,255,0.03)', 'rgba(255,255,255,0.01)']}
                  style={s.statRow}
                >
                  <Text style={s.statLabel}>{STAT_LABELS[stat] || stat}</Text>
                  <Text style={[s.statVal, { color: col }]}>
                    {typeof val === 'number' && val < 1 && val > 0 ? `${(val * 100).toFixed(1)}%` : typeof val === 'number' ? val.toLocaleString() : String(val)}
                  </Text>
                </LinearGradient>
              </Animated.View>
            ))}
          </Animated.View>
        )}

        {/* SKILLS TAB */}
        {tab === 'skills' && data.skills && (
          <Animated.View entering={FadeIn} style={s.skillsWrap}>
            {Object.entries(data.skills).map(([key, skill]: [string, any]) => {
              if (!skill) return (
                <View key={key} style={[s.skillCard, s.skillLocked]}>
                  <Text style={s.skillLockedTxt}>{'\uD83D\uDD12'} {key.replace('_', ' ').toUpperCase()} - Bloccata</Text>
                </View>
              );
              const skillCol = skill.type === 'ultimate' ? COLORS.gold : skill.type === 'passive' ? COLORS.success : col;
              return (
                <Animated.View key={key} entering={FadeInDown}>
                  <LinearGradient
                    colors={[skillCol + '10', 'transparent']}
                    style={[s.skillCard, { borderColor: skillCol + '30' }]}
                  >
                    <View style={s.skillTop}>
                      <View style={[s.skillIconWrap, { backgroundColor: skillCol + '20' }]}>
                        <Text style={s.skillIconTxt}>{skill.icon || '\u2728'}</Text>
                      </View>
                      <View style={s.skillInfo}>
                        <Text style={[s.skillName, { color: skillCol }]}>{skill.name}</Text>
                        <Text style={s.skillType}>
                          {skill.type === 'ultimate' ? '\uD83D\uDC51 ULTIMATE' : skill.type === 'passive' ? '\uD83D\uDEE1\uFE0F PASSIVA' : '\u2694\uFE0F ATTIVA'}
                          {skill.enhanced && ' \u2B50 POTENZIATA'}
                        </Text>
                      </View>
                      {skill.damage_mult > 0 && (
                        <View style={[s.multBadge, { backgroundColor: skillCol + '15' }]}>
                          <Text style={[s.skillMult, { color: skillCol }]}>{skill.damage_mult}x</Text>
                        </View>
                      )}
                    </View>
                    <Text style={s.skillDesc}>{skill.description}</Text>
                    {skill.effect && typeof skill.effect === 'object' && (
                      <View style={s.skillEffects}>
                        {Object.entries(skill.effect).map(([ek, ev]) => (
                          <View key={ek} style={[s.effectBadge, { backgroundColor: COLORS.success + '10' }]}>
                            <Text style={s.skillEffect}>+{typeof ev === 'number' && ev < 1 ? `${(ev as number * 100).toFixed(0)}%` : String(ev)} {ek}</Text>
                          </View>
                        ))}
                      </View>
                    )}
                  </LinearGradient>
                </Animated.View>
              );
            })}
            {data.skills.star_bonus && (
              <LinearGradient
                colors={['rgba(255,215,0,0.08)', 'rgba(255,215,0,0.02)']}
                style={[s.skillCard, { borderColor: COLORS.gold + '40' }]}
              >
                <Text style={s.transcTitle}>{'\uD83D\uDC51'} {data.skills.star_bonus.name}</Text>
                <Text style={s.transcDesc}>{data.skills.star_bonus.description}</Text>
              </LinearGradient>
            )}
          </Animated.View>
        )}

        {/* FUSION TAB */}
        {tab === 'fusion' && fusionInfo && (
          <Animated.View entering={FadeIn} style={s.fusionWrap}>
            <View style={s.fusionHeader}>
              <Text style={s.fusionTitle}>
                Fusione Stelle: {fusionInfo.current_stars}\u2B50 {'\u2192'} {fusionInfo.target_stars}\u2B50
              </Text>
              <Text style={s.fusionMax}>Max raggiungibile: {fusionInfo.max_stars}\u2B50 (base {fusionInfo.base_rarity}\u2B50)</Text>
            </View>
            {fusionInfo.reason && !fusionInfo.requirements && (
              <View style={s.fusionDoneBadge}>
                <Text style={s.fusionDone}>{fusionInfo.reason}</Text>
              </View>
            )}
            {fusionInfo.requirements?.map((req: any, i: number) => (
              <View key={i} style={[s.reqRow, { borderLeftColor: req.met ? COLORS.success : COLORS.error }]}>
                <Text style={s.reqIcon}>{req.met ? '\u2705' : '\u274C'}</Text>
                <Text style={s.reqName}>{req.icon} {req.name}</Text>
                <Text style={[s.reqVal, { color: req.met ? COLORS.success : COLORS.error }]}>
                  {typeof req.have === 'number' && req.have > 999 ? `${(req.have / 1000).toFixed(0)}K` : req.have}/
                  {typeof req.needed === 'number' && req.needed > 999 ? `${(req.needed / 1000).toFixed(0)}K` : req.needed}
                </Text>
              </View>
            ))}
            {fusionInfo.can_fuse && (
              <GradientButton title={'\u2B50 FUSIONE STELLE'} onPress={doStarFusion} variant="gold" size="lg" loading={acting} />
            )}
          </Animated.View>
        )}

        {/* EQUIP TAB */}
        {tab === 'equip' && equipInfo && (
          <Animated.View entering={FadeIn} style={s.equipWrap}>
            <Text style={s.equipTitle}>Equipaggiamento di {equipInfo.hero_name}</Text>
            {equipInfo.equipment?.length > 0 ? equipInfo.equipment.map((eq: any) => (
              <LinearGradient
                key={eq.id}
                colors={['rgba(255,255,255,0.04)', 'rgba(255,255,255,0.01)']}
                style={s.eqCard}
              >
                <Text style={s.eqName}>{eq.name} (Lv.{eq.level})</Text>
                <Text style={s.eqStats}>{Object.entries(eq.stats || {}).map(([k, v]) => `${STAT_LABELS[k] || k}: ${v}`).join(' | ')}</Text>
              </LinearGradient>
            )) : <Text style={s.eqEmpty}>Nessun equipaggiamento</Text>}

            <View style={s.runeSection}>
              <Text style={s.runeTitle}>{'\uD83D\uDCA5'} Slot Rune</Text>
              {[1, 2].map(slot => {
                const rs = slot === 1 ? equipInfo.rune_slot_1 : equipInfo.rune_slot_2;
                return (
                  <LinearGradient
                    key={slot}
                    colors={rs?.unlocked ? ['rgba(255,215,0,0.05)', 'rgba(255,215,0,0.01)'] : ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.01)']}
                    style={[s.runeSlot, !rs?.unlocked && { opacity: 0.4 }]}
                  >
                    <Text style={s.runeSlotLabel}>Slot {slot}: {rs?.unlocked ? '\uD83D\uDD13' : '\uD83D\uDD12'} {rs?.requirement?.description}</Text>
                    {rs?.rune ? (
                      <View style={s.runeDetail}>
                        <Text style={s.runeName}>{rs.rune.icon} {rs.rune.name} ({rs.rune.rarity}\u2B50 Lv.{rs.rune.level})</Text>
                        <Text style={s.runeStats}>Main: {Object.entries(rs.rune.main_stat || {}).map(([k, v]) => `${k}: ${v}`).join(', ')}</Text>
                      </View>
                    ) : <Text style={s.runeEmpty}>{rs?.unlocked ? 'Vuoto - Equipaggia una runa' : 'Bloccato'}</Text>}
                  </LinearGradient>
                );
              })}
            </View>

            {Object.keys(equipInfo.total_equipment_bonus || {}).length > 0 && (
              <LinearGradient
                colors={['rgba(68,221,136,0.06)', 'rgba(68,221,136,0.02)']}
                style={s.totalBonus}
              >
                <Text style={s.totalTitle}>{'\uD83D\uDCAA'} Bonus Totale Equipaggiamento</Text>
                {Object.entries(equipInfo.total_equipment_bonus).map(([stat, val]: [string, any]) => (
                  <Text key={stat} style={s.totalStat}>+{typeof val === 'number' && val < 1 ? `${(val * 100).toFixed(1)}%` : val} {STAT_LABELS[stat] || stat}</Text>
                ))}
              </LinearGradient>
            )}
          </Animated.View>
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c: { flex: 1 },
  err: { color: COLORS.error, textAlign: 'center', marginTop: 50, fontSize: 14 },
  powerBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: 'rgba(255,215,0,0.1)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,215,0,0.2)',
  },
  powerIcon: { fontSize: 12 },
  powerVal: { color: COLORS.gold, fontSize: 11, fontWeight: '800' },
  body: { padding: 8, gap: 8, paddingBottom: 70 },
  // Hero card
  heroCard: { padding: 12, borderRadius: 14, borderWidth: 1 },
  heroTop: { flexDirection: 'row', gap: 12 },
  heroImgWrap: { width: 75, height: 75, borderRadius: 12, borderWidth: 2, overflow: 'hidden' },
  heroImg: { width: '100%', height: '100%' },
  heroImgGrad: { position: 'absolute', bottom: 0, left: 0, right: 0, height: 30 },
  heroImgPh: { width: 75, height: 75, borderRadius: 12, borderWidth: 2, alignItems: 'center', justifyContent: 'center' },
  heroImgInit: { fontSize: 30, fontWeight: '900' },
  heroInfo: { flex: 1 },
  heroName: { fontSize: 16, fontWeight: '900' },
  heroStars: { fontSize: 10, color: COLORS.gold, marginTop: 2 },
  heroMeta: { color: COLORS.textSecondary, fontSize: 9, marginTop: 3 },
  reincBadge: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255,136,68,0.12)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    marginTop: 3,
  },
  reincText: { color: '#FF8844', fontSize: 9, fontWeight: '800' },
  expBarBg: { height: 5, backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 3, marginTop: 6, overflow: 'hidden' },
  expFill: { height: '100%', borderRadius: 3 },
  expTxt: { color: COLORS.textMuted, fontSize: 7, marginTop: 2 },
  levelUpBtnWrap: { alignSelf: 'flex-start', borderRadius: 8, overflow: 'hidden', marginTop: 4 },
  levelUpBtn: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 8 },
  levelUpTxt: { color: '#fff', fontSize: 10, fontWeight: '900', letterSpacing: 0.5 },
  // Stats
  statsGrid: { gap: 2 },
  statRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 5, paddingHorizontal: 10, borderRadius: 6 },
  statLabel: { color: COLORS.textSecondary, fontSize: 10, fontWeight: '600' },
  statVal: { fontSize: 10, fontWeight: '900' },
  // Skills
  skillsWrap: { gap: 5 },
  skillCard: { padding: 10, borderRadius: 10, borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)' },
  skillLocked: { opacity: 0.3 },
  skillLockedTxt: { color: COLORS.textDim, fontSize: 10 },
  skillTop: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  skillIconWrap: { width: 32, height: 32, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  skillIconTxt: { fontSize: 18 },
  skillInfo: { flex: 1 },
  skillName: { fontSize: 12, fontWeight: '900' },
  skillType: { color: COLORS.textMuted, fontSize: 8, marginTop: 1 },
  multBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  skillMult: { fontSize: 14, fontWeight: '900' },
  skillDesc: { color: COLORS.textSecondary, fontSize: 9, marginTop: 4 },
  skillEffects: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 4 },
  effectBadge: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  skillEffect: { color: COLORS.success, fontSize: 8, fontWeight: '700' },
  transcTitle: { color: COLORS.gold, fontSize: 12, fontWeight: '900' },
  transcDesc: { color: COLORS.textSecondary, fontSize: 9, marginTop: 3 },
  // Fusion
  fusionWrap: { gap: 6 },
  fusionHeader: { marginBottom: 4 },
  fusionTitle: { color: '#fff', fontSize: 14, fontWeight: '900' },
  fusionMax: { color: COLORS.textMuted, fontSize: 10, marginTop: 2 },
  fusionDoneBadge: {
    backgroundColor: 'rgba(68,221,136,0.08)',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(68,221,136,0.2)',
  },
  fusionDone: { color: COLORS.success, fontSize: 11, fontWeight: '700', textAlign: 'center' },
  reqRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    padding: 8,
    backgroundColor: 'rgba(255,255,255,0.02)',
    borderRadius: 6,
    borderLeftWidth: 3,
  },
  reqIcon: { fontSize: 14 },
  reqName: { flex: 1, color: COLORS.textSecondary, fontSize: 10 },
  reqVal: { fontSize: 10, fontWeight: '800' },
  // Equipment
  equipWrap: { gap: 5 },
  equipTitle: { color: '#fff', fontSize: 13, fontWeight: '800' },
  eqCard: {
    padding: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  eqName: { color: COLORS.textSecondary, fontSize: 10, fontWeight: '700' },
  eqStats: { color: COLORS.textMuted, fontSize: 8, marginTop: 2 },
  eqEmpty: { color: COLORS.textDim, fontSize: 10, textAlign: 'center', padding: 12 },
  runeSection: { marginTop: 8, gap: 4 },
  runeTitle: { color: COLORS.gold, fontSize: 12, fontWeight: '800' },
  runeSlot: {
    padding: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,215,0,0.15)',
  },
  runeSlotLabel: { color: COLORS.textSecondary, fontSize: 9, fontWeight: '700' },
  runeDetail: { marginTop: 4 },
  runeName: { color: COLORS.gold, fontSize: 10, fontWeight: '700' },
  runeStats: { color: COLORS.textMuted, fontSize: 8, marginTop: 1 },
  runeEmpty: { color: COLORS.textDim, fontSize: 9, marginTop: 3 },
  totalBonus: {
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(68,221,136,0.15)',
    marginTop: 6,
  },
  totalTitle: { color: COLORS.success, fontSize: 11, fontWeight: '800', marginBottom: 4 },
  totalStat: { color: COLORS.success, fontSize: 9, fontWeight: '600' },
});
