import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Dimensions, ScrollView, Image, ImageSourcePropType, Platform, useWindowDimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS, ELEMENTS, RARITY } from '../constants/theme';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useAuth } from '../context/AuthContext';
import { apiCall } from '../utils/api';
import BattleSprite from '../components/BattleSprite';
import { heroBattleImageSource, heroImageSource, GREEK_HOPLITE_COMBAT_BASE } from '../components/ui/hopliteAssets';
import { HOPLITE_BATTLE_ASSET_MANIFEST } from '../components/ui/hopliteAssetManifest';
import { pickBattleBackground, BattleBgResult, preloadBattleAsset } from '../components/ui/battleBackgrounds';
import { buildBattleLayout, getHomePosition } from '../components/battle/motionSystem';
import BattleDebugOverlay, { DebugUnitInfo } from '../components/battle/BattleDebugOverlay';
import BattleLoadingScreen from '../components/battle/BattleLoadingScreen';
import ChatComposer from '../components/chat/ChatComposer';
import ChannelSelector from '../components/chat/ChannelSelector';
import { useChatChannel } from '../hooks/useChatChannel';

/**
 * BATTLE_DEBUG — flag per attivare overlay di debug nativo + log console
 * verbose. Mettere a `true` solo quando si deve diagnosticare un bug di
 * layout/motion su mobile. In produzione/normale uso deve essere `false`:
 *   - disattiva BattleDebugOverlay (banner rosso + grid + bounding box)
 *   - disattiva il badge mount `mN` e l'anchor dot sul BattleSprite
 *   - silenzia tutti i console.log taggati [BATTLE_DEBUG]
 * Tutta l'infrastruttura resta nel codice, pronta per essere riattivata.
 */
const BATTLE_DEBUG = false;
const dbg = (...args: any[]) => { if (BATTLE_DEBUG) console.log('[BATTLE_DEBUG]', ...args); };
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming, withSequence,
  withDelay, withRepeat, FadeIn, FadeInDown, FadeInUp, Easing,
  SlideInLeft, SlideInRight, ZoomIn,
} from 'react-native-reanimated';

const { width: SW, height: SH } = Dimensions.get('window');
const EC = ELEMENTS.colors;
const RARITY_COLORS: Record<number, string> = RARITY.colors;

type Phase = 'loading' | 'preparing' | 'fighting' | 'result';

// Track sprite states per character
interface SpriteData {
  state: 'idle' | 'attack' | 'hit' | 'skill' | 'ultimate' | 'dead' | 'heal' | 'dodge';
  damage: number | null;
  healAmt: number | null;
  isCrit: boolean;
  /**
   * actionInstanceId — identificatore univoco dell'invocazione corrente
   * di un'azione visiva (attack/skill/ultimate/heal/hit/dodge).
   * Incrementato da `nextActionId()` SOLO quando il sistema battle
   * dispatcha una NUOVA azione. I frame player (Hoplite Affondo,
   * Guardia Ferrea) partono UNA sola volta per ogni nuovo id, immuni
   * a re-render spuri di React.
   */
  actionInstanceId: number;
}

