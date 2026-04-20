import React, { useEffect, useState } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Dimensions, ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { useAuth } from '../../context/AuthContext';
import { apiCall } from '../../utils/api';
import { registerForPushNotifications } from '../../utils/pushNotifications';
import ResourceBadge from '../../components/ui/ResourceBadge';
import HomeHeroSplash from '../../components/home/HomeHeroSplash';
import { COLORS } from '../../constants/theme';
import Animated, { FadeInDown } from 'react-native-reanimated';

const { width: W, height: H } = Dimensions.get('window');

const LEFT_MODES = [
  { id: 'story', label: 'Storia', sub: 'Campagna', icon: '\uD83D\uDCD6', gradient: ['#FF6644', '#CC3322'] as const, route: '/story' },
  { id: 'tower', label: 'Torre', sub: 'Infinita', icon: '\uD83C\uDFF0', gradient: ['#AA44FF', '#7722CC'] as const, route: '/tower' },
  { id: 'arena', label: 'Arena', sub: 'PvP', icon: '\uD83C\uDFC6', gradient: ['#FFD700', '#CC9900'] as const, route: '/pvp' },
  { id: 'raid', label: 'Raid', sub: 'Co-op Boss', icon: '\uD83D\uDC32', gradient: ['#FF4444', '#CC2222'] as const, route: '/raid' },
];
const RIGHT_MODES = [
  { id: 'events', label: 'Eventi', sub: 'Giornalieri', icon: '\uD83C\uDF89', gradient: ['#44AAFF', '#2288CC'] as const, route: '/events' },
  { id: 'collection', label: 'Collezione', sub: 'Tutti gli Eroi', icon: '\uD83D\uDCDA', gradient: ['#FF88DD', '#CC4499'] as const, route: '/hero-collection' },
  { id: 'equip', label: 'Equip', sub: 'Equipaggia', icon: '\uD83D\uDDE1\uFE0F', gradient: ['#44CC88', '#229966'] as const, route: '/equipment' },
  { id: 'exclusive', label: 'Esclusivi', sub: 'Armi Uniche', icon: '\uD83D\uDC51', gradient: ['#FFD700', '#DD9900'] as const, route: '/exclusive' },
  { id: 'cosmetics', label: 'Aure', sub: 'Cosmetici', icon: '\u2728', gradient: ['#BB55FF', '#8833CC'] as const, route: '/cosmetics' },
];

