/**
 * HOME — REDESIGN MODULARE LANDSCAPE (Msg 428)
 * ================================================
 *
 * Struttura ispirata alla reference fantasy castle provided.
 *
 * BLOCCHI SEPARATI (non flatten):
 *   1. HomeBackground       — sfondo scenico (gradient + patterns, pronto per asset futuro)
 *   2. HomeProfilePanel     — top-left user info
 *   3. HomeCurrencyBar      — top-right gold/gem
 *   4. HomeTopActions       — wheel/quest/event/bonus
 *   5. HomeLeftUtilityStack — server time, SP offer, crystal packs
 *   6. HomeHeroLayer        — splash libero (solo immagine, tap = Sanctuary)
 *   7. HomeModePanel        — arena/blessing/trial
 *   8. HomeMainBanner       — battle/research tiles
 *   9. HomeBottomNav        — bag/artifact/skill/team/PLAY/guild/shop/forge/home/menu
 *  10. HomeOverflowPanel    — modal overflow per feature non ancora mappate
 *
 * REFRESH LIVE: uso `useFocusEffect` — ogni volta che la Home tab torna
 * in foreground (es. dopo router.back() da /select-home-hero) i dati si
 * ricaricano. Il cambio eroe homepage è IMMEDIATO senza restart app.
 */
import React, { useEffect, useState, useMemo, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Dimensions,
  ScrollView, Modal, Image as RNImage,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, useFocusEffect } from 'expo-router';
import { useAuth } from '../../context/AuthContext';
import { apiCall } from '../../utils/api';
import { registerForPushNotifications } from '../../utils/pushNotifications';
import HomeHeroSplash from '../../components/home/HomeHeroSplash';
import { COLORS } from '../../constants/theme';

const { width: W, height: H } = Dimensions.get('window');
const isLandscape = W > H;

