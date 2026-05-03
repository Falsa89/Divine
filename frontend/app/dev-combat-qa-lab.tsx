/**
 * Combat QA Lab — RM1.19-B
 * ═══════════════════════════════════════════════════════════════════════
 * DEV ONLY screen. Layout aggiornato per device reale.
 *
 * RM1.19-B changes vs RM1.19-A:
 *   - Layout: TUTTI i controlli a sinistra (40%), battlefield a destra
 *     (60%). Niente più overlap dei buttons sui sprites.
 *   - Enemy count: 1 / 2 / 3 / 6 supportati. 6-enemy formation 3×2.
 *   - Bulk enemy controls (kill all / HP=1 all / immortal all / reset all).
 *   - Hero filters: search-by-name + role pills (Tank / DPS Melee / DPS
 *     Ranged / Mage AoE / Assassin / Support / Healer / Control / Hybrid).
 *     Hero metadata data-driven via `LAB_HERO_OPTIONS` (espandibile).
 *   - Hoplite metadata corretta: role=Tank, element=earth, rarity=3.
 *   - Berserker metadata: role=DPS Melee, rarity=3.
 *   - Hoplite freeze defensive fix: auto-return-to-idle 950ms dopo
 *     attack/skill (cycle attack=800ms + buffer); hit/death return-to-idle
 *     800ms (Hoplite rig fa fallback a idle, qui non blocchiamo lo state).
 *
 * Hoplite hit/death note: HeroHopliteRig dichiara esplicitamente fallback
 * all'idle (cfr. commento componente). NON inventiamo asset, NON usiamo
 * Berserker assets. Il lab dispatcha lo stato corretto verso BattleSprite,
 * ma visivamente Hoplite resterà su idle frame finché non saranno forniti
 * i frame reference-locked per hit/death. È una FINDING documentata.
 */
import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView, Pressable, TextInput,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import BattleSprite from '../components/BattleSprite';
import { validateHeroContract } from '../components/ui/hopliteAssets';
// RM1.22-D — Lab options placeholder 1★/2★ (placeholder_dev).
import { PLACEHOLDER_LAB_HERO_OPTIONS_1STAR_2STAR } from '../components/ui/placeholderHeroContracts1star2star';

// ─────────────────────────────────────────────────────────────────────────
// Tipi locali
// ─────────────────────────────────────────────────────────────────────────

type SpriteState = 'idle' | 'attack' | 'hit' | 'skill' | 'ultimate' | 'dead' | 'heal' | 'dodge';
type EnemyProfile = 'immortal' | 'normal' | 'lethal';
type DamageMode = 'off' | 'normal' | 'lethal';
type HeroRole =
  | 'Tank' | 'DPS Melee' | 'DPS Ranged' | 'Mage AoE' | 'Assassin'
  | 'Support' | 'Healer' | 'Control' | 'Hybrid';

type EffectStatus = {
  shield: number;
  taunt: boolean;
  dot: { dmgPerTick: number; ticksLeft: number; tag: string } | null;
  hot: { healPerTick: number; ticksLeft: number; tag: string } | null;
  buffs: string[];
  debuffs: string[];
};

const newEffects = (): EffectStatus => ({
  shield: 0, taunt: false, dot: null, hot: null, buffs: [], debuffs: [],
});

type Unit = {
  id: string;
  heroId: string;
  name: string;
  element: string;
  faction: string;
  rarity: number;
  hp: number;
  maxHp: number;
  immortal: boolean;
  alive: boolean;
  state: SpriteState;
  actionInstanceId: number;
  effects: EffectStatus;
};

type LabHero = {
  id: string;
  name: string;
  element: string;
  faction: string;
  rarity: number;
  role: HeroRole;
};

// ─────────────────────────────────────────────────────────────────────────
// LAB_HERO_OPTIONS — data-driven: aggiungi qui ogni nuovo eroe importato.
// I metadati sono LAB-ONLY (non sostituiscono i contracts in HERO_CONTRACTS).
// Usati per filtri (role/element/faction/rarity/search). RM1.19-B:
//   - Hoplite corretto a element=earth, role=Tank, rarity=3.
//   - Berserker rarity 3 + role=DPS Melee.
// ─────────────────────────────────────────────────────────────────────────
const LAB_HERO_OPTIONS: LabHero[] = [
  { id: 'greek_hoplite',   name: 'Hoplite',   element: 'earth', faction: 'greek', rarity: 3, role: 'Tank' },
  { id: 'norse_berserker', name: 'Berserker', element: 'fire',  faction: 'norse', rarity: 3, role: 'DPS Melee' },
  // RM1.22-D — Placeholder 1★/2★ (placeholder_dev): lab-only metadata.
  // Aggiunti DOPO Hoplite/Berserker per non alterare gli indici fissi
  // (LAB_HERO_OPTIONS[0]=Hoplite, [1]=Berserker) usati altrove nel file.
  ...PLACEHOLDER_LAB_HERO_OPTIONS_1STAR_2STAR,
];

const ALL_ROLES: (HeroRole | 'All')[] = [
  'All', 'Tank', 'DPS Melee', 'DPS Ranged', 'Mage AoE', 'Assassin', 'Support', 'Healer', 'Control', 'Hybrid',
];

const ENEMY_PROFILE_LABEL: Record<EnemyProfile, string> = {
  immortal: 'IMMORTAL', normal: 'NORMAL', lethal: 'LETHAL',
};

const ENEMY_COUNT_OPTIONS = [1, 2, 3, 6] as const;