export default function CombatScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ campaignFaction?: string; campaign_faction?: string }>();
  const { refreshUser } = useAuth();
  // Reattivo a rotation/resize: su mobile dà le dim reali del viewport.
  const { width: winW, height: winH } = useWindowDimensions();
  const [phase, setPhase] = useState<Phase>('loading');
  const [result, setResult] = useState<any>(null);
  const [turn, setTurn] = useState(0);
  const [teamA, setTeamA] = useState<any[]>([]);
  const affinityGrantedRef = React.useRef<boolean>(false);
  const [teamB, setTeamB] = useState<any[]>([]);
  const [speed, setSpeed] = useState(1);
  const [showUlt, setShowUlt] = useState(false);
  const [ultInfo, setUltInfo] = useState({ char: '', skill: '', element: 'neutral' });
  const [error, setError] = useState('');
  const [logLines, setLogLines] = useState<any[]>([]);
  // v16.4 — PERFORMANCE: durante battle, addLog veniva chiamato per ogni
  // azione (attack/ultimate/heal/dot/dodge/skip) e a x3 speed = ~3 setState/s
  // → re-render dell'intero CombatScreen (HUD buttons, sprite props,
  // chat trigger badge…) → JS-thread pressure → touch ritardati.
  // FIX: il log "live" vive in un ref, lo state pubblico (logLines) si
  // aggiorna SOLO quando il drawer è aperto, così la cascata di re-render
  // sparisce a drawer chiuso. Quando l'utente apre il drawer facciamo un
  // sync immediato dal ref → l'utente vede comunque il log completo.
  const logLinesRef = useRef<any[]>([]);
  // v16.1 — Battle Log overlay: il log non è più una fascia fissa che eat-up
  // 110pt di battle viewport. È un overlay on-demand ispirato al pattern
  // chat (panels/tabs). Default tab = 'log', tab 'chat' è placeholder per
  // futura integrazione plaza-chat in-battle (no scope creep ora).
  const [showLog, setShowLog] = useState(false);
  const showLogRef = useRef(false);
  useEffect(() => { showLogRef.current = showLog; }, [showLog]);
  const [logTab, setLogTab] = useState<'log' | 'chat'>('log');
  // v16.5/v16.13/v16.18 — Battle chat composer (tab 'chat' del drawer).
  // SHARED MULTI-CHANNEL via useChatChannel hook (Phase 1).
  // - Solo lazy: enabled solo quando logTab === 'chat' → no fetch in battle.
  // - Cambio canale → refetch automatico.
  // - Send → POST + refetch automatico (gestito dal hook).
  // v16.18 — enabled lazy: fetch solo quando il drawer è aperto E la tab
  // chat è attiva. Cambio canale → refetch automatico via hook.
  const battleChat = useChatChannel({
    enabled: showLog && logTab === 'chat',
    pollingMs: 0, // niente polling in battle: refetch solo on-demand/on-send
  });
  const chatScrollRef = useRef<ScrollView>(null);
  const [spriteStates, setSpriteStates] = useState<Record<string, SpriteData>>({});
  // Background della battaglia: scelto UNA SOLA volta all'inizio di ogni fight
  // e memorizzato qui per restare deterministicamente fisso durante la battaglia.
  const [battleBg, setBattleBg] = useState<BattleBgResult | null>(null);
  // Battlefield REAL rect (misurato via onLayout). Source of truth per le
  // home positions. Fallback a null → il layout assoluto non viene montato
  // finché non abbiamo le misure vere del container → su mobile le unità
  // non finiscono fuori asse per colpa del viewport globale.
  const [bfRect, setBfRect] = useState<{ w: number; h: number } | null>(null);
  // Preload progress tracking per loading screen reale
  const [preloadLoaded, setPreloadLoaded] = useState(0);
  const [preloadTotal, setPreloadTotal] = useState(0);
  const [preloadLabel, setPreloadLabel] = useState('');
  // Pause: quando true, playLog non avanza (il timer interno controlla
  // pausedRef prima di ogni safeTimeout → no-op fino a unpause).
  const [isPaused, setIsPaused] = useState(false);
  const pausedRef = useRef(false);
  useEffect(() => { pausedRef.current = isPaused; }, [isPaused]);
  const timerRef = useRef<any>(null);
  const allTimers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const logRef = useRef<ScrollView>(null);

  // ---- Mappatura coordinate formazione → griglia display 3x3 ----
  // Backend usa sistema 1/4/7 per x (colonne) e y (righe).
  //   x=1 → Support, x=4 → DPS, x=7 → Tank
  //   y=1 → top,    y=4 → mid, y=7 → bottom
  // Team A (player, left side): support a SX (back), tank a DX (front line)
  // Team B (enemy, right side): mirror → tank a SX (front line), support a DX (back)
  const X_MAP_A: Record<number, number> = { 1: 0, 4: 1, 7: 2 };
  const X_MAP_B: Record<number, number> = { 1: 2, 4: 1, 7: 0 };
  const Y_MAP: Record<number, number> = { 1: 0, 4: 1, 7: 2 };

  type GridCell = any | null;
  type Grid3x3 = GridCell[][]; // grid[col][row]

  const buildFormationGrid = (team: any[] | null | undefined, mirror: boolean): Grid3x3 => {
    const g: Grid3x3 = [
      [null, null, null],
      [null, null, null],
      [null, null, null],
    ];
    if (!team) return g;
    const xMap = mirror ? X_MAP_B : X_MAP_A;
    team.forEach((c, idx) => {
      const rawX = Number(c?.grid_x);
      const rawY = Number(c?.grid_y);
      // Se il backend non manda grid_x/grid_y (fallback), degrade come la vecchia logica
      // basata sull'indice (sequential fill row-major per Team A, mirror per Team B).
      let col: number;
      let row: number;
      if (Number.isFinite(rawX) && Number.isFinite(rawY) && xMap[rawX] !== undefined && Y_MAP[rawY] !== undefined) {
        col = xMap[rawX];
        row = Y_MAP[rawY];
      } else {
        // fallback deterministico: riempie col 0..2, row 0..2 in ordine
        col = Math.floor(idx / 3);
        row = idx % 3;
      }
      if (col >= 0 && col < 3 && row >= 0 && row < 3 && !g[col][row]) {
        g[col][row] = c;
      }
    });
    return g;
  };

  // Helper: traccia ogni setTimeout per cleanup sicuro
  // safeTimeout con supporto PAUSA: se pausedRef.current è true, il timer
  // si reinnesca ogni 120ms finché la pausa non viene rilasciata → il
  // playback riprende esattamente dove era stato interrotto senza reset.
  const safeTimeout = (fn: () => void, ms: number) => {
    const tick = (remaining: number) => {
      const id = setTimeout(() => {
        if (pausedRef.current) {
          // pausa attiva → riprogramma tra 120ms senza consumare il tempo
          tick(remaining);
        } else {
          fn();
        }
      }, Math.max(0, remaining));
      allTimers.current.push(id);
      return id;
    };
    return tick(ms);
  };

  // Screen-level animations
  const flash = useSharedValue(0);
  const shakeX = useSharedValue(0);
  const ultScale = useSharedValue(0);
  const ultOp = useSharedValue(0);
  const vsScale = useSharedValue(0);
  const vsOp = useSharedValue(0);

  // v16.3 — NOTIFICATION NOISE REDUCTION
  //   Master gate per le notifiche on-screen invasive (Ultimate Cut-in).
  //   Quando false, i dati vengono comunque registrati via addLog() e
  //   restano disponibili nel Battle Log drawer; solo l'overlay visivo
  //   full-screen viene soppresso. Il timing (safeTimeout) resta invariato
  //   → la battle pacing non cambia.
  const INTRUSIVE_NOTIFICATIONS = false;
  // Banner "BATTLE START" one-shot, mostrato solo all'inizio del fight.
  const startBannerOp = useSharedValue(0);
  const startBannerScale = useSharedValue(0.85);

  const flashStyle = useAnimatedStyle(() => ({ opacity: flash.value }));
  const shakeStyle = useAnimatedStyle(() => ({ transform: [{ translateX: shakeX.value }] }));
  const ultStyle = useAnimatedStyle(() => ({ transform: [{ scale: ultScale.value }], opacity: ultOp.value }));
  const vsStyle = useAnimatedStyle(() => ({ transform: [{ scale: vsScale.value }], opacity: vsOp.value }));
  const startBannerStyle = useAnimatedStyle(() => ({
    opacity: startBannerOp.value,
    transform: [{ scale: startBannerScale.value }],
  }));

  // Layout battle calcolato dal RECT REALE del battlefield (misurato onLayout).
  // Fallback ai winW/winH solo finché il rect non è pronto — le home positions
  // non vengono utilizzate finché layoutReady==true (vedi rendering più sotto).
  // Reattivo solo a cambi significativi (orientation/resize) grazie alle deps.
  const layoutReady = !!bfRect && bfRect.w > 0 && bfRect.h > 0;
  const battleLayout = React.useMemo(() => {
    const w = bfRect?.w ?? winW;
    const h = bfRect?.h ?? Math.max(160, winH - 70 - 46);
    const L = buildBattleLayout(w, h);
    dbg('battleLayout recompute', { bfW: w, bfH: h, tank: L.tankSize, dps: L.dpsSize, sup: L.supSize, rowStep: L.rowStep });
    return L;
  }, [bfRect?.w, bfRect?.h, winW, winH]);

  useEffect(() => { startBattle(); return () => { if (timerRef.current) clearTimeout(timerRef.current); allTimers.current.forEach(id => clearTimeout(id)); allTimers.current = []; }; }, []);

  // BATTLE_DEBUG — trace phase/layout/rect changes con log [BATTLE_DEBUG]
  useEffect(() => {
    dbg('phase change', { phase, layoutReady, bfW: bfRect?.w, bfH: bfRect?.h, winW, winH, bgReason: battleBg?.reason, bgFaction: battleBg?.faction });
  }, [phase, layoutReady, bfRect?.w, bfRect?.h, winW, winH, battleBg?.faction]);

  const initSpriteState = (id: string): SpriteData => ({ state: 'idle', damage: null, healAmt: null, isCrit: false, actionInstanceId: 0 });

  // ═════════════════════════════════════════════════════════════════════
  // Counter monotonico per generare actionInstanceId univoci.
  // Ref → non triggera re-render, valore preservato tra play cycle.
  // ═════════════════════════════════════════════════════════════════════
  const actionCounterRef = useRef(0);
  const nextActionId = () => {
    actionCounterRef.current += 1;
    return actionCounterRef.current;
  };

  const setSpriteState = (id: string, data: Partial<SpriteData>) => {
    if (BATTLE_DEBUG && data.state) dbg('sprite state', { id, state: data.state });
    setSpriteStates(prev => {
      const cur = prev[id] || initSpriteState(id);
      // ═════════════════════════════════════════════════════════════════
      // Guard anti-doppio-trigger: se i campi richiesti in `data`
      // sono GIÀ uguali a quelli correnti, NON creiamo un nuovo
      // oggetto → React skippa il re-render → niente ri-esecuzione
      // dei useEffect di BattleSprite/HeroHopliteRig → no restart
      // animazione. Senza questa guard, dispatch ridondanti (es.
      // setSpriteState(id, {state:'attack'}) quando già 'attack')
      // creerebbero un nuovo reference per prev[id] e Reanimated
      // riceverebbe un nuovo ciclo di effect → potenziale doppio
      // playback dei frame.
      // ═════════════════════════════════════════════════════════════════
      let changed = false;
      for (const k of Object.keys(data)) {
        if ((cur as any)[k] !== (data as any)[k]) { changed = true; break; }
      }
      if (!changed) return prev;
      return { ...prev, [id]: { ...cur, ...data } };
    });
  };

  // v16.7 — RERENDER PRESSURE FIX (next bottleneck after v16.6 HP batching)
  // setSpriteState veniva chiamato N volte dentro forEach(targets) →
  // N re-render della CombatScreen per action. setSpriteStateBatch applica
  // tutti gli update in un singolo setSpriteStates → 1 re-render anche con
  // ULT multi-target. Mantiene la stessa anti-no-op guard per ogni id.
  const setSpriteStateBatch = (updates: { id: string; data: Partial<SpriteData> }[]) => {
    if (updates.length === 0) return;
    if (updates.length === 1) {
      setSpriteState(updates[0].id, updates[0].data);
      return;
    }
    setSpriteStates(prev => {
      let next = prev;
      let anyChanged = false;
      for (const { id, data } of updates) {
        const cur = (next[id] || prev[id]) || initSpriteState(id);
        let localChanged = false;
        for (const k of Object.keys(data)) {
          if ((cur as any)[k] !== (data as any)[k]) { localChanged = true; break; }
        }
        if (!localChanged) continue;
        if (!anyChanged) { next = { ...prev }; anyChanged = true; }
        next[id] = { ...cur, ...data };
      }
      return anyChanged ? next : prev;
    });
  };

  const resetSpriteStates = () => {
    dbg('resetSpriteStates (end of turn)');
    setSpriteStates(prev => {
      const n: Record<string, SpriteData> = {};
      Object.keys(prev).forEach(k => { n[k] = { ...prev[k], state: prev[k].state === 'dead' ? 'dead' : 'idle', damage: null, healAmt: null, isCrit: false }; });
      return n;
    });
  };

  const startBattle = async () => {
    setPhase('loading'); setError(''); setLogLines([]); logLinesRef.current = [];
    affinityGrantedRef.current = false;
    try {
      const r = await apiCall('/api/battle/simulate', { method: 'POST' });
      setResult(r);
      const tA = (r.team_a_final || []).map((c: any) => ({ ...c, current_hp: c.max_hp || c.hp || 10000, max_hp_battle: c.max_hp || c.hp || 10000, is_alive: true }));
      const tB = (r.team_b_final || []).map((c: any) => ({ ...c, current_hp: c.max_hp || c.hp || 10000, max_hp_battle: c.max_hp || c.hp || 10000, is_alive: true }));
      setTeamA(tA);
      setTeamB(tB);
      // ---- Battle background selection (deterministic per-battle) ----------
      // Prio 1: campaign → route param (?campaignFaction=norse) o backend r.campaign_faction
      // Prio 2: dominant faction across both teams
      // Tie-breaker: Team A dominant
      // Fallback: gradient neutro (source=null)
      const campaignFaction = (params?.campaignFaction as string)
        || (params?.campaign_faction as string)
        || r?.campaign_faction
        || r?.context?.campaign_faction
        || null;
      const bg = pickBattleBackground({
        campaignFaction,
        teamA: tA,
        teamB: tB,
        // variantIndex omesso → random, memorizzato in state sotto → fisso per la battaglia
      });
      setBattleBg(bg);
      // ═════════════════════════════════════════════════════════════════════
      // PRELOAD ASSET CRITICI — progress-tracked, visibile nella loading UI.
      // ---------------------------------------------------------------------
      // Manifest completo:
      //   - bg battaglia (1 immagine ~3MB)
      //   - combat_base.png di Hoplite (fallback pose laterale)
      //   - 12 asset rig Hoplite (7 layer + 5 safe fill)
      //   - 8 frame Affondo di Falange
      //   - 6 frame Guardia Ferrea
      // Totale: ~28 asset. Preloadati PRIMA di passare a 'preparing' →
      // la battle parte senza decode lazy, niente "ricaricamento visivo"
      // quando i frame attack/skill entrano in scena per la prima volta.
      //
      // Timeout di safety 3500ms: se per qualche motivo un asset non
      // decoda (es. cache corrotta, file mancante), la battle parte
      // comunque — meglio una piccola latenza sul primo attack che
      // una UI bloccata sulla loading screen all'infinito.
      // ═════════════════════════════════════════════════════════════════════
      const preloadAssets: any[] = [];
      if (bg.source) preloadAssets.push({ src: bg.source, label: `bg · ${bg.faction || 'neutral'}` });
      preloadAssets.push({ src: GREEK_HOPLITE_COMBAT_BASE, label: 'hoplite · combat_base' });
      HOPLITE_BATTLE_ASSET_MANIFEST.forEach((src, idx) => {
        preloadAssets.push({ src, label: `hoplite · asset #${idx + 1}` });
      });
      setPreloadTotal(preloadAssets.length);
      setPreloadLoaded(0);
      setPreloadLabel('Inizializzazione…');

      let loadedCount = 0;
      const loadOne = async (item: { src: any; label: string }) => {
        try {
          await preloadBattleAsset(item.src);
        } catch {
          // ignora — fallback silenzioso, l'asset verrà decodato a caldo
        } finally {
          loadedCount += 1;
          // Batch update via functional setState evita race condition
          setPreloadLoaded(loadedCount);
          setPreloadLabel(item.label);
        }
      };

      const preloadAll = Promise.all(preloadAssets.map(loadOne)).then(() => undefined);
      const preloadTimeout = new Promise<void>(res => setTimeout(res, 3500));
      await Promise.race([preloadAll, preloadTimeout]);
      // Init all sprite states
      const states: Record<string, SpriteData> = {};
      [...tA, ...tB].forEach(c => { states[c.id] = initSpriteState(c.id); });
      setSpriteStates(states);
      setPhase('preparing');
      // VS animation
      vsScale.value = 0; vsOp.value = 0;
      vsScale.value = withSequence(withTiming(1.3, { duration: 300 }), withTiming(1, { duration: 200 }));
      vsOp.value = withSequence(withTiming(1, { duration: 200 }), withDelay(600, withTiming(0, { duration: 200 })));
      safeTimeout(() => {
        setPhase('fighting');
        if (r.battle_log?.length) playLog(r, 0, 0);
        // v16.3 — One-shot lightweight battle-start banner. Fade-in 200ms,
        // hold 1700ms, fade-out 400ms. Single notification per fight.
        startBannerOp.value = 0;
        startBannerScale.value = 0.85;
        startBannerOp.value = withSequence(
          withTiming(1, { duration: 200 }),
          withDelay(1700, withTiming(0, { duration: 400 })),
        );
        startBannerScale.value = withSequence(
          withTiming(1, { duration: 220 }),
          withDelay(1900, withTiming(0.92, { duration: 360 })),
        );
      }, 1400);
    } catch (e: any) { setError(e.message || 'Errore'); setPhase('result'); }
  };

  // =========================================================================
  // Speed profile — differenze REALI e percepibili tra i tre livelli.
  //   1x = 1500ms   → base leggibile, pacing "guarda il combattimento"
  //   2x = 650ms    → ~2.3× più veloce, le azioni scorrono rapide
  //   3x = 300ms    → ~5× più veloce, quasi continuo, "skip-through"
  //
  // BUGFIX: prima la speed NON cambiava davvero a metà battle perché
  // `playLog` è un useCallback scheduling ricorsivo via setTimeout: una
  // volta partito, il callback cattura la propria `delay` in closure e
  // continua a usarla all'infinito anche se l'utente clicca un altro
  // pulsante. Fix: speedRef (mutato subito da setSpeed via useEffect)
  // → delay() legge dal ref, quindi TUTTI i tick successivi vedono il
  // nuovo moltiplicatore anche se sono pianificati da un callback stale.
  // =========================================================================
  const SPEED_BASE: Record<number, number> = { 1: 1500, 2: 650, 3: 300 };
  const speedRef = useRef(speed);
  useEffect(() => { speedRef.current = speed; }, [speed]);
  const grantAffinity = async (team: any[]) => {
    if (affinityGrantedRef.current) return;
    affinityGrantedRef.current = true;
    try {
      const heroIds = Array.from(new Set(
        (team || [])
          .map((c: any) => c.hero_id || c.id)
          .filter(Boolean),
      ));
      if (heroIds.length === 0) return;
      const res = await apiCall('/api/sanctuary/affinity/gain', {
        method: 'POST',
        body: JSON.stringify({ hero_ids: heroIds, source: 'battle_complete' }),
      });
      // If any hero leveled up, console.log for now (in futuro: toast UI)
      if (Array.isArray(res?.results)) {
        const lvUps = res.results.filter((r: any) => r.leveled_up);
        if (lvUps.length) {
          console.log('[Affinity] level-ups:', lvUps.map((r: any) =>
            `${r.hero_name} -> Lv ${r.level} (${r.new_title})`
          ).join(', '));
        }
      }
    } catch (e) {
      console.warn('[Affinity] gain failed', e);
    }
  };

  const delay = () => (SPEED_BASE[speedRef.current] ?? 1500);

  const addLog = (entry: any) => {
    // v16.4 — Push to ref always, ma trigger React re-render SOLO se
    // drawer aperto. A drawer chiuso: zero re-render della CombatScreen
    // durante battle → badge silenziato, HUD non invalidato, touch
    // responsivi anche a x3.
    const nextArr = [...logLinesRef.current.slice(-8), entry];
    logLinesRef.current = nextArr;
    if (showLogRef.current) {
      setLogLines(nextArr);
      safeTimeout(() => logRef.current?.scrollToEnd({ animated: true }), 50);
    }
  };

  // v16.18 — battle chat ora interamente gestita dal hook useChatChannel
  // (vedi `battleChat` sopra). Le ex `loadBattleChat`/`sendBattleChat`
  // sono state rimosse: il hook fa load on enable + refetch on send.

  const playLog = useCallback((res: any, ti: number, ai: number) => {
    if (!res.battle_log || ti >= res.battle_log.length) {
      setTeamA(res.team_a_final); setTeamB(res.team_b_final);
      // Set final dead states
      [...(res.team_a_final || []), ...(res.team_b_final || [])].forEach((c: any) => {
        if (!c.is_alive) setSpriteState(c.id, { state: 'dead' });
      });
      setPhase('result'); refreshUser();
      grantAffinity(res.team_a_final || []);
      return;
    }
    const t = res.battle_log[ti]; setTurn(ti + 1);
    if (ai >= t.actions.length) {
      resetSpriteStates();
      timerRef.current = safeTimeout(() => playLog(res, ti + 1, 0), delay() * 0.3);
      return;
    }
    const a = t.actions[ai];

    // Animate based on action type
    if (a.skill_type === 'sp') {
      // ULTIMATE
      setSpriteState(a.actor_id, { state: 'ultimate', damage: null, isCrit: false, actionInstanceId: nextActionId() });
      // v16.3 — Cut-in overlay gated dietro INTRUSIVE_NOTIFICATIONS. Quando
      // false, salta solo l'overlay visivo full-screen; il timing della
      // azione (safeTimeout + delay()*1.2) e l'addLog ULTIMATE restano
      // identici → battle pacing invariato, drawer log invariato.
      if (INTRUSIVE_NOTIFICATIONS) {
        setShowUlt(true);
        setUltInfo({ char: a.actor || '', skill: a.skill?.name || '', element: a.element || 'neutral' });
        ultScale.value = 0; ultOp.value = 0;
        ultScale.value = withSequence(withTiming(1.2, { duration: 200 }), withTiming(1, { duration: 150 }));
        ultOp.value = withSequence(withTiming(1, { duration: 100 }), withDelay(700, withTiming(0, { duration: 200 })));
        flash.value = withSequence(withTiming(0.5, { duration: 60 }), withTiming(0, { duration: 250 }));
      }
      addLog({ type: 'ultimate', actor: a.actor, skill: a.skill?.name, team: a.team, element: a.element });

      // Apply damage after a beat
      timerRef.current = safeTimeout(() => {
        if (INTRUSIVE_NOTIFICATIONS) setShowUlt(false);
        updateHP(a);
        if (a.targets) {
          // v16.7 — batch: 1 re-render per tutti i target invece di N
          setSpriteStateBatch(
            a.targets.map((tgt: any) => ({
              id: tgt.id,
              data: { state: tgt.killed ? 'dead' : 'hit', damage: a.total_damage || 0, isCrit: !!a.crit, actionInstanceId: nextActionId() } as Partial<SpriteData>,
            })),
          );
        }
        addLog({ type: 'attack', actor: a.actor, skill: a.skill?.name, damage: a.total_damage, crit: a.crit, team: a.team, targets: a.targets?.map((t: any) => t.name).join(', ') });
        timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.6);
      }, delay() * 1.2);
    } else if (a.type === 'attack') {
      // ═════════════════════════════════════════════════════════════════
      // MAPPING attack vs skill — FIX CRITICO.
      // ---------------------------------------------------------------
      // Il backend (battle_engine.py execute_skill) marca lo skill_type
      // con uno di questi 3 valori:
      //   'nad' — Normal Attack (attack base, low cooldown)
      //   'sad' — Strong Active Damage (SKILL attiva con cooldown)
      //   'sp'  — Super/Ultimate (gestito sopra in un branch separato)
      //
      // Il codice precedente checkava `a.skill_type === 'active'` che
      // NON ESISTE nel payload backend → la condizione era sempre FALSE
      // → ogni action finiva sul branch 'attack' anche quando era una
      // SKILL (sad). Risultato: Guardia Ferrea non si attivava MAI in
      // battle reale, Hoplite sembrava usare SEMPRE Affondo di Falange.
      //
      // FIX: checkare `'sad'` → state 'skill' → HeroHopliteRig monta
      // Layer 3 (HeroHopliteGuardiaFerrea) con playKey fresco.
      // Tutto il resto ('nad' e qualsiasi valore sconosciuto) → 'attack'
      // → HeroHopliteAffondo.
      // ═════════════════════════════════════════════════════════════════
      const isSkillAction = a.skill_type === 'sad';
      setSpriteState(a.actor_id, {
        state: isSkillAction ? 'skill' : 'attack',
        damage: null,
        isCrit: false,
        actionInstanceId: nextActionId(),
      });

      // Screen shake for crits
      if (a.crit) {
        shakeX.value = withSequence(
          withTiming(6, { duration: 40 }), withTiming(-6, { duration: 40 }),
          withTiming(3, { duration: 40 }), withTiming(0, { duration: 40 }),
        );
        flash.value = withSequence(withTiming(0.2, { duration: 50 }), withTiming(0, { duration: 120 }));
      }

      // Delay then show hit on targets
      timerRef.current = safeTimeout(() => {
        updateHP(a);
        if (a.targets) {
          // v16.7 — batch: 1 re-render per tutti i target invece di N
          setSpriteStateBatch(
            a.targets.map((tgt: any) => ({
              id: tgt.id,
              data: { state: tgt.killed ? 'dead' : 'hit', damage: a.total_damage || 0, isCrit: !!a.crit, actionInstanceId: nextActionId() } as Partial<SpriteData>,
            })),
          );
        }
        addLog({ type: 'attack', actor: a.actor, skill: a.skill?.name, damage: a.total_damage, crit: a.crit, team: a.team, targets: a.targets?.map((t: any) => t.name).join(', ') });
        timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.5);
      }, delay() * 0.4);
    } else if (a.type === 'heal') {
      setSpriteState(a.actor_id, { state: 'heal', healAmt: a.amount || 0, isCrit: false, actionInstanceId: nextActionId() });
      updateHP(a);
      addLog({ type: 'heal', actor: a.actor, amount: a.amount });
      timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.5);
    } else if (a.type === 'dot') {
      if (a.target_id) setSpriteState(a.target_id, { state: 'hit', damage: a.damage || 0, isCrit: false, actionInstanceId: nextActionId() });
      updateHP(a);
      addLog({ type: 'dot', target: a.target, damage: a.damage, effect: (a as any).effect_name });
      timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.4);
    } else if (a.type === 'dodge') {
      if (a.target_id) setSpriteState(a.target_id, { state: 'dodge', damage: null, isCrit: false, actionInstanceId: nextActionId() });
      addLog({ type: 'dodge', target: a.target });
      timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.4);
    } else {
      addLog({ type: 'skip', actor: a.actor });
      timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.3);
    }
  }, [speed]);

  // v16.6 — RERENDER PRESSURE FIX
  // Vecchia updateHP eseguiva forEach(target → setTeamA + setTeamB) →
  // 2×N setState per attack con N target, e prev.map() ritornava sempre
  // un nuovo array reference anche se nessun item cambiava → ogni
  // setState triggerava root re-render della CombatScreen anche per
  // il team che non conteneva il target. A x3 = molti re-render/sec →
  // sprite props "freschi" → flicker visivo / reset percepito.
  //
  // FIX: una sola passata per team, applica TUTTI i target in un setState,
  // e SKIP totale del setState se il team non contiene nessun target
  // (return prev → React no-op, zero re-render).
  const applyDamageBatch = (targets: { id: string; hp_remaining: number; killed?: boolean }[]) => {
    const ids = new Set(targets.map(t => t.id));
    const idMap = new Map(targets.map(t => [t.id, t]));
    const updater = (prev: any[]) => {
      let touched = false;
      const next = prev.map(c => {
        if (!ids.has(c.id)) return c;
        const t = idMap.get(c.id)!;
        touched = true;
        return { ...c, current_hp: Math.max(0, t.hp_remaining), is_alive: !t.killed };
      });
      return touched ? next : prev;  // ← KEY: ref invariato se nessun match → no re-render
    };
    setTeamA(updater);
    setTeamB(updater);
  };
  const applyDotBatch = (target_id: string, damage: number) => {
    const updater = (prev: any[]) => {
      let touched = false;
      const next = prev.map(c => {
        if (c.id !== target_id) return c;
        touched = true;
        const newHp = Math.max(0, c.current_hp - damage);
        return { ...c, current_hp: newHp, is_alive: newHp > 0 };
      });
      return touched ? next : prev;
    };
    setTeamA(updater);
    setTeamB(updater);
  };
  const applyHealBatch = (actor_id: string, amount: number) => {
    const updater = (prev: any[]) => {
      let touched = false;
      const next = prev.map(c => {
        if (c.id !== actor_id) return c;
        touched = true;
        return { ...c, current_hp: Math.min(c.max_hp_battle, c.current_hp + amount) };
      });
      return touched ? next : prev;
    };
    setTeamA(updater);
    setTeamB(updater);
  };

  const updateHP = (a: any) => {
    if (a.type === 'attack' && a.targets && a.targets.length > 0) {
      applyDamageBatch(a.targets);
    } else if (a.type === 'dot' && a.target_id) {
      applyDotBatch(a.target_id, a.damage || 0);
    } else if (a.type === 'heal' && a.actor_id) {
      applyHealBatch(a.actor_id, a.amount || 0);
    }
  };

  const skip = () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    allTimers.current.forEach(id => clearTimeout(id));
    allTimers.current = [];
    if (result) {
      setTeamA(result.team_a_final); setTeamB(result.team_b_final);
      [...(result.team_a_final || []), ...(result.team_b_final || [])].forEach((c: any) => {
        if (!c.is_alive) setSpriteState(c.id, { state: 'dead' });
      });
      setPhase('result'); refreshUser();
      grantAffinity(result.team_a_final || []);
    }
  };

  const getHpPct = (c: any) => c.max_hp_battle > 0 ? (c.current_hp / c.max_hp_battle) * 100 : 0;
  const getSpriteState = (id: string) => spriteStates[id] || initSpriteState(id);
  // v16.7 — HIT SLOP costante condivisa, dichiarata qui per essere accessibile
  // sia dal chatDrawerNode useMemo (sotto) sia dai bottoni HUD (più in basso).
  const HUD_HIT_SLOP = { top: 8, bottom: 8, left: 6, right: 6 };

  // v16.11 — BOTTOM-ANCHORED FULLSCREEN BACKGROUND
  // ─────────────────────────────────────────────────────────────────────
  // Problema: `resizeMode="cover"` su absoluteFillObject centra verticalmente
  // l'immagine → con i nostri asset (cielo + skyline + pavimento), il
  // "pavimento" finiva fuori schermo a destra/sinistra → percezione di
  // "zoom centrato" anziché vero backdrop fullscreen.
  // Soluzione: risolviamo le dimensioni naturali via
  // Image.resolveAssetSource (sincrono per static require()), calcoliamo
  // la scala COVER (max ratio) e posizioniamo con `bottom: 0`. Il pavimento
  // resta ancorato al bordo inferiore, il crop avviene SOLO in alto (cielo).
  // hooks-order safe: useMemo dichiarato PRIMA del primo early-return
  // (phase==='loading' a riga ~838).
  const hasBgSource = !!battleBg?.source;
  const bgCoverStyle = useMemo(() => {
    if (!hasBgSource) return null;
    try {
      const resolved = Image.resolveAssetSource(battleBg!.source as any);
      const iw = resolved?.width ?? 0;
      const ih = resolved?.height ?? 0;
      if (!iw || !ih || !winW || !winH) {
        return { kind: 'fill' as const };
      }
      const scale = Math.max(winW / iw, winH / ih);
      const renderedW = iw * scale;
      const renderedH = ih * scale;
      return {
        kind: 'anchored' as const,
        width: renderedW,
        height: renderedH,
        left: (winW - renderedW) / 2,
        bottom: 0,
      };
    } catch {
      return { kind: 'fill' as const };
    }
  }, [hasBgSource, battleBg?.source, winW, winH]);

  // v16.7 — DRAWER MEMOIZATION
  // Il chat trigger + drawer JSX viene ricalcolato ad ogni re-render della
  // CombatScreen. Durante battle, anche con v16.6+v16.7 setSpriteState batch,
  // ogni action ne triggera 2 (actor + targets-batch). Senza memo, il drawer
  // (header+ScrollView+composer) viene ricostruito ogni volta → "reset feeling"
  // perché ScrollView + TextInput interno possono percepire props churn.
  // useMemo con deps mirate → JSX reference stabile a parità di state visibile
  // → React bail-out della reconciliation per il drawer subtree, animazioni
  // interne preservate.
  // hooks-order safe: useMemo vive PRIMA dell'early-return phase==='loading'.
  const chatDrawerNode = useMemo(() => {
    if (!showLog) {
      return (
        <TouchableOpacity
          onPress={() => {
            setLogLines(logLinesRef.current);
            setShowLog(true);
          }}
          activeOpacity={0.8}
          style={st.chatTrigger}
          hitSlop={HUD_HIT_SLOP}
        >
          <Text style={st.chatTriggerIcon}>{'\uD83D\uDCAC'}</Text>
        </TouchableOpacity>
      );
    }
    return (
      <View style={st.chatDrawer} pointerEvents="box-none">
        <TouchableOpacity
          style={st.chatBackdrop}
          activeOpacity={1}
          onPress={() => setShowLog(false)}
        />
        <View style={st.chatPanel}>
          <View style={st.chatHeader}>
            <TouchableOpacity
              onPress={() => setLogTab('chat')}
              style={[st.chatTab, logTab === 'chat' && st.chatTabActive]}
              activeOpacity={0.7}
            >
              <Text style={[st.chatTabTxt, logTab === 'chat' && st.chatTabTxtActive]}>
                {'\uD83D\uDCAC'} Chat
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => setLogTab('log')}
              style={[st.chatTab, logTab === 'log' && st.chatTabActive]}
              activeOpacity={0.7}
            >
              <Text style={[st.chatTabTxt, logTab === 'log' && st.chatTabTxtActive]}>
                {'\uD83D\uDCDC'} Battle Log
              </Text>
            </TouchableOpacity>
            <View style={{ flex: 1 }} />
            <TouchableOpacity onPress={() => setShowLog(false)} style={st.chatClose} activeOpacity={0.7}>
              <Text style={st.chatCloseTxt}>{'\u2715'}</Text>
            </TouchableOpacity>
          </View>
          {logTab === 'log' ? (
            <ScrollView
              ref={logRef}
              horizontal={false}
              showsVerticalScrollIndicator
              contentContainerStyle={st.logContent}
              style={st.chatBody}
            >
              {logLines.length === 0 ? (
                <Text style={st.chatEmpty}>Nessun evento registrato.</Text>
              ) : (
                logLines.map((entry: any, i: number) => (
                  <View key={i} style={st.logLine}>
                    {entry.type === 'attack' && (
                      <Text style={st.logText}>
                        <Text style={{ color: entry.team === 'team_a' ? '#44AAFF' : '#FF4444' }}>{entry.actor}</Text>
                        {' '}{entry.skill || 'Attacco'} {'\u2192'} {entry.targets}
                        {' '}<Text style={{ color: entry.crit ? '#FFD700' : '#FF8844' }}>-{entry.damage?.toLocaleString()}</Text>
                        {entry.crit && <Text style={{ color: '#FFD700' }}> CRIT!</Text>}
                      </Text>
                    )}
                    {entry.type === 'ultimate' && (
                      <Text style={st.logText}>
                        <Text style={{ color: '#FFD700' }}>{'\u2B50'} {entry.actor} usa {entry.skill}!</Text>
                      </Text>
                    )}
                    {entry.type === 'heal' && (
                      <Text style={st.logText}>
                        <Text style={{ color: '#44DD88' }}>{'\u2764\uFE0F'} {entry.actor} +{entry.amount?.toLocaleString()} HP</Text>
                      </Text>
                    )}
                    {entry.type === 'dot' && (
                      <Text style={st.logText}>
                        <Text style={{ color: '#FF8844' }}>{'\uD83D\uDD25'} {entry.target} -{entry.damage?.toLocaleString()} ({entry.effect})</Text>
                      </Text>
                    )}
                    {entry.type === 'dodge' && (
                      <Text style={st.logText}>
                        <Text style={{ color: '#44DD99' }}>{'\uD83D\uDCA8'} {entry.target} schiva!</Text>
                      </Text>
                    )}
                    {entry.type === 'skip' && (
                      <Text style={st.logText}>
                        <Text style={{ color: '#666' }}>{entry.actor} bloccato</Text>
                      </Text>
                    )}
                  </View>
                ))
              )}
            </ScrollView>
          ) : (
            <View style={st.chatBody}>
              {/* v16.18 Phase 1 — Channel selector compact in cima */}
              <ChannelSelector
                channels={battleChat.channels}
                active={battleChat.active}
                onChange={battleChat.setActive}
                compact
              />
              <ScrollView
                ref={chatScrollRef}
                showsVerticalScrollIndicator
                contentContainerStyle={{ paddingBottom: 6, gap: 4 }}
                style={{ flex: 1 }}
              >
                {battleChat.messages.length === 0 ? (
                  <Text style={st.chatEmpty}>
                    {!battleChat.isAvailable
                      ? `\uD83D\uDD12 ${battleChat.activeMeta?.lockedReason || 'Canale non disponibile'}`
                      : battleChat.isReadonly
                        ? 'Nessuna notifica di sistema.'
                        : 'Nessun messaggio. Scrivi qualcosa qui sotto.'}
                  </Text>
                ) : (
                  battleChat.messages.map((m: any) => (
                    <View key={m.id || m._id} style={st.chatMsgRow}>
                      <Text style={st.chatMsgUser}>{m.username || 'utente'}:</Text>
                      <Text style={st.chatMsgTxt}>{m.message}</Text>
                    </View>
                  ))
                )}
              </ScrollView>
              <ChatComposer
                onSend={battleChat.send}
                placeholder={
                  !battleChat.isAvailable ? 'Canale bloccato' :
                  battleChat.isReadonly   ? 'Sola lettura'    :
                                            'Scrivi durante la battle\u2026'
                }
                compact
                maxLength={160}
                disabled={!battleChat.isAvailable || battleChat.isReadonly}
              />
            </View>
          )}
        </View>
      </View>
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showLog, logTab, logLines, battleChat]);

  // LOADING — preload reale con progress bar
  if (phase === 'loading') {
    const progress = preloadTotal > 0 ? preloadLoaded / preloadTotal : 0;
    return (
      <BattleLoadingScreen
        progress={progress}
        loaded={preloadLoaded}
        total={preloadTotal}
        label={preloadLabel}
      />
    );
  }

  // PREPARING - VS splash
  if (phase === 'preparing') return (
    <LinearGradient colors={[COLORS.bgPrimary, '#1A0A2E', COLORS.bgPrimary]} style={st.fc}>
      <View style={st.vsContainer}>
        <Animated.View entering={SlideInLeft.duration(400)}>
          <Text style={st.vsTeamName}>LA TUA SQUADRA</Text>
          <Text style={st.vsTeamCount}>{teamA.length} Eroi</Text>
        </Animated.View>
        <Animated.View style={[st.vsBadge, vsStyle]}>
          <Text style={st.vsText}>VS</Text>
        </Animated.View>
        <Animated.View entering={SlideInRight.duration(400)}>
          <Text style={[st.vsTeamName, { color: '#FF4444' }]}>NEMICI</Text>
          <Text style={st.vsTeamCount}>{teamB.length} Eroi</Text>
        </Animated.View>
      </View>
    </LinearGradient>
  );

  // RESULT
  if (phase === 'result') {
    const win = result?.victory;
    return (
      <LinearGradient
        colors={win ? ['#0D0D2B', '#1A1500', '#0D0D2B'] : ['#0D0D2B', '#1A0505', '#0D0D2B']}
        style={{ flex: 1 }}
      >
        {/* Fixed buttons at top for guaranteed accessibility */}
        <View style={st.resTopBar}>
          <TouchableOpacity onPress={startBattle} activeOpacity={0.7}>
            <LinearGradient colors={[COLORS.accent, '#FF4444']} style={st.retryBtn}>
              <Text style={st.retryTxt}>{'\u2694\uFE0F'} RIPROVA</Text>
            </LinearGradient>
          </TouchableOpacity>
          <Text style={[st.resTopTitle, { color: win ? '#FFD700' : '#FF4444' }]}>
            {win ? '\uD83C\uDFC6 VITTORIA!' : '\uD83D\uDCA5 SCONFITTA'}
          </Text>
          <TouchableOpacity style={st.menuBtn} onPress={() => router.back()} activeOpacity={0.7}>
            <Text style={st.menuTxt}>{'\u2190'} INDIETRO</Text>
          </TouchableOpacity>
        </View>

        {/* Scrollable result content */}
        <ScrollView
          contentContainerStyle={st.resultScroll}
          showsVerticalScrollIndicator={false}
        >
          {error ? <Text style={{ color: '#f44', marginTop: 8 }}>{error}</Text> : (
            <View style={st.resultRow}>
              {/* Left column: Stats + MVP */}
              <View style={st.resLeftCol}>
                <Animated.View entering={FadeInDown.delay(200)} style={st.resultStats}>
                  <View style={st.rStatBox}><Text style={st.rStatVal}>{result?.turns}</Text><Text style={st.rStatLabel}>Turni</Text></View>
                  <View style={st.rStatBox}><Text style={st.rStatVal}>{result?.team_a_survivors}/{teamA.length}</Text><Text style={st.rStatLabel}>Superstiti</Text></View>
                </Animated.View>
                {result?.mvp && (
                  <Animated.View entering={FadeInUp.delay(300)} style={st.mvpCard}>
                    <LinearGradient colors={['rgba(255,215,0,0.1)', 'transparent']} style={st.mvpInner}>
                      <Text style={st.mvpLabel}>MVP</Text>
                      <Text style={st.mvpName}>{result.mvp}</Text>
                    </LinearGradient>
                  </Animated.View>
                )}
                {result?.rewards?.account_level_up && (
                  <Text style={st.accLevelUp}>{'\uD83C\uDF1F'} Account Lv.{result.rewards.new_account_level}!</Text>
                )}
              </View>

              {/* Center column: Rewards */}
              <View style={st.resCenterCol}>
                {result?.rewards && (
                  <Animated.View entering={FadeInUp.delay(400)} style={st.rewardsCol}>
                    <Text style={st.rewardsSectionTitle}>RICOMPENSE</Text>
                    <View style={st.rewardsRow}>
                      <View style={st.rewardBadge}><Text style={st.rewardIcon}>{'\uD83D\uDCB0'}</Text><Text style={st.rewardVal}>{result.rewards.gold?.toLocaleString()}</Text></View>
                      <View style={st.rewardBadge}><Text style={st.rewardIcon}>{'\u2728'}</Text><Text style={st.rewardVal}>{result.rewards.exp?.toLocaleString()}</Text></View>
                      {result.rewards.hero_exp > 0 && (
                        <View style={st.rewardBadge}><Text style={st.rewardIcon}>{'\u2694\uFE0F'}</Text><Text style={st.rewardVal}>+{result.rewards.hero_exp}</Text></View>
                      )}
                    </View>
                  </Animated.View>
                )}
                {result?.rewards?.hero_levelups?.length > 0 && (
                  <Animated.View entering={FadeInUp.delay(500)} style={st.levelUpsWrap}>
                    <Text style={st.levelUpsTitle}>LEVEL UP!</Text>
                    {result.rewards.hero_levelups.map((lu: any, i: number) => (
                      <Text key={i} style={st.levelUpItem}>{lu.hero_name}: Lv.{lu.old_level} {'\u2192'} Lv.{lu.new_level}</Text>
                    ))}
                  </Animated.View>
                )}
              </View>

              {/* Right column: Drops */}
              {result?.rewards?.drops?.length > 0 && (
                <View style={st.resRightCol}>
                  <Animated.View entering={FadeInUp.delay(600)} style={st.dropsWrap}>
                    <Text style={st.dropsTitle}>OGGETTI</Text>
                    <View style={st.dropsRow}>
                      {result.rewards.drops.map((d: any, i: number) => (
                        <View key={i} style={st.dropItem}>
                          <Text style={st.dropIcon}>{d.icon}</Text>
                          <Text style={st.dropName}>{d.name}</Text>
                          <Text style={st.dropQty}>x{d.quantity}</Text>
                        </View>
                      ))}
                    </View>
                  </Animated.View>
                </View>
              )}
            </View>
          )}
        </ScrollView>
      </LinearGradient>
    );
  }

  // FIGHTING - Main battle view
  const renderHudCard = (c: any, isAlly: boolean) => {
    const hp = getHpPct(c);
    const hpCol = hp > 60 ? '#44DD88' : hp > 30 ? '#FFAA33' : '#FF3344';
    const rarCol = RARITY_COLORS[Math.min(c.rarity || 1, 6)] || '#888';
    const img = c.hero_image || c.image;
    const dead = !c.is_alive || hp <= 0;
    // Rage (ex sp_gauge) — letto live da spriteStates o dal character data.
    const rageCur = spriteStates[c.id]?.rage ?? c.rage ?? c.sp_gauge ?? 0;
    const rageMax = c.max_rage ?? 100;
    const ragePct = rageMax > 0 ? Math.max(0, Math.min(100, (rageCur / rageMax) * 100)) : 0;
    return (
      <View key={c.id} style={[st.hudCard, dead && { opacity: 0.35 }]}>
        <View style={[st.hudImg, { borderColor: rarCol }]}>
          {img ? (
            <Image source={heroImageSource(img, c.hero_id || c.id, c.hero_name || c.name)} style={st.hudImgInner} resizeMode="cover" />
          ) : (
            <View style={[st.hudImgPh, { backgroundColor: (EC[c.element] || '#888') + '25' }]}>
              <Text style={[st.hudInit, { color: EC[c.element] || '#888' }]}>{(c.name || '?')[0]}</Text>
            </View>
          )}
        </View>
        <View style={st.hudHpOuter}>
          <View style={st.hudHpBg}>
            <View style={[st.hudHpFill, { width: `${Math.max(0, hp)}%`, backgroundColor: hpCol }]} />
          </View>
          {/* Rage bar — giallo/oro, più sottile dell'HP */}
          <View style={st.hudRageBg}>
            <View style={[st.hudRageFill, { width: `${ragePct}%` }]} />
          </View>
        </View>
      </View>
    );
  };

  // v16.8 — CRITICAL FIX: BattleWrapper era definito QUI dentro CombatScreen
  // come `const BattleWrapper = (...) => ...`. Ad ogni re-render della
  // CombatScreen veniva creata una NUOVA function identity → React vedeva
  // un nuovo component type → UNMOUNT + REMOUNT dell'intero subtree
  // sotto BattleWrapper ad ogni action di battle (setSpriteState, updateHP).
  // Conseguenze:
  //   - HUD buttons unmount mid-tap → "intermittent presses"
  //   - BattleSprite/HeroHopliteRig animation timers restart da zero
  //     → idle continua "ticking" anche durante pause (animazione
  //     ricreata fresh ogni volta, non interrotta)
  //   - TextInput/ScrollView del drawer perdono focus/scroll → "reset feeling"
  // FIX: dissolto BattleWrapper. La logica del background image è ora
  // inline nel return JSX → struttura stabile, zero remount durante battle.
  // useMemo non serviva più: una volta che l'albero è stable, useMemo del
  // chatDrawerNode (v16.7) può finalmente fare effetto.
  // v16.11 — `hasBgSource` e `bgCoverStyle` sono ora dichiarati in alto
  // (sopra l'early-return phase==='loading') per rispettare l'hooks order.

  // v16.4.1 — HOOKS ORDER FIX
  // Le useCallback di v16.4 erano state inserite QUI, ma siamo dopo gli
  // early-return per phase 'loading'/'preparing'/'result' (righe ~580/592/611)
  // → quando il phase transitava da loading a fighting il numero di hook
  // chiamati cambiava → React: "Rendered more hooks than during the
  // previous render". Rimosse: la perf di v16.4 viene dalla addLog ref-based
  // + badge rimosso, NON dalla memoization degli handler. Ripristiniamo
  // gli onPress inline (function-identity instabile, accettabile) per
  // tornare a un render valido. hitSlop e openChat-sync li preserviamo
  // come costanti / inline (non sono hook).
  // v16.7 — HUD_HIT_SLOP è ora dichiarato prima del chatDrawerNode useMemo
  // (sopra l'early-return phase==='loading'). Questa duplicazione è rimossa.

  return (
    <View style={{ flex: 1, backgroundColor: '#060614', overflow: 'hidden' }}>
      {hasBgSource ? (
        <>
          {bgCoverStyle && bgCoverStyle.kind === 'anchored' ? (
            <Image
              source={battleBg!.source}
              style={{
                position: 'absolute',
                width: bgCoverStyle.width,
                height: bgCoverStyle.height,
                left: bgCoverStyle.left,
                bottom: bgCoverStyle.bottom,
              }}
              resizeMode="cover"
              fadeDuration={200}
            />
          ) : (
            <Image
              source={battleBg!.source}
              style={StyleSheet.absoluteFillObject}
              resizeMode="cover"
              fadeDuration={200}
            />
          )}
          {/* v16.9 — Overlay vignetta MOLTO leggera (era 0.20/0.02/0.28 →
              0.10/0.0/0.14). Il bg deve essere il vero protagonista;
              il dark scrim non deve creare "fascia" o senso di mascheratura. */}
          <LinearGradient
            colors={['rgba(6,6,20,0.10)', 'rgba(10,8,24,0.00)', 'rgba(6,6,20,0.14)']}
            style={StyleSheet.absoluteFillObject}
            pointerEvents="none"
          />
        </>
      ) : (
        <LinearGradient
          colors={['#060614', '#0A0A24', '#0D0820']}
          style={StyleSheet.absoluteFillObject}
          pointerEvents="none"
        />
      )}
      <Animated.View style={[{ flex: 1 }, shakeStyle]}>
        {/* Flash overlay */}
        <Animated.View style={[st.flashOv, flashStyle]} pointerEvents="none" />

        {/* ===== TOP HUD: Turn + Cards ===== */}
        <View style={st.topHud}>
          {/* Turn + speed controls */}
          <View style={st.turnRow}>
            <View style={st.turnBadge}>
              <Text style={st.turnLabel}>TURNO</Text>
              <Text style={st.turnNum}>{turn}</Text>
            </View>
            <View style={st.spds}>
              <TouchableOpacity
                style={[st.pauseBtn, isPaused && st.pauseBtnActive]}
                onPress={() => setIsPaused(p => !p)}
                activeOpacity={0.7}
                hitSlop={HUD_HIT_SLOP}
              >
                <Text style={st.pauseTxt}>{isPaused ? '\u25B6' : '\u23F8'}</Text>
              </TouchableOpacity>
              {[1, 2, 3].map(s => (
                <TouchableOpacity
                  key={s}
                  style={[st.spdBtn, speed === s && st.spdA]}
                  onPress={() => setSpeed(s)}
                  activeOpacity={0.7}
                  hitSlop={HUD_HIT_SLOP}
                >
                  <Text style={[st.spdTxt, speed === s && { color: COLORS.accent }]}>{s}x</Text>
                </TouchableOpacity>
              ))}
            </View>
            <TouchableOpacity onPress={skip} activeOpacity={0.7} style={st.skipBtn} hitSlop={HUD_HIT_SLOP}>
              <Text style={st.skipTxt}>{'\u23E9'} SALTA</Text>
            </TouchableOpacity>
            {/* v16.2 — RIMOSSO bottone LOG top-right (apriva Modal che crashava
                su web/RN). Sostituito da chat drawer bottom-left in-tree. */}
          </View>
          {/* Hero portrait cards */}
          <View style={st.cardRow}>
            <View style={st.cardTeam}>
              {teamA.map(c => renderHudCard(c, true))}
            </View>
            <View style={st.cardVs}><Text style={st.cardVsTxt}>VS</Text></View>
            <View style={st.cardTeam}>
              {teamB.map(c => renderHudCard(c, false))}
            </View>
          </View>
        </View>

        {/* ===== BATTLEFIELD CENTER: Absolute-positioned sprites ===== */}
        {/*
           ARCHITETTURA MOTION (due livelli indipendenti):
             1. HOME POSITION — wrapper <View position:absolute> posizionato
                con left/bottom calcolati da getHomePosition(team,col,row,layout).
                Il layout viene dal RECT REALE del battlefield (onLayout) → non
                dipende più dal viewport globale, né da stime di safe area.
                Immune al drift da re-render.
             2. ACTION MOTION — transform locale applicato DENTRO BattleSprite
                (transX/transY/rotate/scale). È puramente additivo alla home e
                torna sempre a 0 alla fine. Future skill (approach_target,
                backstab_target, move_to_center, charge_line) useranno lo stesso
                meccanismo passando un MotionIntent esplicito.
        */}
        <View
          style={st.battlefield}
          onLayout={e => {
            const { width, height, x, y } = e.nativeEvent.layout;
            dbg('onLayout battlefield', { w: width, h: height, x, y, winW, winH });
            if (width > 0 && height > 0) {
              setBfRect(prev => {
                if (!prev || Math.abs(prev.w - width) > 2 || Math.abs(prev.h - height) > 2) {
                  dbg('bfRect UPDATED', { prevW: prev?.w, prevH: prev?.h, newW: width, newH: height });
                  return { w: width, h: height };
                }
                return prev;
              });
            }
          }}
        >
          <LinearGradient
            colors={['transparent', 'rgba(30,20,10,0.12)', 'rgba(20,15,8,0.3)']}
            style={st.groundPlane}
            start={{ x: 0.5, y: 0 }}
            end={{ x: 0.5, y: 1 }}
          />

          {/* VS center line (solo estetica, non impatta il layout assoluto) */}
          <View style={st.vsCenter} pointerEvents="none">
            <LinearGradient colors={['transparent', COLORS.accent + '20', 'transparent']} style={st.vsCenterLine} />
          </View>

          {/* Sprites renderizzati SOLO quando il rect del battlefield è noto.
              Evita di calcolare home positions su fallback winW/winH errati. */}
          {layoutReady && (() => {
            const gridA = buildFormationGrid(teamA, false);
            const gridB = buildFormationGrid(teamB, true);
            const L = battleLayout;
            const sprites: React.ReactNode[] = [];
            const debugUnits: DebugUnitInfo[] = [];
            const colSizesA = [L.supSize, L.dpsSize, L.tankSize];
            const colSizesB = [L.tankSize, L.dpsSize, L.supSize];

            // Geometria wrapper UNIFICATA con BattleSprite:
            //   width  = size   (larghezza della cella = larghezza dello sprite)
            //   height = size * 1.25   (altezza ritratto; il bottom del wrapper
            //                           coincide col suolo → home.y)
            // Il wrapper è la HOME assoluta: NON contiene transform. I motion
            // transform (attacco/hit/skill) vengono applicati solo al motion
            // container INTERNO a BattleSprite — il wrapper resta immutabile.
            for (let col = 0; col < 3; col++) {
              for (let row = 0; row < 3; row++) {
                // Team A
                const cA = gridA[col][row];
                if (cA) {
                  const size = colSizesA[col];
                  const slotH = Math.round(size * 1.25);
                  const home = getHomePosition('A', col, row, L);
                  const ss = getSpriteState(cA.id);
                  const zIndex = 10 + (2 - row);
                  debugUnits.push({
                    team: 'A', col, row, id: cA.id, name: cA.name,
                    state: ss.state, facing: 'right', size, zIndex,
                  });
                  if (BATTLE_DEBUG) dbg('render A', { id: cA.id, col, row, homeX: Math.round(home.x), homeY: Math.round(home.y), size, slotH, state: ss.state });
                  sprites.push(
                    <Animated.View
                      key={`a_${cA.id}`}
                      pointerEvents="box-none"
                      style={{
                        position: 'absolute',
                        left: home.x - size / 2,
                        bottom: home.y,
                        width: size,
                        height: slotH,
                        zIndex,
                      }}
                    >
                      <BattleSprite
                        character={cA}
                        state={ss.state}
                        isEnemy={false}
                        hpPercent={getHpPct(cA)}
                        showDamage={ss.damage}
                        showHeal={ss.healAmt}
                        isCrit={ss.isCrit}
                        size={size}
                        debug={BATTLE_DEBUG}
                        actionInstanceId={ss.actionInstanceId}
                        paused={isPaused}
                      />
                    </Animated.View>
                  );
                }
                // Team B
                const cB = gridB[col][row];
                if (cB) {
                  const size = colSizesB[col];
                  const slotH = Math.round(size * 1.25);
                  const home = getHomePosition('B', col, row, L);
                  const ss = getSpriteState(cB.id);
                  const zIndex = 10 + (2 - row);
                  debugUnits.push({
                    team: 'B', col, row, id: cB.id, name: cB.name,
                    state: ss.state, facing: 'left', size, zIndex,
                  });
                  if (BATTLE_DEBUG) dbg('render B', { id: cB.id, col, row, homeX: Math.round(home.x), homeY: Math.round(home.y), size, slotH, state: ss.state });
                  sprites.push(
                    <Animated.View
                      key={`b_${cB.id}`}
                      pointerEvents="box-none"
                      style={{
                        position: 'absolute',
                        left: home.x - size / 2,
                        bottom: home.y,
                        width: size,
                        height: slotH,
                        zIndex,
                      }}
                    >
                      <BattleSprite
                        character={cB}
                        state={ss.state}
                        isEnemy={true}
                        hpPercent={getHpPct(cB)}
                        showDamage={ss.damage}
                        showHeal={ss.healAmt}
                        isCrit={ss.isCrit}
                        size={size}
                        debug={BATTLE_DEBUG}
                        actionInstanceId={ss.actionInstanceId}
                        paused={isPaused}
                      />
                    </Animated.View>
                  );
                }
              }
            }
            return (
              <>
                {sprites}
                <BattleDebugOverlay
                  enabled={BATTLE_DEBUG}
                  bfRect={bfRect}
                  layout={L}
                  units={debugUnits}
                />
              </>
            );
          })()}
        </View>

        {/* v16.1 — RIMOSSO log inline fisso (era 110pt di altezza che
            comprimeva il battle viewport). Sostituito dall'overlay Modal
            qui sotto, accessibile via il bottone "📜 LOG" nel turnRow. */}

        {/* v16.7 — Drawer JSX memoizzato in chatDrawerNode (vedi useMemo
            sopra). Inserito come singolo node statico → React reuses
            same JSX object reference quando deps non cambiano →
            no reconciliation del subtree del drawer durante battle. */}
        {chatDrawerNode}

        {/* v16.3 — BATTLE START BANNER       )}

        {/* v16.3 — BATTLE START BANNER (one-shot, lightweight, non-intrusive)
            Sostituisce le notifiche per-action invasive con UNA sola
            notifica leggera all'inizio del fight. Renderizzato sempre nel
            tree ma con opacity gestita via Reanimated → niente toggle JS,
            niente re-mount. */}
        <Animated.View
          style={[st.startBanner, startBannerStyle]}
          pointerEvents="none"
        >
          <View style={st.startBannerInner}>
            <Text style={st.startBannerText}>BATTAGLIA INIZIA</Text>
          </View>
        </Animated.View>

        {/* Ultimate Cut-in Overlay */}
        {showUlt && (
          <View style={st.ultOv}>
            <LinearGradient
              colors={[(EC[ultInfo.element] || '#FF6B35') + '30', 'rgba(0,0,0,0.9)', (EC[ultInfo.element] || '#FF6B35') + '15']}
              style={st.ultBg}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            >
              <Animated.View style={[st.ultContent, ultStyle]}>
                <View style={[st.ultDecorLine, { backgroundColor: EC[ultInfo.element] || '#FFD700' }]} />
                <Text style={[st.ultChar, { color: EC[ultInfo.element] || '#FFD700', textShadowColor: (EC[ultInfo.element] || '#FFD700') + '80' }]}>{ultInfo.char}</Text>
                <Text style={st.ultSkill}>{ultInfo.skill}</Text>
                <View style={[st.ultDecorLine, { backgroundColor: EC[ultInfo.element] || '#FFD700' }]} />
                <Text style={st.ultLbl}>MOSSA FINALE</Text>
              </Animated.View>
            </LinearGradient>
          </View>
        )}
      </Animated.View>
    </View>
  );
}