export default function HomeTab() {
  const { user, refreshUser } = useAuth();
  const router = useRouter();
  const [homeHero, setHomeHero] = useState<any>(null);
  const [homeSource, setHomeSource] = useState<string>('');
  const [inTutorial, setInTutorial] = useState<boolean>(true);
  const [loading, setLoading] = useState(true);
  const [overflowOpen, setOverflowOpen] = useState(false);
  const [serverTime, setServerTime] = useState<string>('');

  const loadData = useCallback(async () => {
    try {
      const hh = await apiCall('/api/sanctuary/home-hero').catch(() => null);
      if (hh?.hero) {
        setHomeHero(hh.hero);
        setHomeSource(hh.source || '');
        setInTutorial(!!hh.in_tutorial);
      }
      await refreshUser();
    } finally { setLoading(false); }
  }, [refreshUser]);

  // FIX REFRESH LIVE: useFocusEffect garantisce refetch ogni volta che la
  // Home tab torna in foreground (es. dopo router.back() da select-home-hero).
  // Nessun restart app richiesto.
  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [loadData])
  );

  useEffect(() => { registerForPushNotifications().catch(() => {}); }, []);

  // Tick server time ogni 10s
  useEffect(() => {
    const fmt = () => {
      const d = new Date();
      setServerTime(d.toISOString().replace('T', ' ').slice(0, 19) + ' (UTC)');
    };
    fmt();
    const id = setInterval(fmt, 10000);
    return () => clearInterval(id);
  }, []);

  const onHeroTap = () => {
    if (homeHero?.id) {
      router.push({ pathname: '/sanctuary', params: { heroId: homeHero.id } } as any);
    }
  };

  if (loading) {
    return (
      <LinearGradient colors={['#0D0820', '#0A0612']} style={s.container}>
        <ActivityIndicator size="large" color={COLORS.accent} />
      </LinearGradient>
    );
  }

  return (
    <View style={s.container}>
      {/* BLOCCO 1 — BACKGROUND */}
      <HomeBackground />

      {/* BLOCCO 6 — HERO LAYER (sopra background, dietro UI) */}
      <View style={s.heroLayer} pointerEvents="box-none">
        <HomeHeroSplash
          hero={homeHero}
          source={homeSource}
          inTutorial={inTutorial}
          width={Math.min(W * 0.55, 380)}
          height={Math.min(H * 0.75, 560)}
          onPress={onHeroTap}
        />
      </View>

      {/* BLOCCO 2 — TOP LEFT PROFILE */}
      <HomeProfilePanel user={user} onPress={() => router.push('/profile' as any)} />

      {/* BLOCCO 3 — TOP RIGHT CURRENCY */}
      <HomeCurrencyBar user={user} onAddGems={() => router.push('/shop' as any)} />

      {/* BLOCCO 4 — TOP ACTIONS (sotto currency) */}
      <HomeTopActions router={router} onOverflow={() => setOverflowOpen(true)} />

      {/* BLOCCO 5 — LEFT UTILITY STACK */}
      <HomeLeftUtilityStack
        serverTime={serverTime}
        onSpOffer={() => setOverflowOpen(true)}
        router={router}
      />

      {/* BLOCCO 7 — RIGHT MODE PANEL */}
      <HomeModePanel router={router} onOverflow={() => setOverflowOpen(true)} />

      {/* BLOCCO 8 — MAIN BANNER (battle + research tiles) */}
      <HomeMainBanner router={router} onOverflow={() => setOverflowOpen(true)} />

      {/* NOTE: la Bottom Nav custom (10 slot stile reference) è stata
         temporaneamente sostituita dalla tab bar nativa di expo-router
         (HOME / EROI / BATTAGLIA / EVOCA / MENU). In un futuro step
         la tab bar verrà nascosta e HomeBottomNav riattivata con 10 slot. */}

      {/* BLOCCO 10 — OVERFLOW PANEL (Modal) */}
      <HomeOverflowPanel
        open={overflowOpen}
        onClose={() => setOverflowOpen(false)}
        router={router}
      />
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 1 — HomeBackground
 * ═══════════════════════════════════════════════════════════════════ */
function HomeBackground() {
  return (
    <View style={StyleSheet.absoluteFill}>
      <LinearGradient
        colors={['#1e3a7a', '#3a5bbf', '#7ba6e0', '#c9b993', '#8b6f3c']}
        style={StyleSheet.absoluteFill}
        start={{ x: 0.5, y: 0 }}
        end={{ x: 0.5, y: 1 }}
        locations={[0, 0.3, 0.55, 0.78, 1]}
      />
      {/* Overlay sottile per vignettatura */}
      <LinearGradient
        colors={['transparent', 'rgba(10,6,30,0.25)']}
        style={StyleSheet.absoluteFill}
      />
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 2 — HomeProfilePanel
 * ═══════════════════════════════════════════════════════════════════ */
function HomeProfilePanel({ user, onPress }: any) {
  const name = user?.nickname || user?.name || 'Player';
  const power = user?.power || user?.total_power || 0;
  const level = user?.level || 1;
  const exp = user?.exp || 0;
  const expMax = user?.exp_to_next || 1000;
  const vip = user?.vip_level || 0;
  const spirito = user?.spirito || user?.spirit || 0;
  return (
    <TouchableOpacity style={s.profileWrap} onPress={onPress} activeOpacity={0.85}>
      <View style={s.profileAvatar}>
        <Text style={s.profileInitial}>{String(name)[0]?.toUpperCase() || 'P'}</Text>
        <View style={s.profileLvBadge}>
          <Text style={s.profileLvTxt}>{level}</Text>
        </View>
      </View>
      <View style={s.profileBody}>
        <Text style={s.profileName} numberOfLines={1}>{name}</Text>
        <Text style={s.profilePower}>Power {Number(power).toLocaleString()}</Text>
        <View style={s.expBarBg}>
          <View style={[s.expBarFill, { width: `${Math.min(100, (exp / expMax) * 100)}%` }]} />
        </View>
        <View style={s.profileRow}>
          <View style={s.vipPill}>
            <Text style={s.vipTxt}>VIP {vip}</Text>
          </View>
          {spirito > 0 && (
            <View style={s.spiritoPill}>
              <Text style={s.spiritoIco}>{'\uD83D\uDD2E'}</Text>
              <Text style={s.spiritoTxt}>SPIRITO {spirito}</Text>
            </View>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 3 — HomeCurrencyBar
 * ═══════════════════════════════════════════════════════════════════ */
function HomeCurrencyBar({ user, onAddGems }: any) {
  const gold = user?.gold || 0;
  const gems = user?.diamonds || user?.gems || 0;
  return (
    <View style={s.currencyWrap}>
      <View style={s.currencyPill}>
        <Text style={s.currencyIco}>{'\uD83D\uDCB0'}</Text>
        <Text style={s.currencyTxt}>{Number(gold).toLocaleString()}</Text>
        <TouchableOpacity style={s.plusBtn} onPress={onAddGems}>
          <Text style={s.plusTxt}>+</Text>
        </TouchableOpacity>
      </View>
      <View style={s.currencyPill}>
        <Text style={s.currencyIco}>{'\uD83D\uDC8E'}</Text>
        <Text style={s.currencyTxt}>{Number(gems).toLocaleString()}</Text>
        <TouchableOpacity style={s.plusBtn} onPress={onAddGems}>
          <Text style={s.plusTxt}>+</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 4 — HomeTopActions (wheel/quest/event/bonus)
 * ═══════════════════════════════════════════════════════════════════ */
function HomeTopActions({ router, onOverflow }: any) {
  const items = [
    { key: 'wheel', icon: '\uD83C\uDFAF', label: 'WHEEL', onPress: () => router.push('/(tabs)/gacha' as any) },
    { key: 'quest', icon: '\uD83D\uDCDC', label: 'QUEST', onPress: onOverflow },
    { key: 'event', icon: '\uD83C\uDF81', label: 'EVENT', onPress: () => router.push('/events' as any) },
    { key: 'bonus', icon: '\uD83D\uDCBC', label: 'BONUS', onPress: onOverflow },
  ];
  return (
    <View style={s.topActionsRow}>
      {items.map(it => (
        <TouchableOpacity key={it.key} style={s.topActBtn} activeOpacity={0.75} onPress={it.onPress}>
          <View style={s.topActIconBox}>
            <Text style={s.topActIco}>{it.icon}</Text>
          </View>
          <Text style={s.topActLabel}>{it.label}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 5 — HomeLeftUtilityStack (server time + SP Offer + crystals)
 * ═══════════════════════════════════════════════════════════════════ */
function HomeLeftUtilityStack({ serverTime, onSpOffer, router }: any) {
  return (
    <View style={s.leftStack}>
      <View style={s.serverTimeBox}>
        <Text style={s.serverLabel}>SERVER TIME</Text>
        <Text style={s.serverValue}>{serverTime}</Text>
      </View>
      <TouchableOpacity style={s.spOfferBtn} onPress={onSpOffer} activeOpacity={0.8}>
        <LinearGradient
          colors={['#B22222', '#7A1010']}
          start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}
          style={s.spOfferGrad}
        >
          <Text style={s.spOfferTxt}>SP OFFER</Text>
        </LinearGradient>
      </TouchableOpacity>
      <View style={s.crystalRow}>
        {[{ c: 2, g: 100 }, { c: 3, g: 150 }].map((x, i) => (
          <TouchableOpacity key={i} style={s.crystalPack} onPress={() => router.push('/shop' as any)}>
            <Text style={s.crystalNum}>{x.c}</Text>
            <Text style={s.crystalIco}>{'\uD83D\uDC8E'}</Text>
            <Text style={s.crystalPrice}>{x.g}{'\uD83D\uDC8E'}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 7 — HomeModePanel (Arena / Blessing / Trial)
 * ═══════════════════════════════════════════════════════════════════ */
function HomeModePanel({ router, onOverflow }: any) {
  const modes = [
    { key: 'arena',    label: 'ARENA',    ico: '\u2694\uFE0F', onPress: () => router.push('/arena' as any) },
    { key: 'blessing', label: 'BLESSING', ico: '\uD83D\uDCFF', onPress: onOverflow },
    { key: 'trial',    label: 'TRIAL',    ico: '\u26AA',       onPress: () => router.push('/story' as any) },
  ];
  return (
    <View style={s.modePanel}>
      {modes.map(m => (
        <TouchableOpacity key={m.key} style={s.modeTile} onPress={m.onPress} activeOpacity={0.8}>
          <LinearGradient
            colors={['rgba(255,255,255,0.10)', 'rgba(0,0,0,0.35)']}
            style={s.modeTileInner}
          >
            <Text style={s.modeIco}>{m.ico}</Text>
            <Text style={s.modeLabel}>{m.label}</Text>
          </LinearGradient>
        </TouchableOpacity>
      ))}
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 8 — HomeMainBanner (Battle + Research tiles)
 * ═══════════════════════════════════════════════════════════════════ */
function HomeMainBanner({ router, onOverflow }: any) {
  return (
    <View style={s.mainBanner}>
      <TouchableOpacity style={s.bannerTile} onPress={() => router.push('/combat' as any)} activeOpacity={0.85}>
        <LinearGradient
          colors={['rgba(100,20,40,0.75)', 'rgba(20,10,20,0.85)']}
          style={s.bannerTileInner}
        >
          <Text style={s.bannerIco}>{'\u2694\uFE0F'}</Text>
          <Text style={s.bannerLabel}>BATTLE</Text>
        </LinearGradient>
      </TouchableOpacity>
      <TouchableOpacity style={s.bannerTile} onPress={onOverflow} activeOpacity={0.85}>
        <LinearGradient
          colors={['rgba(40,40,90,0.75)', 'rgba(15,15,30,0.85)']}
          style={s.bannerTileInner}
        >
          <Text style={s.bannerIco}>{'\uD83D\uDD2C'}</Text>
          <Text style={s.bannerLabel}>RESEARCH</Text>
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 9 — HomeBottomNav (10 slot)
 * ═══════════════════════════════════════════════════════════════════ */
function HomeBottomNav({ router, onMenu }: any) {
  const ICON = (i: string) => <Text style={s.navIco}>{i}</Text>;
  const nav = [
    { key: 'bag',      label: 'BAG',      ico: ICON('\uD83C\uDF92'), onPress: onMenu },
    { key: 'artifact', label: 'ARTIFACT', ico: ICON('\uD83D\uDD2E'), onPress: () => router.push('/artifacts' as any) },
    { key: 'skill',    label: 'SKILL',    ico: ICON('\uD83D\uDCDA'), onPress: onMenu },
    { key: 'team',     label: 'TEAM',     ico: ICON('\uD83D\uDC65'), onPress: () => router.push('/hero-collection' as any) },
  ];
  const navRight = [
    { key: 'guild', label: 'GUILD', ico: ICON('\uD83D\uDEE1\uFE0F'), onPress: () => router.push('/guild' as any) },
    { key: 'shop',  label: 'SHOP',  ico: ICON('\uD83C\uDFEA'),       onPress: () => router.push('/shop' as any) },
    { key: 'forge', label: 'FORGE', ico: ICON('\u2692\uFE0F'),        onPress: onMenu },
    { key: 'menu',  label: 'MENU',  ico: ICON('\u2630'),              onPress: onMenu },
  ];
  return (
    <View style={s.bottomNav} pointerEvents="box-none">
      <View style={s.bottomNavSide}>
        {nav.map(n => (
          <TouchableOpacity key={n.key} style={s.navBtn} onPress={n.onPress} activeOpacity={0.7}>
            <View style={s.navIconWrap}>{n.ico}</View>
            <Text style={s.navLabel}>{n.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <TouchableOpacity
        style={s.playShield}
        onPress={() => router.push('/combat' as any)}
        activeOpacity={0.85}
      >
        <LinearGradient
          colors={['#B22222', '#7A0A1A', '#4A0510']}
          style={s.playShieldInner}
          start={{ x: 0, y: 0 }} end={{ x: 0, y: 1 }}
        >
          <Text style={s.playText}>PLAY</Text>
        </LinearGradient>
      </TouchableOpacity>
      <View style={s.bottomNavSide}>
        {navRight.map(n => (
          <TouchableOpacity key={n.key} style={s.navBtn} onPress={n.onPress} activeOpacity={0.7}>
            <View style={s.navIconWrap}>{n.ico}</View>
            <Text style={s.navLabel}>{n.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 10 — HomeOverflowPanel (Modal)
 * ═══════════════════════════════════════════════════════════════════ */
type OverflowItem = { key: string; label: string; icon: string; onPress: () => void; note?: string };

function HomeOverflowPanel({ open, onClose, router }: any) {
  // Feature NON ancora mappate nei bottoni principali → qui tutte accessibili.
  const items: OverflowItem[] = [
    { key: 'story',      label: 'Storia',           icon: '\uD83D\uDCDC', onPress: () => { onClose(); router.push('/story' as any); } },
    { key: 'tower',      label: 'Torre',            icon: '\uD83C\uDFEF', onPress: () => { onClose(); router.push('/tower' as any); } },
    { key: 'raid',       label: 'Raid',             icon: '\uD83D\uDD25', onPress: () => { onClose(); router.push('/raids' as any); } },
    { key: 'events',     label: 'Eventi',           icon: '\uD83C\uDF1F', onPress: () => { onClose(); router.push('/events' as any); } },
    { key: 'auras',      label: 'Aure',             icon: '\u2728',       onPress: () => { onClose(); router.push('/(tabs)/cosmetics' as any); } },
    { key: 'exclusive',  label: 'Esclusivi',        icon: '\uD83D\uDC51', onPress: () => { onClose(); router.push('/exclusive-items' as any); } },
    { key: 'equip',      label: 'Equipaggiamento',  icon: '\u2694\uFE0F', onPress: () => { onClose(); router.push('/equipment' as any); } },
    { key: 'battlepass', label: 'Battle Pass',      icon: '\uD83C\uDFC6', onPress: () => { onClose(); router.push('/battlepass' as any); } },
    { key: 'achievements', label: 'Achievements',   icon: '\uD83C\uDFC5', onPress: () => { onClose(); router.push('/achievements' as any); } },
    { key: 'mail',       label: 'Posta',            icon: '\u2709\uFE0F', onPress: () => { onClose(); router.push('/mail' as any); } },
    { key: 'friends',    label: 'Amici',            icon: '\uD83D\uDC65', onPress: () => { onClose(); router.push('/friends' as any); } },
    { key: 'quests',     label: 'Quest Giornaliere',icon: '\u2705',       onPress: () => { onClose(); router.push('/quests' as any); } },
    { key: 'bonus',      label: 'Bonus Giornalieri',icon: '\uD83C\uDF81', onPress: () => { onClose(); router.push('/bonus' as any); note: 'daily'; } },
    { key: 'blessing',   label: 'Benedizioni',      icon: '\uD83D\uDCFF', onPress: () => { onClose(); router.push('/blessings' as any); } },
    { key: 'research',   label: 'Ricerca',          icon: '\uD83D\uDD2C', onPress: () => { onClose(); router.push('/research' as any); } },
    { key: 'forge',      label: 'Fucina',           icon: '\u2692\uFE0F', onPress: () => { onClose(); router.push('/forge' as any); } },
    { key: 'bag',        label: 'Zaino',            icon: '\uD83C\uDF92', onPress: () => { onClose(); router.push('/bag' as any); } },
    { key: 'skills',     label: 'Abilità',          icon: '\uD83D\uDCDA', onPress: () => { onClose(); router.push('/skills' as any); } },
    { key: 'spoffer',    label: 'SP Offer',         icon: '\uD83D\uDCB3', onPress: () => { onClose(); router.push('/shop' as any); } },
    { key: 'collection', label: 'Collezione Eroi',  icon: '\uD83D\uDC65', onPress: () => { onClose(); router.push('/hero-collection' as any); } },
  ];

  return (
    <Modal visible={open} animationType="slide" transparent onRequestClose={onClose}>
      <View style={s.modalBackdrop}>
        <View style={s.modalCard}>
          <View style={s.modalHeader}>
            <Text style={s.modalTitle}>{'\u2630'}  Menu</Text>
            <TouchableOpacity onPress={onClose}><Text style={s.modalClose}>{'\u2715'}</Text></TouchableOpacity>
          </View>
          <Text style={s.modalSub}>
            Contenitore temporaneo con tutte le feature. Verranno riposizionate nei pulsanti principali negli aggiornamenti successivi.
          </Text>
          <ScrollView contentContainerStyle={s.modalGrid}>
            {items.map(it => (
              <TouchableOpacity key={it.key} style={s.modalItem} onPress={it.onPress} activeOpacity={0.75}>
                <Text style={s.modalItemIco}>{it.icon}</Text>
                <Text style={s.modalItemLabel}>{it.label}</Text>
              </TouchableOpacity>
            ))}
            <View style={{ height: 20 }} />
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  STYLES
 * ═══════════════════════════════════════════════════════════════════ */
const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0612' },

  /* HERO LAYER — centrato (leggermente a destra come reference), evita la tab bar */
  heroLayer: {
    position: 'absolute',
    top: 0, bottom: 80, left: 0, right: 0,
    alignItems: 'center', justifyContent: 'center',
    zIndex: 1,
  },

  /* BLOCCO 2 — PROFILE */
  profileWrap: {
    position: 'absolute', top: 12, left: 10,
    flexDirection: 'row', gap: 10, alignItems: 'flex-start',
    zIndex: 20,
  },
  profileAvatar: {
    width: 46, height: 46, borderRadius: 23,
    backgroundColor: '#2a2a4e',
    borderWidth: 2, borderColor: '#FFD700',
    alignItems: 'center', justifyContent: 'center',
  },
  profileInitial: { color: '#FFD700', fontSize: 18, fontWeight: '900' },
  profileLvBadge: {
    position: 'absolute', bottom: -4, right: -4,
    backgroundColor: '#1a1a2e', borderRadius: 10,
    borderWidth: 1, borderColor: '#FFD700',
    paddingHorizontal: 5, minWidth: 20, alignItems: 'center',
  },
  profileLvTxt: { color: '#FFD700', fontSize: 9, fontWeight: '900' },
  profileBody: { minWidth: 110, maxWidth: 200 },
  profileName: { color: '#FFD700', fontSize: 13, fontWeight: '900' },
  profilePower: { color: '#FFF', fontSize: 10, fontWeight: '700', marginTop: 1 },
  expBarBg: {
    height: 4, backgroundColor: 'rgba(255,255,255,0.18)',
    borderRadius: 2, overflow: 'hidden', marginTop: 4,
  },
  expBarFill: { height: '100%', backgroundColor: '#FFD700' },
  profileRow: { flexDirection: 'row', gap: 5, marginTop: 4 },
  vipPill: {
    backgroundColor: 'rgba(178,34,34,0.65)',
    paddingHorizontal: 6, paddingVertical: 1, borderRadius: 4,
    borderWidth: 1, borderColor: '#FFD700',
  },
  vipTxt: { color: '#FFD700', fontSize: 9, fontWeight: '900' },
  spiritoPill: {
    flexDirection: 'row', alignItems: 'center', gap: 3,
    backgroundColor: 'rgba(60,20,120,0.7)',
    paddingHorizontal: 5, paddingVertical: 1, borderRadius: 4,
    borderWidth: 1, borderColor: '#B05CFF',
  },
  spiritoIco: { fontSize: 9 },
  spiritoTxt: { color: '#FF6B6B', fontSize: 8, fontWeight: '900' },

  /* BLOCCO 3 — CURRENCY */
  currencyWrap: {
    position: 'absolute', top: 12, right: 10,
    flexDirection: 'row', gap: 6, zIndex: 20,
  },
  currencyPill: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    backgroundColor: 'rgba(20,20,40,0.80)',
    paddingHorizontal: 6, paddingVertical: 4, borderRadius: 14,
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.5)',
  },
  currencyIco: { fontSize: 12 },
  currencyTxt: { color: '#fff', fontSize: 10, fontWeight: '900' },
  plusBtn: {
    width: 18, height: 18, borderRadius: 9,
    backgroundColor: '#FFD700',
    alignItems: 'center', justifyContent: 'center',
  },
  plusTxt: { color: '#1a0e2e', fontSize: 12, fontWeight: '900' },

  /* BLOCCO 4 — TOP ACTIONS */
  topActionsRow: {
    position: 'absolute', top: 60, right: 10,
    flexDirection: 'row', gap: 6, zIndex: 19,
  },
  topActBtn: { alignItems: 'center', width: 42 },
  topActIconBox: {
    width: 34, height: 34, borderRadius: 17,
    backgroundColor: 'rgba(30,30,50,0.7)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.45)',
    alignItems: 'center', justifyContent: 'center',
  },
  topActIco: { fontSize: 16 },
  topActLabel: { color: '#fff', fontSize: 8, fontWeight: '800', marginTop: 2 },

  /* BLOCCO 5 — LEFT STACK */
  leftStack: {
    position: 'absolute', top: 120, left: 10,
    width: 130, gap: 8, zIndex: 18,
  },
  serverTimeBox: {
    backgroundColor: 'rgba(15,15,30,0.8)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 8, paddingVertical: 5, borderRadius: 6,
  },
  serverLabel: { color: '#AAA', fontSize: 8, fontWeight: '900' },
  serverValue: { color: '#fff', fontSize: 9, fontWeight: '700', marginTop: 2 },
  spOfferBtn: { borderRadius: 4, overflow: 'hidden' },
  spOfferGrad: {
    paddingVertical: 6, borderRadius: 4, alignItems: 'center',
    borderWidth: 1, borderColor: '#FFD700',
  },
  spOfferTxt: { color: '#FFF', fontSize: 11, fontWeight: '900', letterSpacing: 1 },
  crystalRow: { flexDirection: 'row', gap: 6 },
  crystalPack: {
    flex: 1, aspectRatio: 0.7,
    backgroundColor: 'rgba(15,15,30,0.85)',
    borderWidth: 1, borderColor: 'rgba(70,163,255,0.45)',
    borderRadius: 6, alignItems: 'center', justifyContent: 'center', paddingVertical: 4,
  },
  crystalNum: { color: '#fff', fontSize: 16, fontWeight: '900' },
  crystalIco: { fontSize: 24, marginVertical: 2 },
  crystalPrice: { color: '#46A3FF', fontSize: 9, fontWeight: '800' },

  /* BLOCCO 7 — MODE PANEL */
  modePanel: {
    position: 'absolute', top: 115, right: 8,
    width: 72, gap: 6, zIndex: 18,
  },
  modeTile: {
    width: '100%', aspectRatio: 1.05, borderRadius: 6, overflow: 'hidden',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.4)',
  },
  modeTileInner: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 4 },
  modeIco: { fontSize: 26 },
  modeLabel: { color: '#fff', fontSize: 9, fontWeight: '900', letterSpacing: 0.5 },

  /* BLOCCO 8 — MAIN BANNER — sopra la tab bar nativa (~60px) */
  mainBanner: {
    position: 'absolute', bottom: 70, right: 10,
    flexDirection: 'row', gap: 6, zIndex: 17,
  },
  bannerTile: {
    width: 80, height: 70, borderRadius: 6, overflow: 'hidden',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.45)',
  },
  bannerTileInner: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 4 },
  bannerIco: { fontSize: 20 },
  bannerLabel: { color: '#fff', fontSize: 10, fontWeight: '900' },

  /* BLOCCO 9 — BOTTOM NAV */
  bottomNav: {
    position: 'absolute', bottom: 0, left: 0, right: 0,
    flexDirection: 'row', alignItems: 'flex-end',
    paddingBottom: 8, paddingHorizontal: 6,
    backgroundColor: 'rgba(10,6,30,0.82)',
    borderTopWidth: 1, borderTopColor: 'rgba(255,215,0,0.25)',
    zIndex: 25,
  },
  bottomNavSide: {
    flex: 1, flexDirection: 'row', justifyContent: 'space-around',
    alignItems: 'flex-end', gap: 2,
  },
  navBtn: { alignItems: 'center', paddingVertical: 4, paddingHorizontal: 2, minWidth: 40 },
  navIconWrap: {
    width: 36, height: 36, borderRadius: 6,
    backgroundColor: 'rgba(30,30,50,0.7)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.3)',
    alignItems: 'center', justifyContent: 'center',
  },
  navIco: { fontSize: 16 },
  navLabel: { color: '#FFD700', fontSize: 8, fontWeight: '900', marginTop: 2 },

  playShield: {
    width: 72, height: 96, marginHorizontal: 4,
    marginTop: -18,
  },
  playShieldInner: {
    flex: 1, borderRadius: 10,
    borderWidth: 2, borderColor: '#FFD700',
    alignItems: 'center', justifyContent: 'center',
  },
  playText: { color: '#FFD700', fontSize: 20, fontWeight: '900', letterSpacing: 1 },

  /* BLOCCO 10 — OVERFLOW MODAL */
  modalBackdrop: {
    flex: 1, backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  modalCard: {
    backgroundColor: '#12122e',
    borderTopLeftRadius: 18, borderTopRightRadius: 18,
    paddingTop: 12, paddingHorizontal: 12, paddingBottom: 6,
    maxHeight: '85%',
    borderTopWidth: 2, borderTopColor: '#FFD700',
  },
  modalHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    marginBottom: 4,
  },
  modalTitle: { color: '#FFD700', fontSize: 17, fontWeight: '900' },
  modalClose: { color: '#fff', fontSize: 22, paddingHorizontal: 6 },
  modalSub: { color: '#BBB', fontSize: 11, marginBottom: 10, fontStyle: 'italic' },
  modalGrid: {
    flexDirection: 'row', flexWrap: 'wrap', gap: 8, justifyContent: 'space-between',
  },
  modalItem: {
    width: '31%', aspectRatio: 1,
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.25)',
    borderRadius: 10, alignItems: 'center', justifyContent: 'center', gap: 6,
  },
  modalItemIco: { fontSize: 28 },
  modalItemLabel: { color: '#fff', fontSize: 10, fontWeight: '800', textAlign: 'center', paddingHorizontal: 4 },
});