// Damage table dev-only (indipendente da balance produzione)
const DAMAGE_NORMAL = 1500;
const DAMAGE_LETHAL = 999_999;
const DAMAGE_BUTTON_TICK = 2000;
const HEAL_DEFAULT = 4000;
const SHIELD_DEFAULT = 5000;
const DOT_TICK_DAMAGE = 1200;
const DOT_DEFAULT_TICKS = 5;
const DUMMY_BASE_HP = 50_000;
const DUMMY_LETHAL_HP = 80_000;

// RM1.19-B — Auto-return-to-idle dopo animazione finita. Risolve la
// percezione "freeze" su Hoplite: dopo attack/skill (anim ~800ms) torniamo
// a idle. Per hit/death il rig Hoplite fa fallback all'idle frame, quindi
// ritornare a idle è coerente.
const ANIM_AUTO_IDLE_MS: Record<SpriteState, number> = {
  idle: 0, attack: 950, skill: 1000, hit: 700, dead: 0, ultimate: 1100, heal: 600, dodge: 500,
};

function makeHeroUnit(opt: LabHero): Unit {
  return {
    id: 'hero',
    heroId: opt.id,
    name: opt.name,
    element: opt.element,
    faction: opt.faction,
    rarity: opt.rarity,
    hp: 30_000,
    maxHp: 30_000,
    immortal: false,
    alive: true,
    state: 'idle',
    actionInstanceId: 0,
    effects: newEffects(),
  };
}

function makeEnemyUnit(idx: number, profile: EnemyProfile): Unit {
  const hp = profile === 'lethal' ? DUMMY_LETHAL_HP : DUMMY_BASE_HP;
  return {
    id: `enemy_${idx}`,
    heroId: 'placeholder_dummy',
    name: `${String.fromCharCode(65 + idx)}`,
    element: profile === 'lethal' ? 'dark' : profile === 'immortal' ? 'light' : 'earth',
    faction: 'wild',
    rarity: 3,
    hp,
    maxHp: hp,
    immortal: profile === 'immortal',
    alive: true,
    state: 'idle',
    actionInstanceId: 0,
    effects: newEffects(),
  };
}

// ─────────────────────────────────────────────────────────────────────────
// Screen
// ─────────────────────────────────────────────────────────────────────────

