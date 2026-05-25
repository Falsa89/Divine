// SafeFeatureCard.tsx — PROJECT_Y Track B
// Componente locked/preview card riutilizzabile. Sicuro per default: nessun handler
// live, nessuna chiamata mutativa, copy lock in italiano. Pensato per esporre
// in modo controllato feature non ancora attive (Artefatti, Dimora, etc.).
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Platform } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';

export type SafeFeatureVisibility =
  | 'player_visible_locked'
  | 'player_visible_active_read_only'
  | 'dev_admin_only'
  | 'hidden_until_approved';

export interface SafeFeatureCardProps {
  title: string;
  subtitle?: string;
  statusBadge?: string;
  visibility: SafeFeatureVisibility;
  lockReason?: string;
  endpointStatus?: 'live' | 'preview_503' | 'dry_run' | 'none';
  icon?: string;
  onPress?: () => void; // mostrato solo se visibility === read_only o dev_admin_only
  testID?: string;
  accessibilityRole?: 'link' | 'button' | 'none';
  accessibilityHint?: string;
}

const VIS_LABEL: Record<SafeFeatureVisibility, string> = {
  player_visible_locked: 'In arrivo',
  player_visible_active_read_only: 'Anteprima',
  dev_admin_only: 'DEV',
  hidden_until_approved: 'In attesa',
};

export function SafeFeatureCard(props: SafeFeatureCardProps) {
  const isLocked =
    props.visibility === 'player_visible_locked' ||
    props.visibility === 'hidden_until_approved';
  const Wrapper: any = isLocked ? View : TouchableOpacity;
  const interactProps: any = isLocked ? {} : { activeOpacity: 0.85, onPress: props.onPress };

  return (
    <Wrapper
      {...interactProps}
      style={[styles.card, isLocked && styles.cardLocked]}
      accessibilityRole={props.accessibilityRole}
      accessibilityHint={props.accessibilityHint}
      accessibilityState={{ disabled: isLocked }}
      accessibilityLabel={`${props.title}${isLocked ? ' (bloccata)' : ''}`}
      testID={props.testID}
    >
      <LinearGradient
        colors={isLocked ? ['rgba(20,20,60,0.55)', 'rgba(10,10,30,0.55)'] : ['rgba(40,30,80,0.7)', 'rgba(20,15,50,0.7)']}
        style={StyleSheet.absoluteFill}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      />
      <View style={styles.headerRow}>
        <View style={styles.titleWrap}>
          {props.icon ? <Text style={styles.icon}>{props.icon}</Text> : null}
          <Text style={styles.title} numberOfLines={1}>
            {props.title}
          </Text>
        </View>
        <View style={[styles.badge, isLocked && styles.badgeLocked]}>
          <Text style={styles.badgeText}>
            {props.statusBadge ?? VIS_LABEL[props.visibility]}
          </Text>
        </View>
      </View>
      {props.subtitle ? (
        <Text style={styles.subtitle} numberOfLines={2}>
          {props.subtitle}
        </Text>
      ) : null}
      {isLocked && props.lockReason ? (
        <View style={styles.lockReasonWrap}>
          <Text style={styles.lockReason} numberOfLines={3}>
            {String.fromCharCode(0x1F512)} {props.lockReason}
          </Text>
        </View>
      ) : null}
      {props.endpointStatus === 'preview_503' ? (
        <Text style={styles.endpointHint}>Endpoint preview disabilitato (503) — modalità anteprima statica.</Text>
      ) : null}
    </Wrapper>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 14,
    overflow: 'hidden',
    padding: 16,
    marginBottom: 12,
    minHeight: 96,
    borderWidth: 1,
    borderColor: COLORS.borderLight,
    ...Platform.select({
      ios: { shadowColor: '#000', shadowOpacity: 0.4, shadowRadius: 6, shadowOffset: { width: 0, height: 4 } },
      android: { elevation: 3 },
    }),
  },
  cardLocked: {
    opacity: 0.85,
    borderStyle: 'dashed',
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  titleWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  icon: {
    fontSize: 20,
    marginRight: 8,
  },
  title: {
    color: COLORS.textPrimary,
    fontSize: 16,
    fontWeight: '700',
    flexShrink: 1,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    backgroundColor: COLORS.accent,
    marginLeft: 8,
  },
  badgeLocked: {
    backgroundColor: COLORS.warning,
  },
  badgeText: {
    color: '#1a1a1a',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  subtitle: {
    color: COLORS.textSecondary,
    fontSize: 13,
    marginTop: 8,
    lineHeight: 18,
  },
  lockReasonWrap: {
    marginTop: 10,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: COLORS.borderLight,
  },
  lockReason: {
    color: COLORS.textMuted,
    fontSize: 12,
    fontStyle: 'italic',
  },
  endpointHint: {
    color: COLORS.warning,
    fontSize: 11,
    marginTop: 8,
    fontStyle: 'italic',
  },
});

export default SafeFeatureCard;
