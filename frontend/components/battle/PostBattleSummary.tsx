/**
 * PostBattleSummary — main summary view (v16.22 Foundation)
 * ─────────────────────────────────────────────────────────────────────
 * Compact, premium, mobile-friendly post-battle summary.
 *
 * Sections:
 *   1. Outcome banner (VITTORIA / SCONFITTA + turns + duration)
 *   2. Rewards row (auto-claim + expandable details)
 *      - manual_claim items shown distinct + hint "scadono in X giorni"
 *   3. Hero EXP list (avatar, name, level, exp gained, animated bar, level up)
 *   4. Action buttons:
 *      - "📊 Report Battaglia" → opens BattleReportView overlay
 *      - "⚔️ Riprova" / "← Indietro"
 *
 * Architecture: pure presentation. Riceve `summary: PostBattleSummaryData`
 * dal caller (combat.tsx). Le formule di balancing NON sono qui.
 */
import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';
import AnimatedExpBar from './AnimatedExpBar';
import BattleReportView from './BattleReport';
import type { PostBattleSummaryData, RewardItem, HeroExpBreakdown } from './postBattleTypes';
import { COLORS } from '../../constants/theme';
import { resolveHeroImageSource } from '../ui/hopliteAssets';

export interface PostBattleSummaryProps {
  summary: PostBattleSummaryData;
  onRetry: () => void;
  onExit: () => void;
}