export default function DevCombatQALab() {
  const router = useRouter();

  // Hero selection + filters
  const [searchTxt, setSearchTxt] = useState('');
  const [roleFilter, setRoleFilter] = useState<HeroRole | 'All'>('All');
  const filteredHeroes = useMemo(() => {
    const q = searchTxt.trim().toLowerCase();
    return LAB_HERO_OPTIONS.filter(h => {
      if (roleFilter !== 'All' && h.role !== roleFilter) return false;
      if (!q) return true;
      return h.name.toLowerCase().includes(q) || h.id.toLowerCase().includes(q);
    });
  }, [searchTxt, roleFilter]);

  const [heroOptIdx, setHeroOptIdx] = useState(1); // default Berserker
  const [hero, setHero] = useState<Unit>(() => makeHeroUnit(LAB_HERO_OPTIONS[1]));

  // Enemies
  const [enemyCount, setEnemyCount] = useState<number>(6); // RM1.19-B default 6
  const [enemyProfile, setEnemyProfile] = useState<EnemyProfile>('normal');
  const [damageMode, setDamageMode] = useState<DamageMode>('normal');
  const [enemies, setEnemies] = useState<Unit[]>(() =>
    Array.from({ length: 6 }, (_, i) => makeEnemyUnit(i, 'normal'))
  );
  const [selectedEnemyIdx, setSelectedEnemyIdx] = useState(0);

  // Logging
  const [log, setLog] = useState<string[]>([]);
  const logRef = useRef<ScrollView>(null);
  const pushLog = useCallback((line: string) => {
    setLog(prev => {
      const next = [...prev, `[${new Date().toLocaleTimeString().slice(-8)}] ${line}`];
      return next.length > 200 ? next.slice(-200) : next;
    });
  }, []);

  const heroWarnings = useMemo(
    () => validateHeroContract(hero.heroId, hero.name),
    [hero.heroId, hero.name],
  );

  // ─────────────────────────────────────────────────────────────────────
  // Hero swap
  // ─────────────────────────────────────────────────────────────────────
  const swapHero = useCallback((opt: LabHero) => {
    const i = LAB_HERO_OPTIONS.findIndex(o => o.id === opt.id);
    if (i < 0) return;
    setHeroOptIdx(i);
    setHero(makeHeroUnit(opt));
    pushLog(`Hero → ${opt.name} (${opt.id}, ${opt.role})`);
  }, [pushLog]);

  // ─────────────────────────────────────────────────────────────────────
  // Enemy slot management
  // ─────────────────────────────────────────────────────────────────────
  const rebuildEnemies = useCallback((count: number, profile: EnemyProfile) => {
    const arr: Unit[] = [];
    for (let i = 0; i < count; i++) arr.push(makeEnemyUnit(i, profile));
    setEnemies(arr);
    setSelectedEnemyIdx(0);
    pushLog(`Enemies × ${count} (${ENEMY_PROFILE_LABEL[profile]})`);
  }, [pushLog]);

  useEffect(() => {
    rebuildEnemies(enemyCount, enemyProfile);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enemyCount, enemyProfile]);

  // ─────────────────────────────────────────────────────────────────────
  // Animation dispatcher con replay + auto-return-to-idle (Hoplite freeze fix)
  // ─────────────────────────────────────────────────────────────────────
  const heroAutoIdleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const playHeroState = useCallback((state: SpriteState) => {
    setHero(prev => {
      const newAid = prev.actionInstanceId + 1;
      pushLog(`${prev.name} → ${state} (replay#${newAid})`);
      return { ...prev, state, actionInstanceId: newAid };
    });
    // RM1.19-B — auto-return-to-idle. Per stati che NON sono terminali
    // (idle/dead) schedula un setTimeout che riporta a 'idle'. Risolve la
    // percezione "freeze" del rig Hoplite (le animazioni hanno durata
    // fissa, dopodiché il sprite resta sull'ultimo frame).
    if (heroAutoIdleTimerRef.current) clearTimeout(heroAutoIdleTimerRef.current);
    const ms = ANIM_AUTO_IDLE_MS[state] || 0;
    if (ms > 0) {
      heroAutoIdleTimerRef.current = setTimeout(() => {
        setHero(prev => prev.alive && prev.state === state
          ? { ...prev, state: 'idle', actionInstanceId: prev.actionInstanceId + 1 }
          : prev
        );
      }, ms);
    }
  }, [pushLog]);

  useEffect(() => () => {
    if (heroAutoIdleTimerRef.current) clearTimeout(heroAutoIdleTimerRef.current);
  }, []);

  const playEnemyState = useCallback((idx: number, state: SpriteState) => {
    setEnemies(prev => prev.map((e, i) =>
      i === idx ? { ...e, state, actionInstanceId: e.actionInstanceId + 1 } : e
    ));
  }, []);

  // ─────────────────────────────────────────────────────────────────────
  // Damage application
  // ─────────────────────────────────────────────────────────────────────
  const applyDamageToUnit = useCallback(
    (unit: Unit, amount: number): { unit: Unit; absorbed: number; killed: boolean } => {
      if (!unit.alive) return { unit, absorbed: 0, killed: false };
      let remaining = amount;
      let absorbed = 0;
      const newEff: EffectStatus = { ...unit.effects };
      if (newEff.shield > 0) {
        absorbed = Math.min(newEff.shield, remaining);
        newEff.shield -= absorbed;
        remaining -= absorbed;
      }
      let newHp = unit.hp - remaining;
      let killed = false;
      if (unit.immortal) {
        if (newHp < 1) newHp = 1;
      } else if (newHp <= 0) {
        newHp = 0;
        killed = true;
      }
      return {
        unit: {
          ...unit,
          hp: newHp,
          alive: !killed,
          effects: newEff,
          state: killed ? 'dead' : 'hit',
          actionInstanceId: unit.actionInstanceId + 1,
        },
        absorbed,
        killed,
      };
    }, [],
  );

  const damageHero = useCallback((amount: number, source: string) => {
    setHero(prev => {
      const r = applyDamageToUnit(prev, amount);
      const dealt = amount - r.absorbed;
      pushLog(`${prev.name} −${dealt} HP (shield ${r.absorbed}) [${source}] → ${r.unit.hp}/${prev.maxHp}${r.killed ? ' ☠' : ''}${prev.immortal ? ' [IMM]' : ''}`);
      if (!r.killed) {
        if (heroAutoIdleTimerRef.current) clearTimeout(heroAutoIdleTimerRef.current);
        heroAutoIdleTimerRef.current = setTimeout(
          () => setHero(p => p.alive ? { ...p, state: 'idle', actionInstanceId: p.actionInstanceId + 1 } : p),
          ANIM_AUTO_IDLE_MS.hit,
        );
      }
      return r.unit;
    });
  }, [applyDamageToUnit, pushLog]);

  const damageEnemy = useCallback((idx: number, amount: number, source: string) => {
    setEnemies(prev => prev.map((e, i) => {
      if (i !== idx) return e;
      const r = applyDamageToUnit(e, amount);
      const dealt = amount - r.absorbed;
      pushLog(`${e.name} −${dealt} HP (shield ${r.absorbed}) [${source}] → ${r.unit.hp}/${e.maxHp}${r.killed ? ' ☠' : ''}${e.immortal ? ' [IMM]' : ''}`);
      if (!r.killed) {
        setTimeout(
          () => setEnemies(p => p.map((u, j) => j === idx && u.alive ? { ...u, state: 'idle', actionInstanceId: u.actionInstanceId + 1 } : u)),
          ANIM_AUTO_IDLE_MS.hit,
        );
      }
      return r.unit;
    }));
  }, [applyDamageToUnit, pushLog]);

  const healUnit = useCallback((target: 'hero' | 'enemy', enemyIdx: number, amount: number) => {
    if (target === 'hero') {
      setHero(prev => {
        const newHp = Math.min(prev.maxHp, prev.hp + amount);
        const healed = newHp - prev.hp;
        pushLog(`${prev.name} +${healed} HP (heal) → ${newHp}/${prev.maxHp}`);
        return { ...prev, hp: newHp, state: 'heal', actionInstanceId: prev.actionInstanceId + 1 };
      });
      if (heroAutoIdleTimerRef.current) clearTimeout(heroAutoIdleTimerRef.current);
      heroAutoIdleTimerRef.current = setTimeout(
        () => setHero(p => p.alive ? { ...p, state: 'idle', actionInstanceId: p.actionInstanceId + 1 } : p),
        ANIM_AUTO_IDLE_MS.heal,
      );
    } else {
      setEnemies(prev => prev.map((e, i) => {
        if (i !== enemyIdx) return e;
        const newHp = Math.min(e.maxHp, e.hp + amount);
        pushLog(`${e.name} +${newHp - e.hp} HP (heal)`);
        return { ...e, hp: newHp };
      }));
    }
  }, [pushLog]);

  const addShield = useCallback((target: 'hero' | 'enemy', enemyIdx: number, amount: number) => {
    if (target === 'hero') {
      setHero(prev => {
        const newShield = prev.effects.shield + amount;
        pushLog(`${prev.name} +${amount} shield → ${newShield}`);
        return { ...prev, effects: { ...prev.effects, shield: newShield } };
      });
    } else {
      setEnemies(prev => prev.map((e, i) =>
        i === enemyIdx ? { ...e, effects: { ...e.effects, shield: e.effects.shield + amount } } : e
      ));
    }
  }, [pushLog]);

  // ─────────────────────────────────────────────────────────────────────
  // Forced HP / death controls
  // ─────────────────────────────────────────────────────────────────────
  const setHeroHpFull = () => setHero(p => ({ ...p, hp: p.maxHp, alive: true, state: 'idle' }));
  const setHeroHp1 = () => setHero(p => ({ ...p, hp: 1, alive: true }));
  const killHero = () => {
    if (hero.immortal) { pushLog(`Kill bloccato: ${hero.name} è IMMORTAL`); return; }
    setHero(p => ({ ...p, hp: 0, alive: false, state: 'dead', actionInstanceId: p.actionInstanceId + 1 }));
    pushLog(`${hero.name} → KILL [death]`);
  };
  const toggleHeroImmortal = () => setHero(p => {
    pushLog(`${p.name} immortal → ${!p.immortal}`);
    return { ...p, immortal: !p.immortal };
  });

  const setEnemyHp1 = (idx: number) => setEnemies(p => p.map((e, i) =>
    i === idx ? { ...e, hp: 1, alive: true } : e
  ));
  const killEnemy = (idx: number) => {
    const e = enemies[idx]; if (!e) return;
    if (e.immortal) { pushLog(`Kill bloccato: ${e.name} IMM`); return; }
    setEnemies(p => p.map((u, i) =>
      i === idx ? { ...u, hp: 0, alive: false, state: 'dead', actionInstanceId: u.actionInstanceId + 1 } : u
    ));
  };
  const toggleEnemyImmortal = (idx: number) => setEnemies(p => p.map((e, i) => {
    if (i !== idx) return e;
    return { ...e, immortal: !e.immortal };
  }));

  // RM1.19-B — Bulk enemy controls
  const resetAllEnemies = () => {
    rebuildEnemies(enemyCount, enemyProfile);
  };
  const killAllEnemies = () => {
    setEnemies(p => p.map(e => e.immortal ? e : ({ ...e, hp: 0, alive: false, state: 'dead', actionInstanceId: e.actionInstanceId + 1 })));
    pushLog(`All enemies → KILL`);
  };
  const setAllEnemiesHp1 = () => {
    setEnemies(p => p.map(e => ({ ...e, hp: 1, alive: true })));
    pushLog(`All enemies → HP=1`);
  };
  const toggleAllEnemiesImmortal = () => {
    setEnemies(p => {
      const allImm = p.every(e => e.immortal);
      const next = !allImm;
      pushLog(`All enemies immortal → ${next}`);
      return p.map(e => ({ ...e, immortal: next }));
    });
  };

  // ─────────────────────────────────────────────────────────────────────
  // Enemy attack
  // ─────────────────────────────────────────────────────────────────────
  const enemyAttack = useCallback((sourceIdx: number) => {
    const source = enemies[sourceIdx];
    if (!source || !source.alive) return;
    playEnemyState(sourceIdx, 'attack');
    setTimeout(() => playEnemyState(sourceIdx, 'idle'), ANIM_AUTO_IDLE_MS.attack);
    if (damageMode === 'off') {
      pushLog(`${source.name} attack [OFF, no dmg]`);
      return;
    }
    const tauntActive = hero.effects.taunt;
    const dmg = damageMode === 'lethal' ? DAMAGE_LETHAL : DAMAGE_NORMAL;
    pushLog(`${source.name} → hero${tauntActive ? ' (TAUNT)' : ''} ${damageMode.toUpperCase()} ${dmg === DAMAGE_LETHAL ? 'LETHAL' : dmg}`);
    setTimeout(() => damageHero(dmg, source.name), 200);
  }, [enemies, damageMode, hero.effects.taunt, playEnemyState, damageHero, pushLog]);

  // ─────────────────────────────────────────────────────────────────────
  // Skill / Effect sandbox
  // ─────────────────────────────────────────────────────────────────────
  const testSingleDamage = () => {
    if (enemies.length === 0) return;
    playHeroState('attack');
    setTimeout(() => damageEnemy(selectedEnemyIdx, DAMAGE_BUTTON_TICK, `${hero.name} ST`), 250);
  };

  const testAoEDamage = () => {
    playHeroState('skill');
    enemies.forEach((_, i) => {
      setTimeout(() => damageEnemy(i, DAMAGE_BUTTON_TICK, `${hero.name} AoE`), 280 + i * 70);
    });
  };

  const applyDoT = (target: 'hero' | 'enemy') => {
    if (target === 'hero') {
      setHero(p => ({ ...p, effects: { ...p.effects, dot: { dmgPerTick: DOT_TICK_DAMAGE, ticksLeft: DOT_DEFAULT_TICKS, tag: 'Burn' } } }));
      pushLog(`${hero.name} +Burn DoT (${DOT_TICK_DAMAGE}/t × ${DOT_DEFAULT_TICKS})`);
    } else {
      setEnemies(p => p.map((e, i) =>
        i === selectedEnemyIdx ? { ...e, effects: { ...e.effects, dot: { dmgPerTick: DOT_TICK_DAMAGE, ticksLeft: DOT_DEFAULT_TICKS, tag: 'Bleed' } } } : e
      ));
    }
  };

  const tickDoTOnce = () => {
    if (hero.effects.dot && hero.effects.dot.ticksLeft > 0 && hero.alive) {
      const dot = hero.effects.dot;
      damageHero(dot.dmgPerTick, `${dot.tag} DoT`);
      setHero(p => ({ ...p, effects: { ...p.effects, dot: dot.ticksLeft - 1 > 0 ? { ...dot, ticksLeft: dot.ticksLeft - 1 } : null } }));
    }
    enemies.forEach((e, i) => {
      if (e.effects.dot && e.effects.dot.ticksLeft > 0 && e.alive) {
        const dot = e.effects.dot;
        damageEnemy(i, dot.dmgPerTick, `${dot.tag} DoT`);
        setEnemies(p => p.map((u, j) =>
          j === i ? { ...u, effects: { ...u.effects, dot: dot.ticksLeft - 1 > 0 ? { ...dot, ticksLeft: dot.ticksLeft - 1 } : null } } : u
        ));
      }
    });
  };
  const tickDoT5x = () => { for (let k = 0; k < 5; k++) setTimeout(tickDoTOnce, k * 600); };

  const toggleTaunt = () => setHero(p => {
    const next = !p.effects.taunt;
    pushLog(`${p.name} taunt → ${next}`);
    return { ...p, effects: { ...p.effects, taunt: next } };
  });

  const clearAllEffects = () => {
    setHero(p => ({ ...p, effects: newEffects() }));
    setEnemies(p => p.map(e => ({ ...e, effects: newEffects() })));
    pushLog('All effects cleared');
  };

  const resetAll = () => {
    swapHero(LAB_HERO_OPTIONS[heroOptIdx]);
    rebuildEnemies(enemyCount, enemyProfile);
    setLog([]);
    pushLog('=== RESET ===');
  };

  useEffect(() => {
    setTimeout(() => logRef.current?.scrollToEnd({ animated: false }), 30);
  }, [log]);

  // ─────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────
  return (
    <SafeAreaView style={s.root} edges={['top', 'bottom']}>
      <LinearGradient colors={['#0a0a1a', '#0a0a25']} style={StyleSheet.absoluteFillObject} />

      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Text style={s.backTxt}>‹ Indietro</Text>
        </TouchableOpacity>
        <Text style={s.title}>DEV ONLY — Combat QA Lab</Text>
        <View style={s.devBadge}><Text style={s.devBadgeTxt}>DEV</Text></View>
      </View>

      <View style={s.body}>
        {/* ───────────── COL SX (40%): TUTTI I CONTROLLI ───────────── */}
        <ScrollView style={s.colLeft} contentContainerStyle={{ padding: 6, gap: 4 }} showsVerticalScrollIndicator={false}>
          {/* Hero filters */}
          <Text style={s.section}>HERO ({filteredHeroes.length})</Text>
          <TextInput
            style={s.searchInput}
            placeholder="Cerca per nome/id…"
            placeholderTextColor="#666"
            value={searchTxt}
            onChangeText={setSearchTxt}
          />
          <View style={s.row}>
            {ALL_ROLES.map(r => (
              <TouchableOpacity key={r}
                onPress={() => setRoleFilter(r as any)}
                style={[s.miniPill, roleFilter === r && s.pillActive]}>
                <Text style={[s.miniPillTxt, roleFilter === r && s.pillTxtActive]}>{r}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={s.row}>
            {filteredHeroes.length === 0
              ? <Text style={s.dimTxt}>Nessun eroe matcha i filtri.</Text>
              : filteredHeroes.map(o => (
                <TouchableOpacity key={o.id}
                  onPress={() => swapHero(o)}
                  style={[s.pill, hero.heroId === o.id && s.pillActive]}>
                  <Text style={[s.pillTxt, hero.heroId === o.id && s.pillTxtActive]}>{o.name}</Text>
                  <Text style={s.pillSub}>{o.role} · {o.element}</Text>
                </TouchableOpacity>
              ))
            }
          </View>
          {heroWarnings.length > 0 && (
            <View style={s.warnBox}>
              <Text style={s.warnTitle}>⚠ Contract warnings ({heroWarnings.length})</Text>
              {heroWarnings.slice(0, 3).map((w, i) => <Text key={i} style={s.warnItem}>• {w}</Text>)}
            </View>
          )}

          {/* Animation */}
          <Text style={s.section}>ANIMATION</Text>
          <View style={s.btnGrid}>
            {(['idle', 'attack', 'skill', 'hit', 'dead', 'heal'] as SpriteState[]).map(st => (
              <TouchableOpacity key={st} style={s.btn} onPress={() => playHeroState(st)}>
                <Text style={s.btnTxt}>{st === 'dead' ? 'death' : st}</Text>
              </TouchableOpacity>
            ))}
            <TouchableOpacity style={[s.btn, s.btnGreen]} onPress={() => { playHeroState('idle'); }}>
              <Text style={s.btnTxt}>reset</Text>
            </TouchableOpacity>
          </View>

          {/* Hero HP/Death */}
          <Text style={s.section}>HERO HP / DEATH</Text>
          <View style={s.btnGrid}>
            <TouchableOpacity style={s.btn} onPress={setHeroHpFull}><Text style={s.btnTxt}>HP Full</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={setHeroHp1}><Text style={s.btnTxt}>HP=1</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => damageHero(DAMAGE_BUTTON_TICK, 'manual')}><Text style={s.btnTxt}>Dmg {DAMAGE_BUTTON_TICK}</Text></TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnRed]} onPress={() => damageHero(DAMAGE_LETHAL, 'lethal')}><Text style={s.btnTxt}>Lethal</Text></TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnRed]} onPress={killHero}><Text style={s.btnTxt}>Kill</Text></TouchableOpacity>
            <TouchableOpacity
              style={[s.btn, hero.immortal && s.btnAccent]}
              onPress={toggleHeroImmortal}>
              <Text style={s.btnTxt}>IMM: {hero.immortal ? 'ON' : 'OFF'}</Text>
            </TouchableOpacity>
          </View>

          {/* Enemy config */}
          <Text style={s.section}>ENEMY ({enemies.length})</Text>
          <View style={s.row}>
            {ENEMY_COUNT_OPTIONS.map(n => (
              <TouchableOpacity key={n} onPress={() => setEnemyCount(n)} style={[s.pill, enemyCount === n && s.pillActive]}>
                <Text style={[s.pillTxt, enemyCount === n && s.pillTxtActive]}>{n}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={s.row}>
            {(['immortal', 'normal', 'lethal'] as EnemyProfile[]).map(p => (
              <TouchableOpacity key={p} onPress={() => setEnemyProfile(p)} style={[s.pill, enemyProfile === p && s.pillActive]}>
                <Text style={[s.pillTxt, enemyProfile === p && s.pillTxtActive]}>{p}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text style={s.subSection}>damage mode</Text>
          <View style={s.row}>
            {(['off', 'normal', 'lethal'] as DamageMode[]).map(m => (
              <TouchableOpacity key={m} onPress={() => setDamageMode(m)} style={[s.pill, damageMode === m && s.pillActive]}>
                <Text style={[s.pillTxt, damageMode === m && s.pillTxtActive]}>{m}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={s.btnGrid}>
            <TouchableOpacity style={s.btn} onPress={() => enemyAttack(selectedEnemyIdx)}><Text style={s.btnTxt}>Sel→Hero</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => enemies.forEach((_, i) => enemyAttack(i))}><Text style={s.btnTxt}>All→Hero</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={resetAllEnemies}><Text style={s.btnTxt}>Reset Enem.</Text></TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnRed]} onPress={killAllEnemies}><Text style={s.btnTxt}>Kill All</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={setAllEnemiesHp1}><Text style={s.btnTxt}>All HP=1</Text></TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnAccent]} onPress={toggleAllEnemiesImmortal}><Text style={s.btnTxt}>All IMM tg</Text></TouchableOpacity>
          </View>

          <Text style={s.subSection}>selected #{selectedEnemyIdx}</Text>
          <View style={s.btnGrid}>
            <TouchableOpacity style={s.btn} onPress={() => playEnemyState(selectedEnemyIdx, 'hit')}><Text style={s.btnTxt}>hit</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => playEnemyState(selectedEnemyIdx, 'dead')}><Text style={s.btnTxt}>death</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => damageEnemy(selectedEnemyIdx, DAMAGE_BUTTON_TICK, 'manual')}><Text style={s.btnTxt}>Dmg</Text></TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnRed]} onPress={() => damageEnemy(selectedEnemyIdx, DAMAGE_LETHAL, 'lethal')}><Text style={s.btnTxt}>Lethal</Text></TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnRed]} onPress={() => killEnemy(selectedEnemyIdx)}><Text style={s.btnTxt}>Kill</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => setEnemyHp1(selectedEnemyIdx)}><Text style={s.btnTxt}>HP=1</Text></TouchableOpacity>
            <TouchableOpacity
              style={[s.btn, enemies[selectedEnemyIdx]?.immortal && s.btnAccent]}
              onPress={() => toggleEnemyImmortal(selectedEnemyIdx)}>
              <Text style={s.btnTxt}>IMM: {enemies[selectedEnemyIdx]?.immortal ? 'ON' : 'OFF'}</Text>
            </TouchableOpacity>
          </View>

          {/* Skill/Effect (mock) */}
          <Text style={s.section}>SKILL / EFFECT (mock)</Text>
          <View style={s.btnGrid}>
            <TouchableOpacity style={s.btn} onPress={testSingleDamage}><Text style={s.btnTxt}>ST Dmg</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={testAoEDamage}><Text style={s.btnTxt}>AoE Dmg</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => applyDoT('enemy')}><Text style={s.btnTxt}>DoT En</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => applyDoT('hero')}><Text style={s.btnTxt}>DoT Hero</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={tickDoTOnce}><Text style={s.btnTxt}>Tick 1×</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={tickDoT5x}><Text style={s.btnTxt}>Tick 5×</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => healUnit('hero', 0, HEAL_DEFAULT)}><Text style={s.btnTxt}>Heal H</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => healUnit('enemy', selectedEnemyIdx, HEAL_DEFAULT)}><Text style={s.btnTxt}>Heal E</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => addShield('hero', 0, SHIELD_DEFAULT)}><Text style={s.btnTxt}>Shld H</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => addShield('enemy', selectedEnemyIdx, SHIELD_DEFAULT)}><Text style={s.btnTxt}>Shld E</Text></TouchableOpacity>
            <TouchableOpacity style={[s.btn, hero.effects.taunt && s.btnAccent]} onPress={toggleTaunt}>
              <Text style={s.btnTxt}>Taunt: {hero.effects.taunt ? 'ON' : 'OFF'}</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnGreen]} onPress={clearAllEffects}><Text style={s.btnTxt}>Clear FX</Text></TouchableOpacity>
          </View>

          <TouchableOpacity style={[s.btn, s.btnGreen, { marginTop: 4 }]} onPress={resetAll}>
            <Text style={s.btnTxt}>RESET ALL</Text>
          </TouchableOpacity>

          {/* Log compatto */}
          <Text style={s.section}>LOG</Text>
          <View style={s.logBox}>
            <ScrollView ref={logRef} style={s.logScroll} contentContainerStyle={{ padding: 4 }}>
              {log.length === 0
                ? <Text style={s.logTxt}>—</Text>
                : log.map((l, i) => <Text key={i} style={s.logTxt}>{l}</Text>)}
            </ScrollView>
            <TouchableOpacity onPress={() => setLog([])} style={[s.miniPill, { marginTop: 2, alignSelf: 'flex-end' }]}>
              <Text style={s.miniPillTxt}>clear log</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>

        {/* ───────────── COL DX (60%): BATTLEFIELD ───────────── */}
        <View style={s.colRight}>
          <View style={s.battlefield}>
            {/* HERO SIDE */}
            <View style={s.heroSlot}>
              <Text style={s.unitLabel}>{hero.name} {hero.immortal ? 'IMM' : ''} {!hero.alive && '☠'}</Text>
              <View style={{ width: 130, height: 162, alignItems: 'center', justifyContent: 'flex-end' }}>
                <BattleSprite
                  character={{
                    id: hero.id,
                    hero_id: hero.heroId,
                    name: hero.name,
                    hero_name: hero.name,
                    element: hero.element,
                    hero_element: hero.element,
                    faction: hero.faction,
                    rarity: hero.rarity,
                    hero_rarity: hero.rarity,
                  }}
                  state={hero.state}
                  isEnemy={false}
                  hpPercent={hero.maxHp > 0 ? hero.hp / hero.maxHp : 0}
                  size={130}
                  actionInstanceId={hero.actionInstanceId}
                />
              </View>
              <HpBar hp={hero.hp} max={hero.maxHp} color="#44dd66" />
              <EffectsLine eff={hero.effects} />
            </View>

            {/* ENEMY SIDE — formation 3×2 if 6 enemies, else row */}
            <View style={[s.enemySide, enemies.length >= 6 ? s.enemyGrid : null]}>
              {enemies.map((e, i) => (
                <Pressable key={e.id}
                  style={[s.enemySlot, selectedEnemyIdx === i && s.enemySlotSel,
                    enemies.length >= 6 ? s.enemySlotSmall : null]}
                  onPress={() => setSelectedEnemyIdx(i)}>
                  <Text style={s.unitLabelSm}>
                    {selectedEnemyIdx === i ? '▶' : ''}{e.name} {e.immortal ? 'I' : ''} {!e.alive && '☠'}
                  </Text>
                  <View style={{
                    width: enemies.length >= 6 ? 70 : 90,
                    height: enemies.length >= 6 ? 88 : 113,
                    alignItems: 'center', justifyContent: 'flex-end',
                  }}>
                    <BattleSprite
                      character={{
                        id: e.id,
                        hero_id: e.heroId,
                        name: e.name,
                        hero_name: e.name,
                        element: e.element,
                        hero_element: e.element,
                        faction: e.faction,
                        rarity: e.rarity,
                      }}
                      state={e.state}
                      isEnemy={true}
                      hpPercent={e.maxHp > 0 ? e.hp / e.maxHp : 0}
                      size={enemies.length >= 6 ? 70 : 90}
                      actionInstanceId={e.actionInstanceId}
                    />
                  </View>
                  <HpBar hp={e.hp} max={e.maxHp} color="#dd4444" small={enemies.length >= 6} />
                  <EffectsLine eff={e.effects} compact={enemies.length >= 6} />
                </Pressable>
              ))}
            </View>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────────

