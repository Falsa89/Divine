/**
 * Divine Waifus — Treasury Screen (TASK 4.5-B)
 * ──────────────────────────────────────────────────────────────
 * Read-only consumer of `frontend/data/currencies.ts`.
 *
 * SCOPE:
 *  - Display ALL currencies where `isVisibleInTreasury === true`.
 *  - Map a small subset to live runtime values:
 *      • gold            → user.gold
 *      • divine_crystals → user.gems  (legacy runtime field, still in use)
 *  - All other currencies are not yet wired in runtime → shown as
 *    "Non ancora attiva" (placeholder, amount = 0).
 *
 * STRICT CONSTRAINTS (do NOT violate):
 *  - No `<Modal>` (use absolute layers if ever needed).
 *  - No purchases, no claims, no shop actions.
 *  - No mutation of AuthContext.
 *  - Stamina is intentionally hidden (config has isVisibleInTreasury=false).
 *  - Pure read-only static catalog rendering.
 */
import React, { useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, { FadeInDown, FadeIn } from 'react-native-reanimated';

import { useAuth } from '../context/AuthContext';
import ScreenHeader from '../components/ui/ScreenHeader';
import { COLORS, SPACING, BORDER_RADIUS, FONT_SIZES } from '../constants/theme';

import {
  CURRENCY_DEFINITIONS,
} from '../data/currencies';
import type {
  CurrencyDefinition,
  CurrencyCategory,
  CurrencyImportance,
} from '../types/economy';

// ── Category visual mapping ──────────────────────────────────────
const CATEGORY_LABEL: Record<CurrencyCategory, string> = {
  standard: 'STANDARD',
  premium: 'PREMIUM',
  event: 'EVENTO',
  faction: 'FAZIONE',
  guild: 'GILDA',
  ranking: 'RANKING',
  soulbound: 'LEGAME',
  legacy_stamina: 'LEGACY',
  special: 'SPECIALE',
};

const CATEGORY_COLOR: Record<CurrencyCategory, string> = {
  standard: '#4499FF',
  premium: '#FFD700',
  event: '#FF8844',
  faction: '#BB55FF',
  guild: '#FF5544',
  ranking: '#44DD99',
  soulbound: '#FF77CC',
  legacy_stamina: '#888899',
  special: '#AA88FF',
};

const IMPORTANCE_GLOW: Record<CurrencyImportance, string> = {
  primary: 'rgba(255, 215, 0, 0.35)',
  secondary: 'rgba(68, 153, 255, 0.25)',
  tertiary: 'rgba(255, 255, 255, 0.08)',
};

// ── Source / Spend hint i18n (best-effort label dictionary) ──────
const HINT_LABEL: Record<string, string> = {
  // sources
  battle_victory: 'Vittoria battaglia',
  daily_login: 'Login giornaliero',
  shop_purchase: 'Acquisto shop',
  mailbox: 'Posta',
  real_money_purchase: 'Acquisto reale',
  event_milestone: 'Milestone evento',
  achievement: 'Achievement',
  first_clear: 'Prima vittoria',
  milestone: 'Milestone',
  event: 'Evento',
  event_shop: 'Shop evento',
  friend_help: 'Aiuto amici',
  guild_activity: 'Attività gilda',
  social: 'Sociale',
  arena_victory: 'Vittoria arena',
  arena_milestone: 'Milestone arena',
  arena_ranking: 'Ranking arena',
  guild_battle: 'Battaglia gilda',
  live_event: 'Evento live',
  gvg: 'GvG',
  raid_boss: 'Raid boss',
  season_pass: 'Season pass',
  season_milestone: 'Milestone season',
  mode_progression: 'Progressione modalità',
  legacy_regen: 'Rigenerazione legacy',
  // spends
  hero_levelup: 'Level up eroe',
  forge_upgrade: 'Forgia',
  summon: 'Evocazione',
  extra_entries: 'Entry extra',
  shop_premium: 'Shop premium',
  summon_limited: 'Evocazione limitata',
  event_summon: 'Evocazione evento',
  friendship_summon: 'Evocazione amicizia',
  honor_shop: "Shop d'onore",
  guild_shop: 'Shop gilda',
  war_banners_shop: 'Shop stendardi',
  season_shop: 'Shop season',
  prestige_unlock: 'Sblocco prestigio',
  mode_shop: 'Shop modalità',
  legacy_battle_entry: 'Entry battaglia legacy',
};

const labelForHint = (k: string) =>
  HINT_LABEL[k] ?? k.replace(/_/g, ' ');

// ── Runtime amount mapping ───────────────────────────────────────
type AmountState =
  | { kind: 'live'; amount: number }
  | { kind: 'placeholder' };

function getAmountForCurrency(
  def: CurrencyDefinition,
  user: { gold?: number; gems?: number } | null,
): AmountState {
  if (!user) return { kind: 'placeholder' };
  switch (def.id) {
    case 'gold':
      return { kind: 'live', amount: user.gold ?? 0 };
    case 'divine_crystals':
      // Runtime still uses legacy `gems` field — explicit mapping.
      return { kind: 'live', amount: user.gems ?? 0 };
    default:
      return { kind: 'placeholder' };
  }
}

const formatNumber = (n: number) => n.toLocaleString('it-IT');

// ── Currency row card ────────────────────────────────────────────
function CurrencyRow({
  def,
  amountState,
  index,
}: {
  def: CurrencyDefinition;
  amountState: AmountState;
  index: number;
}) {
  const catColor = CATEGORY_COLOR[def.category] ?? '#888899';
  const importance: CurrencyImportance = def.importance ?? 'tertiary';
  const glow = IMPORTANCE_GLOW[importance];
  const isPremium = def.isPremium === true;

  const isLive = amountState.kind === 'live';
  const amountText = isLive ? formatNumber(amountState.amount) : 'Non ancora attiva';

  return (
    <Animated.View
      entering={FadeInDown.delay(index * 30).duration(280)}
      style={s.rowOuter}
    >
      <LinearGradient
        colors={[
          'rgba(20, 20, 60, 0.85)',
          'rgba(10, 10, 32, 0.92)',
        ]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={[
          s.row,
          {
            borderColor: isPremium
              ? COLORS.gold
              : catColor + '55',
            shadowColor: isPremium ? COLORS.gold : catColor,
          },
        ]}
      >
        {/* Top line: icon + name + amount */}
        <View style={s.rowTop}>
          <View
            style={[
              s.iconWrap,
              {
                backgroundColor: catColor + '20',
                borderColor: catColor + '55',
                shadowColor: glow,
              },
            ]}
          >
            <Text style={s.iconTxt}>{def.icon ?? '🔹'}</Text>
          </View>

          <View style={s.titleCol}>
            <View style={s.titleRow}>
              <Text style={s.name} numberOfLines={1}>
                {def.name}
              </Text>
              {def.shortName ? (
                <Text style={s.short}>{def.shortName}</Text>
              ) : null}
            </View>
            <View style={s.badgeRow}>
              <View
                style={[
                  s.catBadge,
                  { backgroundColor: catColor + '22', borderColor: catColor + '66' },
                ]}
              >
                <Text style={[s.catBadgeTxt, { color: catColor }]}>
                  {CATEGORY_LABEL[def.category]}
                </Text>
              </View>
              {isPremium ? (
                <View style={[s.catBadge, s.premiumBadge]}>
                  <Text style={[s.catBadgeTxt, { color: COLORS.gold }]}>PREMIUM</Text>
                </View>
              ) : null}
              {def.expires ? (
                <View style={[s.catBadge, s.expiresBadge]}>
                  <Text style={[s.catBadgeTxt, { color: COLORS.warning }]}>
                    SCADENZA
                  </Text>
                </View>
              ) : null}
            </View>
          </View>

          <View style={s.amountWrap}>
            <Text
              style={[
                s.amount,
                isLive
                  ? { color: isPremium ? COLORS.gold : '#FFFFFF' }
                  : s.amountPlaceholder,
              ]}
              numberOfLines={1}
            >
              {amountText}
            </Text>
            {isLive ? (
              <Text style={s.amountSub}>ATTIVA</Text>
            ) : (
              <Text style={s.amountSubPlaceholder}>NON ANCORA TRACCIATA</Text>
            )}
          </View>
        </View>

        {/* Description */}
        <Text style={s.desc} numberOfLines={3}>
          {def.description}
        </Text>

        {/* Hints */}
        {def.sourceHints.length > 0 ? (
          <View style={s.hintBlock}>
            <Text style={s.hintLabel}>OTTIENI:</Text>
            <View style={s.hintChips}>
              {def.sourceHints.map((h) => (
                <View key={`src-${h}`} style={[s.chip, s.chipSrc]}>
                  <Text style={s.chipTxt}>{labelForHint(h)}</Text>
                </View>
              ))}
            </View>
          </View>
        ) : null}

        {def.spendHints.length > 0 ? (
          <View style={s.hintBlock}>
            <Text style={s.hintLabel}>SPENDI:</Text>
            <View style={s.hintChips}>
              {def.spendHints.map((h) => (
                <View key={`spd-${h}`} style={[s.chip, s.chipSpd]}>
                  <Text style={s.chipTxt}>{labelForHint(h)}</Text>
                </View>
              ))}
            </View>
          </View>
        ) : null}

        {def.relatedScreens.length > 0 ? (
          <Text style={s.relatedTxt} numberOfLines={1}>
            Schermate correlate: {def.relatedScreens.join(' · ')}
          </Text>
        ) : null}
      </LinearGradient>
    </Animated.View>
  );
}

export default function TreasuryScreen() {
  const { user } = useAuth();

  const visibleCurrencies = useMemo(() => {
    const list = Object.values(CURRENCY_DEFINITIONS).filter(
      (c) => c.isVisibleInTreasury === true,
    );
    list.sort((a, b) => a.sortOrder - b.sortOrder);
    return list;
  }, []);

  const stats = useMemo(() => {
    let live = 0;
    let placeholder = 0;
    for (const def of visibleCurrencies) {
      const r = getAmountForCurrency(def, user as any);
      if (r.kind === 'live') live++;
      else placeholder++;
    }
    return { live, placeholder, total: visibleCurrencies.length };
  }, [visibleCurrencies, user]);

  return (
    <LinearGradient
      colors={[COLORS.bgPrimary, '#0A0A24', '#06061A']}
      style={s.container}
    >
      <ScreenHeader title="Tesoreria" showBack />

      <ScrollView
        style={s.scroll}
        contentContainerStyle={s.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Hero summary panel */}
        <Animated.View entering={FadeIn.duration(300)} style={s.heroOuter}>
          <LinearGradient
            colors={['rgba(255, 215, 0, 0.10)', 'rgba(68, 153, 255, 0.06)']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={s.hero}
          >
            <Text style={s.heroTitle}>
              {'\u2728'} VAULT DEL CUSTODE {'\u2728'}
            </Text>
            <Text style={s.heroSub}>
              Catalogo ufficiale delle valute del regno. Solo lettura.
            </Text>
            <View style={s.heroStatsRow}>
              <View style={s.heroStat}>
                <Text style={[s.heroStatVal, { color: COLORS.gold }]}>
                  {stats.total}
                </Text>
                <Text style={s.heroStatLbl}>TOTALI</Text>
              </View>
              <View style={s.heroStatDiv} />
              <View style={s.heroStat}>
                <Text style={[s.heroStatVal, { color: COLORS.success }]}>
                  {stats.live}
                </Text>
                <Text style={s.heroStatLbl}>ATTIVE</Text>
              </View>
              <View style={s.heroStatDiv} />
              <View style={s.heroStat}>
                <Text style={[s.heroStatVal, { color: COLORS.textMuted }]}>
                  {stats.placeholder}
                </Text>
                <Text style={s.heroStatLbl}>FUTURE</Text>
              </View>
            </View>
          </LinearGradient>
        </Animated.View>

        {/* Currency list */}
        {visibleCurrencies.map((def, idx) => {
          const amountState = getAmountForCurrency(def, user as any);
          return (
            <CurrencyRow
              key={def.id}
              def={def}
              amountState={amountState}
              index={idx}
            />
          );
        })}

        {/* Footer disclaimer */}
        <View style={s.footer}>
          <Text style={s.footerTxt}>
            Valori e categorie sono soggetti a bilanciamento.
          </Text>
          <Text style={s.footerTxtDim}>
            Nessun acquisto o claim disponibile in questa schermata.
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

  // Hero panel
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
  },
  heroStatsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SPACING.md,
    gap: SPACING.lg,
  },
  heroStat: { alignItems: 'center', minWidth: 60 },
  heroStatVal: {
    fontSize: FONT_SIZES.xxl,
    fontWeight: '900',
  },
  heroStatLbl: {
    color: COLORS.textMuted,
    fontSize: FONT_SIZES.xs,
    fontWeight: '800',
    letterSpacing: 1.5,
    marginTop: 2,
  },
  heroStatDiv: {
    width: 1,
    height: 26,
    backgroundColor: COLORS.borderLight,
  },

  // Row card
  rowOuter: {
    borderRadius: BORDER_RADIUS.lg,
    overflow: 'hidden',
  },
  row: {
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.lg,
    borderWidth: 1,
    gap: SPACING.sm,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 3,
  },
  rowTop: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.md,
  },
  iconWrap: {
    width: 46,
    height: 46,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.6,
    shadowRadius: 6,
  },
  iconTxt: { fontSize: 22 },
  titleCol: { flex: 1, gap: 4 },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: SPACING.sm,
  },
  name: {
    color: COLORS.textPrimary,
    fontSize: FONT_SIZES.lg,
    fontWeight: '800',
    flexShrink: 1,
  },
  short: {
    color: COLORS.textMuted,
    fontSize: FONT_SIZES.xs,
    fontWeight: '700',
    letterSpacing: 1,
  },
  badgeRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
  },
  catBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    borderWidth: 1,
  },
  catBadgeTxt: {
    fontSize: 8,
    fontWeight: '900',
    letterSpacing: 1.2,
  },
  premiumBadge: {
    backgroundColor: 'rgba(255, 215, 0, 0.10)',
    borderColor: COLORS.borderGold,
  },
  expiresBadge: {
    backgroundColor: 'rgba(255, 170, 68, 0.10)',
    borderColor: 'rgba(255, 170, 68, 0.4)',
  },
  amountWrap: {
    alignItems: 'flex-end',
    minWidth: 80,
  },
  amount: {
    fontSize: FONT_SIZES.xl,
    fontWeight: '900',
  },
  amountPlaceholder: {
    color: COLORS.textMuted,
    fontSize: FONT_SIZES.sm,
    fontWeight: '700',
    fontStyle: 'italic',
  },
  amountSub: {
    color: COLORS.success,
    fontSize: 8,
    fontWeight: '900',
    letterSpacing: 1.2,
    marginTop: 2,
  },
  amountSubPlaceholder: {
    color: COLORS.textDim,
    fontSize: 8,
    fontWeight: '900',
    letterSpacing: 1.2,
    marginTop: 2,
  },

  // Description + hints
  desc: {
    color: COLORS.textSecondary,
    fontSize: FONT_SIZES.sm,
    lineHeight: 14,
  },
  hintBlock: { gap: 4 },
  hintLabel: {
    color: COLORS.textMuted,
    fontSize: 8,
    fontWeight: '900',
    letterSpacing: 1.5,
  },
  hintChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
  },
  chip: {
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 6,
    borderWidth: 1,
  },
  chipSrc: {
    backgroundColor: 'rgba(68, 221, 136, 0.08)',
    borderColor: 'rgba(68, 221, 136, 0.25)',
  },
  chipSpd: {
    backgroundColor: 'rgba(255, 107, 53, 0.08)',
    borderColor: 'rgba(255, 107, 53, 0.25)',
  },
  chipTxt: {
    color: COLORS.textPrimary,
    fontSize: 9,
    fontWeight: '700',
  },
  relatedTxt: {
    color: COLORS.textDim,
    fontSize: FONT_SIZES.xs,
    fontStyle: 'italic',
    marginTop: 2,
  },

  // Footer
  footer: {
    marginTop: SPACING.md,
    paddingHorizontal: SPACING.md,
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
