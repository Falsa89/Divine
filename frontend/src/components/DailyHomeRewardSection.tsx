/**
 * Pack 98 — Daily Home Reward Section (gated wrapper per home embedding).
 *
 * DOPPIO flag check obbligatorio:
 *   1. `EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED` (Pack 97) === 'true'
 *   2. `EXPO_PUBLIC_DAILY_HOME_UNLOCK` (Pack 98) === 'true'
 *
 * Se ANCHE UNO solo dei flag e' false (default), il componente returns null.
 * Nessun render in produzione di default. Nessun render senza server scope.
 *
 * Embed safety:
 *   - `useServerScope().serverId` deve essere truthy.
 *   - `useAuth().token` deve essere truthy.
 *
 * Composizione: wrappa `DailyLoginClaimButton` (Pack 97) + `DailyQuestClaimButton`
 * (Pack 98). Nessun altro consumer (no mail/achievements/battlepass/event/AFK).
 */
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { useAuth } from '../auth/AuthContext';
import { useServerScope } from '../hooks/useServerScope';
import DailyLoginClaimButton from './DailyLoginClaimButton';
import DailyQuestClaimButton from './DailyQuestClaimButton';

const UI_FLAG_PACK_97 = (process.env.EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED || 'false').toString().toLowerCase();
const HOME_FLAG_PACK_98 = (process.env.EXPO_PUBLIC_DAILY_HOME_UNLOCK || 'false').toString().toLowerCase();

export const DAILY_HOME_UI_ENABLED = UI_FLAG_PACK_97 === 'true';
export const DAILY_HOME_UNLOCKED = HOME_FLAG_PACK_98 === 'true';

export type DailyHomeRewardSectionProps = {
  /** Override per pagina preview/test. Default: false. */
  forceVisible?: boolean;
  onClaimed?: (source: 'daily_login' | 'daily_quest', rewards: Record<string, number>) => void;
};

export const DailyHomeRewardSection: React.FC<DailyHomeRewardSectionProps> = ({
  forceVisible = false,
  onClaimed,
}) => {
  // Module-level constants check FIRST (no hooks). Default OFF on both flags
  // means the section is never rendered in production.
  if (!forceVisible && (!DAILY_HOME_UI_ENABLED || !DAILY_HOME_UNLOCKED)) {
    return null;
  }
  // Only when flags are on (or forceVisible) we proceed to render the inner
  // wrapper that itself calls auth + scope hooks safely.
  return (
    <DailyHomeRewardSectionInner forceVisible={forceVisible} onClaimed={onClaimed} />
  );
};

const DailyHomeRewardSectionInner: React.FC<DailyHomeRewardSectionProps> = ({
  forceVisible = false,
  onClaimed,
}) => {
  const auth = useAuth();
  const scope = useServerScope();
  // Gate 2: server scope required (no silent s1)
  if (!scope?.serverId) return null;
  // Gate 3: auth required
  if (!auth?.token) return null;

  return (
    <View style={styles.wrap}>
      <Text style={styles.h1}>Ricompense giornaliere</Text>
      <DailyLoginClaimButton
        forceVisible={forceVisible || true}
        onClaimed={(r) => onClaimed && onClaimed('daily_login', r)}
      />
      <DailyQuestClaimButton
        forceVisible={forceVisible || true}
        questId="daily_quest_1"
        onClaimed={(r) => onClaimed && onClaimed('daily_quest', r)}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  wrap: { paddingHorizontal: 12, paddingVertical: 8 },
  h1: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 8 },
});

export default DailyHomeRewardSection;