function HpBar({ hp, max, color, small }: { hp: number; max: number; color: string; small?: boolean }) {
  const pct = max > 0 ? Math.max(0, Math.min(1, hp / max)) : 0;
  return (
    <View style={[s.hpBarRoot, small && { width: 70, height: 10 }]}>
      <View style={[s.hpBarFill, { width: `${pct * 100}%`, backgroundColor: color }]} />
      <Text style={[s.hpBarTxt, small && { fontSize: 7 }]}>
        {Math.round(hp).toLocaleString()}/{max.toLocaleString()}
      </Text>
    </View>
  );
}

function EffectsLine({ eff, compact }: { eff: EffectStatus; compact?: boolean }) {
  const tags: string[] = [];
  if (eff.shield > 0) tags.push(`🛡${eff.shield}`);
  if (eff.taunt) tags.push('TAUNT');
  if (eff.dot) tags.push(`🔥${eff.dot.tag} ${eff.dot.ticksLeft}t`);
  if (eff.hot) tags.push(`💚${eff.hot.tag} ${eff.hot.ticksLeft}t`);
  for (const b of eff.buffs) tags.push(`+${b}`);
  for (const d of eff.debuffs) tags.push(`-${d}`);
  if (tags.length === 0) return null;
  return <Text style={[s.eff, compact && { fontSize: 7, maxWidth: 70 }]}>{tags.join(' ')}</Text>;
}

