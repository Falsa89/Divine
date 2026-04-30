/**
 * Divine Waifus — Hero Training Stub Screen (TASK 4.5-C)
 * ──────────────────────────────────────────────────────────────────
 * READ-ONLY second consumer of `frontend/data/`.
 *
 * Consumes:
 *  - MODE_DEFINITIONS       (data/modes.ts)
 *  - MATERIAL_DEFINITIONS   (data/materials.ts)
 *  - CONSUMABLE_DEFINITIONS (data/materials.ts)
 *  - REWARD_TABLES          (data/rewardTables.ts)
 *  - CURRENCY_DEFINITIONS   (data/currencies.ts)  — for currency icon lookup
 *  - PROTOTYPE_FLAGS        (data/prototypeFlags.ts) — top banner status
 *
 * STRICT CONSTRAINTS:
 *  - No backend calls.
 *  - No state mutation.
 *  - No real entry consumption / no battle start.
 *  - No purchases / claim.
 *  - No <Modal>.
 *  - Buttons are visually disabled.
 */
import React, { useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, { FadeIn, FadeInDown } from 'react-native-reanimated';

import ScreenHeader from '../components/ui/ScreenHeader';
import { COLORS, SPACING, BORDER_RADIUS, FONT_SIZES } from '../constants/theme';

import {
  MODE_DEFINITIONS,
  MATERIAL_DEFINITIONS,
  CONSUMABLE_DEFINITIONS,
  REWARD_TABLES,
  CURRENCY_DEFINITIONS,
  PROTOTYPE_FLAGS,
} from '../data';
import type { ModeDefinition } from '../types/modes';
import type { RewardItem } from '../types/rewards';

// ── Trial blueprint ──────────────────────────────────────────────
// Each trial card composes its display content from:
//   - a ModeDefinition (data/modes.ts)
//   - example material/consumable IDs from data/materials.ts
//   - the mode's rewardTableId for the reward preview block
//   - an optional UI rotation note (Trial Elementale)
interface TrialCardConfig {
  modeId: string;
  emoji: string;
  primaryRewardLabel: string;
  exampleMaterialIds: string[];
  rotationNote?: string;
  accent: readonly [string, string];
}

const TRIAL_CARDS: TrialCardConfig[] = [
  {
    modeId: 'hero_training_exp_trial',
    emoji: '\uD83D\uDCD8', // 📘
    primaryRewardLabel: 'Tomi EXP',
    exampleMaterialIds: ['minor_exp_tome', 'medium_exp_tome', 'major_exp_tome'],
    accent: ['#4499FF', '#1E5BB8'] as const,
  },
  {
    modeId: 'hero_training_ascension_trial',
    emoji: '\u2728', // ✨
    primaryRewardLabel: "Pietre d'Ascensione",
    exampleMaterialIds: [
      'minor_ascension_stone',
      'medium_ascension_stone',
      'major_ascension_stone',
    ],
    accent: ['#BB55FF', '#7733CC'] as const,
  },
  {
    modeId: 'hero_training_gold_trial',
    emoji: '\uD83E\uDE99', // 🪙
    primaryRewardLabel: 'Oro',
    exampleMaterialIds: [],
    accent: ['#FFD700', '#C9A800'] as const,
  },
  {
    modeId: 'hero_training_elemental_trial',
    emoji: '\uD83D\uDD25', // 🔥
    primaryRewardLabel: 'Essenze Elementali',
    exampleMaterialIds: [
      'fire_essence',
      'water_essence',
      'earth_essence',
      'wind_essence',
      'light_essence',
      'shadow_essence',
    ],
    rotationNote: 'Rotazione elementale giornaliera — placeholder',
    accent: ['#FF6B35', '#CC4422'] as const,
  },
];

// ── Helpers ──────────────────────────────────────────────────────
function getMatOrConsumable(id: string) {
  return (
    MATERIAL_DEFINITIONS[id] ??
    CONSUMABLE_DEFINITIONS[id] ??
    null
  );
}

/** Resolve a generic RewardItem to display chunks (icon + name + amount). */
function resolveRewardItem(item: RewardItem): {
  icon: string;
  label: string;
  amount: number;
} {
  const amt = item.amount ?? 0;
  switch (item.itemType) {
    case 'currency': {
      const def = item.itemId
        ? CURRENCY_DEFINITIONS[item.itemId as string]
        : undefined;
      return {
        icon: item.icon ?? def?.icon ?? '\uD83D\uDCB0',
        label: item.name ?? def?.name ?? String(item.itemId ?? 'Valuta'),
        amount: amt,
      };
    }
    case 'material': {
      const def = item.itemId ? MATERIAL_DEFINITIONS[item.itemId] : undefined;
      return {
        icon: item.icon ?? def?.icon ?? '\uD83E\uDDF1',
        label: item.name ?? def?.name ?? String(item.itemId ?? 'Materiale'),
        amount: amt,
      };
    }
    case 'consumable': {
      const def = item.itemId ? CONSUMABLE_DEFINITIONS[item.itemId] : undefined;
      return {
        icon: item.icon ?? def?.icon ?? '\uD83D\uDCDC',
        label: item.name ?? def?.name ?? String(item.itemId ?? 'Consumabile'),
        amount: amt,
      };
    }
    case 'hero_exp':
      return { icon: '\u2B50', label: 'EXP Eroe', amount: amt };
    case 'account_exp':
      return { icon: '\u2728', label: 'EXP Account', amount: amt };
    case 'equipment':
      return {
        icon: item.icon ?? '\uD83D\uDDE1\uFE0F',
        label: item.name ?? 'Equipaggiamento',
        amount: amt,
      };
    case 'artifact':
      return {
        icon: item.icon ?? '\uD83D\uDC8E',
        label: item.name ?? 'Artefatto',
        amount: amt,
      };
    case 'chest':
      return {
        icon: item.icon ?? '\uD83C\uDF81',
        label: item.name ?? 'Scrigno',
        amount: amt,
      };
    default:
      return {
        icon: '\u2754',
        label: String(item.itemId ?? item.itemType),
        amount: amt,
      };
  }
}

function statusBadge(mode: ModeDefinition): {
  label: string;
  color: string;
} {
  if (mode.isPrototypeEnabled === true) {
    return { label: 'PROTOTIPO', color: COLORS.success };
  }
  if (mode.isPlaceholder === true) {
    return { label: 'PLACEHOLDER', color: COLORS.warning };
  }
  return { label: 'CONCEPT', color: COLORS.textMuted };
}

// ── Trial Card Component ─────────────────────────────────────────
function TrialCard({
  config,
  index,
}: {
  config: TrialCardConfig;
  index: number;
}) {
  const mode = MODE_DEFINITIONS[config.modeId];
  if (!mode) {
    return (
      <View style={s.cardError}>
        <Text style={s.cardErrorTxt}>
          Mode mancante: {config.modeId}
        </Text>
      </View>
    );
  }

  const rewardTable = mode.rewardTableId
    ? REWARD_TABLES[mode.rewardTableId]
    : undefined;
  const guaranteed: RewardItem[] = rewardTable?.guaranteedRewards ?? [];
  const possible: RewardItem[] = rewardTable?.possibleDrops ?? [];

  const badge = statusBadge(mode);

  // entries preview (read from config; do NOT consume)
  const entriesText =
    mode.hasEntryLimit && mode.baseEntries
      ? `Ingressi giornalieri: ${mode.baseEntries} (placeholder)`
      : 'Ingressi giornalieri: placeholder';

  // unlock info (UI-only)
  const unlockText = mode.unlockAccountLevel
    ? `Sblocco: account Lv.${mode.unlockAccountLevel}`
    : null;

  const buttonLabel = mode.isPrototypeEnabled
    ? 'Entra — presto'
    : 'Non attivo nel prototipo';

  return (
    <Animated.View
      entering={FadeInDown.delay(index * 70).duration(300)}
      style={s.cardOuter}
    >
      <LinearGradient
        colors={['rgba(20, 20, 60, 0.92)', 'rgba(8, 8, 28, 0.95)']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={[s.card, { borderColor: config.accent[0] + '55' }]}
      >
        {/* Top — emoji + name + status */}
        <View style={s.cardTop}>
          <View
            style={[
              s.emojiWrap,
              {
                backgroundColor: config.accent[0] + '22',
                borderColor: config.accent[0] + '66',
                shadowColor: config.accent[0],
              },
            ]}
          >
            <Text style={s.emojiTxt}>{config.emoji}</Text>
          </View>
          <View style={s.cardTitleCol}>
            <Text style={s.cardName} numberOfLines={1}>
              {mode.name}
            </Text>
            <Text style={s.cardCategory}>
              ADDESTRAMENTO {'\u2022'} {mode.family.toUpperCase()}
            </Text>
          </View>
          <View
            style={[
              s.statusBadge,
              {
                backgroundColor: badge.color + '22',
                borderColor: badge.color + '66',
              },
            ]}
          >
            <Text style={[s.statusBadgeTxt, { color: badge.color }]}>
              {badge.label}
            </Text>
          </View>
        </View>

        {/* Description */}
        <Text style={s.cardDesc} numberOfLines={3}>
          {mode.description}
        </Text>

        {/* Rotation note (Trial Elementale) */}
        {config.rotationNote ? (
          <View style={s.rotationBanner}>
            <Text style={s.rotationTxt}>
              {'\uD83D\uDD04'} {config.rotationNote}
            </Text>
          </View>
        ) : null}

        {/* Primary reward + secondary pattern (Oro + EXP Account) */}
        <View style={s.rewardHeader}>
          <Text style={[s.sectionLabel, { color: config.accent[0] }]}>
            REWARD PRIMARIA
          </Text>
          <Text style={s.primaryRewardTxt}>{config.primaryRewardLabel}</Text>
        </View>

        <View style={s.secondaryRow}>
          <View style={s.secondaryChip}>
            <Text style={s.secondaryChipIcon}>
              {CURRENCY_DEFINITIONS.gold.icon}
            </Text>
            <Text style={s.secondaryChipTxt}>+ Oro</Text>
          </View>
          <View style={s.secondaryChip}>
            <Text style={s.secondaryChipIcon}>{'\u2728'}</Text>
            <Text style={s.secondaryChipTxt}>+ EXP Account</Text>
          </View>
        </View>

        {/* Reward preview list (from rewardTable.guaranteedRewards) */}
        {guaranteed.length > 0 ? (
          <View style={s.rewardBlock}>
            <Text style={s.sectionLabel}>DROP GARANTITI (anteprima)</Text>
            <View style={s.rewardList}>
              {guaranteed.map((it, i) => {
                const r = resolveRewardItem(it);
                return (
                  <View
                    key={`g-${it.id}-${i}`}
                    style={[s.rewardChip, s.rewardChipGuaranteed]}
                  >
                    <Text style={s.rewardChipIcon}>{r.icon}</Text>
                    <Text style={s.rewardChipTxt}>
                      {r.label}{' '}
                      <Text style={s.rewardChipAmt}>x{r.amount}</Text>
                    </Text>
                  </View>
                );
              })}
            </View>
          </View>
        ) : null}

        {possible.length > 0 ? (
          <View style={s.rewardBlock}>
            <Text style={s.sectionLabel}>DROP POSSIBILI</Text>
            <View style={s.rewardList}>
              {possible.map((it, i) => {
                const r = resolveRewardItem(it);
                return (
                  <View
                    key={`p-${it.id}-${i}`}
                    style={[s.rewardChip, s.rewardChipPossible]}
                  >
                    <Text style={s.rewardChipIcon}>{r.icon}</Text>
                    <Text style={s.rewardChipTxt}>
                      {r.label}{' '}
                      <Text style={s.rewardChipAmt}>x{r.amount}</Text>
                    </Text>
                  </View>
                );
              })}
            </View>
          </View>
        ) : null}

        {/* Example materials list (from data/materials.ts) */}
        {config.exampleMaterialIds.length > 0 ? (
          <View style={s.rewardBlock}>
            <Text style={s.sectionLabel}>MATERIALI (esempi)</Text>
            <View style={s.rewardList}>
              {config.exampleMaterialIds.map((mid) => {
                const def = getMatOrConsumable(mid);
                if (!def) {
                  return (
                    <View
                      key={`m-${mid}`}
                      style={[s.rewardChip, s.rewardChipMissing]}
                    >
                      <Text style={s.rewardChipTxt}>
                        {mid} (mancante)
                      </Text>
                    </View>
                  );
                }
                return (
                  <View
                    key={`m-${mid}`}
                    style={[s.rewardChip, s.rewardChipMaterial]}
                  >
                    <Text style={s.rewardChipIcon}>{def.icon ?? '\u2728'}</Text>
                    <Text style={s.rewardChipTxt}>{def.name}</Text>
                  </View>
                );
              })}
            </View>
          </View>
        ) : null}

        {/* Footer info: entries + unlock */}
        <View style={s.cardFooter}>
          <Text style={s.footerTxt}>{entriesText}</Text>
          {unlockText ? (
            <Text style={s.footerTxtDim}>{unlockText}</Text>
          ) : null}
        </View>

        {/* Disabled CTA — purely visual, no onPress */}
        <TouchableOpacity
          activeOpacity={1}
          disabled
          style={s.ctaOuter}
        >
          <LinearGradient
            colors={['rgba(255, 255, 255, 0.04)', 'rgba(255, 255, 255, 0.02)']}
            style={[
              s.cta,
              { borderColor: 'rgba(255, 255, 255, 0.12)' },
            ]}
          >
            <Text style={s.ctaTxt}>{buttonLabel}</Text>
          </LinearGradient>
        </TouchableOpacity>
      </LinearGradient>
    </Animated.View>
  );
}

// ── Screen ───────────────────────────────────────────────────────
export default function HeroTrainingScreen() {
  const flag = PROTOTYPE_FLAGS.hero_training;

  const releasePhaseLabel = useMemo(() => {
    if (!flag) return 'foundation';
    return flag.releasePhase ?? 'foundation';
  }, [flag]);

  return (
    <LinearGradient
      colors={[COLORS.bgPrimary, '#0A0A24', '#06061A']}
      style={s.container}
    >
      <ScreenHeader title="Addestramento Eroico" showBack />

      <ScrollView
        style={s.scroll}
        contentContainerStyle={s.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Intro panel */}
        <Animated.View entering={FadeIn.duration(300)} style={s.heroOuter}>
          <LinearGradient
            colors={['rgba(255, 215, 0, 0.10)', 'rgba(187, 85, 255, 0.06)']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={s.hero}
          >
            <Text style={s.heroTitle}>
              {'\u2694\uFE0F'} CRESCITA EROI {'\u2694\uFE0F'}
            </Text>
            <Text style={s.heroSub}>
              Quattro Trial dedicati al farming di tomi EXP, pietre d'ascensione,
              oro e essenze elementali.
            </Text>
            <View style={s.heroBadgeRow}>
              <View style={s.heroBadge}>
                <Text style={s.heroBadgeTxt}>
                  FASE: {releasePhaseLabel.toUpperCase()}
                </Text>
              </View>
              <View style={[s.heroBadge, s.heroBadgeWarn]}>
                <Text style={[s.heroBadgeTxt, { color: COLORS.warning }]}>
                  ANTEPRIMA — DATI PLACEHOLDER
                </Text>
              </View>
            </View>
          </LinearGradient>
        </Animated.View>

        {/* Trial cards grid (responsive: 2 cols on landscape via flexWrap) */}
        <View style={s.grid}>
          {TRIAL_CARDS.map((cfg, i) => (
            <TrialCard key={cfg.modeId} config={cfg} index={i} />
          ))}
        </View>

        {/* Footer disclaimer */}
        <View style={s.footer}>
          <Text style={s.footerTxt}>
            Valori e drop provvisori — bilanciamento non definitivo.
          </Text>
          <Text style={s.footerTxtDim}>
            Nessuna run reale, nessun acquisto, nessun consumo di ingressi.
          </Text>
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

// ── Styles ───────────────────────────────────────────────────────
const s = StyleSheet.create({
  container: { flex: 1 },
  scroll: { flex: 1 },
  scrollContent: {
    paddingHorizontal: SPACING.md,
    paddingTop: SPACING.md,
    paddingBottom: SPACING.xxl,
    gap: SPACING.sm,
  },

  // Intro hero panel
  heroOuter: {
    borderRadius: BORDER_RADIUS.lg,
    overflow: 'hidden',
    marginBottom: SPACING.sm,
  },
  hero: {
    padding: SPACING.lg,
    borderRadius: BORDER_RADIUS.lg,
    borderWidth: 1,
    borderColor: COLORS.borderGold,
    alignItems: 'center',
  },
  heroTitle: {
    color: COLORS.gold,
    fontSize: FONT_SIZES.lg,
    fontWeight: '900',
    letterSpacing: 3,
  },
  heroSub: {
    color: COLORS.textSecondary,
    fontSize: FONT_SIZES.sm,
    marginTop: 4,
    textAlign: 'center',
    lineHeight: 14,
  },
  heroBadgeRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: SPACING.sm,
    marginTop: SPACING.md,
  },
  heroBadge: {
    paddingHorizontal: SPACING.md,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: COLORS.borderLight,
    backgroundColor: 'rgba(255, 255, 255, 0.04)',
  },
  heroBadgeWarn: {
    borderColor: 'rgba(255, 170, 68, 0.4)',
    backgroundColor: 'rgba(255, 170, 68, 0.08)',
  },
  heroBadgeTxt: {
    color: COLORS.textPrimary,
    fontSize: 9,
    fontWeight: '900',
    letterSpacing: 1.5,
  },

  // Grid (landscape 2 cols, portrait 1 col via responsive flexBasis)
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: SPACING.sm,
  },

  // Card outer (landscape: ~48% width per card)
  cardOuter: {
    width: '49%',
    minWidth: 280,
    borderRadius: BORDER_RADIUS.lg,
    overflow: 'hidden',
  },
  card: {
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.lg,
    borderWidth: 1,
    gap: SPACING.sm,
  },
  cardError: { padding: SPACING.md },
  cardErrorTxt: { color: COLORS.error, fontSize: FONT_SIZES.sm },

  // Card top
  cardTop: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  emojiWrap: {
    width: 44,
    height: 44,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.55,
    shadowRadius: 6,
    elevation: 3,
  },
  emojiTxt: { fontSize: 22 },
  cardTitleCol: { flex: 1 },
  cardName: {
    color: COLORS.textPrimary,
    fontSize: FONT_SIZES.lg,
    fontWeight: '900',
  },
  cardCategory: {
    color: COLORS.textMuted,
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 1.4,
    marginTop: 1,
  },
  statusBadge: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
  },
  statusBadgeTxt: {
    fontSize: 8,
    fontWeight: '900',
    letterSpacing: 1.2,
  },

  cardDesc: {
    color: COLORS.textSecondary,
    fontSize: FONT_SIZES.sm,
    lineHeight: 14,
  },

  // Rotation banner
  rotationBanner: {
    paddingHorizontal: SPACING.md,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: 'rgba(255, 107, 53, 0.12)',
    borderWidth: 1,
    borderColor: 'rgba(255, 107, 53, 0.3)',
  },
  rotationTxt: {
    color: COLORS.accent,
    fontSize: FONT_SIZES.sm,
    fontWeight: '700',
  },

  // Reward header
  rewardHeader: {
    paddingTop: 4,
  },
  primaryRewardTxt: {
    color: COLORS.textPrimary,
    fontSize: FONT_SIZES.lg,
    fontWeight: '800',
    marginTop: 2,
  },

  // Secondary chips (Oro + EXP Account)
  secondaryRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  secondaryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: SPACING.sm,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: 'rgba(255, 215, 0, 0.3)',
    backgroundColor: 'rgba(255, 215, 0, 0.08)',
  },
  secondaryChipIcon: { fontSize: 11 },
  secondaryChipTxt: {
    color: COLORS.gold,
    fontSize: 10,
    fontWeight: '800',
  },

  // Reward block
  rewardBlock: { gap: 4 },
  sectionLabel: {
    color: COLORS.textMuted,
    fontSize: 8,
    fontWeight: '900',
    letterSpacing: 1.5,
  },
  rewardList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
  },
  rewardChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 7,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
  },
  rewardChipIcon: { fontSize: 11 },
  rewardChipTxt: {
    color: COLORS.textPrimary,
    fontSize: 10,
    fontWeight: '700',
  },
  rewardChipAmt: {
    color: COLORS.gold,
    fontWeight: '900',
  },
  rewardChipGuaranteed: {
    backgroundColor: 'rgba(68, 221, 136, 0.10)',
    borderColor: 'rgba(68, 221, 136, 0.32)',
  },
  rewardChipPossible: {
    backgroundColor: 'rgba(68, 153, 255, 0.10)',
    borderColor: 'rgba(68, 153, 255, 0.32)',
  },
  rewardChipMaterial: {
    backgroundColor: 'rgba(187, 85, 255, 0.10)',
    borderColor: 'rgba(187, 85, 255, 0.32)',
  },
  rewardChipMissing: {
    backgroundColor: 'rgba(255, 68, 102, 0.10)',
    borderColor: 'rgba(255, 68, 102, 0.32)',
  },

  // Card footer (entries + unlock)
  cardFooter: {
    paddingTop: 4,
    gap: 2,
  },

  // CTA disabled button
  ctaOuter: {
    borderRadius: BORDER_RADIUS.md,
    overflow: 'hidden',
    marginTop: 4,
  },
  cta: {
    paddingVertical: SPACING.sm,
    alignItems: 'center',
    borderRadius: BORDER_RADIUS.md,
    borderWidth: 1,
  },
  ctaTxt: {
    color: COLORS.textMuted,
    fontSize: FONT_SIZES.sm,
    fontWeight: '900',
    letterSpacing: 1.5,
  },

  // Screen footer
  footer: {
    marginTop: SPACING.md,
    alignItems: 'center',
    gap: 2,
  },
  footerTxt: {
    color: COLORS.textMuted,
    fontSize: FONT_SIZES.xs,
    fontWeight: '700',
  },
  footerTxtDim: {
    color: COLORS.textDim,
    fontSize: FONT_SIZES.xs,
    fontStyle: 'italic',
  },
});