export default function HomeTab() {
  const { user, logout, refreshUser } = useAuth();
  const router = useRouter();
  const [homeHero, setHomeHero] = useState<any>(null);
  const [homeSource, setHomeSource] = useState<string>('');
  const [inTutorial, setInTutorial] = useState<boolean>(true);
  const [heroCount, setHeroCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);
  useEffect(() => { registerForPushNotifications().catch(() => {}); }, []);

  const loadData = async () => {
    try {
      const [hh, uh] = await Promise.all([
        apiCall('/api/sanctuary/home-hero').catch(() => null),
        apiCall('/api/user/heroes').catch(() => []),
      ]);
      if (hh?.hero) {
        setHomeHero(hh.hero);
        setHomeSource(hh.source || '');
        setInTutorial(!!hh.in_tutorial);
      }
      setHeroCount(Array.isArray(uh) ? uh.length : 0);
      await refreshUser();
    } catch (e) {} finally { setLoading(false); }
  };

  if (loading) return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', COLORS.bgPrimary]} style={s.container}>
      <ActivityIndicator size="large" color={COLORS.accent} />
    </LinearGradient>
  );

  return (
    <LinearGradient
      colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']}
      style={s.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
    >
      {/* Top Bar */}
      <LinearGradient
        colors={[COLORS.gradientHeader[0], COLORS.gradientHeader[1]]}
        style={s.topBar}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
      >
        <View style={s.userBadge}>
          <LinearGradient
            colors={[COLORS.accent, '#FF4444']}
            style={s.avatarCircle}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          >
            <Text style={s.avatarText}>{user?.username?.[0]?.toUpperCase() || 'G'}</Text>
          </LinearGradient>
          <View>
            <Text style={s.username}>{user?.username || 'Giocatore'}</Text>
            <Text style={s.userLvl}>Lv.{user?.level || 1} {'\u2022'} {user?.active_title || 'Novizio'}</Text>
          </View>
        </View>
        <View style={s.resources}>
          <ResourceBadge icon={'\uD83D\uDCB0'} value={user?.gold || 0} compact />
          <ResourceBadge icon={'\uD83D\uDC8E'} value={user?.gems || 0} compact />
          <ResourceBadge icon={'\u26A1'} value={`${user?.stamina || 0}/${user?.max_stamina || 100}`} compact />
        </View>
        <TouchableOpacity style={s.logoutBtn} onPress={logout}>
          <Text style={s.logoutTxt}>Esci</Text>
        </TouchableOpacity>
      </LinearGradient>

      {/* Body */}
      <View style={s.body}>
        {/* Left Modes */}
        <ScrollView
          style={s.sideCol}
          contentContainerStyle={s.sideColContent}
          showsVerticalScrollIndicator={false}
          nestedScrollEnabled
        >
          {LEFT_MODES.map((m, i) => (
            <Animated.View key={m.id} entering={FadeInDown.delay(i * 60).duration(300)}>
              <TouchableOpacity
                style={s.modeBtn}
                onPress={() => router.push(m.route as any)}
                activeOpacity={0.7}
              >
                <LinearGradient
                  colors={[m.gradient[0] + '20', m.gradient[1] + '08']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={s.modeBtnInner}
                >
                  <View style={[s.modeBtnIconWrap, { backgroundColor: m.gradient[0] + '25' }]}>
                    <Text style={s.modeBtnIcon}>{m.icon}</Text>
                  </View>
                  <View style={s.modeBtnText}>
                    <Text style={[s.modeBtnTitle, { color: m.gradient[0] }]}>{m.label}</Text>
                    <Text style={s.modeBtnSub}>{m.sub}</Text>
                  </View>
                  <Text style={[s.modeBtnArrow, { color: m.gradient[0] }]}>{'\u203A'}</Text>
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>
          ))}
        </ScrollView>

        {/* Center Hero Splash — ANIMATO (respiro + blink) */}
        <View style={s.centerCol}>
          <HomeHeroSplash
            hero={homeHero}
            source={homeSource}
            inTutorial={inTutorial}
            width={Math.min(W * 0.48, 260)}
            height={Math.min(H * 0.55, 380)}
            onPress={() => {
              if (homeHero?.id) {
                router.push({ pathname: '/sanctuary', params: { heroId: homeHero.id } } as any);
              }
            }}
          />
          <View style={s.collBadge}>
            <Text style={s.collText}>{heroCount} eroi nella collezione</Text>
          </View>
          {/* COMBATTI button */}
          <TouchableOpacity
            onPress={() => router.push('/combat' as any)}
            activeOpacity={0.7}
            style={s.fightBtnWrap}
          >
            <LinearGradient
              colors={[COLORS.accent, '#FF4444']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={s.fightBtn}
            >
              <Text style={s.fightBtnIcon}>{'\u2694\uFE0F'}</Text>
              <Text style={s.fightBtnText}>COMBATTI!</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>

        {/* Right Modes */}
        <ScrollView
          style={s.sideCol}
          contentContainerStyle={s.sideColContent}
          showsVerticalScrollIndicator={false}
          nestedScrollEnabled
        >
          {RIGHT_MODES.map((m, i) => (
            <Animated.View key={m.id} entering={FadeInDown.delay(i * 60 + 100).duration(300)}>
              <TouchableOpacity
                style={s.modeBtn}
                onPress={() => router.push(m.route as any)}
                activeOpacity={0.7}
              >
                <LinearGradient
                  colors={[m.gradient[0] + '20', m.gradient[1] + '08']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                  style={s.modeBtnInner}
                >
                  <View style={[s.modeBtnIconWrap, { backgroundColor: m.gradient[0] + '25' }]}>
                    <Text style={s.modeBtnIcon}>{m.icon}</Text>
                  </View>
                  <View style={s.modeBtnText}>
                    <Text style={[s.modeBtnTitle, { color: m.gradient[0] }]}>{m.label}</Text>
                    <Text style={s.modeBtnSub}>{m.sub}</Text>
                  </View>
                  <Text style={[s.modeBtnArrow, { color: m.gradient[0] }]}>{'\u203A'}</Text>
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>
          ))}
        </ScrollView>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },
  // Top Bar
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,107,53,0.15)',
  },
  userBadge: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  avatarCircle: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { color: '#fff', fontSize: 15, fontWeight: '900' },
  username: { color: '#fff', fontSize: 13, fontWeight: '800' },
  userLvl: { color: COLORS.textMuted, fontSize: 9, marginTop: 1 },
  resources: { flex: 1, flexDirection: 'row', justifyContent: 'center', gap: 8 },
  logoutBtn: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 8,
    backgroundColor: 'rgba(255,68,68,0.1)',
    borderWidth: 1,
    borderColor: 'rgba(255,68,68,0.25)',
  },
  logoutTxt: { color: COLORS.error, fontSize: 10, fontWeight: '700' },
  // Body
  body: { flex: 1, flexDirection: 'row', paddingHorizontal: 8, paddingVertical: 6 },
  sideCol: { width: 140 },
  sideColContent: { gap: 6, justifyContent: 'center', flexGrow: 1 },
  modeBtn: {
    borderRadius: 12,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    minHeight: 48,
  },
  modeBtnInner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 10,
    paddingHorizontal: 10,
  },
  modeBtnIconWrap: {
    width: 30,
    height: 30,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modeBtnIcon: { fontSize: 16 },
  modeBtnText: { flex: 1 },
  modeBtnTitle: { fontSize: 11, fontWeight: '900', letterSpacing: 0.5 },
  modeBtnSub: { fontSize: 8, color: COLORS.textDim, marginTop: 1 },
  modeBtnArrow: { fontSize: 18, fontWeight: '700' },
  // Center
  centerCol: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  heroGlowOuter: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
    borderWidth: 1.5,
  },
  heroGlowInner: {
    position: 'absolute',
    width: 160,
    height: 160,
    borderRadius: 80,
  },
  heroContainer: { marginBottom: 10 },
  heroFrame: {
    width: 130,
    height: 130,
    borderRadius: 16,
    borderWidth: 2.5,
    overflow: 'hidden',
    backgroundColor: '#1a1230',
  },
  heroImg: { width: '100%', height: '100%' },
  heroFrameGradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 40,
  },
  heroName: { fontSize: 18, fontWeight: '900', letterSpacing: 2, textAlign: 'center' },
  heroStars: { fontSize: 14, marginTop: 3, textAlign: 'center', color: COLORS.gold },
  heroClass: { color: COLORS.textMuted, fontSize: 10, marginTop: 2, letterSpacing: 1, textAlign: 'center' },
  collBadge: {
    marginTop: 10,
    paddingHorizontal: 14,
    paddingVertical: 4,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
  },
  collText: { color: COLORS.textDim, fontSize: 10, fontWeight: '600' },
  fightBtnWrap: {
    marginTop: 10,
    borderRadius: 14,
    overflow: 'hidden',
  },
  fightBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingHorizontal: 28,
    paddingVertical: 12,
    borderRadius: 14,
  },
  fightBtnIcon: { fontSize: 18 },
  fightBtnText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '900',
    letterSpacing: 2,
  },
});