// ─────────────────────────────────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────────────────────────────────

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#070713' },
  header: {
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: 8, paddingVertical: 4,
    backgroundColor: 'rgba(255,68,68,0.1)', borderBottomWidth: 1, borderBottomColor: '#ff4444',
  },
  backBtn: { paddingHorizontal: 8, paddingVertical: 4 },
  backTxt: { color: '#fff', fontSize: 12, fontWeight: '700' },
  title: { flex: 1, color: '#fff', fontSize: 13, fontWeight: '900', textAlign: 'center' },
  devBadge: { paddingHorizontal: 6, paddingVertical: 2, backgroundColor: '#ff4444', borderRadius: 3 },
  devBadgeTxt: { color: '#fff', fontWeight: '900', fontSize: 9 },

  body: { flex: 1, flexDirection: 'row' },
  // RM1.19-B — controlli a sinistra (40%), battlefield a destra (60%).
  colLeft: { width: '40%', borderRightWidth: 1, borderRightColor: '#222' },
  colRight: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 6 },

  section: { color: '#ffaa55', fontSize: 10, fontWeight: '900', letterSpacing: 1, marginTop: 4 },
  subSection: { color: '#888', fontSize: 9, fontWeight: '700', marginTop: 2 },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 3 },
  btnGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 3 },
  dimTxt: { color: '#666', fontSize: 9, fontStyle: 'italic' },

  searchInput: {
    backgroundColor: 'rgba(255,255,255,0.06)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.12)',
    paddingHorizontal: 8, paddingVertical: 5, color: '#fff', fontSize: 11, borderRadius: 4,
  },

  pill: {
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4,
    backgroundColor: 'rgba(255,255,255,0.06)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
  },
  miniPill: {
    paddingHorizontal: 6, paddingVertical: 3, borderRadius: 3,
    backgroundColor: 'rgba(255,255,255,0.04)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
  },
  pillActive: { backgroundColor: 'rgba(255,170,85,0.2)', borderColor: '#ffaa55' },
  pillTxt: { color: '#ddd', fontSize: 10, fontWeight: '700' },
  miniPillTxt: { color: '#bbb', fontSize: 9, fontWeight: '600' },
  pillTxtActive: { color: '#ffaa55' },
  pillSub: { color: '#999', fontSize: 8 },

  btn: {
    paddingHorizontal: 6, paddingVertical: 5, borderRadius: 3,
    backgroundColor: 'rgba(68,153,221,0.18)', borderWidth: 1, borderColor: 'rgba(68,153,221,0.4)',
    minWidth: 56, alignItems: 'center',
  },
  btnRed: { backgroundColor: 'rgba(221,68,68,0.2)', borderColor: '#dd4444' },
  btnGreen: { backgroundColor: 'rgba(68,221,102,0.2)', borderColor: '#44dd66' },
  btnAccent: { backgroundColor: 'rgba(255,170,85,0.3)', borderColor: '#ffaa55' },
  btnTxt: { color: '#fff', fontSize: 9, fontWeight: '700' },

  warnBox: {
    padding: 4, backgroundColor: 'rgba(221,170,68,0.1)', borderWidth: 1, borderColor: '#ddaa44', borderRadius: 4,
  },
  warnTitle: { color: '#ddaa44', fontSize: 9, fontWeight: '900' },
  warnItem: { color: '#ffeebb', fontSize: 8, marginTop: 1 },

  battlefield: {
    width: '100%', height: '100%',
    flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between',
    paddingHorizontal: 12, paddingBottom: 16, paddingTop: 8,
    backgroundColor: 'rgba(20,20,40,0.4)', borderRadius: 8,
  },
  heroSlot: { alignItems: 'center', minWidth: 140 },
  enemySide: { flexDirection: 'row', alignItems: 'flex-end', gap: 8 },
  // 6-enemy formation 3×2: wrap verticale.
  enemyGrid: { flexWrap: 'wrap', alignContent: 'flex-end', maxHeight: '100%', gap: 4 },
  enemySlot: { alignItems: 'center', padding: 3, borderRadius: 4, borderWidth: 2, borderColor: 'transparent' },
  enemySlotSmall: { width: '32%' },
  enemySlotSel: { borderColor: '#ffaa55', backgroundColor: 'rgba(255,170,85,0.05)' },
  unitLabel: { color: '#fff', fontSize: 10, fontWeight: '700', marginBottom: 2 },
  unitLabelSm: { color: '#fff', fontSize: 8, fontWeight: '700', marginBottom: 1 },

  hpBarRoot: {
    width: 110, height: 12, backgroundColor: 'rgba(0,0,0,0.6)', borderRadius: 6,
    overflow: 'hidden', marginTop: 2, justifyContent: 'center', alignItems: 'center',
  },
  hpBarFill: { position: 'absolute', left: 0, top: 0, bottom: 0 },
  hpBarTxt: { color: '#fff', fontSize: 7, fontWeight: '900', textShadowColor: '#000', textShadowRadius: 2 },
  eff: { color: '#bbb', fontSize: 8, marginTop: 1, maxWidth: 130, textAlign: 'center' },

  logBox: { backgroundColor: 'rgba(0,0,0,0.5)', borderRadius: 3, padding: 3, marginTop: 2 },
  logScroll: { maxHeight: 140 },
  logTxt: { color: '#9c9', fontSize: 8, fontFamily: 'monospace' as any, lineHeight: 11 },
});

// ─────────────────────────────────────────────────────────────────────────
// FUTURE HERO IMPORT NOTE — RM1.19-B
// ─────────────────────────────────────────────────────────────────────────
// Ogni nuovo eroe importato in HERO_CONTRACTS DEVE essere validato qui:
//   1. Aggiungerlo a LAB_HERO_OPTIONS con id, name, element, faction,
//      rarity, role (Tank/DPS/etc.) → appare automaticamente nei filtri.
//   2. Verifica idle / attack / skill / hit / death (auto-return-to-idle
//      ti riporta automaticamente al loop dopo ogni anim).
//   3. Verifica scale comparando con Hoplite/Berserker (selezionali e
//      confronta l'altezza body vs reference).
//   4. Test enemy normal/lethal mode + immortal → conferma death + hit
//      animation triggers correttamente.
//   5. 6-enemy AoE test (preset default).
//   6. Taunt test → enemy attack redirected (log dice "TAUNT").
//   7. DoT test → tick damage propaga, può uccidere se non immortal.
//   8. Heal/Shield test → shield assorbe prima di HP, log conferma.
//   9. Contract warnings = 0 visibile in alto a sinistra.
// Cfr. /app/docs/NEW_HERO_IMPORT_CHECKLIST.md.
