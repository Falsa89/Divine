/**
 * HOME — SHELL VISIVA PREMIUM v2 (Fase A)
 * ================================================================
 *
 * Palette: GOLD (#FFD700 / #C9A759 / #F7D563) + DEEP BLUE
 *          (#0A1838 / #0F2148 / #1B3570 / #243A6A).
 * Accenti: cremisi (#B22222) solo per urgenza/notifiche/SP Offer.
 *
 * Componenti modulari (nessun flatten, testi veri, bottoni veri):
 *   BLOCCO 1  — HomeBackground       (ImageBackground scenico + overlay blu notte)
 *   BLOCCO 2  — HomeHeroLayer        (splash libero, NO frame/NO label/NO testo)
 *   BLOCCO 3  — HomeProfilePanel     (top-left: avatar, lv, exp, power, VIP, spirito, titolo)
 *   BLOCCO 4  — HomeCurrencyBar      (top-right: Gold+, Gems+)
 *   BLOCCO 5  — HomeTopActions       (Wheel/Quest/Event + slot evento opzionali nascosti se vuoti)
 *   BLOCCO 6  — HomeLeftUtilityStack (Server time / SP Offer / Box 2 / Box 3)
 *   BLOCCO 7  — HomeModePanel        (Arena / Blessing / Trial / Battle / Research)
 *   BLOCCO 8  — HomeMainBanner       (Summon banner rate-up con artwork hero)
 *   BLOCCO 9  — HomeChatNotifPanel   (chat + feed notifiche, espandibile)
 *   BLOCCO 10 — HomeBottomNav        (custom 10 slot: Chat, Bag, Artifact, Skill, Team,
 *                                     PLAY [centrale], Guild, Shop, Forge, Menu)
 *   BLOCCO 11 — HomeOverflowPanel    (pannello con tutte le feature residue)
 *
 * REFRESH LIVE: useFocusEffect → /api/sanctuary/home-hero ri-fetch
 *   ad ogni focus della tab. Cambio eroe IMMEDIATO senza restart.
 *
 * NO animazioni globali fake (blink/opacity). Hero statico.
 * NO testi/card/border sotto/intorno al personaggio.
 */
import React, { useEffect, useState, useCallback, useRef } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ActivityIndicator,
  Dimensions, ScrollView, Modal, ImageBackground, Pressable,
  useWindowDimensions, Image as RNImage,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, useFocusEffect } from 'expo-router';
import { useAuth } from '../../context/AuthContext';
import { apiCall } from '../../utils/api';
import { registerForPushNotifications } from '../../utils/pushNotifications';
import HomeHeroSplash from '../../components/home/HomeHeroSplash';
import { COLORS } from '../../constants/theme';
import {
  HOME_BACKGROUNDS, HOME_PANELS, HOME_BUTTONS, HOME_NAV_ICONS,
  HOME_BANNERS, HOME_PLAY_SHIELD, HOME_NAV_BAR_BASE, HOME_SIDE_FRAME,
  HOME_NAV_ICON_IMAGES, HOME_ROUTES, resolveHomeBackground, type HomeScene,
} from '../../constants/homeAssetsManifest';
import { AssetSlot, ButtonAssetSlot } from '../../components/home/AssetSlot';
import { useServerTimePhase, type TimePhase } from '../../utils/serverTimePhase';
import { preloadAssets } from '../../utils/preloadAssets';
import HomeLoadingScreen from '../../components/home/HomeLoadingScreen';

const { width: W, height: H } = Dimensions.get('window');

/* ─────────────────────────── DESIGN TOKENS ───────────────────────────
 * NB: TOKENS NEUTRI, NON UNA DIREZIONE ARTISTICA FINALE.
 *     Quando arriveranno gli asset definitivi dal team art, i pannelli
 *     useranno frame-immagine e questi gradient "placeholder" scompariranno.
 * ─────────────────────────────────────────────────────────────────── */
const GOLD       = '#FFD700';
const GOLD_WARM  = '#C9A759';
const GOLD_PALE  = '#F7D563';
const NIGHT_0    = '#05091A';
const NIGHT_1    = '#0A1838';
const NIGHT_2    = '#0F2148';
const NIGHT_3    = '#1B3570';
const CRIMSON    = '#B22222';

/** Scena homepage corrente. In futuro sar\u00e0 data da `user.home_scene`. */
const CURRENT_SCENE: HomeScene = 'default';

/** Mostra in alto un piccolo badge "FASE: night" utile in dev/QA. */
const SHOW_PHASE_BADGE = true;