const st = StyleSheet.create({
  fc: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  loadIcon: { fontSize: 40, marginBottom: 12 },
  loadTxt: { color: COLORS.textSecondary, fontSize: 14, fontWeight: '700', letterSpacing: 1 },
  // VS Screen
  vsContainer: { flexDirection: 'row', alignItems: 'center', gap: 30 },
  vsTeamName: { color: '#44AAFF', fontSize: 18, fontWeight: '900', letterSpacing: 2, textAlign: 'center' },
  vsTeamCount: { color: COLORS.textMuted, fontSize: 11, textAlign: 'center', marginTop: 4 },
  vsBadge: { width: 70, height: 70, borderRadius: 35, backgroundColor: 'rgba(255,107,53,0.15)', borderWidth: 2, borderColor: COLORS.accent, alignItems: 'center', justifyContent: 'center' },
  vsText: { fontSize: 28, fontWeight: '900', color: COLORS.accent, letterSpacing: 4, textShadowColor: 'rgba(255,107,53,0.6)', textShadowRadius: 15, textShadowOffset: { width: 0, height: 0 } },
  // ===== TOP HUD =====
  topHud: {
    // v16.9 — Reduced opacity 0.95 → 0.62 + linear scrim fa percepire
    // l'HUD come overlay di un fullscreen backdrop, non come una fascia
    // che spezza la scena. Il bg battle si vede attraverso, dando il
    // "real fullscreen" feel richiesto. Il testo HUD resta leggibile
    // grazie al text-shadow già presente sui sub-elementi.
    backgroundColor: 'rgba(6,6,20,0.62)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,107,53,0.22)',
    paddingHorizontal: 10,
    paddingTop: 4,
    paddingBottom: 4,
    // v16.8 — zIndex elevato per garantire che HUD intercetti touch sempre.
    zIndex: 50,
    elevation: 4,
  },
  turnRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  turnBadge: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  turnLabel: { color: COLORS.textMuted, fontSize: 8, fontWeight: '800', letterSpacing: 1 },
  turnNum: { color: COLORS.gold, fontSize: 18, fontWeight: '900' },
  spds: { flexDirection: 'row', gap: 4 },
  spdBtn: { paddingHorizontal: 12, paddingVertical: 5, borderRadius: 8, backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)' },
  spdA: { backgroundColor: 'rgba(255,107,53,0.15)', borderColor: COLORS.accent + '60' },
  spdTxt: { color: COLORS.textMuted, fontSize: 11, fontWeight: '800' },
  skipBtn: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 8, backgroundColor: 'rgba(255,68,68,0.08)', borderWidth: 1, borderColor: 'rgba(255,68,68,0.2)' },
  skipTxt: { color: COLORS.error, fontSize: 11, fontWeight: '800' },
  // Card portraits row
  cardRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardTeam: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 3,
    flexWrap: 'wrap',
  },
  cardVs: {
    paddingHorizontal: 8,
  },
  cardVsTxt: {
    color: COLORS.accent,
    fontSize: 10,
    fontWeight: '900',
    letterSpacing: 1,
  },
  hudCard: {
    alignItems: 'center',
    width: 50,
  },
  hudImg: {
    width: 44,
    height: 44,
    borderRadius: 8,
    borderWidth: 2,
    overflow: 'hidden',
    backgroundColor: '#0A0A20',
  },
  hudImgInner: {
    width: 40,
    height: 40,
    borderRadius: 6,
  },
  hudImgPh: {
    width: 40,
    height: 40,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
  },
  hudInit: {
    fontSize: 18,
    fontWeight: '900',
  },
  hudHpOuter: {
    width: 44,
    marginTop: 3,
  },
  hudHpBg: {
    width: '100%',
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.12)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  hudHpFill: {
    height: '100%',
    borderRadius: 2,
  },
  hudRageBg: {
    width: '100%',
    height: 3,
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 2,
    overflow: 'hidden',
    marginTop: 2,
  },
  hudRageFill: {
    height: '100%',
    borderRadius: 2,
    backgroundColor: '#FFC629',  // giallo rage
  },
  pauseBtn: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    marginRight: 6,
  },
  pauseBtnActive: {
    backgroundColor: 'rgba(255,107,53,0.25)',
    borderColor: COLORS.accent,
  },
  pauseTxt: {
    color: '#FFF',
    fontSize: 13,
    fontWeight: '800',
  },
  // ====== BATTLEFIELD ======
  battlefield: {
    flex: 1,
    // NO flexDirection/alignItems → i children sono posizionati in absolute
    // via getHomePosition(). Il battlefield è solo il container relativo.
    position: 'relative',
    overflow: 'visible',
  },
  groundPlane: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '68%',                 // pavimento più bilanciato, non schiaccia la scena verso il fondo
  },
  teamGrid: {
    // Non più flex:1 → i due team si avvicinano al centro, no vuoto eccessivo
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'flex-end',        // ancora i personaggi al suolo
    gap: 4,
    paddingHorizontal: 2,
    overflow: 'visible',
  },
  gridCol: {
    justifyContent: 'flex-end',    // ancoraggio al suolo nella colonna
    alignItems: 'center',
    overflow: 'visible',           // sprite più alti dello slot si espandono verso l'alto
  },
  emptySlot: {
    // Row-step compatto → le 3 righe della griglia 3x3 restano tutte visibili
    // senza clippare, e gli sprite (size*1.25) si sovrappongono con effetto profondità.
    width: 160,
    height: 48,
  },
  spriteSlot: {
    alignItems: 'center',
    justifyContent: 'flex-end',    // sprite ancorato al fondo dello slot, eccesso esce verso l'alto
    height: 48,                    // row-step → depth stagger tra righe
    overflow: 'visible',
  },
  vsCenter: {
    position: 'absolute',
    left: '50%',
    top: 10,
    bottom: 10,
    width: 2,
    marginLeft: -1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  vsCenterLine: {
    width: 2,
    flex: 1,
  },
  vsBubble: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: 'rgba(255,107,53,0.12)',
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.3)',
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 4,
  },
  vsBubbleTxt: {
    color: COLORS.accent,
    fontSize: 8,
    fontWeight: '900',
  },
  // Log Panel
  // v16.2 — Battle log RIMOSSO dalla scena fissa, ora è un drawer in-tree
  // bottom-left (chat-style). I sub-style logContent/logLine/logText sono
  // ancora referenziati dal drawer → mantenuti.
  // ======= CHAT TRIGGER (bottom-left, floating) =======
  chatTrigger: {
    position: 'absolute',
    left: 12,
    bottom: 12,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(10,10,28,0.88)',
    borderWidth: 1.5,
    borderColor: 'rgba(255,107,53,0.55)',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 60,
    elevation: 6,
    shadowColor: '#000',
    shadowOpacity: 0.5,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
  chatTriggerIcon: {
    fontSize: 20,
  },
  chatTriggerBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    minWidth: 20,
    height: 18,
    borderRadius: 9,
    paddingHorizontal: 5,
    backgroundColor: COLORS.accent,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#0A0A1C',
  },
  chatTriggerBadgeTxt: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '900',
  },
  // ======= DRAWER (full-screen overlay container, in-tree) =======
  chatDrawer: {
    position: 'absolute',
    left: 0, right: 0, top: 0, bottom: 0,
    zIndex: 70,
  },
  chatBackdrop: {
    position: 'absolute',
    left: 0, right: 0, top: 0, bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.42)',
  },
  chatPanel: {
    position: 'absolute',
    left: 12,
    bottom: 12,
    width: 360,
    maxWidth: '70%',
    height: '78%',
    maxHeight: 320,
    backgroundColor: 'rgba(10,10,28,0.97)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.45)',
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOpacity: 0.6,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
    elevation: 8,
  },
  chatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 6,
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.08)',
    gap: 4,
  },
  chatTab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.04)',
    gap: 4,
  },
  chatTabActive: {
    backgroundColor: 'rgba(255,107,53,0.18)',
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.5)',
  },
  chatTabTxt: {
    color: 'rgba(255,255,255,0.55)',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  chatTabTxtActive: {
    color: '#fff',
  },
  chatTabBadge: {
    minWidth: 18,
    height: 14,
    borderRadius: 7,
    paddingHorizontal: 4,
    backgroundColor: COLORS.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  chatTabBadgeTxt: {
    color: '#fff',
    fontSize: 9,
    fontWeight: '900',
  },
  chatClose: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(255,255,255,0.06)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  chatCloseTxt: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '900',
  },
  chatBody: {
    flex: 1,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  chatEmpty: {
    color: 'rgba(255,255,255,0.45)',
    fontSize: 11,
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 12,
  },
  // v16.5 — Battle Chat tab message rows
  chatMsgRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 4,
    flexWrap: 'wrap',
  },
  chatMsgUser: {
    color: COLORS.accent,
    fontSize: 11,
    fontWeight: '800',
  },
  chatMsgTxt: {
    color: '#E8E8F2',
    fontSize: 11,
    flexShrink: 1,
    lineHeight: 15,
  },
  logContent: { gap: 4, paddingBottom: 6 },
  logLine: { paddingVertical: 1 },
  logText: {
    color: '#F0F0F6',
    fontSize: 12,
    lineHeight: 16,
    fontWeight: '500',
    textShadowColor: 'rgba(0,0,0,0.85)',
    textShadowRadius: 2,
  },
  // Flash
  flashOv: { ...StyleSheet.absoluteFillObject, backgroundColor: '#fff', zIndex: 100 },
  // Ultimate
  ultOv: { ...StyleSheet.absoluteFillObject, zIndex: 90 },
  // v16.3 — Battle Start Banner (single, non-intrusive)
  startBanner: {
    position: 'absolute',
    top: '38%',
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 85,
  },
  startBannerInner: {
    paddingHorizontal: 26,
    paddingVertical: 10,
    borderRadius: 22,
    backgroundColor: 'rgba(10,10,28,0.78)',
    borderWidth: 1.5,
    borderColor: 'rgba(255,107,53,0.55)',
    shadowColor: '#000',
    shadowOpacity: 0.5,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 8,
    elevation: 8,
  },
  startBannerText: {
    color: COLORS.accent,
    fontSize: 15,
    fontWeight: '900',
    letterSpacing: 4,
    textShadowColor: 'rgba(0,0,0,0.85)',
    textShadowRadius: 4,
  },
  ultBg: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  ultContent: { alignItems: 'center', gap: 6 },
  ultDecorLine: { width: 180, height: 2, borderRadius: 1 },
  ultChar: { fontSize: 30, fontWeight: '900', letterSpacing: 4, textShadowRadius: 20, textShadowOffset: { width: 0, height: 0 } },
  ultSkill: { fontSize: 18, fontWeight: '800', color: '#fff', letterSpacing: 2 },
  ultLbl: { fontSize: 10, fontWeight: '700', color: COLORS.textMuted, letterSpacing: 6, marginTop: 4 },
  // Result
  resTopBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,215,0,0.15)',
    backgroundColor: 'rgba(6,6,20,0.95)',
  },
  resTopTitle: {
    fontSize: 20,
    fontWeight: '900',
    letterSpacing: 3,
    textShadowRadius: 15,
    textShadowOffset: { width: 0, height: 0 },
  },
  resultScroll: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 12,
  },
  resultRow: {
    flexDirection: 'row',
    gap: 12,
    alignItems: 'flex-start',
    justifyContent: 'center',
  },
  resLeftCol: {
    flex: 1,
    gap: 8,
    alignItems: 'center',
  },
  resCenterCol: {
    flex: 1,
    gap: 8,
    alignItems: 'center',
  },
  resRightCol: {
    flex: 1,
    alignItems: 'center',
  },
  resultContainer: { alignItems: 'center', gap: 8 },
  resultEmoji: { fontSize: 48 },
  resTitle: { fontSize: 36, fontWeight: '900', letterSpacing: 6, textShadowRadius: 20, textShadowOffset: { width: 0, height: 0 } },
  resultStats: { flexDirection: 'row', gap: 20 },
  rStatBox: { alignItems: 'center' },
  rStatVal: { color: '#fff', fontSize: 20, fontWeight: '900' },
  rStatLabel: { color: COLORS.textMuted, fontSize: 9, marginTop: 2 },
  mvpCard: { borderRadius: 10, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(255,215,0,0.25)' },
  mvpInner: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 14, paddingVertical: 8 },
  mvpLabel: { color: COLORS.gold, fontSize: 12, fontWeight: '900', letterSpacing: 2 },
  mvpName: { color: '#fff', fontSize: 14, fontWeight: '800' },
  rewardsCol: { alignItems: 'center', gap: 6 },
  rewardsSectionTitle: { color: COLORS.gold, fontSize: 10, fontWeight: '900', letterSpacing: 2 },
  rewardsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, justifyContent: 'center' },
  rewardBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: 'rgba(255,215,0,0.08)', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 8, borderWidth: 1, borderColor: 'rgba(255,215,0,0.2)' },
  rewardIcon: { fontSize: 14 },
  rewardVal: { color: COLORS.gold, fontSize: 12, fontWeight: '800' },
  resBtns: { flexDirection: 'row', gap: 12, marginTop: 16 },
  retryBtn: { paddingHorizontal: 22, paddingVertical: 10, borderRadius: 10 },
  retryTxt: { color: '#fff', fontSize: 12, fontWeight: '900', letterSpacing: 1 },
  menuBtn: { paddingHorizontal: 22, paddingVertical: 10, backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 10, borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)' },
  menuTxt: { color: '#fff', fontSize: 12, fontWeight: '800', letterSpacing: 1 },
  levelUpsWrap: { backgroundColor: 'rgba(68,221,136,0.08)', borderRadius: 8, padding: 8, borderWidth: 1, borderColor: 'rgba(68,221,136,0.2)', alignItems: 'center' },
  levelUpsTitle: { color: '#44DD88', fontSize: 10, fontWeight: '900', letterSpacing: 1, marginBottom: 3 },
  levelUpItem: { color: '#44DD88', fontSize: 10, fontWeight: '700' },
  accLevelUp: { color: '#FFD700', fontSize: 14, fontWeight: '900', letterSpacing: 1, textShadowColor: 'rgba(255,215,0,0.4)', textShadowRadius: 10, textShadowOffset: { width: 0, height: 0 } },
  dropsWrap: { backgroundColor: 'rgba(255,215,0,0.06)', borderRadius: 8, padding: 8, borderWidth: 1, borderColor: 'rgba(255,215,0,0.15)', alignItems: 'center' },
  dropsTitle: { color: COLORS.gold, fontSize: 10, fontWeight: '900', letterSpacing: 1, marginBottom: 4 },
  dropsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, justifyContent: 'center' },
  dropItem: { alignItems: 'center', width: 60 },
  dropIcon: { fontSize: 18 },
  dropName: { color: '#fff', fontSize: 7, fontWeight: '700', textAlign: 'center', marginTop: 2 },
  dropQty: { color: COLORS.gold, fontSize: 9, fontWeight: '900' },
});
