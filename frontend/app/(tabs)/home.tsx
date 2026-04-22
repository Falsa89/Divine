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
  Animated, InteractionManager,
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
  HOME_PROFILE_PANEL, HOME_CURRENCY_BAR, HOME_TOP_ACTIONS,
  HOME_LEFT_STACK, HOME_MODE_PANEL_ASSETS, HOME_MAIN_BANNER_ASSETS,
} from '../../constants/homeAssetsManifest';
import { AssetSlot, ButtonAssetSlot, type ButtonAsset } from '../../components/home/AssetSlot';
import { AssetBackedGradient } from '../../components/home/AssetBackedGradient';
import { SlotImage } from '../../components/home/SlotImage';
import { AvatarFrameSelector } from '../../components/home/AvatarFrameSelector';
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
const SHOW_PHASE_BADGE = false;

/* ==================================================================== */
export default function HomeTab() {
  const { user, refreshUser } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();  // notch/safe-area per iPhone landscape
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
  // Ref anti-restart: il preload gate DEVE partire UNA SOLA VOLTA per sessione.
  // Senza questo ref, cambi a `homeHero` / `phase` (useFocusEffect + sync server time)
  // ri-scatenano il useEffect, cancellano l'hard timer e azzerano il counter.
  const preloadStartedRef = useRef<boolean>(false);

  // ─── CROSSFADE GATE (anti-blackout) ─────────────────────────────────────
  // Il loading non è più un "early return" che smonta la loading screen e
  // mount-a poi la home (finestra di ~1-3 frame di blackout). La home viene
  // montata subito sotto un OVERLAY (LoadingScreen) che fa fade-out SOLO
  // quando la scena è visivamente pronta al primo frame utile.
  //
  // "Visivamente pronta" ≡ tutte queste condizioni vere:
  //   1) `!loading`           → dati utente/hero già caricati
  //   2) `preloadDone`        → asset core in cache (o hard timeout scattato)
  //   3) `homeFirstFrameReady`→ onLayout del root home triggerato + 2×rAF +
  //                             InteractionManager.runAfterInteractions ok
  //
  // Solo allora parte un Animated.timing(opacity 1→0) sull'overlay. A fine
  // animazione l'overlay viene smontato.
  const [homeFirstFrameReady, setHomeFirstFrameReady] = useState(false);
  const [overlayMounted, setOverlayMounted] = useState(true);
  const overlayOpacity = useRef(new Animated.Value(1)).current;
  const firstFrameSignaledRef = useRef<boolean>(false);

  // SERVER TIME + FASE TEMPORALE centralizzata (unico hook, nessun hardcode)
  const { phase, formatted: serverTime, synced } = useServerTimePhase(1);

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

  // PRELOAD GATE: appena loadData è finito (hero + user), prefetchiamo TUTTI
  // gli asset core della home in parallelo. NON dipendiamo da `synced`:
  // la sync temporale può arrivare in ritardo ma non deve bloccare la UI.
  //
  // Garanzie (richieste utente):
  //  - Nessun deadlock su `synced` → non è dipendenza del preload.
  //  - Hard timeout globale di 4s: se per qualunque motivo il preload non
  //    si conclude (network stallato, asset rotto, bug expo-asset su web),
  //    la home viene sbloccata comunque.
  //  - Promise.allSettled + timeout per-asset (3s) in preloadAssets().
  //  - Un asset fallito NON blocca gli altri né la home.
  //  - `preloadStartedRef` garantisce che il gate parta UNA SOLA VOLTA,
  //    impedendo a cambi su homeHero/phase di riavviarlo e cancellare il
  //    hard timer.
  useEffect(() => {
    if (loading) return;              // aspetta loadData (hero + user)
    if (preloadDone) return;          // già sbloccata
    if (preloadStartedRef.current) return; // già avviato in questa sessione
    preloadStartedRef.current = true;

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
      // Pack A v2 — Profile Panel (drop-in RGBA): 5 asset caricati prima del fade-in
      HOME_PROFILE_PANEL.frame,
      HOME_PROFILE_PANEL.avatarRing,
      HOME_PROFILE_PANEL.expBarBg,
      HOME_PROFILE_PANEL.expBarFill,
      HOME_PROFILE_PANEL.lvBadge,
      // Hero home: string URI remota o require locale — preloadAssets le gestisce entrambe
      homeHero?.asset_splash || homeHero?.asset_base || homeHero?.image_url,
    ];

    let canceled = false;

    // HARD TIMEOUT GLOBALE: qualunque cosa succeda, dopo 4s sblocchiamo.
    const HARD_TIMEOUT_MS = 4000;
    const hardTimer = setTimeout(() => {
      if (canceled) return;
      console.warn('[HomePreload] hard timeout reached — unblocking UI');
      setPreloadDone(true);
    }, HARD_TIMEOUT_MS);

    (async () => {
      try {
        const res = await preloadAssets(coreAssets, (done, total) => {
          if (!canceled) setPreloadProgress({ done, total });
        });
        if (!canceled) {
          console.log(`[HomePreload] ${res.loaded}/${res.total} loaded, ${res.failed} failed`);
        }
      } catch (e) {
        console.warn('[HomePreload] error (ignored):', e);
      } finally {
        if (!canceled) {
          clearTimeout(hardTimer);
          setPreloadDone(true);
        }
      }
    })();

    return () => {
      canceled = true;
      clearTimeout(hardTimer);
    };
    // NOTA: `synced` NON è nella dep list → il preload non è mai bloccato
    // dalla sync del server time. `homeHero`/`phase` sono letti ma non
    // dependenti: il ref `preloadStartedRef` garantisce single-run.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading]);

  // ─── FIRST-FRAME SIGNAL ────────────────────────────────────────────────
  // Chiamato da `onLayout` del root della home montata. L'evento `onLayout`
  // fires DOPO che React Native ha committato il layout di quel nodo. Con
  // un doppio requestAnimationFrame aspettiamo che il paint del frame
  // successivo sia stato schedulato, e con InteractionManager aspettiamo
  // che eventuali transizioni/interactions mount-time siano smaltite.
  // Solo allora la scena è davvero "visibile" e possiamo fadeare via
  // l'overlay senza rischio di blackout.
  const handleHomeRootLayout = useCallback(() => {
    if (firstFrameSignaledRef.current) return;
    firstFrameSignaledRef.current = true;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        InteractionManager.runAfterInteractions(() => {
          setHomeFirstFrameReady(true);
        });
      });
    });
  }, []);

  // ─── OVERLAY FADE-OUT ──────────────────────────────────────────────────
  // Parte SOLO quando tutte e 3 le condizioni sono soddisfatte. Non usiamo
  // mai delay arbitrari né progress finti al 99%: questo useEffect reagisce
  // esclusivamente allo stato reale.
  useEffect(() => {
    const ready = !loading && preloadDone && homeFirstFrameReady;
    if (!ready) return;
    if (!overlayMounted) return;
    const anim = Animated.timing(overlayOpacity, {
      toValue: 0,
      duration: 260,
      useNativeDriver: true,
    });
    anim.start(({ finished }) => {
      if (finished) setOverlayMounted(false);
    });
    return () => { anim.stop(); };
  }, [loading, preloadDone, homeFirstFrameReady, overlayMounted, overlayOpacity]);

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

  // NOTA: NON usiamo più early-return `if (loading || !preloadDone) return <Loading/>`
  // perché causava un blackout di 1-3 frame tra unmount del loading e primo paint
  // della home. Ora rendiamo SEMPRE la home (quando !loading) sotto un overlay
  // di loading che fa fade-out solo quando la scena è visivamente pronta.

  const overlayBlocksUI = loading || !preloadDone || !homeFirstFrameReady;

  return (
    <View style={s.container}>
      {/* HOME — montata appena i dati base sono disponibili. Resta "sotto"
          l'overlay fino a `homeFirstFrameReady`. In questo modo React ha
          tempo di completare layout + primo paint mentre l'utente vede ancora
          la loading screen → zero blackout. */}
      {!loading && (
        <View style={StyleSheet.absoluteFillObject} onLayout={handleHomeRootLayout}>
          {/* BLOCCO 1 — BACKGROUND full-bleed SOTTO il notch (vogliamo
              il castello/cielo che arriva fino al bordo fisico del device) */}
          <HomeBackground scene={CURRENT_SCENE} phase={phase} />

          {/* BLOCCO 2 — HERO LAYER full-bleed (hero centrato nello schermo,
              anche lui può "respirare" sotto il dynamic island) */}
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

          {/* SAFE-AREA WRAPPER — contiene tutti i pannelli UI interattivi.
              Gli insets left/right proteggono dal notch/dynamic island
              iPhone in landscape, top/bottom da status-bar/gesture-bar.
              I pannelli figli usano position absolute con coordinate
              relative a QUESTO wrapper, quindi "left:6" parte automaticamente
              DOPO il notch. */}
          <View
            pointerEvents="box-none"
            style={{
              position: 'absolute',
              left: insets.left,
              right: insets.right,
              top: insets.top,
              bottom: 0,
            }}
          >
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
        </View>
      )}

      {/* OVERLAY LOADING — crossfade anti-blackout. Coperto fino a che la
          scena non è visivamente pronta, poi fade-out 260ms, poi unmount. */}
      {overlayMounted && (
        <Animated.View
          style={[
            StyleSheet.absoluteFillObject,
            { opacity: overlayOpacity, zIndex: 9999 },
          ]}
          pointerEvents={overlayBlocksUI ? 'auto' : 'none'}
        >
          <HomeLoadingScreen
            done={preloadProgress.done}
            total={preloadProgress.total}
            label={
              loading
                ? 'CARICAMENTO DATI…'
                : !preloadDone
                  ? 'PREPARAZIONE HOMEPAGE…'
                  : 'AVVIO SCENA…'
            }
          />
        </Animated.View>
      )}
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

  // ─── Mobile-first responsive sizing ────────────────────────────────
  // Mobile landscape detection basata su ALTEZZA viewport (più robusta di
  // vw<900, che falliva su iPhone 14 Pro Max 932×430). vh<500 cattura TUTTI
  // gli smartphone landscape (SE 375 → Pro Max 430) e lascia i tablet
  // (iPad ≥ 768 vh) nel ramo desktop.
  const { height: vh, width: vw } = useWindowDimensions();
  // ─── RESPONSIVE TIERS (phoneLandscape / tablet / desktop) ──────────
  //   phoneLandscape: vh < 500        (iPhone SE 375 → Pro Max 430)
  //   tablet:         500 ≤ vh < 900  (iPad mini/air landscape)
  //   desktop:        vh ≥ 900        (web desktop)
  // NB: "isMobile" mantenuto come alias di phoneLandscape per compat locale.
  const isPhone  = vh < 500;
  const isTablet = vh >= 500 && vh < 900;
  const isMobile = isPhone;   // alias locale (non esportato)

  // ─── PANEL MOBILE RECALIBRATION (v3 — leggibile, non "desktop rimpicciolito") ─
  // Precedente pass v2 (210×80, font 8-11pt) risultava micro-scalato su
  // phone landscape reale: DPR 3x su iPhone rendeva i font 8-9pt ai limiti
  // della leggibilità HIG. Ora: panel più presente (250×89), typography
  // dichiaratamente pensata per smartphone landscape.
  const panelW     = isPhone ? 250 : isTablet ? 300 : 340;
  const panelRatio = isPhone ? 2.8 : 2.9;
  // Slot avatar occupa ~34% della panelW sul frame 3:1 → mantiene proporzione
  // corretta con ring decor. 250 * 0.34 = 85.
  const padL     = isPhone ? Math.round(panelW * 0.34) : isTablet ? 92 : 104;
  const padR     = isPhone ? 22  : isTablet ? 32 : 42;
  const padT     = isPhone ? 11  : isTablet ? 16 : 20;
  const padB     = isPhone ? 11  : isTablet ? 15 : 18;

  // ─── AVATAR — dimensioni bilanciate col panel ───────────────────────
  // panelH = 250/2.8 = 89.3 → avFrameW target ≈ 75% panelH = 67 → 68
  // avSize (portrait) ≈ 70% avFrameW = 47.6 → 48 (1:1 perfetto)
  const avSize   = isPhone ? 48 : isTablet ? 60 : 72;
  const avFrameW = isPhone ? 68 : isTablet ? 82 : 98;
  const avInit   = isPhone ? 19 : isTablet ? 22 : 26;
  // Anchor: slot centrato a 17% panelW (standard frame 3:1 premium).
  //   17% di 250 = 42.5 → avLeft = 42.5 - 34 = 8.5 → 9
  const avLeft   = isPhone
    ? Math.round(panelW * 0.17 - avFrameW / 2)
    : isTablet
      ? Math.round(panelW * 0.15 - avFrameW / 2)
      : 6;
  // avTop: centro verticale dello slot del frame (50% panelH − avFrameW/2)
  const avTop    = isPhone || isTablet
    ? Math.round((panelW / panelRatio) * 0.50 - avFrameW / 2)
    : undefined;

  // ─── LEVEL BADGE — scalato col ring ─────────────────────────────────
  const lvSize   = isPhone ? 26 : isTablet ? 32 : 38;
  const lvFont   = isPhone ? 10 : isTablet ? 12 : 13;

  // ─── TYPOGRAPHY — leggibile su DPR 3x smartphone (minimum 10pt) ─────
  const nameFS   = isPhone ? 13 : isTablet ? 13 : 14;
  const pwrFS    = isPhone ? 11 : isTablet ? 11 : 11;
  const pwrLblFS = isPhone ? 10 : 9;
  const pillFS   = isPhone ? 10 : 9;
  const expFS    = isPhone ? 10 : 9;
  const expH     = isPhone ? 10 : 12;

  // Open/Close del selector avatar/frame (stub tecnico)
  const [selectorOpen, setSelectorOpen] = React.useState<false | 'avatar' | 'frame'>(false);

  return (
    <View style={[s.profileWrap, { width: panelW, aspectRatio: panelRatio }]}>
      <AssetBackedGradient
        source={HOME_PROFILE_PANEL.frame}
        decorSource={HOME_PROFILE_PANEL.decor}
        capInsets={HOME_PROFILE_PANEL.capInsets}
        fallbackColors={['rgba(11,23,60,0.95)', 'rgba(8,15,40,0.85)']}
        style={[
          s.profilePanel,
          { paddingLeft: padL, paddingRight: padR, paddingTop: padT, paddingBottom: padB },
        ]}
      >
        {/* AVATAR + LV BADGE — tap apre AvatarFrameSelector (tab Avatar).
            ARCHITETTURA REALE basata su verifica PIL dell'asset:
              ► `home_profile_avatar_ring.png` NON è un ring trasparente-in-
                mezzo. Center pixel verificato = (244,244,244, alpha 255)
                → FULLY OPAQUE. È un *portrait placeholder composito*:
                cornice dorata + inner area bianca-crema dove l'utente caricherà
                la sua foto avatar. Usarlo come overlay TOP avrebbe coperto
                la foto utente → errore logico.
              ► Corretta architettura:
                1. avatarRing come BASE (si vede sempre, forma lo slot).
                2. User avatar / initial POSIZIONATA SOPRA nel centro crema.
                3. lvBadge sopra tutto nell'angolo SE.
              ► Quando in futuro l'utente caricherà un avatar:
                renderizzare l'immagine come cerchio cropped sopra il ring,
                sostituendo l'inner crema. Il ring dorato resta visibile
                come cornice. */}
        <View
          style={[
            s.avatarFrame,
            {
              width: avFrameW, height: avFrameW,
              left: avLeft,
              top: avTop,
            },
          ]}
          pointerEvents="box-none"
        >
          {/* (1) AVATAR RING — BASE layer (cornice+inner crema, asset-driven) */}
          <TouchableOpacity
            onPress={() => setSelectorOpen('avatar')}
            onLongPress={() => setSelectorOpen('frame')}  // long-press: tab Frames
            activeOpacity={0.85}
            style={{
              position: 'absolute',
              left: 0, top: 0,
              width: avFrameW, height: avFrameW,
              alignItems: 'center', justifyContent: 'center',
            }}
          >
            {HOME_PROFILE_PANEL.avatarRing ? (
              <RNImage
                source={HOME_PROFILE_PANEL.avatarRing}
                style={{
                  position: 'absolute',
                  left: 0, top: 0,
                  width: avFrameW, height: avFrameW,
                }}
                resizeMode="contain"
                pointerEvents="none"
              />
            ) : (
              // Fallback tecnico se ring asset mancante: cerchio NIGHT+border
              <View
                style={[
                  s.avatarInner,
                  { width: avSize, height: avSize, borderRadius: avSize / 2 },
                ]}
              />
            )}

            {/* (2) INITIAL / USER PORTRAIT — sopra il ring, centrato nell'inner. */}
            {HOME_PROFILE_PANEL.avatarPlaceholder ? (
              <RNImage
                source={HOME_PROFILE_PANEL.avatarPlaceholder}
                style={{
                  width: avSize, height: avSize, borderRadius: avSize / 2,
                  // Sopra il ring base
                }}
                resizeMode="cover"
              />
            ) : (
              <Text
                style={[
                  s.avatarInitial,
                  {
                    fontSize: avInit,
                    // Dark contrast sopra l'inner crema del ring
                    color: NIGHT_1,
                    textShadowColor: 'rgba(255,255,255,0.6)',
                    textShadowOffset: { width: 0, height: 1 },
                    textShadowRadius: 1,
                  },
                ]}
              >
                {String(name)[0]?.toUpperCase() || 'P'}
              </Text>
            )}
          </TouchableOpacity>

          {/* (3) Level badge — angolo SE sopra ring */}
          <View
            style={[
              s.lvBadge,
              {
                width: lvSize, height: lvSize,
                right: -Math.round(lvSize * 0.15),
                bottom: -Math.round(lvSize * 0.10),
              },
            ]}
            pointerEvents="none"
          >
            {HOME_PROFILE_PANEL.lvBadge ? (
              <RNImage
                source={HOME_PROFILE_PANEL.lvBadge}
                style={[StyleSheet.absoluteFillObject as any, { width: '100%', height: '100%' }]}
                resizeMode="contain"
              />
            ) : null}
            <Text style={[s.lvBadgeTxt, { fontSize: lvFont }]}>{level}</Text>
          </View>
        </View>

        {/* TEXT BLOCK */}
        <View style={s.profileRow1}>
          <View style={{ flex: 1 }}>
            <Text style={[s.profName, { fontSize: nameFS }]} numberOfLines={1}>{name}</Text>
            <View style={s.expWrap}>
              <View style={[s.expBarBg, { height: expH, borderRadius: expH / 2 }]}>
                {HOME_PROFILE_PANEL.expBarBg ? (
                  <RNImage
                    source={HOME_PROFILE_PANEL.expBarBg}
                    style={[StyleSheet.absoluteFillObject as any, { width: '100%', height: '100%' }]}
                    resizeMode="stretch"
                  />
                ) : null}
                <AssetBackedGradient
                  source={HOME_PROFILE_PANEL.expBarFill}
                  fallbackColors={[GOLD_PALE, GOLD]}
                  fallbackStart={{ x: 0, y: 0 }} fallbackEnd={{ x: 1, y: 0 }}
                  style={[s.expBarFill, { width: `${Math.min(100, (exp / expMax) * 100)}%` }] as any}
                />
              </View>
              <Text style={[s.expTxt, { fontSize: expFS }]}>{exp}/{expMax}</Text>
            </View>
          </View>
        </View>

        {/* POWER */}
        <TouchableOpacity
          style={s.powerRow}
          onPress={() => router.push('/profile' as any)}
          activeOpacity={0.8}
        >
          <Text style={[s.powerIcon, { fontSize: pwrFS + 1 }]}>{'\u26A1'}</Text>
          <Text style={[s.powerLbl, { fontSize: pwrLblFS }]}>POWER</Text>
          <Text style={[s.powerVal, { fontSize: pwrFS }]}>{Number(power).toLocaleString()}</Text>
        </TouchableOpacity>

        {/* PILLS RIGA UNICA: VIP · SP · Title */}
        <View style={s.pillsRow}>
          <TouchableOpacity style={s.vipPill} activeOpacity={0.7}
            onPress={() => router.push('/vip' as any)}>
            <Text style={[s.vipStar, { fontSize: pillFS - 1 }]}>{'\u2605'}</Text>
            <Text style={[s.vipTxt, { fontSize: pillFS }]}>VIP {vip}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={s.spiritoPill} activeOpacity={0.7}
            onPress={() => router.push('/profile' as any)}>
            <Text style={[s.spiritoIco, { fontSize: pillFS - 1 }]}>{'\uD83D\uDD2E'}</Text>
            <Text style={[s.spiritoTxt, { fontSize: pillFS }]}>SP {spirito}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={s.titleBadge} activeOpacity={0.7}
            onPress={() => router.push('/achievements' as any)}>
            <Text style={[s.titleTxt, { fontSize: pillFS }]} numberOfLines={1}>
              {'\u2756'} {title}
            </Text>
          </TouchableOpacity>
        </View>
      </AssetBackedGradient>

      {/* STUB SELECTOR — avatar (tap breve) / frame (long-press) */}
      <AvatarFrameSelector
        visible={!!selectorOpen}
        initialTab={selectorOpen === 'frame' ? 'frame' : 'avatar'}
        onClose={() => setSelectorOpen(false)}
      />
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
  const goldCfg = HOME_CURRENCY_BAR.gold || {};
  const gemsCfg = HOME_CURRENCY_BAR.gems || {};
  return (
    <View style={s.currencyWrap}>
      {/* GOLD PILL — asset-driven (Pack B.gold). Fallback: gradient+border. */}
      <AssetBackedGradient
        source={goldCfg.frame}
        capInsets={goldCfg.capInsets}
        fallbackColors={['rgba(20,33,72,0.95)', 'rgba(8,15,40,0.85)']}
        style={[s.currencyPill, { borderColor: 'rgba(255,215,0,0.65)' }]}
      >
        {goldCfg.icon ? (
          <RNImage source={goldCfg.icon} style={{ width: 18, height: 18 }} resizeMode="contain" />
        ) : (
          <Text style={s.currencyIco}>{'\uD83D\uDCB0'}</Text>
        )}
        <Text style={s.currencyTxt}>{Number(gold).toLocaleString()}</Text>
        <TouchableOpacity style={s.plusBtn} onPress={onAddGems} activeOpacity={0.7}>
          <ButtonAssetSlot
            asset={goldCfg.plusBtn}
            state="default"
            style={s.plusBtnInner as any}
            fallback={
              <LinearGradient colors={[GOLD_PALE, GOLD]} style={s.plusBtnInner}>
                <Text style={s.plusTxt}>+</Text>
              </LinearGradient>
            }
          />
        </TouchableOpacity>
      </AssetBackedGradient>

      {/* GEMS PILL — asset-driven (Pack B.gems). Fallback: gradient+border. */}
      <AssetBackedGradient
        source={gemsCfg.frame}
        capInsets={gemsCfg.capInsets}
        fallbackColors={['rgba(20,33,72,0.95)', 'rgba(8,15,40,0.85)']}
        style={[s.currencyPill, { borderColor: 'rgba(100,170,255,0.65)' }]}
      >
        {gemsCfg.icon ? (
          <RNImage source={gemsCfg.icon} style={{ width: 18, height: 18 }} resizeMode="contain" />
        ) : (
          <Text style={s.currencyIco}>{'\uD83D\uDC8E'}</Text>
        )}
        <Text style={s.currencyTxt}>{Number(gems).toLocaleString()}</Text>
        <TouchableOpacity style={s.plusBtn} onPress={onAddGems} activeOpacity={0.7}>
          <ButtonAssetSlot
            asset={gemsCfg.plusBtn}
            state="default"
            style={s.plusBtnInner as any}
            fallback={
              <LinearGradient colors={['#6EC8FF', '#2C7DD8']} style={s.plusBtnInner}>
                <Text style={[s.plusTxt, { color: '#fff' }]}>+</Text>
              </LinearGradient>
            }
          />
        </TouchableOpacity>
      </AssetBackedGradient>
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
    { key: 'wheel', icon: '\uD83C\uDFA1', label: 'WHEEL', onPress: () => goTo('wheel'), iconOverride: HOME_TOP_ACTIONS.iconWheel },
    { key: 'quest', icon: '\uD83D\uDCDC', label: 'QUEST', onPress: () => goTo('quest'), iconOverride: HOME_TOP_ACTIONS.iconQuest },
    { key: 'event', icon: '\uD83C\uDF81', label: 'EVENT', onPress: () => goTo('event'), iconOverride: HOME_TOP_ACTIONS.iconEvent },
  ];

  const items = [...base, ...eventSlots];

  return (
    <View style={s.topActionsRow}>
      {items.map(it => {
        // Asset resolution: priorità a asset specifico (HOME_BUTTONS[key]),
        // poi frame comune (HOME_TOP_ACTIONS.commonFrame), poi fallback emoji.
        const specificAsset = (HOME_BUTTONS as any)[it.key] as ButtonAsset | undefined;
        const hasSpecific = !!(specificAsset && (specificAsset.default || specificAsset.pressed));
        const mergedAsset: ButtonAsset | undefined = hasSpecific
          ? specificAsset
          : HOME_TOP_ACTIONS.commonFrame;
        return (
          <TouchableOpacity key={it.key} style={s.topActBtn} activeOpacity={0.75} onPress={it.onPress}>
            <ButtonAssetSlot
              asset={mergedAsset}
              state="default"
              style={s.topActIconBox as any}
              fallback={
                <View style={s.placeholderFill}>
                  {(it as any).iconOverride ? (
                    <RNImage source={(it as any).iconOverride} style={{ width: 28, height: 28 }} resizeMode="contain" />
                  ) : (
                    <Text style={s.topActIco}>{it.icon}</Text>
                  )}
                </View>
              }
            />
            <Text style={s.topActLabel}>{it.label}</Text>
          </TouchableOpacity>
        );
      })}
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
      {/* SERVER TIME BOX — asset-driven frame (Pack D.serverTimeFrame). */}
      <View style={s.serverTimeBox}>
        {HOME_LEFT_STACK.serverTimeFrame ? (
          <RNImage
            source={HOME_LEFT_STACK.serverTimeFrame}
            style={[StyleSheet.absoluteFillObject as any, { width: '100%', height: '100%' }]}
            resizeMode="stretch"
          />
        ) : null}
        <Text style={s.serverLabel}>
          {HOME_LEFT_STACK.serverTimeIcon ? '' : '\uD83D\uDD50 '}
          SERVER TIME {synced ? '' : '·sync'}
        </Text>
        <Text style={s.serverValue}>{serverTime}</Text>
        <Text style={s.serverPhase}>fase: {phase}</Text>
      </View>

      {/* SP OFFER — asset-driven frame (Pack D.spOfferFrame). Fallback: gradient red. */}
      <TouchableOpacity style={s.spOfferBtn} onPress={onSpOffer} activeOpacity={0.85}>
        <AssetBackedGradient
          source={HOME_LEFT_STACK.spOfferFrame}
          fallbackColors={['#D13B3B', '#8A1515']}
          fallbackStart={{ x: 0, y: 0 }} fallbackEnd={{ x: 1, y: 1 }}
          style={s.spOfferGrad}
        >
          {HOME_LEFT_STACK.spOfferBadge ? (
            <RNImage source={HOME_LEFT_STACK.spOfferBadge} style={{ width: 28, height: 28 }} resizeMode="contain" />
          ) : (
            <Text style={s.spOfferBadge}>SP</Text>
          )}
          <View style={{ flex: 1 }}>
            <Text style={s.spOfferTitle}>SP OFFER</Text>
            <Text style={s.spOfferSub}>Bundle esclusivo</Text>
          </View>
          {HOME_LEFT_STACK.spOfferArrow ? (
            <RNImage source={HOME_LEFT_STACK.spOfferArrow} style={{ width: 14, height: 14 }} resizeMode="contain" />
          ) : (
            <Text style={s.spOfferArrow}>{'\u203A'}</Text>
          )}
        </AssetBackedGradient>
      </TouchableOpacity>

      {/* CRYSTAL PACKS — frame asset-driven per-tier (Pack D.crystalPackFrameByTier). */}
      <View style={s.crystalRow}>
        {[
          { tier: 2, gems: 100,  col1: '#1D4C8A', col2: '#0A1F3C' },
          { tier: 3, gems: 150,  col1: '#4B2080', col2: '#1A0A3C' },
        ].map((x, i) => {
          const perTier = HOME_LEFT_STACK.crystalPackFrameByTier?.[x.tier];
          const frameSrc = perTier || HOME_LEFT_STACK.crystalPackFrame;
          return (
            <TouchableOpacity
              key={i}
              style={s.crystalPack}
              onPress={() => goTo('goldPlus')}
              activeOpacity={0.85}
            >
              <AssetBackedGradient
                source={frameSrc}
                fallbackColors={[x.col1, x.col2]}
                style={s.crystalPackInner}
              >
                <Text style={s.crystalTier}>×{x.tier}</Text>
                {HOME_LEFT_STACK.crystalPackIcon ? (
                  <RNImage source={HOME_LEFT_STACK.crystalPackIcon} style={{ width: 28, height: 28 }} resizeMode="contain" />
                ) : (
                  <Text style={s.crystalIco}>{'\uD83D\uDC8E'}</Text>
                )}
                <View style={s.crystalPriceWrap}>
                  <Text style={s.crystalPriceIco}>{'\uD83D\uDC8E'}</Text>
                  <Text style={s.crystalPrice}>{x.gems}</Text>
                </View>
              </AssetBackedGradient>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

/* ═══════════════════════════════════════════════════════════════════
 *  BLOCCO 7 — HomeModePanel
 *  Arena / Blessing / Trial / Battle / Research (verticale, a destra)
 * ═══════════════════════════════════════════════════════════════════ */
function HomeModePanel({ goTo }: any) {
  const modes: Array<{ key: any; label: string; ico: string; iconOverride?: any }> = [
    { key: 'arena',    label: 'ARENA',    ico: '\u2694\uFE0F', iconOverride: HOME_MODE_PANEL_ASSETS.iconArena },
    { key: 'blessing', label: 'BLESSING', ico: '\uD83D\uDCFF', iconOverride: HOME_MODE_PANEL_ASSETS.iconBlessing },
    { key: 'trial',    label: 'TRIAL',    ico: '\u26AA'      , iconOverride: HOME_MODE_PANEL_ASSETS.iconTrial },
    { key: 'battle',   label: 'BATTLE',   ico: '\u2620\uFE0F', iconOverride: HOME_MODE_PANEL_ASSETS.iconBattle },
    { key: 'research', label: 'RESEARCH', ico: '\uD83D\uDD2C', iconOverride: HOME_MODE_PANEL_ASSETS.iconResearch },
  ];
  return (
    <View style={s.modePanel}>
      {modes.map(m => {
        const specificAsset = (HOME_BUTTONS as any)[m.key] as ButtonAsset | undefined;
        const hasSpecific = !!(specificAsset && (specificAsset.default || specificAsset.pressed));
        const mergedAsset: ButtonAsset | undefined = hasSpecific
          ? specificAsset
          : HOME_MODE_PANEL_ASSETS.commonFrame;
        return (
          <TouchableOpacity
            key={m.key}
            style={s.modeTile}
            onPress={() => goTo(m.key)}
            activeOpacity={0.82}
          >
            <ButtonAssetSlot
              asset={mergedAsset}
              state="default"
              style={s.modeTileInner as any}
              fallback={
                <LinearGradient
                  colors={['rgba(27,53,112,0.92)', 'rgba(10,24,56,0.92)']}
                  style={s.modeTileInnerFallback}
                >
                  {m.iconOverride ? (
                    <RNImage source={m.iconOverride} style={{ width: 26, height: 26 }} resizeMode="contain" />
                  ) : (
                    <Text style={s.modeIco}>{m.ico}</Text>
                  )}
                  <Text style={s.modeLabel}>{m.label}</Text>
                </LinearGradient>
              }
            />
          </TouchableOpacity>
        );
      })}
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
      {/* FRAME principale del banner — Pack F.frame (9-slice opzionale). */}
      <AssetBackedGradient
        source={HOME_MAIN_BANNER_ASSETS.frame || HOME_BANNERS.summonMain.frame}
        capInsets={HOME_MAIN_BANNER_ASSETS.capInsets}
        fallbackColors={['rgba(27,53,112,0.97)', 'rgba(8,15,40,0.95)']}
        fallbackStart={{ x: 0, y: 0 }} fallbackEnd={{ x: 1, y: 1 }}
        style={s.bannerInner}
      >
        {/* Ribbon "RATE-UP" decorativo (opzionale) */}
        {HOME_MAIN_BANNER_ASSETS.ribbon ? (
          <RNImage
            source={HOME_MAIN_BANNER_ASSETS.ribbon}
            style={{ position: 'absolute', top: -6, left: -4, width: 80, height: 22 }}
            resizeMode="contain"
            pointerEvents="none"
          />
        ) : null}
        <View style={s.bannerLeft}>
          {HOME_MAIN_BANNER_ASSETS.rateUpBadge ? (
            <RNImage
              source={HOME_MAIN_BANNER_ASSETS.rateUpBadge}
              style={{ width: 60, height: 16, marginBottom: 2 }}
              resizeMode="contain"
            />
          ) : (
            <Text style={s.bannerTag}>RATE-UP</Text>
          )}
          <Text style={s.bannerTitle} numberOfLines={1}>{featuredName}</Text>
          <Text style={s.bannerSub}>Evoca ora</Text>
          {/* SUMMON CTA — ButtonAsset opzionale (Pack F.summonCta). */}
          <ButtonAssetSlot
            asset={HOME_MAIN_BANNER_ASSETS.summonCta}
            state="default"
            style={s.bannerBtn as any}
            fallback={
              <View style={s.bannerBtn}>
                <Text style={s.bannerBtnTxt}>SUMMON {'\u203A'}</Text>
              </View>
            }
          />
        </View>
        {HOME_MAIN_BANNER_ASSETS.sparkle ? (
          <RNImage
            source={HOME_MAIN_BANNER_ASSETS.sparkle}
            style={{ width: 22, height: 22, position: 'absolute', right: 10, top: 10 }}
            resizeMode="contain"
          />
        ) : (
          <Text style={s.bannerSparkle}>{'\u2728'}</Text>
        )}
      </AssetBackedGradient>
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
  const { width: vw, height: vh } = useWindowDimensions();
  const insets = useSafeAreaInsets();

  // === RESPONSIVE TIERS ===
  //   phoneLandscape: vh < 500  (iPhone/Android phones landscape)
  //   tablet:         500 ≤ vh < 900
  //   desktop:        vh ≥ 900
  const isPhone  = vh < 500;
  const isTablet = vh >= 500 && vh < 900;
  const isMobile = isPhone;   // alias interno (compat)

  // === BAR_W ===
  // Phone: cap 360 (era 400) → meno dominante. 46% vw (era 50%).
  // Tablet: invariato dal pass precedente.
  // Desktop: invariato.
  const BAR_W = isPhone
    ? Math.max(260, Math.min(vw * 0.46, 360))
    : isTablet
      ? Math.max(320, Math.min(vw * 0.58, 520))
      : Math.max(320, Math.min(vw * 0.62, 560));

  // === BAR_H ===
  // Phone: clip ulteriore → 42% del full (era 50%), clamp 18% vh (era 22%).
  //   A vw=844, BAR_W=360 → BAR_H_FULL = 154.2 → visible = min(64.8, 70.2) = 64.8 → 16.6% vh ✅
  // Tablet: 65% del full con clamp 25% vh.
  // Desktop: ratio naturale full (invariato).
  const BAR_RATIO_FULL = 1916 / 821;      // 2.334 nativo
  const BAR_H_FULL     = BAR_W / BAR_RATIO_FULL;
  const BAR_H_VISIBLE  = isPhone
    ? Math.min(BAR_H_FULL * 0.42, vh * 0.18)
    : isTablet
      ? Math.min(BAR_H_FULL * 0.65, vh * 0.25)
      : BAR_H_FULL;
  const BAR_H = BAR_H_VISIBLE;

  // === PLAY ===
  // Phone: 15% barra (era 17%), clamp 18% vh (era 21%) → PLAY meno debordante.
  const PLAY_W = isPhone
    ? Math.max(50, Math.min(BAR_W * 0.15, vh * 0.18))
    : isTablet
      ? Math.max(56, BAR_W * 0.18)
      : Math.max(58, BAR_W * 0.20);
  const PLAY_H = PLAY_W * (86 / 72);

  // === SIDE ICONS ===
  // Phone: 7.5% barra (era 8%) → meno presenti, coerenti con barra ridotta.
  const SIDE_W = isPhone
    ? Math.max(32, BAR_W * 0.075)
    : isTablet
      ? Math.max(34, BAR_W * 0.085)
      : Math.max(34, BAR_W * 0.090);
  const SIDE_H = SIDE_W * (48 / 42);
  const SIDE_GAP  = Math.max(1, BAR_W * (isPhone ? 0.0022 : 0.003));
  const GROUP_GAP = Math.max(3, BAR_W * (isPhone ? 0.009  : 0.012));

  // === BTN_BOTTOM ===
  // Phone: *0.18 (era *0.20) → icone rimangono al centro della fascia piatta
  // anche con BAR_H_VISIBLE ridotta.
  const BTN_BOTTOM = insets.bottom + 4 + Math.round(BAR_H_VISIBLE * (isPhone ? 0.18 : 0.22));

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
      {/* (1) BARRA BASE — àncora visiva. Centrata matematicamente al viewport.
          Contenitore a VISIBLE height con overflow:hidden. L'immagine è
          renderizzata al suo aspect ratio NATURALE (no stretch) e ancorata
          al bottom del contenitore: se BAR_H_VISIBLE < BAR_H_FULL (mobile),
          la decorazione superiore dell'asset viene clippata — la fascia
          funzionale (slot icone + medaglione) resta integralmente visibile. */}
      {HOME_NAV_BAR_BASE ? (
        <View
          style={{
            position: 'absolute',
            bottom: insets.bottom - 2,
            left: '50%',
            width: BAR_W,
            height: BAR_H_VISIBLE,
            transform: [{ translateX: -BAR_W / 2 }],
            overflow: 'hidden',
          }}
          pointerEvents="none"
        >
          <RNImage
            source={HOME_NAV_BAR_BASE}
            style={{
              position: 'absolute',
              bottom: 0, left: 0,
              width: BAR_W,
              height: BAR_H_FULL,   // aspect NATURALE, nessuno stretch
            }}
            resizeMode="contain"
          />
        </View>
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
        {left.map(n => {
          const { key, ...rest } = n;
          return (
            <NavBtn key={key} navKey={key} {...rest} width={SIDE_W} height={SIDE_H} />
          );
        })}
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
        {right.map(n => {
          const { key, ...rest } = n;
          return (
            <NavBtn key={key} navKey={key} {...rest} width={SIDE_W} height={SIDE_H} />
          );
        })}
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

  /* BLOCCO 3 — PROFILE PANEL (Pack A v2 asset-driven, MOBILE-FIRST) */
  profileWrap: {
    position: 'absolute', top: 6, left: 6,
    zIndex: 20,
    // width + aspectRatio vengono passati inline da HomeProfilePanel:
    //   mobile: 220 × (220/2.7) = 220 × 81
    //   desktop: 340 × (340/3) = 340 × 113
  },
  profilePanel: {
    // NO border CSS legacy, NO borderRadius legacy, NO shadow:
    // il nuovo frame asset fornisce bordo/ombra/profondità premium.
    width: '100%', height: '100%',
    // Padding allineato alle ZONE SICURE del frame Pack A v2:
    //  - top: 20 (ben sotto il bordo decorativo superiore + gemma centrata)
    //  - bottom: 18 (sopra il slot titolo basso del frame)
    //  - left: 104 (spazio per oval avatar integrato + gemma sinistra)
    //  - right: 42 (spazio per gemma destra decorativa)
    paddingTop: 20, paddingBottom: 18,
    paddingLeft: 104,
    paddingRight: 42,
    justifyContent: 'center',
  },
  profileRow1: { flexDirection: 'row', alignItems: 'center' },
  // Avatar dentro lo slot oval del frame — posizionamento absolute slot-based.
  // top/left/width/height passati inline da HomeProfilePanel (avTop/avLeft
  // proporzionali al panel). Non più flex-center generico.
  avatarFrame: {
    position: 'absolute',
    // NB: nessun `top: 0, bottom: 0, justifyContent: 'center'`:
    //     l'avatar è ora ancorato al vero slot del frame (premium look).
  },
  // Portrait CERCHIO PERFETTO. NO borderWidth/shadow legacy: il ring asset
  // (avatarRing overlay) fornisce bordo+glow premium; il border CSS
  // duplicato creava il fastidioso "cerchio appoggiato sopra".
  avatarInner: {
    width: 72, height: 72, borderRadius: 36,
    overflow: 'hidden',
    backgroundColor: NIGHT_1,
    alignItems: 'center', justifyContent: 'center',
  },
  avatarInitial: { color: GOLD, fontSize: 26, fontWeight: '900' },
  lvBadge: {
    // Posizione calibrata inline da HomeProfilePanel (right/bottom proporzionali
    // a lvSize). Solo proprietà non dipendenti dalla dimensione qui.
    position: 'absolute',
    alignItems: 'center', justifyContent: 'center',
  },
  lvBadgeTxt: {
    color: '#fff', fontSize: 13, fontWeight: '900',
    textShadowColor: '#000', textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 2,
  },
  profName: {
    color: GOLD, fontSize: 14, fontWeight: '900', letterSpacing: 0.4,
    marginBottom: 1,
  },
  expWrap: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    marginTop: 2,
  },
  expBarBg: {
    flex: 1, height: 12,
    borderRadius: 6, overflow: 'hidden',
    // Fallback color se l'asset expBarBg è undefined; con asset RGBA l'overlay lo copre.
    backgroundColor: 'rgba(0,0,0,0.35)',
  },
  expBarFill: { height: '100%' },
  expTxt: {
    color: '#F0E8D8', fontSize: 9, fontWeight: '800',
    minWidth: 40, textAlign: 'right',
  },

  powerRow: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    marginTop: 3, paddingVertical: 1, paddingHorizontal: 2,
    borderRadius: 3,
  },
  powerIcon: { fontSize: 11, color: GOLD_PALE },
  powerLbl: { color: GOLD_PALE, fontSize: 9, fontWeight: '900', letterSpacing: 0.6 },
  powerVal: { color: '#fff', fontSize: 11, fontWeight: '900', marginLeft: 'auto' },

  pillsRow: { flexDirection: 'row', gap: 5, marginTop: 3, alignItems: 'center' },
  vipPill: {
    flexDirection: 'row', alignItems: 'center', gap: 3,
    backgroundColor: 'rgba(178,34,34,0.5)',
    paddingHorizontal: 6, paddingVertical: 1, borderRadius: 3,
  },
  vipStar: { color: GOLD, fontSize: 8 },
  vipTxt: { color: GOLD, fontSize: 9, fontWeight: '900' },
  spiritoPill: {
    flexDirection: 'row', alignItems: 'center', gap: 3,
    backgroundColor: 'rgba(60,20,120,0.5)',
    paddingHorizontal: 6, paddingVertical: 1, borderRadius: 3,
  },
  spiritoIco: { fontSize: 8 },
  spiritoTxt: { color: '#FFE0FF', fontSize: 9, fontWeight: '900' },
  // "Apprendista" → pill flex-row nella stessa riga dei VIP/SP (più ordinato)
  titleBadge: {
    flexDirection: 'row', alignItems: 'center',
    paddingVertical: 1, paddingHorizontal: 4,
    marginLeft: 'auto',
  },
  titleTxt: { color: '#D8E0FF', fontSize: 9, fontWeight: '700', fontStyle: 'italic' },

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
    color: GOLD_PALE, fontSize: 8, fontWeight: '900',
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