export default function PostBattleSummary({ summary, onRetry, onExit }: PostBattleSummaryProps) {
  const [rewardsExpanded, setRewardsExpanded] = useState(false);
  const [reportOpen, setReportOpen] = useState(false);

  const win = summary.outcome === 'victory';
  const allAutoRewards = summary.rewards.auto_claim;
  const importantRewards = summary.rewards.manual_claim;
  // Top 3 da mostrare in compact mode; il resto solo se expanded.
  const topAutoRewards = allAutoRewards.slice(0, 3);
  const hasMoreAuto = allAutoRewards.length > 3;

  return (
    <LinearGradient
      colors={win ? ['#0D0D2B', '#1A1500', '#0D0D2B'] : ['#0D0D2B', '#1A0505', '#0D0D2B']}
      style={s.screen}
    >
      {/* ─── Outcome Banner ─── */}
      <Animated.View entering={FadeInDown.duration(300)} style={s.banner}>
        <Text style={[s.outcome, { color: win ? '#FFD700' : '#FF4444' }]}>
          {win ? '\uD83C\uDFC6 VITTORIA' : '\uD83D\uDCA5 SCONFITTA'}
        </Text>
        {!!summary.headline && <Text style={s.headline}>{summary.headline}</Text>}
        <View style={s.bannerStats}>
          <Stat label="Turni" value={String(summary.turns)} />
          <Stat label="Durata" value={`${summary.duration_sec}s`} />
          {summary.rewards.account_level_up && (
            <Stat label="Account" value={`Lv.${summary.rewards.new_account_level}`} accent="#FFD700" />
          )}
        </View>
      </Animated.View>

      <ScrollView
        contentContainerStyle={s.scroll}
        showsVerticalScrollIndicator={false}
      >
        {/* ─── Rewards ─── */}
        <Animated.View entering={FadeInUp.delay(120).duration(280)} style={s.card}>
          <View style={s.cardHead}>
            <Text style={s.cardTitle}>{'\uD83C\uDF81'} RICOMPENSE</Text>
            {(hasMoreAuto || importantRewards.length > 0) && (
              <TouchableOpacity
                onPress={() => setRewardsExpanded(v => !v)}
                hitSlop={{top:6,bottom:6,left:6,right:6}}
                activeOpacity={0.7}
              >
                <Text style={s.expandTxt}>
                  {rewardsExpanded ? 'Nascondi \u25B2' : 'Dettagli \u25BC'}
                </Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Compact row — top auto rewards always visible */}
          <View style={s.rewardsRow}>
            {topAutoRewards.map((r, i) => (
              <RewardChip key={`top-${i}`} reward={r} />
            ))}
            {!rewardsExpanded && hasMoreAuto && (
              <View style={s.moreChip}>
                <Text style={s.moreChipTxt}>+{allAutoRewards.length - 3}</Text>
              </View>
            )}
          </View>

          {/* Expanded — full auto + important */}
          {rewardsExpanded && (
            <>
              {hasMoreAuto && (
                <View style={[s.rewardsRow, { marginTop: 6 }]}>
                  {allAutoRewards.slice(3).map((r, i) => (
                    <RewardChip key={`extra-${i}`} reward={r} />
                  ))}
                </View>
              )}
              {importantRewards.length > 0 && (
                <View style={s.importantWrap}>
                  <Text style={s.importantTitle}>
                    {'\u2728'} RICOMPENSE IMPORTANTI
                  </Text>
                  <Text style={s.importantHint}>
                    {summary.rewards.expires_in_days
                      ? `Da reclamare in mailbox \u00B7 scadenza ${summary.rewards.expires_in_days} giorni`
                      : 'Da reclamare in mailbox'}
                  </Text>
                  <View style={s.rewardsRow}>
                    {importantRewards.map((r, i) => (
                      <RewardChip key={`imp-${i}`} reward={r} important />
                    ))}
                  </View>
                </View>
              )}
            </>
          )}
        </Animated.View>

        {/* ─── Hero EXP ─── */}
        {summary.hero_exp.length > 0 && (
          <Animated.View entering={FadeInUp.delay(220).duration(280)} style={s.card}>
            <Text style={s.cardTitle}>{'\u2694\uFE0F'} ESPERIENZA EROI</Text>
            <View style={{ gap: 8, marginTop: 8 }}>
              {summary.hero_exp.map((h, idx) => (
                <HeroExpRow key={h.user_hero_id} hero={h} delayMs={idx * 110} />
              ))}
            </View>
          </Animated.View>
        )}

        {/* Bottom action row */}
        <View style={s.actionRow}>
          <TouchableOpacity
            onPress={() => setReportOpen(true)}
            activeOpacity={0.78}
            style={[s.actionBtn, s.actionBtnSecondary]}
          >
            <Text style={s.actionTxt}>{'\uD83D\uDCCA'} REPORT BATTAGLIA</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={onRetry} activeOpacity={0.78} style={s.actionBtn}>
            <LinearGradient colors={[COLORS.accent, '#FF4444']} style={s.actionGrad}>
              <Text style={s.actionTxt}>{'\u2694\uFE0F'} RIPROVA</Text>
            </LinearGradient>
          </TouchableOpacity>
          <TouchableOpacity onPress={onExit} activeOpacity={0.78} style={[s.actionBtn, s.actionBtnExit]}>
            <Text style={s.actionTxt}>{'\u2190'} INDIETRO</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Modal-less report overlay */}
      <BattleReportView
        visible={reportOpen}
        onClose={() => setReportOpen(false)}
        report={summary.battle_report}
      />
    </LinearGradient>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────

function Stat({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <View style={s.stat}>
      <Text style={[s.statVal, accent ? { color: accent } : null]}>{value}</Text>
      <Text style={s.statLabel}>{label}</Text>
    </View>
  );
}

function RewardChip({ reward, important }: { reward: RewardItem; important?: boolean }) {
  return (
    <View style={[s.chip, important && s.chipImportant]}>
      <Text style={s.chipIcon}>{reward.icon}</Text>
      <View style={s.chipBody}>
        <Text style={s.chipName} numberOfLines={1}>{reward.name}</Text>
        <Text style={s.chipAmount}>x{reward.amount.toLocaleString()}</Text>
      </View>
    </View>
  );
}

function HeroExpRow({ hero, delayMs }: { hero: HeroExpBreakdown; delayMs: number }) {
  // Resolve avatar safely: il backend può inviare stringhe `asset:*` (es. il
  // sentinel di Hoplite `asset:greek_hoplite:splash`) che React Native NON sa
  // gestire come uri remoto. Il resolver locale traduce tali sentinel in
  // require() locali; per altri eroi ritorna {uri: ...} normale; null se
  // niente di valido — in quel caso si usa il fallback con la lettera.
  const avatarSource = resolveHeroImageSource(hero.avatar, hero.hero_id, hero.name);
  return (
    <View style={s.heroRow}>
      <View style={s.heroAvatarWrap}>
        {avatarSource ? (
          <Image source={avatarSource} style={s.heroAvatarImg} resizeMode="cover" />
        ) : (
          <Text style={s.heroAvatarFallback}>{(hero.name || '?').slice(0,1).toUpperCase()}</Text>
        )}
      </View>
      <View style={s.heroBody}>
        <View style={s.heroLine}>
          <Text style={s.heroName} numberOfLines={1}>{hero.name}</Text>
          <Text style={s.heroLevel}>
            Lv.{hero.level_after}
            {hero.leveled_up && (
              <Text style={s.heroLevelUp}> {'(+' + (hero.level_after - hero.level_before) + ')'} </Text>
            )}
          </Text>
        </View>
        <View style={s.heroBarRow}>
          <View style={{ flex: 1 }}>
            <AnimatedExpBar
              expBefore={hero.exp_before}
              expAfter={hero.exp_after}
              expToNextBefore={hero.exp_to_next_before}
              expToNextAfter={hero.exp_to_next_after}
              leveledUp={hero.leveled_up}
              startDelayMs={delayMs}
              height={7}
            />
          </View>
          <Text style={s.heroGain}>+{hero.exp_gained} EXP</Text>
        </View>
        {hero.leveled_up && (
          <Text style={s.heroLevelUpBadge}>{'\u2728'} LEVEL UP</Text>
        )}
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1 },

  banner: {
    paddingTop: 14,
    paddingBottom: 12,
    paddingHorizontal: 18,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.08)',
  },
  outcome: {
    fontSize: 26,
    fontWeight: '900',
    letterSpacing: 2,
    textShadowColor: 'rgba(0,0,0,0.6)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 6,
  },
  headline: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 11,
    fontWeight: '700',
    marginTop: 2,
    letterSpacing: 1,
  },
  bannerStats: {
    flexDirection: 'row',
    gap: 18,
    marginTop: 8,
  },
  stat: { alignItems: 'center' },
  statVal: { color: '#fff', fontSize: 14, fontWeight: '900' },
  statLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 9, letterSpacing: 0.7, marginTop: 1 },

  scroll: { padding: 12, gap: 10, paddingBottom: 24 },

  card: {
    backgroundColor: 'rgba(11,23,60,0.65)',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  cardHead: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  cardTitle: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '900',
    letterSpacing: 1.2,
  },
  expandTxt: {
    color: '#FFD7A8',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.5,
  },

  rewardsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 8,
    paddingVertical: 5,
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.10)',
    minHeight: 30,
  },
  chipImportant: {
    backgroundColor: 'rgba(255,215,0,0.14)',
    borderColor: 'rgba(255,215,0,0.55)',
  },
  chipIcon: { fontSize: 14 },
  chipBody: { flexShrink: 1 },
  chipName: { color: '#fff', fontSize: 10, fontWeight: '700' },
  chipAmount: { color: '#FFD700', fontSize: 11, fontWeight: '900' },
  moreChip: {
    paddingHorizontal: 8,
    paddingVertical: 5,
    backgroundColor: 'rgba(255,107,53,0.18)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.42)',
    minHeight: 30,
    alignItems: 'center',
    justifyContent: 'center',
  },
  moreChipTxt: { color: '#FFD7A8', fontSize: 10, fontWeight: '900' },

  importantWrap: {
    marginTop: 10,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,215,0,0.22)',
  },
  importantTitle: {
    color: '#FFD700',
    fontSize: 10,
    fontWeight: '900',
    letterSpacing: 1,
    marginBottom: 2,
  },
  importantHint: {
    color: 'rgba(255,255,255,0.5)',
    fontSize: 9,
    fontStyle: 'italic',
    marginBottom: 6,
  },

  // Hero exp
  heroRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 4,
  },
  heroAvatarWrap: {
    width: 38, height: 38, borderRadius: 19,
    backgroundColor: 'rgba(255,107,53,0.22)',
    borderWidth: 1.5, borderColor: 'rgba(255,215,0,0.55)',
    alignItems: 'center', justifyContent: 'center',
    overflow: 'hidden',
  },
  heroAvatarImg: { width: '100%', height: '100%' },
  heroAvatarFallback: { color: '#fff', fontWeight: '900', fontSize: 16 },
  heroBody: { flex: 1 },
  heroLine: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  heroName: { color: '#fff', fontSize: 12, fontWeight: '800', flexShrink: 1 },
  heroLevel: { color: 'rgba(255,255,255,0.7)', fontSize: 11, fontWeight: '700' },
  heroLevelUp: { color: '#FFD700', fontSize: 11, fontWeight: '900' },
  heroBarRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 4 },
  heroGain: { color: '#FFD700', fontSize: 10, fontWeight: '900', minWidth: 56, textAlign: 'right' },
  heroLevelUpBadge: {
    color: '#FFD700',
    fontSize: 9,
    fontWeight: '900',
    letterSpacing: 0.8,
    marginTop: 2,
  },

  actionRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 4,
  },
  actionBtn: {
    flex: 1,
    minHeight: 38,
    borderRadius: 8,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255,107,53,0.16)',
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.42)',
  },
  actionBtnSecondary: {
    backgroundColor: 'rgba(91,200,255,0.12)',
    borderColor: 'rgba(91,200,255,0.42)',
  },
  actionBtnExit: {
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderColor: 'rgba(255,255,255,0.18)',
  },
  actionGrad: {
    flex: 1,
    width: '100%',
    minHeight: 38,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionTxt: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '900',
    letterSpacing: 0.8,
    paddingHorizontal: 8,
  },
});
