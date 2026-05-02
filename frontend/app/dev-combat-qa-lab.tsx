/**
 * Combat QA Lab — RM1.19
 * ═══════════════════════════════════════════════════════════════════════
 * DEV ONLY screen. Non è un'esperienza di gameplay.
 *
 * Scopo: harness riusabile per validare ogni eroe importato (presente o
 * futuro) coprendo:
 *   - Animazioni: idle / attack / skill / hit / death (replay supportato
 *     via actionInstanceId incrementale).
 *   - Render path reale: usa BattleSprite di produzione (Hoplite rig
 *     branch, Berserker runtime sheet branch, static fallback per future
 *     heroes). Niente fake renderer.
 *   - Dummies: 1-3 enemy slot configurabili (Immortal / Normal / Lethal).
 *   - Forced HP / death: damage diretto, lethal, kill, immortal toggle
 *     per eroe selezionato e per ogni enemy.
 *   - Skill/Effect sandbox locale (mock dev-only): single damage, AoE,
 *     DoT (tick), HoT, heal, shield assorb prima di HP, buff/debuff text,
 *     taunt con redirect del target dell'enemy attack.
 *   - Event log scorrevole con ogni dispatch.
 *
 * VINCOLI (RM1.19):
 *   - NON modifica produzione battle balance/logic (nessun import di
 *     skill_engine prod, nessuna chiamata a backend battle).
 *   - NON tocca runtime sheets / source_sheets / Hoplite assets.
 *   - NON regredisce Berserker o Hoplite (BattleSprite usato as-is).
 *   - Effetti sono mock dev-only. Quando il production skill engine
 *     sarà disaccoppiato, i mock potranno essere sostituiti 1:1 senza
 *     toccare la UI.
 *
 * Hoplite hit/death: HeroHopliteRig esplicitamente fa fallback a `idle`
 * per gli stati hit/death (cfr. commento in HeroHopliteRig.tsx). Il lab
 * dispatcha lo stato corretto verso BattleSprite, ma visivamente Hoplite
 * resterà in idle. Questa è una FINDING: servono asset frame-based per
 * hit/death di Hoplite. NON inventiamo asset, NON usiamo Berserker.
 */
import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView, Pressable,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import BattleSprite from '../components/BattleSprite';
import { validateHeroContract } from '../components/ui/hopliteAssets';

// ─────────────────────────────────────────────────────────────────────────
// Helpers e tipi locali
// ─────────────────────────────────────────────────────────────────────────

type SpriteState = 'idle' | 'attack' | 'hit' | 'skill' | 'ultimate' | 'dead' | 'heal' | 'dodge';

type EnemyProfile = 'immortal' | 'normal' | 'lethal';
type DamageMode = 'off' | 'normal' | 'lethal';

type EffectStatus = {
  shield: number;
  taunt: boolean;
  dot: { dmgPerTick: number; ticksLeft: number; tag: string } | null;
  hot: { healPerTick: number; ticksLeft: number; tag: string } | null;
  buffs: string[];
  debuffs: string[];
};

const newEffects = (): EffectStatus => ({
  shield: 0,
  taunt: false,
  dot: null,
  hot: null,
  buffs: [],
  debuffs: [],
});

type Unit = {
  id: string;
  heroId: string;
  name: string;
  element: string;
  faction: string;
  hp: number;
  maxHp: number;
  immortal: boolean;
  alive: boolean;
  state: SpriteState;
  actionInstanceId: number;
  effects: EffectStatus;
};

// Lista eroi selezionabili per il lab. Espandibile manualmente quando
// vengono importati nuovi eroi: l'unica condizione è avere un contract
// in HERO_CONTRACTS (validato a runtime via validateHeroContract).
const LAB_HERO_OPTIONS: { id: string; name: string; element: string; faction: string; rarity: number }[] = [
  { id: 'greek_hoplite',   name: 'Hoplite',   element: 'light', faction: 'greek',   rarity: 5 },
  { id: 'norse_berserker', name: 'Berserker', element: 'fire',  faction: 'norse',   rarity: 5 },
];

const ENEMY_PROFILE_LABEL: Record<EnemyProfile, string> = {
  immortal: 'IMMORTAL',
  normal: 'NORMAL',
  lethal: 'LETHAL',
};

// Damage table per "Normal" e "Lethal" enemy attack mode. Volutamente
// indipendenti dalla balance di produzione: questo è un harness QA.
const DAMAGE_NORMAL = 1500;
const DAMAGE_LETHAL = 999_999;
const DAMAGE_BUTTON_TICK = 2000;
const HEAL_BUTTON_TICK = 2000;
const DOT_TICK_DAMAGE = 1200;
const DOT_DEFAULT_TICKS = 5;
const SHIELD_DEFAULT = 5000;
const HEAL_DEFAULT = 4000;