/* ==================================================================== */
export default function HomeTab() {
  const { user, refreshUser } = useAuth();
  const router = useRouter();
  const [homeHero, setHomeHero] = useState<any>(null);
  const [homeSource, setHomeSource] = useState<string>('');
  const [inTutorial, setInTutorial] = useState<boolean>(true);
  const [loading, setLoading] = useState(true);
  const [overflowOpen, setOverflowOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);

  // PRELOAD GATE: blocca il render della home fino a quando gli asset core
  // sono stati prefetchati nella cache del renderer. Evita il "pop-in" dei
  // pulsanti/icone uno alla volta dopo il login.
  const [preloadDone, setPreloadDone] = useState(false);
  const [preloadProgress, setPreloadProgress] = useState({ done: 0, total: 0 });

  // SERVER TIME + FASE TEMPORALE centralizzata (unico hook, nessun hardcode)
  const { phase, formatted: serverTime, synced } = useServerTimePhase(60);

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

  // REFRESH LIVE: refetch su ogni focus della tab (post-select hero etc.)
  useFocusEffect(useCallback(() => { loadData(); }, [loadData]));

  useEffect(() => { registerForPushNotifications().catch(() => {}); }, []);

  // PRELOAD GATE: una volta sincronizzata la fase + caricato homeHero,
  // prefetchiamo TUTTI gli asset core della home. Finché non terminiamo,
  // mostriamo HomeLoadingScreen.
  useEffect(() => {
    if (loading) return;     // aspetta che loadData sia finito (hero + user)
    if (!synced) return;     // aspetta sync server time (per background corretto)
    if (preloadDone) return; // già fatto

    const coreAssets: any[] = [
      // Background della fase corrente (più fallback per sicurezza)
      resolveHomeBackground('default', phase),
      HOME_BACKGROUNDS.default.night,
      HOME_BACKGROUNDS.default.day,
      HOME_BACKGROUNDS.default.dawn,
      HOME_BACKGROUNDS.default.sunset,
      // Bottom nav
      HOME_NAV_BAR_BASE,
      // PLAY states (tutti e 3 preload ESPLICITO)
      HOME_PLAY_SHIELD.idle,
      HOME_PLAY_SHIELD.pressed,
      HOME_PLAY_SHIELD.selected,
      // Frame side buttons
      HOME_SIDE_FRAME.default,
      HOME_SIDE_FRAME.selected,
      HOME_SIDE_FRAME.pressed,
      // 9 icone nav
      ...Object.values(HOME_NAV_ICON_IMAGES),
      // Hero home: se è un asset locale (require), aggiungilo; se remote URI, passalo diretto
      homeHero?.asset_splash || homeHero?.asset_base || homeHero?.image_url,
    ];

    let canceled = false;
    (async () => {
      const res = await preloadAssets(coreAssets, (done, total) => {
        if (!canceled) setPreloadProgress({ done, total });
      });
      if (!canceled) {
        // Log utile per debug
        console.log(`[HomePreload] ${res.loaded}/${res.total} loaded, ${res.failed} failed`);
        setPreloadDone(true);
      }
    })();

    return () => { canceled = true; };
  }, [loading, synced, phase, homeHero, preloadDone]);

  const onHeroTap = () => {
    if (homeHero?.id) {
      router.push({ pathname: '/sanctuary', params: { heroId: homeHero.id } } as any);
    }
  };

  // Helper: route utility che evita hardcode sparsi; '' = apre overflow/chat in-home.
  const goTo = (key: keyof typeof HOME_ROUTES) => {
    const route = HOME_ROUTES[key];
    if (!route) { setOverflowOpen(true); return; }
    router.push(route as any);
  };

  if (loading || !preloadDone) {
    return (
      <HomeLoadingScreen
        done={preloadProgress.done}
        total={preloadProgress.total}
        label={loading ? 'CARICAMENTO DATI…' : 'PREPARAZIONE HOMEPAGE…'}
      />
    );
  }

  return (
    <View style={s.container}>
      {/* BLOCCO 1 — BACKGROUND (asset-driven per scena \u00d7 fase) */}
      <HomeBackground scene={CURRENT_SCENE} phase={phase} />

      {/* BLOCCO 2 — HERO LAYER (sopra bg, sotto UI) */}
      <View style={s.heroLayer} pointerEvents="box-none">
        <HomeHeroSplash
          hero={homeHero}
          source={homeSource}
          inTutorial={inTutorial}
          width={Math.min(W * 0.55, 420)}
          height={Math.min(H * 0.80, 600)}
          onPress={onHeroTap}
        />
      </View>

      {/* BLOCCO 3 — PROFILO (top-left) */}
      <HomeProfilePanel user={user} router={router} />

      {/* BLOCCO 4 — VALUTE (top-right) */}
      <HomeCurrencyBar user={user} onAddGems={() => goTo('gemsPlus')} />

      {/* BLOCCO 5 — TOP ACTIONS (sotto valute, destra) */}
      <HomeTopActions goTo={goTo} />

      {/* BLOCCO 6 — LEFT UTILITY STACK */}
      <HomeLeftUtilityStack
        serverTime={serverTime}
        phase={phase}
        synced={synced}
        onSpOffer={() => goTo('spOffer')}
        goTo={goTo}
      />

      {/* BLOCCO 7 — RIGHT MODE PANEL (Arena/Blessing/Trial/Battle/Research) */}
      <HomeModePanel goTo={goTo} />

      {/* BLOCCO 8 — MAIN BANNER (summon rate-up) */}
      <HomeMainBanner onPress={() => goTo('mainBanner')} homeHero={homeHero} />

      {/* BLOCCO 9 — CHAT / NOTIFICHE (bottom-left, sopra bottom nav) */}
      <HomeChatNotifPanel
        open={chatOpen}
        onToggle={() => setChatOpen(v => !v)}
      />

      {/* BLOCCO 10 — BOTTOM NAV CUSTOM (10 slot, PLAY centrale) */}
      <HomeBottomNav
        goTo={goTo}
        onChat={() => setChatOpen(true)}
        onMenu={() => setOverflowOpen(true)}
      />

      {/* BLOCCO 11 — OVERFLOW (feature residue) */}
      <HomeOverflowPanel
        open={overflowOpen}
        onClose={() => setOverflowOpen(false)}
        router={router}
      />

      {/* Badge fase temporale (dev/QA). Disattivabile con SHOW_PHASE_BADGE=false */}
      {SHOW_PHASE_BADGE ? (
        <View style={s.phaseBadge} pointerEvents="none">
          <Text style={s.phaseBadgeTxt}>
            {synced ? 'S' : '~'}  {phase.toUpperCase()}  {serverTime}
          </Text>
        </View>
      ) : null}
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 1 — HomeBackground (asset-driven)
 *  Legge manifest[scena][fase] + fallback tecnico neutro se mancante.
 *  L'overlay blu \u00e8 volutamente MINIMALE per non "colorare" l'asset
 *  definitivo quando arriver\u00e0.
 * ═══════════════════════════════════════════════════════════════════ */
function HomeBackground({ scene, phase }: { scene: HomeScene; phase: TimePhase }) {
  const asset = resolveHomeBackground(scene, phase);
  // Fallback neutro se NESSUN asset per la scena/fase (scena nuova non ancora pop.)
  if (!asset) {
    return (
      <LinearGradient
        colors={[NIGHT_0, NIGHT_1, NIGHT_2]}
        style={StyleSheet.absoluteFill}
      />
    );
  }
  return (
    <View style={StyleSheet.absoluteFill}>
      <ImageBackground source={asset} style={StyleSheet.absoluteFill} resizeMode="cover">
        {/* Overlay minimale per leggibilit\u00e0 UI. Nessun bloom decorativo. */}
        <View style={s.bgReadabilityOverlay} />
      </ImageBackground>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 3 — HomeProfilePanel
 *  Pannello profilo premium con decorazione gold-on-navy
 * ═══════════════════════════════════════════════════════════════════ */
function HomeProfilePanel({ user, router }: any) {
  const name    = user?.nickname || user?.name || 'Player';
  const power   = user?.power || user?.total_power || 0;
  const level   = user?.level || 1;
  const exp     = user?.exp || 0;
  const expMax  = user?.exp_to_next || 1000;
  const vip     = user?.vip_level || 0;
  const spirito = user?.spirito || user?.spirit || 0;
  const title   = user?.title || 'Apprendista';

  return (
    <View style={s.profileWrap}>
      <LinearGradient
        colors={['rgba(11,23,60,0.95)', 'rgba(8,15,40,0.85)']}
        style={s.profilePanel}
      >
        {/* ROW 1 — Avatar + Nome + Lv */}
        <View style={s.profileRow1}>
          <TouchableOpacity
            onPress={() => router.push('/profile' as any)}
            activeOpacity={0.8}
            style={s.avatarFrame}
          >
            <LinearGradient
              colors={[GOLD_PALE, GOLD, GOLD_WARM]}
              style={s.avatarRing}
            >
              <View style={s.avatarInner}>
                <Text style={s.avatarInitial}>
                  {String(name)[0]?.toUpperCase() || 'P'}
                </Text>
              </View>
            </LinearGradient>
            <View style={s.lvBadge}>
              <Text style={s.lvBadgeTxt}>{level}</Text>
            </View>
          </TouchableOpacity>
          <View style={{ flex: 1, marginLeft: 10 }}>
            <Text style={s.profName} numberOfLines={1}>{name}</Text>
            <View style={s.expWrap}>
              <View style={s.expBarBg}>
                <LinearGradient
                  colors={[GOLD_PALE, GOLD]}
                  start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
                  style={[s.expBarFill, { width: `${Math.min(100, (exp / expMax) * 100)}%` }]}
                />
              </View>
              <Text style={s.expTxt}>{exp}/{expMax}</Text>
            </View>
          </View>
        </View>

        {/* ROW 2 — Power */}
        <TouchableOpacity
          style={s.powerRow}
          onPress={() => router.push('/profile' as any)}
          activeOpacity={0.8}
        >
          <Text style={s.powerIcon}>{'\u26A1'}</Text>
          <Text style={s.powerLbl}>POWER</Text>
          <Text style={s.powerVal}>{Number(power).toLocaleString()}</Text>
        </TouchableOpacity>

        {/* ROW 3 — VIP / Spirito / Titolo */}
        <View style={s.pillsRow}>
          <TouchableOpacity style={s.vipPill} activeOpacity={0.7}
            onPress={() => router.push('/vip' as any)}>
            <Text style={s.vipStar}>{'\u2605'}</Text>
            <Text style={s.vipTxt}>VIP {vip}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={s.spiritoPill} activeOpacity={0.7}
            onPress={() => router.push('/profile' as any)}>
            <Text style={s.spiritoIco}>{'\uD83D\uDD2E'}</Text>
            <Text style={s.spiritoTxt}>SP {spirito}</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity style={s.titleBadge} activeOpacity={0.7}
          onPress={() => router.push('/achievements' as any)}>
          <Text style={s.titleTxt} numberOfLines={1}>{'\u2756'}  {title}</Text>
        </TouchableOpacity>
      </LinearGradient>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 4 — HomeCurrencyBar
 *  Gold + Gems con pulsanti "+"
 * ═══════════════════════════════════════════════════════════════════ */
function HomeCurrencyBar({ user, onAddGems }: any) {
  const gold = user?.gold || 0;
  const gems = user?.diamonds || user?.gems || 0;
  return (
    <View style={s.currencyWrap}>
      <LinearGradient
        colors={['rgba(20,33,72,0.95)', 'rgba(8,15,40,0.85)']}
        style={[s.currencyPill, { borderColor: 'rgba(255,215,0,0.65)' }]}
      >
        <Text style={s.currencyIco}>{'\uD83D\uDCB0'}</Text>
        <Text style={s.currencyTxt}>{Number(gold).toLocaleString()}</Text>
        <TouchableOpacity style={s.plusBtn} onPress={onAddGems} activeOpacity={0.7}>
          <LinearGradient
            colors={[GOLD_PALE, GOLD]}
            style={s.plusBtnInner}
          >
            <Text style={s.plusTxt}>+</Text>
          </LinearGradient>
        </TouchableOpacity>
      </LinearGradient>
      <LinearGradient
        colors={['rgba(20,33,72,0.95)', 'rgba(8,15,40,0.85)']}
        style={[s.currencyPill, { borderColor: 'rgba(100,170,255,0.65)' }]}
      >
        <Text style={s.currencyIco}>{'\uD83D\uDC8E'}</Text>
        <Text style={s.currencyTxt}>{Number(gems).toLocaleString()}</Text>
        <TouchableOpacity style={s.plusBtn} onPress={onAddGems} activeOpacity={0.7}>
          <LinearGradient
            colors={['#6EC8FF', '#2C7DD8']}
            style={s.plusBtnInner}
          >
            <Text style={[s.plusTxt, { color: '#fff' }]}>+</Text>
          </LinearGradient>
        </TouchableOpacity>
      </LinearGradient>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 5 — HomeTopActions
 *  Wheel / Quest / Event + slot evento 1/2 (nascosti se vuoti)
 * ═══════════════════════════════════════════════════════════════════ */
function HomeTopActions({ goTo }: any) {
  // Slot evento: array di eventi attivi (vuoti → NON renderizzati)
  const eventSlots: Array<{ key: string; icon: string; label: string; onPress: () => void }> = [];

  const base = [
    { key: 'wheel', icon: '\uD83C\uDFA1', label: 'WHEEL', onPress: () => goTo('wheel') },
    { key: 'quest', icon: '\uD83D\uDCDC', label: 'QUEST', onPress: () => goTo('quest') },
    { key: 'event', icon: '\uD83C\uDF81', label: 'EVENT', onPress: () => goTo('event') },
  ];

  const items = [...base, ...eventSlots];

  return (
    <View style={s.topActionsRow}>
      {items.map(it => (
        <TouchableOpacity key={it.key} style={s.topActBtn} activeOpacity={0.75} onPress={it.onPress}>
          <ButtonAssetSlot
            asset={(HOME_BUTTONS as any)[it.key]}
            state="default"
            style={s.topActIconBox as any}
            fallback={
              <View style={s.placeholderFill}>
                <Text style={s.topActIco}>{it.icon}</Text>
              </View>
            }
          />
          <Text style={s.topActLabel}>{it.label}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 6 — HomeLeftUtilityStack
 *  Server time / SP Offer / Box 2 / Box 3
 * ═══════════════════════════════════════════════════════════════════ */
function HomeLeftUtilityStack({ serverTime, phase, synced, onSpOffer, goTo }: any) {
  return (
    <View style={s.leftStack}>
      <View style={s.serverTimeBox}>
        <Text style={s.serverLabel}>{'\uD83D\uDD50'} SERVER TIME {synced ? '' : '·sync'}</Text>
        <Text style={s.serverValue}>{serverTime}</Text>
        <Text style={s.serverPhase}>fase: {phase}</Text>
      </View>

      <TouchableOpacity style={s.spOfferBtn} onPress={onSpOffer} activeOpacity={0.85}>
        <LinearGradient
          colors={['#D13B3B', '#8A1515']}
          start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}
          style={s.spOfferGrad}
        >
          <Text style={s.spOfferBadge}>SP</Text>
          <View style={{ flex: 1 }}>
            <Text style={s.spOfferTitle}>SP OFFER</Text>
            <Text style={s.spOfferSub}>Bundle esclusivo</Text>
          </View>
          <Text style={s.spOfferArrow}>{'\u203A'}</Text>
        </LinearGradient>
      </TouchableOpacity>

      <View style={s.crystalRow}>
        {[
          { tier: 2, gems: 100,  col1: '#1D4C8A', col2: '#0A1F3C' },
          { tier: 3, gems: 150,  col1: '#4B2080', col2: '#1A0A3C' },
        ].map((x, i) => (
          <TouchableOpacity
            key={i}
            style={s.crystalPack}
            onPress={() => goTo('goldPlus')}
            activeOpacity={0.85}
          >
            <LinearGradient
              colors={[x.col1, x.col2]}
              style={s.crystalPackInner}
            >
              <Text style={s.crystalTier}>×{x.tier}</Text>
              <Text style={s.crystalIco}>{'\uD83D\uDC8E'}</Text>
              <View style={s.crystalPriceWrap}>
                <Text style={s.crystalPriceIco}>{'\uD83D\uDC8E'}</Text>
                <Text style={s.crystalPrice}>{x.gems}</Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 7 — HomeModePanel
 *  Arena / Blessing / Trial / Battle / Research (verticale, a destra)
 * ═══════════════════════════════════════════════════════════════════ */
function HomeModePanel({ goTo }: any) {
  const modes: Array<{ key: any; label: string; ico: string }> = [
    { key: 'arena',    label: 'ARENA',    ico: '\u2694\uFE0F' },
    { key: 'blessing', label: 'BLESSING', ico: '\uD83D\uDCFF' },
    { key: 'trial',    label: 'TRIAL',    ico: '\u26AA'       },
    { key: 'battle',   label: 'BATTLE',   ico: '\u2620\uFE0F' },
    { key: 'research', label: 'RESEARCH', ico: '\uD83D\uDD2C' },
  ];
  return (
    <View style={s.modePanel}>
      {modes.map(m => (
        <TouchableOpacity
          key={m.key}
          style={s.modeTile}
          onPress={() => goTo(m.key)}
          activeOpacity={0.82}
        >
          <ButtonAssetSlot
            asset={(HOME_BUTTONS as any)[m.key]}
            state="default"
            style={s.modeTileInner as any}
            fallback={
              <LinearGradient
                colors={['rgba(27,53,112,0.92)', 'rgba(10,24,56,0.92)']}
                style={s.modeTileInnerFallback}
              >
                <Text style={s.modeIco}>{m.ico}</Text>
                <Text style={s.modeLabel}>{m.label}</Text>
              </LinearGradient>
            }
          />
        </TouchableOpacity>
      ))}
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 8 — HomeMainBanner
 *  Summon banner rate-up (artwork hero in primo piano)
 * ═══════════════════════════════════════════════════════════════════ */
function HomeMainBanner({ onPress, homeHero }: any) {
  const featuredName = homeHero?.name || 'Hoplite';
  return (
    <TouchableOpacity
      style={s.mainBanner}
      onPress={onPress}
      activeOpacity={0.88}
    >
      <AssetSlot
        asset={HOME_BANNERS.summonMain.frame}
        style={s.bannerInnerAbs as any}
      >
        <LinearGradient
          colors={['rgba(27,53,112,0.97)', 'rgba(8,15,40,0.95)']}
          start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}
          style={s.bannerInner}
        >
          <View style={s.bannerLeft}>
            <Text style={s.bannerTag}>RATE-UP</Text>
            <Text style={s.bannerTitle} numberOfLines={1}>{featuredName}</Text>
            <Text style={s.bannerSub}>Evoca ora</Text>
            <View style={s.bannerBtn}>
              <Text style={s.bannerBtnTxt}>SUMMON {'\u203A'}</Text>
            </View>
          </View>
          <Text style={s.bannerSparkle}>{'\u2728'}</Text>
        </LinearGradient>
      </AssetSlot>
    </TouchableOpacity>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 9 — HomeChatNotifPanel
 *  Pannello chat + notifiche, espandibile
 * ═══════════════════════════════════════════════════════════════════ */
function HomeChatNotifPanel({ open, onToggle }: any) {
  // Messaggi mock iniziali: in futuro arriveranno dal backend chat + sistema
  const feed = [
    { type: 'system', txt: 'Benvenuto in Divine Waifus. Tap su PLAY per iniziare.' },
    { type: 'system', txt: 'Nuovo evento: "Prova del Fuoco" disponibile per 48h.' },
    { type: 'chat',   from: 'Aether', txt: 'qualcuno per arena?' },
    { type: 'chat',   from: 'Nyx',    txt: 'boss di gilda alle 21' },
  ];

  return (
    <View style={[s.chatPanel, open && s.chatPanelOpen]}>
      <LinearGradient
        colors={['rgba(11,23,60,0.88)', 'rgba(8,15,40,0.92)']}
        style={s.chatInner}
      >
        <TouchableOpacity style={s.chatHeader} onPress={onToggle} activeOpacity={0.8}>
          <Text style={s.chatIco}>{'\uD83D\uDCAC'}</Text>
          <Text style={s.chatTitle}>CHAT · NOTIFICHE</Text>
          <Text style={s.chatToggle}>{open ? '\u25BC' : '\u25B2'}</Text>
        </TouchableOpacity>
        {open ? (
          <ScrollView style={s.chatBody} showsVerticalScrollIndicator={false}>
            {feed.map((m, i) => (
              <View key={i} style={s.chatMsg}>
                {m.type === 'system' ? (
                  <>
                    <Text style={s.chatSysTag}>[SISTEMA]</Text>
                    <Text style={s.chatMsgTxt}>{m.txt}</Text>
                  </>
                ) : (
                  <>
                    <Text style={s.chatFrom}>{m.from}:</Text>
                    <Text style={s.chatMsgTxt}>{m.txt}</Text>
                  </>
                )}
              </View>
            ))}
          </ScrollView>
        ) : (
          <View style={s.chatPreview}>
            <Text style={s.chatPreviewTag}>[SISTEMA]</Text>
            <Text style={s.chatPreviewTxt} numberOfLines={1}>
              {feed[0]?.txt}
            </Text>
          </View>
        )}
      </LinearGradient>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 10 — HomeBottomNav
 *
 *  LAYOUT — mobile-first, ancoraggio ASSOLUTO al centro della barra base.
 *  ─────────────────────────────────────────────────────────────────────
 *  Il problema del layout precedente era che il row aveva 5+4 bottoni con
 *  `justifyContent: center`: la somma asimmetrica spostava PLAY di mezzo
 *  pulsante rispetto al vero centro visivo della barra.
 *
 *  Nuovo sistema:
 *   - `bottomNavBarBase` è l'ÀNCORA: posizionata a `left: 50% - barW/2`
 *   - `PlayShield` usa lo STESSO ancoraggio: `left: 50% - playW/2`
 *     → PLAY è MATEMATICAMENTE centrato sulla barra, indipendentemente dal
 *       numero di pulsanti laterali
 *   - I gruppi sinistra/destra sono posizionati con `right: 50% + halfPlayW + gap`
 *     e `left: 50% + halfPlayW + gap` → simmetrici attorno al PLAY
 *   - Tutte le dimensioni scalano proporzionalmente al viewport (mobile-first
 *     ma responsive a tablet / desktop) tramite `useWindowDimensions`.
 *   - `useSafeAreaInsets().bottom` aggiunge padding per notch iPhone / gesture bar Android.
 *
 *  Nessun offset hardcoded viewport-specifico.
 * ═══════════════════════════════════════════════════════════════════ */
function HomeBottomNav({ goTo, onChat, onMenu }: any) {
  const { width: vw } = useWindowDimensions();
  const insets = useSafeAreaInsets();

  // === RESPONSIVE METRICS ===
  // Barra base: 55% del viewport, cap 420px, min 300px (iPhone SE landscape)
  const BAR_W = Math.max(300, Math.min(vw * 0.55, 420));
  const BAR_H = BAR_W / 2.333;                // aspect del PNG source
  const PLAY_W = Math.max(58, BAR_W * 0.20);  // ~20% della barra
  const PLAY_H = PLAY_W * (86 / 72);          // aspect shield
  const SIDE_W = Math.max(34, BAR_W * 0.115); // ~11.5% della barra
  const SIDE_H = SIDE_W * (48 / 42);          // aspect frame
  const SIDE_GAP = Math.max(1, BAR_W * 0.004);
  const GROUP_GAP = Math.max(2, BAR_W * 0.005); // gap tra PLAY e gruppo laterale
  const NAV_H = BAR_H * 0.62;                 // container solo la fascia bassa della barra (quella "piatta")
  const BTN_BOTTOM = insets.bottom + 8;       // baseline comune tutti i bottoni (safe-area aware)

  const left: Array<{ key: any; label: string; ico: string; onPress: () => void }> = [
    { key: 'chat',     label: 'CHAT',     ico: '\uD83D\uDCAC', onPress: onChat },
    { key: 'bag',      label: 'BAG',      ico: '\uD83C\uDF92', onPress: () => goTo('bag') },
    { key: 'artifact', label: 'ARTIFACT', ico: '\uD83D\uDD2E', onPress: () => goTo('artifact') },
    { key: 'skill',    label: 'SKILL',    ico: '\uD83D\uDCDA', onPress: () => goTo('skill') },
    { key: 'team',     label: 'TEAM',     ico: '\uD83D\uDC65', onPress: () => goTo('team') },
  ];
  const right: Array<{ key: any; label: string; ico: string; onPress: () => void }> = [
    { key: 'guild', label: 'GUILD', ico: '\uD83D\uDEE1\uFE0F', onPress: () => goTo('guild') },
    { key: 'shop',  label: 'SHOP',  ico: '\uD83C\uDFEA',        onPress: () => goTo('shop') },
    { key: 'forge', label: 'FORGE', ico: '\u2692\uFE0F',         onPress: () => goTo('forge') },
    { key: 'menu',  label: 'MENU',  ico: '\u2630',               onPress: onMenu },
  ];

  // marginHorizontal per i side-group (dalla centerline): halfPlay + gap
  const flankOffset = PLAY_W / 2 + GROUP_GAP;

  return (
    <View
      style={[s.bottomNav, { height: BAR_H + insets.bottom }]}
      pointerEvents="box-none"
    >
      {/* (1) BARRA BASE — àncora visiva. Centrata matematicamente al viewport. */}
      {HOME_NAV_BAR_BASE ? (
        <RNImage
          source={HOME_NAV_BAR_BASE}
          style={{
            position: 'absolute',
            bottom: insets.bottom - 2,
            left: '50%',
            width: BAR_W,
            height: BAR_H,
            transform: [{ translateX: -BAR_W / 2 }],
          }}
          resizeMode="contain"
          pointerEvents="none"
        />
      ) : null}

      {/* (2) PLAY SHIELD — ancoraggio CENTRATO MATEMATICAMENTE sulla barra */}
      <PlayShield
        onPress={() => goTo('play')}
        width={PLAY_W}
        height={PLAY_H}
        bottom={BTN_BOTTOM}
      />

      {/* (3) GRUPPO SINISTRA — posizionato a destra del centro, orientato verso DX,
             simmetrico al gruppo destra rispetto al PLAY */}
      <View
        style={{
          position: 'absolute',
          bottom: BTN_BOTTOM,
          right: '50%',
          marginRight: flankOffset,
          flexDirection: 'row',
          alignItems: 'flex-end',
          gap: SIDE_GAP,
        }}
      >
        {left.map(n => (
          <NavBtn key={n.key} navKey={n.key} {...n} width={SIDE_W} height={SIDE_H} />
        ))}
      </View>

      {/* (4) GRUPPO DESTRA — posizionato a sinistra del centro, orientato verso SX */}
      <View
        style={{
          position: 'absolute',
          bottom: BTN_BOTTOM,
          left: '50%',
          marginLeft: flankOffset,
          flexDirection: 'row',
          alignItems: 'flex-end',
          gap: SIDE_GAP,
        }}
      >
        {right.map(n => (
          <NavBtn key={n.key} navKey={n.key} {...n} width={SIDE_W} height={SIDE_H} />
        ))}
      </View>
    </View>
  );
}

function NavBtn({ label, ico, onPress, navKey, width = 42, height = 48 }: any) {
  const [pressed, setPressed] = useState(false);

  const frameSrc = (pressed ? HOME_SIDE_FRAME.pressed : undefined) || HOME_SIDE_FRAME.default;
  const iconSrc = navKey ? (HOME_NAV_ICON_IMAGES as any)[navKey] : undefined;

  // Aree interne proporzionali (icona alta 60%, label bassa 20%)
  const iconTop = Math.round(height * 0.10);
  const iconH   = Math.round(height * 0.55);
  const labelBottom = Math.round(height * 0.06);
  const labelH  = Math.round(height * 0.22);

  return (
    <Pressable
      onPress={onPress}
      onPressIn={() => setPressed(true)}
      onPressOut={() => setPressed(false)}
      style={{ alignItems: 'center', width }}
    >
      <View style={{ width, height, position: 'relative' }}>
        {frameSrc ? (
          <RNImage
            source={frameSrc}
            style={s.navFrameImg}
            resizeMode="contain"
            pointerEvents="none"
          />
        ) : null}
        <View
          style={[s.navIconArea, { top: iconTop, height: iconH }]}
          pointerEvents="none"
        >
          {iconSrc ? (
            <RNImage source={iconSrc} style={s.navIconImg} resizeMode="contain" />
          ) : (
            <Text style={s.navIco}>{ico}</Text>
          )}
        </View>
        <View
          style={[s.navLabelArea, { bottom: labelBottom, height: labelH }]}
          pointerEvents="none"
        >
          <Text style={s.navLabel} numberOfLines={1}>{label}</Text>
        </View>
        {pressed ? <View style={s.navPressedOverlay} pointerEvents="none" /> : null}
      </View>
    </Pressable>
  );
}

/**
 * PlayShield — asset-driven.
 * Stati cablati in runtime:
 *   - idle    (default)
 *   - pressed (durante il tap, fornito da Pressable)
 *
 * Stati preparati nel manifest ma NON ancora usati in runtime:
 *   - selected  (sarà usato quando il PLAY farà parte di una selezione persistente)
 *   - glow      (overlay FX opzionale, default OFF per evitare layering sporco)
 *
 * NOTA: il testo "PLAY" è BAKED negli asset. Nessun <Text> sovrapposto.
 */
// GLOW: disabilitato completamente. Verrà rivalutato in una passata futura
// come asset dedicato o effetto speciale separato. Per ora non renderizzato.

/**
 * PlayShield — action button con state machine a 3 stati:
 *   'idle'    → asset nav_btn_play_idle.png      (stato base stabile)
 *   'pressed' → asset nav_btn_play_pressed.png   (mentre il tocco è giù)
 *   'confirm' → asset nav_btn_play_selected.png  (breve release-confirm prima della nav)
 *
 * Flow:
 *   onPressIn  → state = 'pressed'  (IMMEDIATO, 0 ms)
 *   held       → resta 'pressed'
 *   onPress    → state = 'confirm' per CONFIRM_VISIBLE_MS, poi navigazione
 *   cancel     → (release fuori area) torna a 'idle' senza nav
 *
 * NESSUN overlay artificiale, NESSUN translateY, NESSUNO scale/breathing,
 * NESSUN glow. Il feedback avviene SOLO via swap dell'asset approvato.
 */
type PlayState = 'idle' | 'pressed' | 'confirm';
const CONFIRM_VISIBLE_MS = 120;

type PlayShieldProps = {
  onPress: () => void;
  width?: number;
  height?: number;
  bottom?: number;
};

function PlayShield({ onPress, width = 72, height = 86, bottom = 10 }: PlayShieldProps) {
  const [playState, setPlayState] = useState<PlayState>('idle');
  const confirmedRef = useRef<boolean>(false);
  const navTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // RESET ON FOCUS: quando la home riprende focus (es. ritorno da battle),
  // qualsiasi residuo di 'pressed' / 'confirm' viene azzerato. PLAY torna
  // sempre a 'idle' all'ingresso nella home.
  useFocusEffect(useCallback(() => {
    setPlayState('idle');
    confirmedRef.current = false;
    if (navTimerRef.current) {
      clearTimeout(navTimerRef.current);
      navTimerRef.current = null;
    }
  }, []));

  useEffect(() => () => {
    if (navTimerRef.current) clearTimeout(navTimerRef.current);
  }, []);

  // (1) Press-in: PRESSED attivo immediatamente, senza ritardi.
  const handlePressIn = () => {
    confirmedRef.current = false;
    if (navTimerRef.current) clearTimeout(navTimerRef.current);
    setPlayState('pressed');
  };

  // (2) Press valido (release dentro area): CONFIRM breve, poi nav.
  const handlePress = () => {
    confirmedRef.current = true;
    setPlayState('confirm');
    if (navTimerRef.current) clearTimeout(navTimerRef.current);
    navTimerRef.current = setTimeout(() => {
      onPress();   // navigazione dopo il breve confirm state
    }, CONFIRM_VISIBLE_MS);
  };

  // (3) Press-out: se il tap NON è stato confermato (drag fuori / cancel),
  //     torna a idle. Se è stato confermato, la sequenza confirm→nav è già in corso.
  const handlePressOut = () => {
    if (!confirmedRef.current) {
      setPlayState('idle');
    }
    // else: la transizione è gestita da handlePress, non tocchiamo lo stato
  };

  // Asset selection: swap REALE dell'immagine. NIENTE overlay, niente transform extra.
  let src = HOME_PLAY_SHIELD.idle;
  if (playState === 'pressed' && HOME_PLAY_SHIELD.pressed) {
    src = HOME_PLAY_SHIELD.pressed;
  } else if (playState === 'confirm' && HOME_PLAY_SHIELD.selected) {
    src = HOME_PLAY_SHIELD.selected;
  }

  return (
    <Pressable
      onPress={handlePress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      style={{
        position: 'absolute',
        bottom,
        left: '50%',
        width, height,
        transform: [{ translateX: -width / 2 }],
        alignItems: 'center', justifyContent: 'center',
      }}
    >
      {src ? (
        <RNImage source={src} style={s.playShieldImg} resizeMode="contain" />
      ) : (
        // Fallback tecnico solo se il manifest è vuoto
        <LinearGradient colors={[GOLD_PALE, GOLD, '#B8902A']} style={s.playShieldOuter}>
          <Text style={s.playText}>PLAY</Text>
        </LinearGradient>
      )}
    </Pressable>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 11 — HomeOverflowPanel (feature residue)
 * ═══════════════════════════════════════════════════════════════════ */
type OverflowItem = { key: string; label: string; icon: string; onPress: () => void };

function HomeOverflowPanel({ open, onClose, router }: any) {
  const items: OverflowItem[] = [
    { key: 'story',      label: 'Storia',           icon: '\uD83D\uDCDC', onPress: () => { onClose(); router.push('/story' as any); } },
    { key: 'tower',      label: 'Torre',            icon: '\uD83C\uDFEF', onPress: () => { onClose(); router.push('/tower' as any); } },
    { key: 'raid',       label: 'Raid',             icon: '\uD83D\uDD25', onPress: () => { onClose(); router.push('/raid' as any); } },
    { key: 'events',     label: 'Eventi',           icon: '\uD83C\uDF1F', onPress: () => { onClose(); router.push('/events' as any); } },
    { key: 'auras',      label: 'Aure',             icon: '\u2728',       onPress: () => { onClose(); router.push('/(tabs)/cosmetics' as any); } },
    { key: 'exclusive',  label: 'Esclusivi',        icon: '\uD83D\uDC51', onPress: () => { onClose(); router.push('/exclusive' as any); } },
    { key: 'equip',      label: 'Equipaggiamento',  icon: '\u2694\uFE0F', onPress: () => { onClose(); router.push('/equipment' as any); } },
    { key: 'battlepass', label: 'Battle Pass',      icon: '\uD83C\uDFC6', onPress: () => { onClose(); router.push('/battlepass' as any); } },
    { key: 'achievements', label: 'Obiettivi',      icon: '\uD83C\uDFC5', onPress: () => { onClose(); router.push('/achievements' as any); } },
    { key: 'mail',       label: 'Posta',            icon: '\u2709\uFE0F', onPress: () => { onClose(); router.push('/mail' as any); } },
    { key: 'friends',    label: 'Amici',            icon: '\uD83D\uDC65', onPress: () => { onClose(); router.push('/friends' as any); } },
    { key: 'quests',     label: 'Quest',            icon: '\u2705',       onPress: () => { onClose(); router.push('/quests' as any); } },
    { key: 'blessing',   label: 'Benedizioni',      icon: '\uD83D\uDCFF', onPress: () => { onClose(); router.push('/blessings' as any); } },
    { key: 'research',   label: 'Ricerca',          icon: '\uD83D\uDD2C', onPress: () => { onClose(); router.push('/research' as any); } },
    { key: 'collection', label: 'Collezione Eroi',  icon: '\uD83D\uDCDA', onPress: () => { onClose(); router.push('/hero-collection' as any); } },
    { key: 'sanctuary',  label: 'Santuario',        icon: '\u26E9\uFE0F', onPress: () => { onClose(); router.push('/sanctuary' as any); } },
    { key: 'gvg',        label: 'Conquista',        icon: '\uD83C\uDFF0', onPress: () => { onClose(); router.push('/gvg' as any); } },
    { key: 'plaza',      label: 'Piazza',           icon: '\uD83C\uDFDB\uFE0F', onPress: () => { onClose(); router.push('/plaza' as any); } },
    { key: 'territory',  label: 'Territorio',       icon: '\uD83D\uDDFA\uFE0F', onPress: () => { onClose(); router.push('/territory' as any); } },
    { key: 'rankings',   label: 'Classifiche',      icon: '\uD83D\uDCCA', onPress: () => { onClose(); router.push('/rankings' as any); } },
    { key: 'servers',    label: 'Server',           icon: '\uD83C\uDF10', onPress: () => { onClose(); router.push('/servers' as any); } },
    { key: 'pvp',        label: 'Arena PVP',        icon: '\uD83E\uDD4A', onPress: () => { onClose(); router.push('/pvp' as any); } },
    { key: 'economy',    label: 'Economia',         icon: '\uD83D\uDCB9', onPress: () => { onClose(); router.push('/economy' as any); } },
    { key: 'spoffer',    label: 'SP Offer',         icon: '\uD83D\uDCB3', onPress: () => { onClose(); router.push('/shop' as any); } },
  ];

  return (
    <Modal visible={open} animationType="slide" transparent onRequestClose={onClose}>
      <View style={s.modalBackdrop}>
        <LinearGradient
          colors={['rgba(11,23,60,0.98)', 'rgba(5,9,26,0.98)']}
          style={s.modalCard}
        >
          <View style={s.modalHeader}>
            <Text style={s.modalTitle}>{'\u2630'}  MENU — FEATURE AGGIUNTIVE</Text>
            <TouchableOpacity onPress={onClose}>
              <Text style={s.modalClose}>{'\u2715'}</Text>
            </TouchableOpacity>
          </View>
          <Text style={s.modalSub}>
            Contenitore temporaneo: le feature verranno riposizionate nei pulsanti
            principali negli aggiornamenti successivi.
          </Text>
          <ScrollView contentContainerStyle={s.modalGrid}>
            {items.map(it => (
              <TouchableOpacity
                key={it.key}
                style={s.modalItem}
                onPress={it.onPress}
                activeOpacity={0.78}
              >
                <LinearGradient
                  colors={['rgba(27,53,112,0.92)', 'rgba(10,24,56,0.92)']}
                  style={s.modalItemInner}
                >
                  <Text style={s.modalItemIco}>{it.icon}</Text>
                  <Text style={s.modalItemLabel}>{it.label}</Text>
                </LinearGradient>
              </TouchableOpacity>
            ))}
            <View style={{ height: 24 }} />
          </ScrollView>
        </LinearGradient>
      </View>
    </Modal>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  STYLES
 * ═══════════════════════════════════════════════════════════════════ */
const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: NIGHT_0, justifyContent: 'center', alignItems: 'center' },

  /* HERO LAYER — leggermente a destra per far respirare il lato sinistro (profilo/chat) */
  heroLayer: {
    position: 'absolute',
    top: 0, bottom: 68, left: 0, right: 0,
    alignItems: 'center', justifyContent: 'center',
    zIndex: 1,
  },

  /* BLOCCO 3 — PROFILE PANEL */
  profileWrap: {
    position: 'absolute', top: 8, left: 8,
    zIndex: 20,
    width: 232,
  },
  profilePanel: {
    borderRadius: 10,
    borderWidth: 1.5, borderColor: GOLD_WARM,
    paddingHorizontal: 8, paddingVertical: 8,
    shadowColor: '#000', shadowOpacity: 0.6, shadowOffset: { width: 0, height: 3 }, shadowRadius: 6,
    elevation: 8,
  },
  profileRow1: { flexDirection: 'row', alignItems: 'center' },
  avatarFrame: { position: 'relative' },
  avatarRing: {
    width: 46, height: 46, borderRadius: 23,
    padding: 2,
    shadowColor: GOLD, shadowOpacity: 0.8, shadowRadius: 6,
  },
  avatarInner: {
    flex: 1, borderRadius: 21,
    backgroundColor: NIGHT_1,
    alignItems: 'center', justifyContent: 'center',
  },
  avatarInitial: { color: GOLD, fontSize: 20, fontWeight: '900' },
  lvBadge: {
    position: 'absolute', bottom: -4, right: -6,
    backgroundColor: NIGHT_0, borderRadius: 10,
    borderWidth: 1.5, borderColor: GOLD,
    paddingHorizontal: 5, paddingVertical: 1, minWidth: 22, alignItems: 'center',
  },
  lvBadgeTxt: { color: GOLD, fontSize: 10, fontWeight: '900' },
  profName: { color: GOLD, fontSize: 14, fontWeight: '900', letterSpacing: 0.4 },
  expWrap: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 5 },
  expBarBg: {
    flex: 1, height: 6, backgroundColor: 'rgba(0,0,0,0.55)',
    borderRadius: 3, overflow: 'hidden',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.35)',
  },
  expBarFill: { height: '100%' },
  expTxt: { color: '#E8E8F0', fontSize: 8, fontWeight: '800' },

  powerRow: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    marginTop: 6, paddingVertical: 3, paddingHorizontal: 6,
    backgroundColor: 'rgba(255,215,0,0.08)',
    borderRadius: 5,
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.30)',
  },
  powerIcon: { fontSize: 12 },
  powerLbl: { color: GOLD_PALE, fontSize: 9, fontWeight: '900', letterSpacing: 0.6 },
  powerVal: { color: '#fff', fontSize: 11, fontWeight: '900', marginLeft: 'auto' },

  pillsRow: { flexDirection: 'row', gap: 5, marginTop: 5 },
  vipPill: {
    flexDirection: 'row', alignItems: 'center', gap: 3,
    backgroundColor: 'rgba(178,34,34,0.55)',
    paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4,
    borderWidth: 1, borderColor: GOLD,
  },
  vipStar: { color: GOLD, fontSize: 9 },
  vipTxt: { color: GOLD, fontSize: 9, fontWeight: '900' },
  spiritoPill: {
    flexDirection: 'row', alignItems: 'center', gap: 3,
    backgroundColor: 'rgba(60,20,120,0.55)',
    paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4,
    borderWidth: 1, borderColor: '#B05CFF',
  },
  spiritoIco: { fontSize: 9 },
  spiritoTxt: { color: '#FFE0FF', fontSize: 9, fontWeight: '900' },
  titleBadge: {
    marginTop: 5, paddingVertical: 3, paddingHorizontal: 6,
    backgroundColor: 'rgba(15,33,72,0.75)',
    borderRadius: 4, borderLeftWidth: 2, borderLeftColor: GOLD,
  },
  titleTxt: { color: '#D8E0FF', fontSize: 10, fontWeight: '700', fontStyle: 'italic' },

  /* BLOCCO 4 — CURRENCY */
  currencyWrap: {
    position: 'absolute', top: 10, right: 10,
    flexDirection: 'row', gap: 6, zIndex: 20,
  },
  currencyPill: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    paddingLeft: 8, paddingRight: 4, paddingVertical: 3, borderRadius: 16,
    borderWidth: 1.5,
    shadowColor: '#000', shadowOpacity: 0.5, shadowRadius: 4,
    elevation: 5,
  },
  currencyIco: { fontSize: 14 },
  currencyTxt: { color: '#fff', fontSize: 12, fontWeight: '900', minWidth: 40 },
  plusBtn: { width: 22, height: 22, borderRadius: 11 },
  plusBtnInner: {
    flex: 1, borderRadius: 11, alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.25)',
  },
  plusTxt: { color: '#1a0e2e', fontSize: 14, fontWeight: '900' },

  /* BLOCCO 5 — TOP ACTIONS */
  topActionsRow: {
    position: 'absolute', top: 58, right: 10,
    flexDirection: 'row', gap: 6, zIndex: 19,
  },
  topActBtn: { alignItems: 'center', width: 42 },
  topActIconBox: {
    width: 36, height: 36, borderRadius: 18,
    borderWidth: 1.5, borderColor: 'rgba(255,215,0,0.55)',
    alignItems: 'center', justifyContent: 'center',
    shadowColor: '#000', shadowOpacity: 0.5, shadowRadius: 4,
  },
  topActIco: { fontSize: 17 },
  topActLabel: { color: GOLD_PALE, fontSize: 8, fontWeight: '900', marginTop: 3, letterSpacing: 0.5 },

  /* BLOCCO 6 — LEFT STACK */
  leftStack: {
    position: 'absolute', top: 152, left: 8,
    width: 140, gap: 6, zIndex: 18,
  },
  serverTimeBox: {
    backgroundColor: 'rgba(8,15,40,0.85)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.20)',
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6,
    borderLeftWidth: 2, borderLeftColor: GOLD_WARM,
  },
  serverLabel: { color: GOLD_PALE, fontSize: 8, fontWeight: '900', letterSpacing: 0.5 },
  serverValue: { color: '#fff', fontSize: 11, fontWeight: '800', marginTop: 2, letterSpacing: 0.3 },

  spOfferBtn: { borderRadius: 6, overflow: 'hidden', marginTop: 2 },
  spOfferGrad: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    paddingHorizontal: 8, paddingVertical: 8,
    borderRadius: 6,
    borderWidth: 1.5, borderColor: GOLD,
  },
  spOfferBadge: {
    color: GOLD, fontSize: 12, fontWeight: '900',
    backgroundColor: 'rgba(0,0,0,0.35)',
    paddingHorizontal: 6, paddingVertical: 1,
    borderRadius: 4,
    borderWidth: 1, borderColor: GOLD,
  },
  spOfferTitle: { color: '#fff', fontSize: 11, fontWeight: '900', letterSpacing: 1 },
  spOfferSub: { color: 'rgba(255,255,255,0.75)', fontSize: 8, fontWeight: '700' },
  spOfferArrow: { color: GOLD, fontSize: 18, fontWeight: '900' },

  crystalRow: { flexDirection: 'row', gap: 5 },
  crystalPack: {
    flex: 1, borderRadius: 6, overflow: 'hidden',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.35)',
  },
  crystalPackInner: {
    paddingVertical: 6, alignItems: 'center', gap: 2,
  },
  crystalTier: { color: GOLD, fontSize: 14, fontWeight: '900' },
  crystalIco: { fontSize: 22, marginVertical: 0 },
  crystalPriceWrap: {
    flexDirection: 'row', alignItems: 'center', gap: 2,
    backgroundColor: 'rgba(0,0,0,0.4)',
    paddingHorizontal: 6, paddingVertical: 1, borderRadius: 4,
  },
  crystalPriceIco: { fontSize: 9 },
  crystalPrice: { color: '#fff', fontSize: 9, fontWeight: '900' },

  /* BLOCCO 7 — MODE PANEL (right rail) */
  modePanel: {
    position: 'absolute', top: 108, right: 8,
    width: 62, gap: 5, zIndex: 18,
  },
  modeTile: {
    width: '100%', aspectRatio: 1, borderRadius: 6, overflow: 'hidden',
    borderWidth: 1.5, borderColor: 'rgba(255,215,0,0.50)',
    shadowColor: '#000', shadowOpacity: 0.45, shadowRadius: 3,
  },
  modeTileInner: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 2 },
  modeIco: { fontSize: 22 },
  modeLabel: { color: GOLD_PALE, fontSize: 8, fontWeight: '900', letterSpacing: 0.5 },

  /* BLOCCO 8 — MAIN BANNER (summon rate-up) */
  mainBanner: {
    position: 'absolute', bottom: 70, right: 78,
    width: 170, height: 62,
    borderRadius: 8, overflow: 'hidden',
    borderWidth: 1.5, borderColor: GOLD,
    zIndex: 17,
    shadowColor: GOLD, shadowOpacity: 0.3, shadowRadius: 6,
  },
  bannerInner: {
    flex: 1, flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 10, paddingVertical: 6, overflow: 'hidden',
  },
  bannerLeft: { flex: 1 },
  bannerTag: {
    color: NIGHT_0, fontSize: 8, fontWeight: '900',
    backgroundColor: GOLD,
    alignSelf: 'flex-start',
    paddingHorizontal: 5, paddingVertical: 1,
    borderRadius: 3, letterSpacing: 0.5,
  },
  bannerTitle: {
    color: GOLD, fontSize: 14, fontWeight: '900',
    marginTop: 2, letterSpacing: 0.3,
  },
  bannerSub: { color: 'rgba(255,255,255,0.75)', fontSize: 8, fontWeight: '700' },
  bannerBtn: {
    marginTop: 3, alignSelf: 'flex-start',
    backgroundColor: 'rgba(255,215,0,0.2)',
    paddingHorizontal: 8, paddingVertical: 2,
    borderRadius: 4, borderWidth: 1, borderColor: GOLD,
  },
  bannerBtnTxt: { color: GOLD, fontSize: 9, fontWeight: '900', letterSpacing: 0.8 },
  bannerSparkle: {
    position: 'absolute', right: 8, top: 6,
    fontSize: 20,
  },

  /* BLOCCO 9 — CHAT / NOTIF PANEL */
  chatPanel: {
    position: 'absolute', bottom: 68, left: 8,
    width: 230, height: 64,
    borderRadius: 8, overflow: 'hidden',
    borderWidth: 1.5, borderColor: 'rgba(255,215,0,0.45)',
    zIndex: 17,
  },
  chatPanelOpen: {
    height: 170,
  },
  chatInner: { flex: 1 },
  chatHeader: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 8, paddingVertical: 5,
    borderBottomWidth: 1, borderBottomColor: 'rgba(255,215,0,0.25)',
    backgroundColor: 'rgba(0,0,0,0.35)',
  },
  chatIco: { fontSize: 12 },
  chatTitle: { color: GOLD_PALE, fontSize: 9, fontWeight: '900', letterSpacing: 0.6, flex: 1 },
  chatToggle: { color: GOLD, fontSize: 10, fontWeight: '900' },
  chatBody: { flex: 1, paddingHorizontal: 8, paddingVertical: 4 },
  chatMsg: { flexDirection: 'row', gap: 5, marginBottom: 3, alignItems: 'flex-start' },
  chatSysTag: { color: '#F7B85C', fontSize: 9, fontWeight: '900' },
  chatFrom: { color: '#6EC8FF', fontSize: 9, fontWeight: '900' },
  chatMsgTxt: { color: '#E8E8F0', fontSize: 9, fontWeight: '600', flex: 1 },
  chatPreview: {
    flexDirection: 'row', gap: 5, paddingHorizontal: 8, paddingVertical: 5,
    alignItems: 'center',
  },
  chatPreviewTag: { color: '#F7B85C', fontSize: 8, fontWeight: '900' },
  chatPreviewTxt: { color: '#E8E8F0', fontSize: 9, fontWeight: '600', flex: 1 },

  /* BLOCCO 10 — BOTTOM NAV (solo proprietà base; positioning fatto inline
     tramite useWindowDimensions per essere responsive) */
  bottomNav: {
    position: 'absolute', bottom: 0, left: 0, right: 0,
    zIndex: 25,
  },
  bottomNavBg: { ...StyleSheet.absoluteFillObject },
  navFrameImg: {
    position: 'absolute',
    width: '100%', height: '100%',
    left: 0, top: 0,
  },
  navIconArea: {
    position: 'absolute',
    left: 0, right: 0,
    alignItems: 'center', justifyContent: 'center',
  },
  navLabelArea: {
    position: 'absolute',
    left: 1, right: 1,
    alignItems: 'center', justifyContent: 'center',
  },
  navPressedOverlay: {
    position: 'absolute',
    left: '12%', top: '10%',
    right: '12%', bottom: '10%',
    backgroundColor: 'rgba(0,0,0,0.22)',
    borderRadius: 6,
  },
  navIco: { fontSize: 15 },
  navIconImg: {
    width: '100%', height: '100%',
  },
  navLabel: {
    color: GOLD_PALE, fontSize: 7, fontWeight: '900',
    letterSpacing: 0.2, textAlign: 'center',
  },

  /* ── vecchi stili icon-wrap (mantengo come fallback per compatibilità) ── */
  navIconWrap: {
    width: 38, height: 38, borderRadius: 8,
    borderWidth: 1.2, borderColor: 'rgba(255,215,0,0.45)',
    alignItems: 'center', justifyContent: 'center',
    shadowColor: '#000', shadowOpacity: 0.5, shadowRadius: 3,
  },

  /* PLAY CENTRALE — mobile-first. Ancora alla stessa baseline dei side buttons
     (bottom 8 nel navInnerRow) ma con altezza maggiore per sporgere verso l'alto
     sopra la fascia piatta e dentro lo stemma centrale della barra base. */
  playShield: {
    width: 72, height: 86,
    marginHorizontal: 4,
    alignItems: 'center', justifyContent: 'center',
  },
  playShieldImg: {
    width: '100%', height: '100%',
  },
  playShieldOuter: {
    flex: 1, borderRadius: 12, padding: 2.5,
    shadowColor: GOLD, shadowOpacity: 0.8, shadowRadius: 8, elevation: 12,
  },
  playShieldInner: {
    flex: 1, borderRadius: 10,
    alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.3)',
  },
  playText: { color: GOLD, fontSize: 21, fontWeight: '900', letterSpacing: 2, textShadowColor: '#000', textShadowRadius: 4 },
  playSubText: { color: GOLD_PALE, fontSize: 8, fontWeight: '800', letterSpacing: 1.5, marginTop: 1 },

  /* BLOCCO 11 — OVERFLOW MODAL */
  modalBackdrop: {
    flex: 1, backgroundColor: 'rgba(0,0,0,0.75)',
    justifyContent: 'flex-end',
  },
  modalCard: {
    borderTopLeftRadius: 18, borderTopRightRadius: 18,
    paddingTop: 14, paddingHorizontal: 14, paddingBottom: 6,
    maxHeight: '90%',
    borderTopWidth: 2, borderTopColor: GOLD,
  },
  modalHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    marginBottom: 6,
  },
  modalTitle: { color: GOLD, fontSize: 15, fontWeight: '900', letterSpacing: 0.6 },
  modalClose: { color: '#fff', fontSize: 22, paddingHorizontal: 6 },
  modalSub: { color: '#B0B8D8', fontSize: 10, marginBottom: 12, fontStyle: 'italic' },
  modalGrid: {
    flexDirection: 'row', flexWrap: 'wrap', gap: 8, justifyContent: 'flex-start',
  },
  modalItem: {
    width: '15.5%', aspectRatio: 1,
    borderRadius: 8, overflow: 'hidden',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.30)',
  },
  modalItemInner: {
    flex: 1, alignItems: 'center', justifyContent: 'center', gap: 3, padding: 4,
  },
  modalItemIco: { fontSize: 22 },
  modalItemLabel: {
    color: '#fff', fontSize: 9, fontWeight: '800',
    textAlign: 'center',
  },

  /* ─────────── SLOT ASSET-DRIVEN (fallback tecnici neutri) ─────────── */
  bgReadabilityOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(8,14,38,0.30)', // overlay minimale per leggibilità UI, nessun bloom
  },
  placeholderFill: {
    flex: 1, width: '100%', height: '100%',
    alignItems: 'center', justifyContent: 'center',
    backgroundColor: 'rgba(27,53,112,0.92)',
    borderRadius: 18,
  },
  modeTileInnerFallback: {
    flex: 1, alignItems: 'center', justifyContent: 'center', gap: 2,
  },
  navIconWrapFallback: {
    flex: 1, width: '100%', height: '100%',
    alignItems: 'center', justifyContent: 'center',
    borderRadius: 8,
  },
  bannerInnerAbs: {
    flex: 1, overflow: 'hidden',
  },

  /* Server time phase (dev info) */
  serverPhase: {
    color: GOLD_PALE, fontSize: 8, fontWeight: '700',
    marginTop: 2, letterSpacing: 0.4, textTransform: 'uppercase',
  },

  /* Badge fase temporale (dev/QA) */
  phaseBadge: {
    position: 'absolute',
    top: 4, left: '50%',
    transform: [{ translateX: -90 }],
    width: 180,
    paddingHorizontal: 8, paddingVertical: 3,
    borderRadius: 12,
    backgroundColor: 'rgba(0,0,0,0.55)',
    borderWidth: 1, borderColor: 'rgba(255,215,0,0.45)',
    zIndex: 99,
    alignItems: 'center',
  },
  phaseBadgeTxt: {
    color: GOLD_PALE, fontSize: 9, fontWeight: '900',
    letterSpacing: 0.6,
  },
});
