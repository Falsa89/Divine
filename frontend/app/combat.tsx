import React, { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Dimensions, ScrollView, Image, ImageSourcePropType, Platform, useWindowDimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS, ELEMENTS, RARITY } from '../constants/theme';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useAuth } from '../context/AuthContext';
import { apiCall } from '../utils/api';
import BattleSprite from '../components/BattleSprite';
import { heroBattleImageSource, heroImageSource, GREEK_HOPLITE_COMBAT_BASE } from '../components/ui/hopliteAssets';
import { pickBattleBackground, BattleBgResult, preloadBattleAsset } from '../components/ui/battleBackgrounds';
import { buildBattleLayout, getHomePosition } from '../components/battle/motionSystem';
import BattleDebugOverlay, { DebugUnitInfo } from '../components/battle/BattleDebugOverlay';

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
  const [teamB, setTeamB] = useState<any[]>([]);
  const [speed, setSpeed] = useState(1);
  const [showUlt, setShowUlt] = useState(false);
  const [ultInfo, setUltInfo] = useState({ char: '', skill: '', element: 'neutral' });
  const [error, setError] = useState('');
  const [logLines, setLogLines] = useState<any[]>([]);
  const [spriteStates, setSpriteStates] = useState<Record<string, SpriteData>>({});
  // Background della battaglia: scelto UNA SOLA volta all'inizio di ogni fight
  // e memorizzato qui per restare deterministicamente fisso durante la battaglia.
  const [battleBg, setBattleBg] = useState<BattleBgResult | null>(null);
  // Battlefield REAL rect (misurato via onLayout). Source of truth per le
  // home positions. Fallback a null → il layout assoluto non viene montato
  // finché non abbiamo le misure vere del container → su mobile le unità
  // non finiscono fuori asse per colpa del viewport globale.
  const [bfRect, setBfRect] = useState<{ w: number; h: number } | null>(null);
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
  const safeTimeout = (fn: () => void, ms: number) => {
    const id = setTimeout(fn, ms);
    allTimers.current.push(id);
    return id;
  };

  // Screen-level animations
  const flash = useSharedValue(0);
  const shakeX = useSharedValue(0);
  const ultScale = useSharedValue(0);
  const ultOp = useSharedValue(0);
  const vsScale = useSharedValue(0);
  const vsOp = useSharedValue(0);

  const flashStyle = useAnimatedStyle(() => ({ opacity: flash.value }));
  const shakeStyle = useAnimatedStyle(() => ({ transform: [{ translateX: shakeX.value }] }));
  const ultStyle = useAnimatedStyle(() => ({ transform: [{ scale: ultScale.value }], opacity: ultOp.value }));
  const vsStyle = useAnimatedStyle(() => ({ transform: [{ scale: vsScale.value }], opacity: vsOp.value }));

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

  const initSpriteState = (id: string): SpriteData => ({ state: 'idle', damage: null, healAmt: null, isCrit: false });

  const setSpriteState = (id: string, data: Partial<SpriteData>) => {
    if (BATTLE_DEBUG && data.state) dbg('sprite state', { id, state: data.state });
    setSpriteStates(prev => ({ ...prev, [id]: { ...(prev[id] || initSpriteState(id)), ...data } }));
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
    setPhase('loading'); setError(''); setLogLines([]);
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
      // ---- Preload asset critici PRIMA di avviare la scena ----------------
      // Evita su mobile/Expo Go il flash nero iniziale dovuto al tempo di
      // decode dei PNG di sfondo (~3 MB ciascuno). Timeout di safety per
      // non bloccare mai la battle se il preload fallisce.
      const preloadTimeout = new Promise<void>(res => setTimeout(res, 2500));
      await Promise.race([
        Promise.all([
          preloadBattleAsset(bg.source),
          preloadBattleAsset(GREEK_HOPLITE_COMBAT_BASE),
        ]).then(() => undefined),
        preloadTimeout,
      ]);
      // Init all sprite states
      const states: Record<string, SpriteData> = {};
      [...tA, ...tB].forEach(c => { states[c.id] = initSpriteState(c.id); });
      setSpriteStates(states);
      setPhase('preparing');
      // VS animation
      vsScale.value = 0; vsOp.value = 0;
      vsScale.value = withSequence(withTiming(1.3, { duration: 300 }), withTiming(1, { duration: 200 }));
      vsOp.value = withSequence(withTiming(1, { duration: 200 }), withDelay(600, withTiming(0, { duration: 200 })));
      safeTimeout(() => { setPhase('fighting'); if (r.battle_log?.length) playLog(r, 0, 0); }, 1400);
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
  const delay = () => (SPEED_BASE[speedRef.current] ?? 1500);

  const addLog = (entry: any) => {
    setLogLines(prev => [...prev.slice(-8), entry]);
    safeTimeout(() => logRef.current?.scrollToEnd({ animated: true }), 50);
  };

  const playLog = useCallback((res: any, ti: number, ai: number) => {
    if (!res.battle_log || ti >= res.battle_log.length) {
      setTeamA(res.team_a_final); setTeamB(res.team_b_final);
      // Set final dead states
      [...(res.team_a_final || []), ...(res.team_b_final || [])].forEach((c: any) => {
        if (!c.is_alive) setSpriteState(c.id, { state: 'dead' });
      });
      setPhase('result'); refreshUser(); return;
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
      setSpriteState(a.actor_id, { state: 'ultimate', damage: null, isCrit: false });
      setShowUlt(true);
      setUltInfo({ char: a.actor || '', skill: a.skill?.name || '', element: a.element || 'neutral' });
      ultScale.value = 0; ultOp.value = 0;
      ultScale.value = withSequence(withTiming(1.2, { duration: 200 }), withTiming(1, { duration: 150 }));
      ultOp.value = withSequence(withTiming(1, { duration: 100 }), withDelay(700, withTiming(0, { duration: 200 })));
      flash.value = withSequence(withTiming(0.5, { duration: 60 }), withTiming(0, { duration: 250 }));
      addLog({ type: 'ultimate', actor: a.actor, skill: a.skill?.name, team: a.team, element: a.element });

      // Apply damage after a beat
      timerRef.current = safeTimeout(() => {
        setShowUlt(false);
        updateHP(a);
        if (a.targets) {
          a.targets.forEach((tgt: any) => {
            setSpriteState(tgt.id, { state: tgt.killed ? 'dead' : 'hit', damage: a.total_damage || 0, isCrit: !!a.crit });
          });
        }
        addLog({ type: 'attack', actor: a.actor, skill: a.skill?.name, damage: a.total_damage, crit: a.crit, team: a.team, targets: a.targets?.map((t: any) => t.name).join(', ') });
        timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.6);
      }, delay() * 1.2);
    } else if (a.type === 'attack') {
      // Set attacker to attack state
      setSpriteState(a.actor_id, { state: a.skill_type === 'active' ? 'skill' : 'attack', damage: null, isCrit: false });

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
          a.targets.forEach((tgt: any) => {
            setSpriteState(tgt.id, { state: tgt.killed ? 'dead' : 'hit', damage: a.total_damage || 0, isCrit: !!a.crit });
          });
        }
        addLog({ type: 'attack', actor: a.actor, skill: a.skill?.name, damage: a.total_damage, crit: a.crit, team: a.team, targets: a.targets?.map((t: any) => t.name).join(', ') });
        timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.5);
      }, delay() * 0.4);
    } else if (a.type === 'heal') {
      setSpriteState(a.actor_id, { state: 'heal', healAmt: a.amount || 0, isCrit: false });
      updateHP(a);
      addLog({ type: 'heal', actor: a.actor, amount: a.amount });
      timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.5);
    } else if (a.type === 'dot') {
      if (a.target_id) setSpriteState(a.target_id, { state: 'hit', damage: a.damage || 0, isCrit: false });
      updateHP(a);
      addLog({ type: 'dot', target: a.target, damage: a.damage, effect: (a as any).effect_name });
      timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.4);
    } else if (a.type === 'dodge') {
      if (a.target_id) setSpriteState(a.target_id, { state: 'dodge', damage: null, isCrit: false });
      addLog({ type: 'dodge', target: a.target });
      timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.4);
    } else {
      addLog({ type: 'skip', actor: a.actor });
      timerRef.current = safeTimeout(() => playLog(res, ti, ai + 1), delay() * 0.3);
    }
  }, [speed]);

  const updateHP = (a: any) => {
    if (a.type === 'attack' && a.targets) {
      a.targets.forEach((t: any) => {
        const upd = (prev: any[]) => prev.map(c => c.id === t.id ? { ...c, current_hp: Math.max(0, t.hp_remaining), is_alive: !t.killed } : c);
        setTeamA(upd); setTeamB(upd);
      });
    } else if (a.type === 'dot' && a.target_id) {
      const upd = (prev: any[]) => prev.map(c => c.id === a.target_id ? { ...c, current_hp: Math.max(0, c.current_hp - (a.damage || 0)), is_alive: c.current_hp - (a.damage || 0) > 0 } : c);
      setTeamA(upd); setTeamB(upd);
    } else if (a.type === 'heal' && a.actor_id) {
      const upd = (prev: any[]) => prev.map(c => c.id === a.actor_id ? { ...c, current_hp: Math.min(c.max_hp_battle, c.current_hp + (a.amount || 0)) } : c);
      setTeamA(upd); setTeamB(upd);
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
    }
  };

  const getHpPct = (c: any) => c.max_hp_battle > 0 ? (c.current_hp / c.max_hp_battle) * 100 : 0;
  const getSpriteState = (id: string) => spriteStates[id] || initSpriteState(id);

  // LOADING
  if (phase === 'loading') return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={st.fc}>
      <Animated.View entering={ZoomIn.duration(300)}>
        <Text style={st.loadIcon}>{'\u2694\uFE0F'}</Text>
      </Animated.View>
      <Text style={st.loadTxt}>Preparazione Battaglia...</Text>
    </LinearGradient>
  );

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
    return (
      <View key={c.id} style={[st.hudCard, dead && { opacity: 0.35 }]}>
        <View style={[st.hudImg, { borderColor: rarCol }]}>
          {img ? (
            // Top HUD portrait = SPLASH ART (UI context), NON combat pose.
            // Regola pipeline: le top hero cards usano sempre la splash, mai combat_base né idle.
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
        </View>
      </View>
    );
  };

  // Wrapper dinamico: se è stato scelto uno sfondo fazione renderizza l'Image
  // absolute-fill con width/height ESPLICITI presi da useWindowDimensions
  // (pattern cross-platform affidabile su iOS/Android/Web — evita il bug
  // RN-Web dell'Image che altrimenti userebbe le dimensioni native del PNG
  // e lascerebbe fasce nere, e evita anche che su native 'width:100%' si
  // comporti in modo diverso dal previsto).
  // resizeMode="cover" gestisce il crop su tutte le piattaforme.
  // Overlay scuro MOLTO leggero: il bg resta dominante e nitido.
  const BattleWrapper = ({ children }: { children: React.ReactNode }) => {
    if (battleBg?.source) {
      return (
        <View style={{ flex: 1, backgroundColor: '#060614', overflow: 'hidden' }}>
          <Image
            source={battleBg.source}
            style={{ position: 'absolute', top: 0, left: 0, width: winW, height: winH }}
            resizeMode="cover"
            fadeDuration={200}
          />
          {/* Overlay scuro molto leggero — il bg DEVE restare dominante */}
          <LinearGradient
            colors={['rgba(6,6,20,0.20)', 'rgba(10,8,24,0.02)', 'rgba(6,6,20,0.28)']}
            style={StyleSheet.absoluteFillObject}
            pointerEvents="none"
          />
          {children}
        </View>
      );
    }
    return (
      <LinearGradient colors={['#060614', '#0A0A24', '#0D0820']} style={{ flex: 1 }}>
        {children}
      </LinearGradient>
    );
  };

  return (
    <BattleWrapper>
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
              {[1, 2, 3].map(s => (
                <TouchableOpacity key={s} style={[st.spdBtn, speed === s && st.spdA]} onPress={() => setSpeed(s)}>
                  <Text style={[st.spdTxt, speed === s && { color: COLORS.accent }]}>{s}x</Text>
                </TouchableOpacity>
              ))}
            </View>
            <TouchableOpacity onPress={skip} activeOpacity={0.7} style={st.skipBtn}>
              <Text style={st.skipTxt}>{'\u23E9'} SALTA</Text>
            </TouchableOpacity>
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

        {/* Action Log - bottom */}
        <View style={st.logPanel}>
          <ScrollView
            ref={logRef}
            horizontal={false}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={st.logContent}
          >
            {logLines.map((entry, i) => (
              <View key={i} style={st.logLine}>
                {entry.type === 'attack' && (
                  <Text style={st.logText} numberOfLines={1}>
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
            ))}
          </ScrollView>
        </View>

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
    </BattleWrapper>
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
    backgroundColor: 'rgba(6,6,20,0.95)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,107,53,0.1)',
    paddingHorizontal: 10,
    paddingTop: 4,
    paddingBottom: 4,
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
    width: 38,
  },
  hudImg: {
    width: 32,
    height: 32,
    borderRadius: 6,
    borderWidth: 1.5,
    overflow: 'hidden',
    backgroundColor: '#0A0A20',
  },
  hudImgInner: {
    width: 29,
    height: 29,
    borderRadius: 4,
  },
  hudImgPh: {
    width: 29,
    height: 29,
    borderRadius: 4,
    alignItems: 'center',
    justifyContent: 'center',
  },
  hudInit: {
    fontSize: 14,
    fontWeight: '900',
  },
  hudHpOuter: {
    width: 32,
    marginTop: 2,
  },
  hudHpBg: {
    width: '100%',
    height: 3,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  hudHpFill: {
    height: '100%',
    borderRadius: 2,
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
  logPanel: {
    height: 46,
    backgroundColor: 'rgba(6,6,20,0.95)',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,107,53,0.1)',
    paddingHorizontal: 12,
    paddingVertical: 3,
  },
  logContent: { gap: 1 },
  logLine: { paddingVertical: 1 },
  logText: { color: '#ccc', fontSize: 10 },
  // Flash
  flashOv: { ...StyleSheet.absoluteFillObject, backgroundColor: '#fff', zIndex: 100 },
  // Ultimate
  ultOv: { ...StyleSheet.absoluteFillObject, zIndex: 90 },
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