// HP base per un dummy enemy (Normal/Lethal). Immortal usa lo stesso valore
// nominale ma il flag `immortal` impedisce di scendere sotto 1.
const DUMMY_BASE_HP = 50_000;
const DUMMY_LETHAL_HP = 80_000;

// Factory unit
function makeHeroUnit(opt: typeof LAB_HERO_OPTIONS[number]): Unit {
  return {
    id: 'hero',
    heroId: opt.id,
    name: opt.name,
    element: opt.element,
    faction: opt.faction,
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
    name: `Dummy ${String.fromCharCode(65 + idx)} (${ENEMY_PROFILE_LABEL[profile]})`,
    element: profile === 'lethal' ? 'dark' : profile === 'immortal' ? 'light' : 'earth',
    faction: 'wild',
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

  // Hero selection
  const [heroOptIdx, setHeroOptIdx] = useState(1); // default Berserker (più test recenti)
  const [hero, setHero] = useState<Unit>(() => makeHeroUnit(LAB_HERO_OPTIONS[1]));

  // Enemies
  const [enemyCount, setEnemyCount] = useState(1);
  const [enemyProfile, setEnemyProfile] = useState<EnemyProfile>('normal');
  const [damageMode, setDamageMode] = useState<DamageMode>('normal');
  const [enemies, setEnemies] = useState<Unit[]>(() => [makeEnemyUnit(0, 'normal')]);
  const [selectedEnemyIdx, setSelectedEnemyIdx] = useState(0);

  // Logging
  const [log, setLog] = useState<string[]>([]);
  const logRef = useRef<ScrollView>(null);
  const pushLog = useCallback((line: string) => {
    setLog(prev => {
      const next = [...prev, `[${new Date().toLocaleTimeString()}] ${line}`];
      return next.length > 200 ? next.slice(-200) : next;
    });
  }, []);

  // Validation warnings sull'eroe corrente (read-only, mostrato in UI)
  const heroWarnings = useMemo(
    () => validateHeroContract(hero.heroId, hero.name),
    [hero.heroId, hero.name],
  );

  // ─────────────────────────────────────────────────────────────────────
  // Hero swap
  // ─────────────────────────────────────────────────────────────────────
  const swapHero = useCallback((idx: number) => {
    const opt = LAB_HERO_OPTIONS[idx];
    if (!opt) return;
    setHeroOptIdx(idx);
    setHero(makeHeroUnit(opt));
    pushLog(`Hero swap → ${opt.name} (${opt.id})`);
  }, [pushLog]);

  // ─────────────────────────────────────────────────────────────────────
  // Enemy slot management
  // ─────────────────────────────────────────────────────────────────────
  const rebuildEnemies = useCallback((count: number, profile: EnemyProfile) => {
    const arr: Unit[] = [];
    for (let i = 0; i < count; i++) arr.push(makeEnemyUnit(i, profile));
    setEnemies(arr);
    setSelectedEnemyIdx(0);
    pushLog(`Enemy slots ricreati: count=${count}, profile=${ENEMY_PROFILE_LABEL[profile]}`);
  }, [pushLog]);

  useEffect(() => {
    rebuildEnemies(enemyCount, enemyProfile);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enemyCount, enemyProfile]);

  // ─────────────────────────────────────────────────────────────────────
  // Animation dispatcher con replay (incrementa actionInstanceId)
  // ─────────────────────────────────────────────────────────────────────
  const playHeroState = useCallback((state: SpriteState) => {
    setHero(prev => ({ ...prev, state, actionInstanceId: prev.actionInstanceId + 1 }));
    pushLog(`${hero.name} → state=${state} (replay#${hero.actionInstanceId + 1})`);
  }, [hero.name, hero.actionInstanceId, pushLog]);

  const playEnemyState = useCallback((idx: number, state: SpriteState) => {
    setEnemies(prev => prev.map((e, i) =>
      i === idx ? { ...e, state, actionInstanceId: e.actionInstanceId + 1 } : e
    ));
    const e = enemies[idx];
    if (e) pushLog(`${e.name} → state=${state}`);
  }, [enemies, pushLog]);

  // ─────────────────────────────────────────────────────────────────────
  // Damage/Heal/Shield application (con effetti e immortal)
  // ─────────────────────────────────────────────────────────────────────

  /**
   * Applica damage a una unit. Rispetta:
   *  - shield (assorbe prima dell'HP)
   *  - immortal flag (HP non scende sotto 1, no death)
   *  - alive flag (no damage a unit morta)
   * Triggers hit animation. Se HP raggiunge 0 e non immortal, schedula
   * death animation dopo un breve delay.
   */
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
    },
    [],
  );

  const damageHero = useCallback((amount: number, source: string) => {
    setHero(prev => {
      const r = applyDamageToUnit(prev, amount);
      const dealt = amount - r.absorbed;
      pushLog(`${prev.name} took ${dealt} damage (shield absorbed ${r.absorbed}) from ${source} → HP ${r.unit.hp}/${prev.maxHp}${r.killed ? ' [DEATH]' : ''}${prev.immortal ? ' [IMMORTAL locked at ≥1]' : ''}`);
      // Reset to idle dopo un breve delay solo se non killed
      if (!r.killed) {
        setTimeout(() => setHero(p => p.alive ? { ...p, state: 'idle' } : p), 700);
      }
      return r.unit;
    });
  }, [applyDamageToUnit, pushLog]);

  const damageEnemy = useCallback((idx: number, amount: number, source: string) => {
    setEnemies(prev => prev.map((e, i) => {
      if (i !== idx) return e;
      const r = applyDamageToUnit(e, amount);
      const dealt = amount - r.absorbed;
      pushLog(`${e.name} took ${dealt} damage (shield ${r.absorbed}) from ${source} → HP ${r.unit.hp}/${e.maxHp}${r.killed ? ' [DEATH]' : ''}${e.immortal ? ' [IMMORTAL]' : ''}`);
      if (!r.killed) {
        setTimeout(() => setEnemies(p => p.map((u, j) => j === idx && u.alive ? { ...u, state: 'idle' } : u)), 700);
      }
      return r.unit;
    }));
  }, [applyDamageToUnit, pushLog]);

  const healUnit = useCallback((target: 'hero' | 'enemy', enemyIdx: number, amount: number) => {
    if (target === 'hero') {
      setHero(prev => {
        const newHp = Math.min(prev.maxHp, prev.hp + amount);
        const healed = newHp - prev.hp;
        pushLog(`${prev.name} healed for ${healed} → HP ${newHp}/${prev.maxHp}`);
        return { ...prev, hp: newHp, state: 'heal', actionInstanceId: prev.actionInstanceId + 1 };
      });
      setTimeout(() => setHero(p => p.alive ? { ...p, state: 'idle' } : p), 600);
    } else {
      setEnemies(prev => prev.map((e, i) => {
        if (i !== enemyIdx) return e;
        const newHp = Math.min(e.maxHp, e.hp + amount);
        pushLog(`${e.name} healed for ${newHp - e.hp} → HP ${newHp}/${e.maxHp}`);
        return { ...e, hp: newHp };
      }));
    }
  }, [pushLog]);

  const addShield = useCallback((target: 'hero' | 'enemy', enemyIdx: number, amount: number) => {
    if (target === 'hero') {
      setHero(prev => {
        const newShield = prev.effects.shield + amount;
        pushLog(`${prev.name} gained shield +${amount} → shield ${newShield}`);
        return { ...prev, effects: { ...prev.effects, shield: newShield } };
      });
    } else {
      setEnemies(prev => prev.map((e, i) =>
        i === enemyIdx ? { ...e, effects: { ...e.effects, shield: e.effects.shield + amount } } : e
      ));
      const e = enemies[enemyIdx];
      if (e) pushLog(`${e.name} gained shield +${amount}`);
    }
  }, [enemies, pushLog]);

  // ─────────────────────────────────────────────────────────────────────
  // Forced HP / death controls
  // ─────────────────────────────────────────────────────────────────────
  const setHeroHpFull = () => setHero(p => ({ ...p, hp: p.maxHp, alive: true, state: 'idle' }));
  const setHeroHp1 = () => setHero(p => ({ ...p, hp: 1, alive: true }));
  const killHero = () => {
    if (hero.immortal) { pushLog(`Kill bloccato: ${hero.name} è IMMORTAL`); return; }
    setHero(p => ({ ...p, hp: 0, alive: false, state: 'dead', actionInstanceId: p.actionInstanceId + 1 }));
    pushLog(`${hero.name} → forced KILL [death anim]`);
  };
  const toggleHeroImmortal = () => setHero(p => {
    pushLog(`${p.name} immortal toggle → ${!p.immortal}`);
    return { ...p, immortal: !p.immortal };
  });

  const setEnemyHpFull = (idx: number) => setEnemies(p => p.map((e, i) =>
    i === idx ? { ...e, hp: e.maxHp, alive: true, state: 'idle' } : e
  ));
  const setEnemyHp1 = (idx: number) => setEnemies(p => p.map((e, i) =>
    i === idx ? { ...e, hp: 1, alive: true } : e
  ));
  const killEnemy = (idx: number) => {
    const e = enemies[idx];
    if (!e) return;
    if (e.immortal) { pushLog(`Kill bloccato: ${e.name} è IMMORTAL`); return; }
    setEnemies(p => p.map((u, i) =>
      i === idx ? { ...u, hp: 0, alive: false, state: 'dead', actionInstanceId: u.actionInstanceId + 1 } : u
    ));
    pushLog(`${e.name} → forced KILL`);
  };
  const toggleEnemyImmortal = (idx: number) => setEnemies(p => p.map((e, i) => {
    if (i !== idx) return e;
    pushLog(`${e.name} immortal → ${!e.immortal}`);
    return { ...e, immortal: !e.immortal };
  }));

  // ─────────────────────────────────────────────────────────────────────
  // Enemy attack simulation (Off / Normal / Lethal)
  // ─────────────────────────────────────────────────────────────────────
  const enemyAttack = useCallback((sourceIdx: number) => {
    const source = enemies[sourceIdx];
    if (!source || !source.alive) return;
    // Trigger attack anim sull'enemy
    playEnemyState(sourceIdx, 'attack');
    setTimeout(() => playEnemyState(sourceIdx, 'idle'), 600);

    if (damageMode === 'off') {
      pushLog(`${source.name} attack (mode=OFF, no damage)`);
      return;
    }
    // Target selection: taunt > selected hero
    const target = hero.effects.taunt ? 'hero (taunt)' : 'hero';
    const dmg = damageMode === 'lethal' ? DAMAGE_LETHAL : DAMAGE_NORMAL;
    pushLog(`${source.name} attacca → target=${target}, mode=${damageMode.toUpperCase()}, damage=${dmg === DAMAGE_LETHAL ? 'LETHAL' : dmg}`);
    setTimeout(() => damageHero(dmg, source.name), 200);
  }, [enemies, damageMode, hero.effects.taunt, playEnemyState, damageHero, pushLog]);

  // ─────────────────────────────────────────────────────────────────────
  // Skill / Effect sandbox (mock dev-only)
  // ─────────────────────────────────────────────────────────────────────
  const testSingleDamage = () => {
    if (enemies.length === 0) return;
    playHeroState('attack');
    setTimeout(() => playHeroState('idle'), 600);
    setTimeout(() => damageEnemy(selectedEnemyIdx, DAMAGE_BUTTON_TICK, `${hero.name} skill`), 200);
  };

  const testAoEDamage = () => {
    playHeroState('skill');
    setTimeout(() => playHeroState('idle'), 800);
    enemies.forEach((_, i) => {
      setTimeout(() => damageEnemy(i, DAMAGE_BUTTON_TICK, `${hero.name} AoE`), 250 + i * 80);
    });
  };

  const applyDoT = (target: 'hero' | 'enemy') => {
    if (target === 'hero') {
      setHero(p => ({ ...p, effects: { ...p.effects, dot: { dmgPerTick: DOT_TICK_DAMAGE, ticksLeft: DOT_DEFAULT_TICKS, tag: 'Burn' } } }));
      pushLog(`${hero.name} affected by Burn DoT (${DOT_TICK_DAMAGE}/tick × ${DOT_DEFAULT_TICKS})`);
    } else {
      setEnemies(p => p.map((e, i) =>
        i === selectedEnemyIdx ? { ...e, effects: { ...e.effects, dot: { dmgPerTick: DOT_TICK_DAMAGE, ticksLeft: DOT_DEFAULT_TICKS, tag: 'Bleed' } } } : e
      ));
      const e = enemies[selectedEnemyIdx];
      if (e) pushLog(`${e.name} affected by Bleed DoT`);
    }
  };

  const tickDoTOnce = () => {
    // Hero DoT
    if (hero.effects.dot && hero.effects.dot.ticksLeft > 0 && hero.alive) {
      const dot = hero.effects.dot;
      damageHero(dot.dmgPerTick, `${dot.tag} DoT`);
      setHero(p => ({ ...p, effects: { ...p.effects, dot: dot.ticksLeft - 1 > 0 ? { ...dot, ticksLeft: dot.ticksLeft - 1 } : null } }));
    }
    // Enemy DoT
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

  const tickDoT5x = () => {
    for (let k = 0; k < 5; k++) {
      setTimeout(() => tickDoTOnce(), k * 600);
    }
  };

  const applyTauntToHero = () => {
    setHero(p => ({ ...p, effects: { ...p.effects, taunt: true } }));
    pushLog(`${hero.name} gained Taunt → enemy attacks redirected`);
  };

  const clearTaunt = () => {
    setHero(p => ({ ...p, effects: { ...p.effects, taunt: false } }));
    pushLog(`${hero.name} Taunt cleared`);
  };

  const applyBuff = (target: 'hero' | 'enemy', tag: string) => {
    if (target === 'hero') {
      setHero(p => ({ ...p, effects: { ...p.effects, buffs: [...p.effects.buffs, tag] } }));
      pushLog(`${hero.name} +Buff: ${tag}`);
    } else {
      setEnemies(p => p.map((e, i) =>
        i === selectedEnemyIdx ? { ...e, effects: { ...e.effects, buffs: [...e.effects.buffs, tag] } } : e
      ));
    }
  };

  const applyDebuff = (target: 'hero' | 'enemy', tag: string) => {
    if (target === 'hero') {
      setHero(p => ({ ...p, effects: { ...p.effects, debuffs: [...p.effects.debuffs, tag] } }));
      pushLog(`${hero.name} +Debuff: ${tag}`);
    } else {
      setEnemies(p => p.map((e, i) =>
        i === selectedEnemyIdx ? { ...e, effects: { ...e.effects, debuffs: [...e.effects.debuffs, tag] } } : e
      ));
    }
  };

  const clearAllEffects = () => {
    setHero(p => ({ ...p, effects: newEffects() }));
    setEnemies(p => p.map(e => ({ ...e, effects: newEffects() })));
    pushLog('All effects cleared');
  };

  const resetAll = () => {
    swapHero(heroOptIdx);
    rebuildEnemies(enemyCount, enemyProfile);
    pushLog('=== RESET ALL ===');
  };

  // Auto-scroll log
  useEffect(() => {
    setTimeout(() => logRef.current?.scrollToEnd({ animated: false }), 50);
  }, [log]);

  // ─────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────
  return (
    <SafeAreaView style={s.root} edges={['top', 'bottom']}>
      <LinearGradient colors={['#0a0a1a', '#0a0a25']} style={StyleSheet.absoluteFillObject} />

      {/* Header */}
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Text style={s.backTxt}>‹ Indietro</Text>
        </TouchableOpacity>
        <Text style={s.title}>DEV ONLY — Combat QA Lab</Text>
        <View style={s.devBadge}><Text style={s.devBadgeTxt}>DEV</Text></View>
      </View>

      <View style={s.body}>
        {/* ── COL SX: HERO + ANIM BUTTONS + HP CONTROLS ── */}
        <ScrollView style={s.colLeft} contentContainerStyle={{ padding: 8, gap: 6 }}>
          <Text style={s.section}>HERO SELECT</Text>
          <View style={s.row}>
            {LAB_HERO_OPTIONS.map((o, i) => (
              <TouchableOpacity key={o.id}
                onPress={() => swapHero(i)}
                style={[s.pill, heroOptIdx === i && s.pillActive]}>
                <Text style={[s.pillTxt, heroOptIdx === i && s.pillTxtActive]}>{o.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
          {heroWarnings.length > 0 && (
            <View style={s.warnBox}>
              <Text style={s.warnTitle}>⚠ Contract warnings ({heroWarnings.length})</Text>
              {heroWarnings.slice(0, 4).map((w, i) => <Text key={i} style={s.warnItem}>• {w}</Text>)}
            </View>
          )}

          <Text style={s.section}>ANIMATION</Text>
          <View style={s.btnGrid}>
            {(['idle', 'attack', 'skill', 'hit', 'dead', 'heal'] as SpriteState[]).map(st => (
              <TouchableOpacity key={st} style={s.btn} onPress={() => playHeroState(st)}>
                <Text style={s.btnTxt}>{st === 'dead' ? 'death' : st}</Text>
              </TouchableOpacity>
            ))}
            <TouchableOpacity style={[s.btn, s.btnGreen]} onPress={() => { playHeroState('idle'); pushLog('Reset → idle'); }}>
              <Text style={s.btnTxt}>reset</Text>
            </TouchableOpacity>
          </View>

          <Text style={s.section}>HERO HP / DEATH</Text>
          <View style={s.btnGrid}>
            <TouchableOpacity style={s.btn} onPress={setHeroHpFull}><Text style={s.btnTxt}>HP Full</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={setHeroHp1}><Text style={s.btnTxt}>HP=1</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => damageHero(DAMAGE_BUTTON_TICK, 'manual')}>
              <Text style={s.btnTxt}>Damage {DAMAGE_BUTTON_TICK}</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnRed]} onPress={() => damageHero(DAMAGE_LETHAL, 'manual lethal')}>
              <Text style={s.btnTxt}>Lethal Dmg</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnRed]} onPress={killHero}><Text style={s.btnTxt}>Kill Hero</Text></TouchableOpacity>
            <TouchableOpacity
              style={[s.btn, hero.immortal && s.btnAccent]}
              onPress={toggleHeroImmortal}>
              <Text style={s.btnTxt}>Immortal: {hero.immortal ? 'ON' : 'OFF'}</Text>
            </TouchableOpacity>
          </View>

          <Text style={s.section}>SKILL / EFFECT (mock)</Text>
          <View style={s.btnGrid}>
            <TouchableOpacity style={s.btn} onPress={testSingleDamage}><Text style={s.btnTxt}>ST Damage</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={testAoEDamage}><Text style={s.btnTxt}>AoE Damage</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => applyDoT('enemy')}><Text style={s.btnTxt}>Apply DoT to Enemy</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => applyDoT('hero')}><Text style={s.btnTxt}>Apply DoT to Hero</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={tickDoTOnce}><Text style={s.btnTxt}>Tick DoT 1×</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={tickDoT5x}><Text style={s.btnTxt}>Tick DoT 5×</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => healUnit('hero', 0, HEAL_DEFAULT)}><Text style={s.btnTxt}>Heal Hero</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => healUnit('enemy', selectedEnemyIdx, HEAL_DEFAULT)}><Text style={s.btnTxt}>Heal Enemy</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => addShield('hero', 0, SHIELD_DEFAULT)}><Text style={s.btnTxt}>Shield Hero</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => addShield('enemy', selectedEnemyIdx, SHIELD_DEFAULT)}><Text style={s.btnTxt}>Shield Enemy</Text></TouchableOpacity>
            <TouchableOpacity style={[s.btn, hero.effects.taunt && s.btnAccent]} onPress={hero.effects.taunt ? clearTaunt : applyTauntToHero}>
              <Text style={s.btnTxt}>Taunt: {hero.effects.taunt ? 'ON' : 'OFF'}</Text>
            </TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => applyBuff('hero', 'ATK+')}><Text style={s.btnTxt}>Buff Hero</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => applyDebuff('enemy', 'DEF-')}><Text style={s.btnTxt}>Debuff Enemy</Text></TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnGreen]} onPress={clearAllEffects}><Text style={s.btnTxt}>Clear Effects</Text></TouchableOpacity>
          </View>

          <TouchableOpacity style={[s.btn, s.btnGreen, { marginTop: 8 }]} onPress={resetAll}>
            <Text style={s.btnTxt}>RESET ALL</Text>
          </TouchableOpacity>
        </ScrollView>

        {/* ── COL CENTER: BATTLEFIELD ── */}
        <View style={s.colCenter}>
          <View style={s.battlefield}>
            {/* Hero side */}
            <View style={s.heroSlot}>
              <Text style={s.unitLabel}>{hero.name} {hero.immortal ? '(IMM)' : ''} {hero.alive ? '' : '☠'}</Text>
              <View style={{ width: 110, height: 138, alignItems: 'center', justifyContent: 'flex-end' }}>
                <BattleSprite
                  character={{
                    id: hero.id,
                    hero_id: hero.heroId,
                    name: hero.name,
                    hero_name: hero.name,
                    element: hero.element,
                    hero_element: hero.element,
                    faction: hero.faction,
                    rarity: 5,
                    hero_rarity: 5,
                  }}
                  state={hero.state}
                  isEnemy={false}
                  hpPercent={hero.maxHp > 0 ? hero.hp / hero.maxHp : 0}
                  size={110}
                  actionInstanceId={hero.actionInstanceId}
                />
              </View>
              <HpBar hp={hero.hp} max={hero.maxHp} color="#44dd66" />
              <EffectsLine eff={hero.effects} />
            </View>

            {/* Enemy side */}
            <View style={s.enemySide}>
              {enemies.map((e, i) => (
                <Pressable key={e.id} style={[s.enemySlot, selectedEnemyIdx === i && s.enemySlotSel]}
                  onPress={() => setSelectedEnemyIdx(i)}>
                  <Text style={s.unitLabel}>
                    {selectedEnemyIdx === i ? '▶ ' : ''}{e.name} {e.immortal ? '(IMM)' : ''} {e.alive ? '' : '☠'}
                  </Text>
                  <View style={{ width: 90, height: 113, alignItems: 'center', justifyContent: 'flex-end' }}>
                    <BattleSprite
                      character={{
                        id: e.id,
                        hero_id: e.heroId,
                        name: e.name,
                        hero_name: e.name,
                        element: e.element,
                        hero_element: e.element,
                        faction: e.faction,
                        rarity: 3,
                      }}
                      state={e.state}
                      isEnemy={true}
                      hpPercent={e.maxHp > 0 ? e.hp / e.maxHp : 0}
                      size={90}
                      actionInstanceId={e.actionInstanceId}
                    />
                  </View>
                  <HpBar hp={e.hp} max={e.maxHp} color="#dd4444" />
                  <EffectsLine eff={e.effects} />
                </Pressable>
              ))}
            </View>
          </View>
        </View>

        {/* ── COL DX: ENEMY CONTROLS + LOG ── */}
        <ScrollView style={s.colRight} contentContainerStyle={{ padding: 8, gap: 6 }}>
          <Text style={s.section}>ENEMY CONFIG</Text>
          <View style={s.row}>
            {([1, 2, 3] as const).map(n => (
              <TouchableOpacity key={n}
                onPress={() => setEnemyCount(n)}
                style={[s.pill, enemyCount === n && s.pillActive]}>
                <Text style={s.pillTxt}>{n}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={s.row}>
            {(['immortal', 'normal', 'lethal'] as EnemyProfile[]).map(p => (
              <TouchableOpacity key={p}
                onPress={() => setEnemyProfile(p)}
                style={[s.pill, enemyProfile === p && s.pillActive]}>
                <Text style={[s.pillTxt, enemyProfile === p && s.pillTxtActive]}>{p}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={s.section}>ENEMY DAMAGE MODE</Text>
          <View style={s.row}>
            {(['off', 'normal', 'lethal'] as DamageMode[]).map(m => (
              <TouchableOpacity key={m}
                onPress={() => setDamageMode(m)}
                style={[s.pill, damageMode === m && s.pillActive]}>
                <Text style={[s.pillTxt, damageMode === m && s.pillTxtActive]}>{m}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={s.section}>ENEMY ATTACK</Text>
          <View style={s.btnGrid}>
            <TouchableOpacity style={s.btn} onPress={() => enemyAttack(selectedEnemyIdx)}>
              <Text style={s.btnTxt}>Selected Attacca Hero</Text>
            </TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => enemies.forEach((_, i) => enemyAttack(i))}>
              <Text style={s.btnTxt}>All Enemies Attack</Text>
            </TouchableOpacity>
          </View>

          <Text style={s.section}>SELECTED ENEMY (#{selectedEnemyIdx})</Text>
          <View style={s.btnGrid}>
            <TouchableOpacity style={s.btn} onPress={() => playEnemyState(selectedEnemyIdx, 'idle')}><Text style={s.btnTxt}>idle</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => playEnemyState(selectedEnemyIdx, 'attack')}><Text style={s.btnTxt}>attack</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => playEnemyState(selectedEnemyIdx, 'hit')}><Text style={s.btnTxt}>hit</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => playEnemyState(selectedEnemyIdx, 'dead')}><Text style={s.btnTxt}>death</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => setEnemyHpFull(selectedEnemyIdx)}><Text style={s.btnTxt}>HP Full</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => setEnemyHp1(selectedEnemyIdx)}><Text style={s.btnTxt}>HP=1</Text></TouchableOpacity>
            <TouchableOpacity style={s.btn} onPress={() => damageEnemy(selectedEnemyIdx, DAMAGE_BUTTON_TICK, 'manual')}>
              <Text style={s.btnTxt}>Damage</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnRed]} onPress={() => damageEnemy(selectedEnemyIdx, DAMAGE_LETHAL, 'manual lethal')}>
              <Text style={s.btnTxt}>Lethal</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[s.btn, s.btnRed]} onPress={() => killEnemy(selectedEnemyIdx)}><Text style={s.btnTxt}>Kill</Text></TouchableOpacity>
            <TouchableOpacity
              style={[s.btn, enemies[selectedEnemyIdx]?.immortal && s.btnAccent]}
              onPress={() => toggleEnemyImmortal(selectedEnemyIdx)}>
              <Text style={s.btnTxt}>Immortal: {enemies[selectedEnemyIdx]?.immortal ? 'ON' : 'OFF'}</Text>
            </TouchableOpacity>
          </View>

          <Text style={s.section}>EVENT LOG</Text>
          <View style={s.logBox}>
            <ScrollView ref={logRef} style={s.logScroll} contentContainerStyle={{ padding: 6 }}>
              {log.map((l, i) => <Text key={i} style={s.logTxt}>{l}</Text>)}
            </ScrollView>
            <TouchableOpacity onPress={() => setLog([])} style={[s.btn, { marginTop: 4 }]}>
              <Text style={s.btnTxt}>Clear Log</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────────

function HpBar({ hp, max, color }: { hp: number; max: number; color: string }) {
  const pct = max > 0 ? Math.max(0, Math.min(1, hp / max)) : 0;
  return (
    <View style={s.hpBarRoot}>
      <View style={[s.hpBarFill, { width: `${pct * 100}%`, backgroundColor: color }]} />
      <Text style={s.hpBarTxt}>{Math.round(hp).toLocaleString()} / {max.toLocaleString()}</Text>
    </View>
  );
}

function EffectsLine({ eff }: { eff: EffectStatus }) {
  const tags: string[] = [];
  if (eff.shield > 0) tags.push(`🛡 ${eff.shield}`);
  if (eff.taunt) tags.push('TAUNT');
  if (eff.dot) tags.push(`🔥${eff.dot.tag} ${eff.dot.ticksLeft}t`);
  if (eff.hot) tags.push(`💚${eff.hot.tag} ${eff.hot.ticksLeft}t`);
  for (const b of eff.buffs) tags.push(`+${b}`);
  for (const d of eff.debuffs) tags.push(`-${d}`);
  if (tags.length === 0) return <Text style={s.eff}>—</Text>;
  return <Text style={s.eff}>{tags.join(' · ')}</Text>;
}

// ─────────────────────────────────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────────────────────────────────

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#070713' },
  header: {
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: 8, paddingVertical: 6,
    backgroundColor: 'rgba(255,68,68,0.1)', borderBottomWidth: 1, borderBottomColor: '#ff4444',
  },
  backBtn: { paddingHorizontal: 10, paddingVertical: 4 },
  backTxt: { color: '#fff', fontSize: 14, fontWeight: '700' },
  title: { flex: 1, color: '#fff', fontSize: 14, fontWeight: '900', textAlign: 'center' },
  devBadge: { paddingHorizontal: 8, paddingVertical: 3, backgroundColor: '#ff4444', borderRadius: 4 },
  devBadgeTxt: { color: '#fff', fontWeight: '900', fontSize: 10 },

  body: { flex: 1, flexDirection: 'row' },
  colLeft: { width: 240, borderRightWidth: 1, borderRightColor: '#222' },
  colCenter: { flex: 1, alignItems: 'center', justifyContent: 'flex-start', paddingTop: 12 },
  colRight: { width: 280, borderLeftWidth: 1, borderLeftColor: '#222' },

  section: { color: '#ffaa55', fontSize: 11, fontWeight: '900', letterSpacing: 1, marginTop: 4 },
  row: { flexDirection: 'row', flexWrap: 'wrap', gap: 4 },
  btnGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 4 },

  pill: {
    paddingHorizontal: 10, paddingVertical: 5, borderRadius: 4,
    backgroundColor: 'rgba(255,255,255,0.06)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
  },
  pillActive: { backgroundColor: 'rgba(255,170,85,0.2)', borderColor: '#ffaa55' },
  pillTxt: { color: '#ddd', fontSize: 11, fontWeight: '700' },
  pillTxtActive: { color: '#ffaa55' },

  btn: {
    paddingHorizontal: 8, paddingVertical: 6, borderRadius: 4,
    backgroundColor: 'rgba(68,153,221,0.18)', borderWidth: 1, borderColor: 'rgba(68,153,221,0.4)',
    minWidth: 70, alignItems: 'center',
  },
  btnRed: { backgroundColor: 'rgba(221,68,68,0.2)', borderColor: '#dd4444' },
  btnGreen: { backgroundColor: 'rgba(68,221,102,0.2)', borderColor: '#44dd66' },
  btnAccent: { backgroundColor: 'rgba(255,170,85,0.3)', borderColor: '#ffaa55' },
  btnTxt: { color: '#fff', fontSize: 11, fontWeight: '700' },

  warnBox: {
    padding: 6, backgroundColor: 'rgba(221,170,68,0.1)', borderWidth: 1, borderColor: '#ddaa44', borderRadius: 4,
  },
  warnTitle: { color: '#ddaa44', fontSize: 11, fontWeight: '900' },
  warnItem: { color: '#ffeebb', fontSize: 9, marginTop: 2 },

  battlefield: {
    width: '100%', height: '92%',
    flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingBottom: 24,
    backgroundColor: 'rgba(20,20,40,0.4)', borderRadius: 8,
  },
  heroSlot: { alignItems: 'center', minWidth: 130 },
  enemySide: { flexDirection: 'row', alignItems: 'flex-end', gap: 12 },
  enemySlot: { alignItems: 'center', padding: 4, borderRadius: 6, borderWidth: 2, borderColor: 'transparent' },
  enemySlotSel: { borderColor: '#ffaa55', backgroundColor: 'rgba(255,170,85,0.05)' },
  unitLabel: { color: '#fff', fontSize: 10, fontWeight: '700', marginBottom: 4 },

  hpBarRoot: {
    width: 110, height: 14, backgroundColor: 'rgba(0,0,0,0.6)', borderRadius: 7,
    overflow: 'hidden', marginTop: 4, justifyContent: 'center', alignItems: 'center',
  },
  hpBarFill: { position: 'absolute', left: 0, top: 0, bottom: 0 },
  hpBarTxt: { color: '#fff', fontSize: 8, fontWeight: '900', textShadowColor: '#000', textShadowRadius: 2 },
  eff: { color: '#bbb', fontSize: 9, marginTop: 2, maxWidth: 130, textAlign: 'center' },

  logBox: { backgroundColor: 'rgba(0,0,0,0.4)', borderRadius: 4, padding: 4, marginTop: 4 },
  logScroll: { maxHeight: 200 },
  logTxt: { color: '#aacc99', fontSize: 9, fontFamily: 'monospace' as any },
});

// ─────────────────────────────────────────────────────────────────────────
// FUTURE HERO IMPORT NOTE
// ─────────────────────────────────────────────────────────────────────────
// Ogni nuovo eroe importato DEVE essere validato in questo Combat QA Lab
// prima di considerarsi "done":
//   1. Aggiungerlo a LAB_HERO_OPTIONS (id, name, element, faction, rarity).
//   2. Verificare nel lab: idle, attack, skill, hit, death.
//   3. Verificare scale vs Hoplite/Berserker (selezionare entrambi e
//      confrontare l'altezza nel battlefield).
//   4. Eseguire enemy attack mode=normal e mode=lethal sul nuovo eroe.
//   5. Test taunt/DoT/heal/shield se la kit lo prevede.
//   6. Confermare che validateHeroContract(id) ritorni 0 warning visibili
//      in alto a sinistra nel pannello "Contract warnings".
// Cfr. /app/docs/NEW_HERO_IMPORT_CHECKLIST.md.
