// MEGA_RELEASE_ACCELERATION_35 v86 — Playable Mode Visual Battle Preview (preview-only, deeplink-only)
//
// Guardrail (assertito per design e per validator):
//   - preview-only, deterministic, NON authoritative
//   - nessun fetch backend, nessun DB write, nessun endpoint live
//   - nessun import da story.tsx o combat.tsx
//   - nessun import del modulo di combattimento autoritativo
//   - nessun reward live, nessun account/inventory/MMR/tower-completion mutation
//   - nessun bottone di claim reale
//   - nessuna progressione di Story, nessuna assegnazione frammenti raid boss
//   - label UI obbligatorie: PREVIEW, LOCAL, NOT LIVE REWARD, NON AUTHORITATIVE
//   - schermata deeplink-only (NON esposta a produzione)
//
// UI in italiano. TypeScript-only.

import React, { useMemo, useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";

type Mode = "training" | "story" | "boss" | "tower" | "event" | "arena";

type TimelineStep = {
  turn: number;
  actor: string;
  action: string;
  target?: string;
  preview_dmg?: number;
  preview_heal?: number;
};

type Unit = {
  slot?: number;
  alias: string;
  role?: string;
  hp: number;
  atk?: number;
  def?: number;
  speed?: number;
};

type BattlePayload = {
  mode: Mode;
  preview_only: true;
  deterministic: true;
  authoritative: false;
  reward_grant: false;
  db_write: false;
  account_mutation: false;
  inventory_mutation: false;
  battle_engine_attached: false;
  seed: string;
  player_team: Unit[];
  enemy_team?: Unit[];
  boss?: Unit & { phases?: string[] };
  timeline: TimelineStep[];
  preview_outcome: {
    player_wins: boolean;
    authoritative: false;
    applies_to_account: false;
  };
  ui_labels_required: string[];
};

// Local deterministic payloads (embedded mirror of /app/data/design/playable_mode_visual_battle_routing/*).
// NON fetch, NON DB. Solo costanti locali.
const PAYLOADS: Record<Mode, BattlePayload> = {
  training: {
    mode: "training",
    preview_only: true,
    deterministic: true,
    authoritative: false,
    reward_grant: false,
    db_write: false,
    account_mutation: false,
    inventory_mutation: false,
    battle_engine_attached: false,
    seed: "training-preview-seed-0001",
    player_team: [
      { slot: 1, alias: "alpha_trainee_hero_01", role: "dps_melee", hp: 1200, atk: 180, def: 90, speed: 95 },
      { slot: 2, alias: "alpha_trainee_hero_02", role: "healer", hp: 1000, atk: 120, def: 80, speed: 85 },
      { slot: 3, alias: "alpha_trainee_hero_03", role: "tank", hp: 1800, atk: 110, def: 160, speed: 60 },
    ],
    enemy_team: [
      { slot: 1, alias: "training_dummy_a", hp: 900, atk: 100, def: 70 },
      { slot: 2, alias: "training_dummy_b", hp: 900, atk: 100, def: 70 },
    ],
    timeline: [
      { turn: 1, actor: "alpha_trainee_hero_03", action: "taunt", target: "all_enemies", preview_dmg: 0 },
      { turn: 1, actor: "alpha_trainee_hero_01", action: "basic_atk", target: "training_dummy_a", preview_dmg: 220 },
      { turn: 2, actor: "training_dummy_a", action: "basic_atk", target: "alpha_trainee_hero_03", preview_dmg: 140 },
      { turn: 2, actor: "alpha_trainee_hero_02", action: "heal", target: "alpha_trainee_hero_03", preview_heal: 220 },
      { turn: 3, actor: "alpha_trainee_hero_01", action: "ultimate", target: "training_dummy_a", preview_dmg: 680 },
    ],
    preview_outcome: { player_wins: true, authoritative: false, applies_to_account: false },
    ui_labels_required: ["PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"],
  },
  story: {
    mode: "story",
    preview_only: true,
    deterministic: true,
    authoritative: false,
    reward_grant: false,
    db_write: false,
    account_mutation: false,
    inventory_mutation: false,
    battle_engine_attached: false,
    seed: "story-preview-seed-0001",
    player_team: [
      { slot: 1, alias: "alpha_story_hero_01", role: "dps_ranged", hp: 1100, atk: 200, def: 80, speed: 110 },
      { slot: 2, alias: "alpha_story_hero_02", role: "support", hp: 1050, atk: 130, def: 85, speed: 100 },
      { slot: 3, alias: "alpha_story_hero_03", role: "tank", hp: 1700, atk: 115, def: 150, speed: 65 },
    ],
    enemy_team: [
      { slot: 1, alias: "story_grunt_a", hp: 850, atk: 110, def: 60 },
      { slot: 2, alias: "story_grunt_b", hp: 850, atk: 110, def: 60 },
      { slot: 3, alias: "story_lieutenant", hp: 1500, atk: 160, def: 90 },
    ],
    timeline: [
      { turn: 1, actor: "alpha_story_hero_03", action: "shield_wall", target: "self_team", preview_dmg: 0 },
      { turn: 1, actor: "alpha_story_hero_01", action: "piercing_arrow", target: "story_lieutenant", preview_dmg: 320 },
      { turn: 2, actor: "story_grunt_a", action: "basic_atk", target: "alpha_story_hero_03", preview_dmg: 130 },
      { turn: 2, actor: "alpha_story_hero_02", action: "buff_atk", target: "alpha_story_hero_01", preview_dmg: 0 },
      { turn: 3, actor: "alpha_story_hero_01", action: "ultimate", target: "all_enemies", preview_dmg: 540 },
    ],
    preview_outcome: { player_wins: true, authoritative: false, applies_to_account: false },
    ui_labels_required: ["PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"],
  },
  boss: {
    mode: "boss",
    preview_only: true,
    deterministic: true,
    authoritative: false,
    reward_grant: false,
    db_write: false,
    account_mutation: false,
    inventory_mutation: false,
    battle_engine_attached: false,
    seed: "boss-preview-seed-0001",
    player_team: [
      { slot: 1, alias: "alpha_boss_hero_01", role: "dps_melee", hp: 1400, atk: 220, def: 100, speed: 105 },
      { slot: 2, alias: "alpha_boss_hero_02", role: "dps_ranged", hp: 1200, atk: 240, def: 80, speed: 115 },
      { slot: 3, alias: "alpha_boss_hero_03", role: "healer", hp: 1100, atk: 130, def: 90, speed: 95 },
      { slot: 4, alias: "alpha_boss_hero_04", role: "tank", hp: 2200, atk: 130, def: 180, speed: 55 },
    ],
    boss: { alias: "alpha_raid_boss_placeholder_01", hp: 12000, atk: 380, def: 220, phases: ["intro", "enrage", "final"] },
    timeline: [
      { turn: 1, actor: "alpha_boss_hero_04", action: "taunt", target: "alpha_raid_boss_placeholder_01", preview_dmg: 0 },
      { turn: 1, actor: "alpha_boss_hero_01", action: "basic_atk", target: "alpha_raid_boss_placeholder_01", preview_dmg: 360 },
      { turn: 1, actor: "alpha_boss_hero_02", action: "piercing_shot", target: "alpha_raid_boss_placeholder_01", preview_dmg: 420 },
      { turn: 2, actor: "alpha_raid_boss_placeholder_01", action: "sweep", target: "all_player", preview_dmg: 280 },
      { turn: 2, actor: "alpha_boss_hero_03", action: "aoe_heal", target: "all_player", preview_heal: 280 },
      { turn: 3, actor: "alpha_boss_hero_01", action: "ultimate", target: "alpha_raid_boss_placeholder_01", preview_dmg: 900 },
    ],
    preview_outcome: { player_wins: false, authoritative: false, applies_to_account: false },
    ui_labels_required: ["PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"],
  },
  tower: {
    mode: "tower",
    preview_only: true,
    deterministic: true,
    authoritative: false,
    reward_grant: false,
    db_write: false,
    account_mutation: false,
    inventory_mutation: false,
    battle_engine_attached: false,
    seed: "tower-preview-seed-0001",
    player_team: [
      { slot: 1, alias: "alpha_tower_hero_01", role: "dps_melee", hp: 1300, atk: 210, def: 95, speed: 100 },
      { slot: 2, alias: "alpha_tower_hero_02", role: "support", hp: 1050, atk: 140, def: 85, speed: 95 },
      { slot: 3, alias: "alpha_tower_hero_03", role: "tank", hp: 1900, atk: 120, def: 170, speed: 60 },
    ],
    enemy_team: [
      { slot: 1, alias: "tower_minion_a", hp: 950, atk: 115, def: 75 },
      { slot: 2, alias: "tower_minion_b", hp: 950, atk: 115, def: 75 },
      { slot: 3, alias: "tower_minion_c", hp: 950, atk: 115, def: 75 },
    ],
    timeline: [
      { turn: 1, actor: "alpha_tower_hero_03", action: "shield_wall", target: "self_team", preview_dmg: 0 },
      { turn: 1, actor: "alpha_tower_hero_01", action: "cleave", target: "all_enemies", preview_dmg: 240 },
      { turn: 2, actor: "tower_minion_a", action: "basic_atk", target: "alpha_tower_hero_03", preview_dmg: 130 },
      { turn: 2, actor: "alpha_tower_hero_02", action: "buff_def", target: "alpha_tower_hero_03", preview_dmg: 0 },
      { turn: 3, actor: "alpha_tower_hero_01", action: "ultimate", target: "all_enemies", preview_dmg: 560 },
    ],
    preview_outcome: { player_wins: true, authoritative: false, applies_to_account: false },
    ui_labels_required: ["PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"],
  },
  event: {
    mode: "event",
    preview_only: true,
    deterministic: true,
    authoritative: false,
    reward_grant: false,
    db_write: false,
    account_mutation: false,
    inventory_mutation: false,
    battle_engine_attached: false,
    seed: "event-preview-seed-0001",
    player_team: [
      { slot: 1, alias: "alpha_event_hero_01", role: "dps_ranged", hp: 1150, atk: 230, def: 85, speed: 120 },
      { slot: 2, alias: "alpha_event_hero_02", role: "healer", hp: 1000, atk: 125, def: 80, speed: 105 },
      { slot: 3, alias: "alpha_event_hero_03", role: "tank", hp: 1800, atk: 130, def: 165, speed: 60 },
    ],
    enemy_team: [
      { slot: 1, alias: "event_mob_a", hp: 900, atk: 110, def: 70 },
      { slot: 2, alias: "event_elite_b", hp: 1400, atk: 150, def: 95 },
    ],
    timeline: [
      { turn: 1, actor: "alpha_event_hero_03", action: "taunt", target: "all_enemies", preview_dmg: 0 },
      { turn: 1, actor: "alpha_event_hero_01", action: "basic_atk", target: "event_elite_b", preview_dmg: 300 },
      { turn: 2, actor: "event_elite_b", action: "basic_atk", target: "alpha_event_hero_03", preview_dmg: 160 },
      { turn: 2, actor: "alpha_event_hero_02", action: "heal", target: "alpha_event_hero_03", preview_heal: 240 },
      { turn: 3, actor: "alpha_event_hero_01", action: "ultimate", target: "event_elite_b", preview_dmg: 720 },
    ],
    preview_outcome: { player_wins: true, authoritative: false, applies_to_account: false },
    ui_labels_required: ["PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"],
  },
  arena: {
    mode: "arena",
    preview_only: true,
    deterministic: true,
    authoritative: false,
    reward_grant: false,
    db_write: false,
    account_mutation: false,
    inventory_mutation: false,
    battle_engine_attached: false,
    seed: "arena-preview-seed-0001",
    player_team: [
      { slot: 1, alias: "alpha_arena_hero_01", role: "dps_melee", hp: 1250, atk: 215, def: 95, speed: 110 },
      { slot: 2, alias: "alpha_arena_hero_02", role: "dps_ranged", hp: 1150, atk: 235, def: 80, speed: 115 },
      { slot: 3, alias: "alpha_arena_hero_03", role: "support", hp: 1050, atk: 130, def: 85, speed: 100 },
    ],
    enemy_team: [
      { slot: 1, alias: "arena_dummy_pvp_a", hp: 1100, atk: 200, def: 90, speed: 105 },
      { slot: 2, alias: "arena_dummy_pvp_b", hp: 1100, atk: 200, def: 90, speed: 105 },
      { slot: 3, alias: "arena_dummy_pvp_c", hp: 1100, atk: 200, def: 90, speed: 105 },
    ],
    timeline: [
      { turn: 1, actor: "alpha_arena_hero_03", action: "buff_atk", target: "alpha_arena_hero_02", preview_dmg: 0 },
      { turn: 1, actor: "alpha_arena_hero_02", action: "piercing_shot", target: "arena_dummy_pvp_a", preview_dmg: 320 },
      { turn: 2, actor: "arena_dummy_pvp_a", action: "basic_atk", target: "alpha_arena_hero_01", preview_dmg: 150 },
      { turn: 2, actor: "alpha_arena_hero_01", action: "cleave", target: "all_enemies", preview_dmg: 220 },
      { turn: 3, actor: "alpha_arena_hero_02", action: "ultimate", target: "all_enemies", preview_dmg: 540 },
    ],
    preview_outcome: { player_wins: true, authoritative: false, applies_to_account: false },
    ui_labels_required: ["PREVIEW", "LOCAL", "NOT LIVE REWARD", "NON AUTHORITATIVE"],
  },
};

const MODE_LABELS: Record<Mode, string> = {
  training: "Training",
  story: "Story",
  boss: "Boss",
  tower: "Tower",
  event: "Event",
  arena: "Arena",
};

function isValidMode(s: string | undefined): s is Mode {
  return s === "training" || s === "story" || s === "boss" || s === "tower" || s === "event" || s === "arena";
}

export default function PlayableModeBattlePreview() {
  const params = useLocalSearchParams<{ mode?: string }>();
  const router = useRouter();
  const initial: Mode = isValidMode(params?.mode) ? (params.mode as Mode) : "training";
  const [activeMode, setActiveMode] = useState<Mode>(initial);
  const [step, setStep] = useState<number>(0);

  // === v88 Battle Preview Experience state ============================================
  // autoplay / pause / speed: solo timer locale, NESSUNA chiamata HTTP, NESSUNA mutazione persistente.
  const [autoplay, setAutoplay] = useState<boolean>(false);
  const [speed, setSpeed] = useState<1 | 2>(1);
  // floating mock damage/heal toasts (solo visualizzazione locale).
  type Toast = { id: number; text: string; kind: "dmg" | "heal"; target: string };
  const [toasts, setToasts] = useState<Toast[]>([]);

  const payload = useMemo<BattlePayload>(() => PAYLOADS[activeMode], [activeMode]);
  const totalSteps = payload.timeline.length;
  const currentStep = payload.timeline[Math.min(step, totalSteps - 1)];
  const atEnd = step >= totalSteps - 1;

  // Sync params -> activeMode when user opens via deeplink ?mode=...
  React.useEffect(() => {
    if (isValidMode(params?.mode) && params?.mode !== activeMode) {
      setActiveMode(params.mode as Mode);
      setStep(0);
      setAutoplay(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params?.mode]);

  // Autoplay: NON è un loop di rete, è un setTimeout locale. Si ferma all'end.
  React.useEffect(() => {
    if (!autoplay) return;
    if (atEnd) {
      setAutoplay(false);
      return;
    }
    const ms = 1200 / speed;
    const t = setTimeout(() => setStep((s) => Math.min(s + 1, totalSteps - 1)), ms);
    return () => clearTimeout(t);
  }, [autoplay, step, speed, atEnd, totalSteps]);

  // Floating mock damage/heal toast su cambio step (preview-only).
  React.useEffect(() => {
    const ev = payload.timeline[Math.min(step, totalSteps - 1)];
    const dmg = ev.preview_dmg ?? 0;
    const heal = ev.preview_heal ?? 0;
    if (!ev.target) return;
    const newToasts: Toast[] = [];
    const targets =
      ev.target === "all_enemies" || ev.target === "all_player"
        ? [ev.target]
        : [ev.target];
    if (dmg > 0) {
      newToasts.push({ id: Date.now() + Math.random(), text: `-${dmg}`, kind: "dmg", target: targets[0] });
    }
    if (heal > 0) {
      newToasts.push({ id: Date.now() + Math.random(), text: `+${heal}`, kind: "heal", target: targets[0] });
    }
    if (newToasts.length === 0) return;
    setToasts((prev) => [...prev.slice(-4), ...newToasts]);
    const ttl = 900 / speed;
    const t = setTimeout(() => {
      setToasts((prev) => prev.filter((x) => !newToasts.some((n) => n.id === x.id)));
    }, ttl);
    return () => clearTimeout(t);
  }, [step, payload, speed, totalSteps]);
  // === END v88 state ==================================================================

  const switchMode = (m: Mode) => {
    setActiveMode(m);
    setStep(0);
    setAutoplay(false);
    setToasts([]);
  };

  // === v88 Enemy AI hints (derivati LOCALMENTE dal payload, no engine) =================
  const enemyAliasSet = useMemo<Set<string>>(
    () =>
      new Set([
        ...(payload.enemy_team ?? []).map((u) => u.alias),
        ...(payload.boss ? [payload.boss.alias] : []),
      ]),
    [payload]
  );
  const aiHintFor = (alias: string): string | null => {
    if (!enemyAliasSet.has(alias)) return null;
    const future = payload.timeline.slice(step + 1).find((ev) => ev.actor === alias);
    if (!future) return "in attesa";
    const dmg = future.preview_dmg ?? 0;
    const heal = future.preview_heal ?? 0;
    if (heal > 0) return "intent: cura (preview)";
    if (future.target === "all_player" && dmg > 0) return `intent: AoE ~${dmg}`;
    if (future.target === "all_enemies") return "intent: AoE alleati";
    if (dmg > 0) return `intent: ST ~${dmg}`;
    if (future.action.includes("taunt")) return "intent: taunt";
    if (future.action.includes("buff")) return "intent: buff";
    return `intent: ${future.action}`;
  };
  // === END enemy AI hints =============================================================

  const next = () => setStep((s) => Math.min(s + 1, totalSteps - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));
  const reset = () => {
    setStep(0);
    setAutoplay(false);
    setToasts([]);
  };

  // === v87 Visual Layer (preview-only, deterministic, local) ============================
  // Calcola HP locale di ciascuna unità accumulando preview_dmg / preview_heal lungo la
  // timeline fino allo step corrente. NON modifica alcun dato esterno e NON applica
  // alcun effetto reale: è solo una proiezione visiva del payload.
  const previewHpByAlias = useMemo<Record<string, { current: number; max: number }>>(() => {
    const map: Record<string, { current: number; max: number }> = {};
    payload.player_team.forEach((u) => {
      map[u.alias] = { current: u.hp, max: u.hp };
    });
    (payload.enemy_team ?? []).forEach((u) => {
      map[u.alias] = { current: u.hp, max: u.hp };
    });
    if (payload.boss) {
      map[payload.boss.alias] = { current: payload.boss.hp, max: payload.boss.hp };
    }
    // Applica gli step fino a quello corrente (incluso).
    const playerAliases = new Set(payload.player_team.map((u) => u.alias));
    const enemyAliases = new Set([
      ...(payload.enemy_team ?? []).map((u) => u.alias),
      ...(payload.boss ? [payload.boss.alias] : []),
    ]);
    for (let i = 0; i <= Math.min(step, totalSteps - 1); i++) {
      const ev = payload.timeline[i];
      const dmg = ev.preview_dmg ?? 0;
      const heal = ev.preview_heal ?? 0;
      if (dmg > 0 && ev.target) {
        const isPlayerActor = playerAliases.has(ev.actor);
        // target speciali: distribuisci ai gruppi
        if (ev.target === "all_enemies") {
          const enemies = isPlayerActor ? enemyAliases : playerAliases;
          enemies.forEach((a) => {
            if (map[a]) map[a].current = Math.max(0, map[a].current - dmg);
          });
        } else if (ev.target === "all_player") {
          playerAliases.forEach((a) => {
            if (map[a]) map[a].current = Math.max(0, map[a].current - dmg);
          });
        } else if (ev.target !== "self_team" && map[ev.target]) {
          map[ev.target].current = Math.max(0, map[ev.target].current - dmg);
        }
      }
      if (heal > 0 && ev.target) {
        if (ev.target === "all_player") {
          playerAliases.forEach((a) => {
            if (map[a]) map[a].current = Math.min(map[a].max, map[a].current + heal);
          });
        } else if (map[ev.target]) {
          map[ev.target].current = Math.min(map[ev.target].max, map[ev.target].current + heal);
        }
      }
    }
    return map;
  }, [payload, step, totalSteps]);

  const isActive = (alias: string): boolean =>
    currentStep.actor === alias || currentStep.target === alias;

  const isAllyTarget = (alias: string): boolean => {
    const t = currentStep.target;
    if (!t) return false;
    const playerAliases = new Set(payload.player_team.map((u) => u.alias));
    if (t === "all_player") return playerAliases.has(alias);
    if (t === "all_enemies") return !playerAliases.has(alias);
    return t === alias;
  };

  const renderHpBar = (alias: string) => {
    const hp = previewHpByAlias[alias];
    if (!hp) return null;
    const pct = hp.max > 0 ? Math.max(0, Math.min(1, hp.current / hp.max)) : 0;
    const color =
      pct > 0.66 ? "#22c55e" : pct > 0.33 ? "#eab308" : "#ef4444";
    return (
      <View style={styles.hpBarOuter}>
        <View style={[styles.hpBarFill, { width: `${Math.round(pct * 100)}%`, backgroundColor: color }]} />
        <Text style={styles.hpBarText}>
          {hp.current} / {hp.max}
        </Text>
      </View>
    );
  };

  // Portrait/silhouette placeholder: deriva una "lettera + accent color" dall'alias.
  // Nessun asset esterno, nessun import di immagini reali.
  const PORTRAIT_COLORS = ["#f97316", "#22d3ee", "#a78bfa", "#34d399", "#f43f5e", "#facc15", "#60a5fa", "#fb7185"];
  const portraitFor = (alias: string) => {
    const seed = Array.from(alias).reduce((acc, c) => acc + c.charCodeAt(0), 0);
    const color = PORTRAIT_COLORS[seed % PORTRAIT_COLORS.length];
    const letter = (alias.match(/[A-Za-z0-9]/)?.[0] ?? "?").toUpperCase();
    return { color, letter };
  };

  const renderUnitCard = (alias: string, opts?: { isBoss?: boolean; sub?: string }) => {
    const { color, letter } = portraitFor(alias);
    const active = isActive(alias);
    const targeted = isAllyTarget(alias) && currentStep.target !== alias.split(":")[0];
    const hint = aiHintFor(alias);
    const localToasts = toasts.filter((t) => t.target === alias);
    return (
      <View
        key={alias}
        style={[styles.unitCard, active ? styles.unitCardActive : null, opts?.isBoss ? styles.unitCardBoss : null]}
      >
        <View style={[styles.portraitBox, { backgroundColor: color }]}>
          <Text style={styles.portraitLetter}>{letter}</Text>
          {opts?.isBoss ? <Text style={styles.portraitBossTag}>BOSS</Text> : null}
          {localToasts.map((t) => (
            <Text
              key={t.id}
              style={[
                styles.floatingToast,
                t.kind === "dmg" ? styles.floatingToastDmg : styles.floatingToastHeal,
              ]}
            >
              {t.text}
            </Text>
          ))}
        </View>
        <View style={styles.unitInfo}>
          <Text style={styles.unitAlias} numberOfLines={1}>
            {alias}
          </Text>
          {opts?.sub ? <Text style={styles.unitSub}>{opts.sub}</Text> : null}
          {renderHpBar(alias)}
          {targeted ? <Text style={styles.targetedTag}>· bersaglio del turno</Text> : null}
          {hint ? <Text style={styles.aiHintTag}>{hint}</Text> : null}
        </View>
      </View>
    );
  };
  // === END v87 Visual Layer =============================================================

  return (
    <SafeAreaView style={styles.screen}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.h1}>Playable Mode · Visual Battle Preview</Text>
        <View style={styles.badgesRow}>
          {payload.ui_labels_required.map((b) => (
            <View key={b} style={styles.badge}>
              <Text style={styles.badgeText}>{b}</Text>
            </View>
          ))}
        </View>

        <Text style={styles.subtitle}>Modalità (preview locale deterministica)</Text>
        <View style={styles.modeRow}>
          {(Object.keys(MODE_LABELS) as Mode[]).map((m) => (
            <TouchableOpacity
              key={m}
              onPress={() => switchMode(m)}
              style={[styles.modeChip, activeMode === m ? styles.modeChipActive : null]}
            >
              <Text style={[styles.modeChipText, activeMode === m ? styles.modeChipTextActive : null]}>
                {MODE_LABELS[m]}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Seed deterministico</Text>
          <Text style={styles.cardMono}>{payload.seed}</Text>
        </View>

        <View style={styles.teamsCol}>
          <Text style={styles.teamHeader}>Player Team</Text>
          <View style={styles.unitsGrid}>
            {payload.player_team.map((u) =>
              renderUnitCard(u.alias, { sub: `${u.role ?? "unit"} · ATK ${u.atk ?? "-"} · DEF ${u.def ?? "-"}` })
            )}
          </View>
          <Text style={styles.teamHeader}>{payload.boss ? "Boss" : "Enemy Team"}</Text>
          <View style={styles.unitsGrid}>
            {payload.boss ? (
              renderUnitCard(payload.boss.alias, {
                isBoss: true,
                sub: `ATK ${payload.boss.atk ?? "-"} · DEF ${payload.boss.def ?? "-"} · phases ${payload.boss.phases?.length ?? 0}`,
              })
            ) : (
              (payload.enemy_team ?? []).map((u) =>
                renderUnitCard(u.alias, { sub: `enemy · ATK ${u.atk ?? "-"} · DEF ${u.def ?? "-"}` })
              )
            )}
          </View>
        </View>

        <Text style={styles.subtitle}>Timeline turni (preview)</Text>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>
            Turno {currentStep.turn} · Azione {step + 1}/{totalSteps}
          </Text>
          <Text style={styles.cardLine}>
            Attore: <Text style={styles.bold}>{currentStep.actor}</Text>
          </Text>
          <Text style={styles.cardLine}>
            Azione: <Text style={styles.bold}>{currentStep.action}</Text>
          </Text>
          {currentStep.target ? (
            <Text style={styles.cardLine}>
              Target: <Text style={styles.bold}>{currentStep.target}</Text>
            </Text>
          ) : null}
          {typeof currentStep.preview_dmg === "number" ? (
            <Text style={styles.cardLine}>
              Danno preview: <Text style={styles.bold}>{currentStep.preview_dmg}</Text>
            </Text>
          ) : null}
          {typeof currentStep.preview_heal === "number" ? (
            <Text style={styles.cardLine}>
              Heal preview: <Text style={styles.bold}>{currentStep.preview_heal}</Text>
            </Text>
          ) : null}

          <View style={styles.ctrlRow}>
            <TouchableOpacity onPress={prev} style={styles.ctrlBtn}>
              <Text style={styles.ctrlBtnText}>‹ Indietro</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={next} style={styles.ctrlBtnPrimary}>
              <Text style={styles.ctrlBtnPrimaryText}>Avvia battaglia preview ›</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={reset} style={styles.ctrlBtn}>
              <Text style={styles.ctrlBtnText}>Reset</Text>
            </TouchableOpacity>
          </View>

          {/* v88 — Autoplay / Pause / Speed (preview-only, no network) */}
          <View style={styles.ctrlRow}>
            <TouchableOpacity
              onPress={() => setAutoplay((a) => !a)}
              style={[styles.ctrlBtn, autoplay ? styles.ctrlBtnActive : null]}
            >
              <Text style={[styles.ctrlBtnText, autoplay ? styles.ctrlBtnTextActive : null]}>
                {autoplay ? "⏸ Pause" : "▶ Autoplay"}
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => setSpeed((s) => (s === 1 ? 2 : 1))}
              style={[styles.ctrlBtn, speed === 2 ? styles.ctrlBtnActive : null]}
            >
              <Text style={[styles.ctrlBtnText, speed === 2 ? styles.ctrlBtnTextActive : null]}>
                Velocità {speed}x
              </Text>
            </TouchableOpacity>
            <View style={styles.stepBadge}>
              <Text style={styles.stepBadgeText}>
                {step + 1}/{totalSteps}
              </Text>
            </View>
          </View>
        </View>

        {/* v88 — End Preview Summary */}
        {atEnd ? (
          <View style={styles.endSummaryCard}>
            <Text style={styles.endSummaryTitle}>Riepilogo preview</Text>
            <Text style={styles.endSummaryLine}>
              Esito mock: <Text style={styles.bold}>{payload.preview_outcome.player_wins ? "Vittoria preview" : "Sconfitta preview"}</Text>
            </Text>
            <Text style={styles.endSummaryLine}>NON AUTHORITATIVE · NO REWARD APPLIED</Text>
            <Text style={styles.endSummaryLine}>db_write=false · account_mutation=false · inventory_mutation=false</Text>
            <Text style={styles.endSummaryLine}>battle_engine_attached=false · endpoint_live=false</Text>
          </View>
        ) : null}

        <View style={styles.cardWarn}>
          <Text style={styles.cardWarnTitle}>Vincoli locali</Text>
          <Text style={styles.cardWarnLine}>preview_only=true · deterministic=true · authoritative=false</Text>
          <Text style={styles.cardWarnLine}>reward_grant=false · db_write=false · account_mutation=false</Text>
          <Text style={styles.cardWarnLine}>inventory_mutation=false · battle_engine_attached=false</Text>
          <Text style={styles.cardWarnLine}>NESSUN claim reale, NESSUN endpoint live, NESSUNA MMR/Tower/Story update.</Text>
        </View>

        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backBtnText}>← Torna indietro</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#0d1117" },
  content: { padding: 16, paddingBottom: 48 },
  h1: { color: "#fff", fontSize: 22, fontWeight: "700", marginBottom: 8 },
  subtitle: { color: "#cbd5e1", fontSize: 14, fontWeight: "600", marginTop: 16, marginBottom: 8 },
  badgesRow: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginBottom: 8 },
  badge: {
    backgroundColor: "#1f2937",
    borderColor: "#facc15",
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginRight: 6,
    marginBottom: 6,
  },
  badgeText: { color: "#facc15", fontSize: 11, fontWeight: "700", letterSpacing: 0.6 },
  modeRow: { flexDirection: "row", flexWrap: "wrap", marginBottom: 8 },
  modeChip: {
    backgroundColor: "#111827",
    borderColor: "#374151",
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 8,
    marginBottom: 8,
  },
  modeChipActive: { backgroundColor: "#2563eb", borderColor: "#2563eb" },
  modeChipText: { color: "#94a3b8", fontSize: 13, fontWeight: "600" },
  modeChipTextActive: { color: "#fff" },
  card: {
    backgroundColor: "#111827",
    borderColor: "#1f2937",
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 12,
  },
  cardTitle: { color: "#e2e8f0", fontSize: 14, fontWeight: "700", marginBottom: 6 },
  cardLine: { color: "#cbd5e1", fontSize: 13, marginBottom: 4 },
  cardMono: { color: "#a5f3fc", fontSize: 12, fontFamily: "Menlo" },
  bold: { color: "#fff", fontWeight: "700" },
  teamsRow: { flexDirection: "row", gap: 8, marginTop: 8 },
  teamsCol: { marginTop: 8 },
  teamHeader: {
    color: "#cbd5e1",
    fontWeight: "700",
    fontSize: 13,
    letterSpacing: 0.4,
    textTransform: "uppercase",
    marginTop: 8,
    marginBottom: 6,
  },
  unitsGrid: { flexDirection: "row", flexWrap: "wrap", marginBottom: 6 },
  unitCard: {
    flexDirection: "row",
    alignItems: "center",
    width: "100%",
    backgroundColor: "#0b1220",
    borderColor: "#1f2937",
    borderWidth: 1,
    borderRadius: 10,
    padding: 8,
    marginBottom: 6,
  },
  unitCardActive: { borderColor: "#22d3ee", backgroundColor: "#0f1f2e" },
  unitCardBoss: { borderColor: "#f97316" },
  portraitBox: {
    width: 44,
    height: 44,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 10,
  },
  portraitLetter: { color: "#0d1117", fontSize: 20, fontWeight: "800" },
  portraitBossTag: {
    position: "absolute",
    bottom: -10,
    color: "#fb923c",
    fontSize: 9,
    fontWeight: "800",
    letterSpacing: 0.6,
  },
  unitInfo: { flex: 1 },
  unitAlias: { color: "#fff", fontSize: 13, fontWeight: "700" },
  unitSub: { color: "#94a3b8", fontSize: 11, marginTop: 2 },
  targetedTag: { color: "#22d3ee", fontSize: 10, marginTop: 2 },
  aiHintTag: { color: "#fbbf24", fontSize: 10, marginTop: 2, fontStyle: "italic" },
  floatingToast: {
    position: "absolute",
    top: -16,
    fontSize: 13,
    fontWeight: "800",
    paddingHorizontal: 4,
    borderRadius: 4,
    overflow: "hidden",
  },
  floatingToastDmg: { color: "#fef2f2", backgroundColor: "#dc2626" },
  floatingToastHeal: { color: "#f0fdf4", backgroundColor: "#16a34a" },
  ctrlBtnActive: { backgroundColor: "#2563eb", borderColor: "#2563eb" },
  ctrlBtnTextActive: { color: "#fff" },
  stepBadge: {
    backgroundColor: "#0b1220",
    borderColor: "#1f2937",
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 8,
    minWidth: 56,
    alignItems: "center",
  },
  stepBadgeText: { color: "#94a3b8", fontSize: 12, fontWeight: "700" },
  endSummaryCard: {
    backgroundColor: "#0b2516",
    borderColor: "#16a34a",
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 12,
  },
  endSummaryTitle: { color: "#bbf7d0", fontSize: 14, fontWeight: "800", marginBottom: 6 },
  endSummaryLine: { color: "#86efac", fontSize: 12, marginBottom: 2 },
  hpBarOuter: {
    height: 12,
    backgroundColor: "#1f2937",
    borderRadius: 6,
    marginTop: 6,
    overflow: "hidden",
    position: "relative",
    justifyContent: "center",
  },
  hpBarFill: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    borderRadius: 6,
  },
  hpBarText: {
    color: "#fff",
    fontSize: 9,
    fontWeight: "700",
    textAlign: "center",
    zIndex: 1,
  },
  teamCard: {
    flex: 1,
    backgroundColor: "#0b1220",
    borderColor: "#1f2937",
    borderWidth: 1,
    borderRadius: 10,
    padding: 10,
    marginRight: 6,
  },
  teamTitle: { color: "#e2e8f0", fontWeight: "700", marginBottom: 6 },
  unitLine: { color: "#94a3b8", fontSize: 12, marginBottom: 2 },
  ctrlRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 10 },
  ctrlBtn: {
    backgroundColor: "#1f2937",
    borderColor: "#374151",
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },
  ctrlBtnText: { color: "#cbd5e1", fontSize: 12, fontWeight: "600" },
  ctrlBtnPrimary: {
    backgroundColor: "#16a34a",
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  ctrlBtnPrimaryText: { color: "#fff", fontSize: 12, fontWeight: "700" },
  cardWarn: {
    backgroundColor: "#1c1917",
    borderColor: "#f97316",
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginTop: 4,
    marginBottom: 12,
  },
  cardWarnTitle: { color: "#fb923c", fontWeight: "700", marginBottom: 4 },
  cardWarnLine: { color: "#fed7aa", fontSize: 12, marginBottom: 2 },
  backBtn: {
    alignSelf: "flex-start",
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: "#0b1220",
    borderColor: "#1f2937",
    borderWidth: 1,
    marginTop: 8,
  },
  backBtnText: { color: "#cbd5e1", fontSize: 13 },
});
