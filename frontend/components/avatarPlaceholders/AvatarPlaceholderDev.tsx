/**
 * v93 — Avatar Placeholder Dev components.
 * DEV ONLY — NON canonical, NON final, NO monetization, NO cosmetic unlock.
 *
 * Componenti SVG-like (basati su react-native-svg, gia' installato) per
 * rappresentare i 7 avatar registrati. Non sono asset finali, non sono
 * direzione artistica.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Circle, Rect, Polygon, Path } from 'react-native-svg';

type Props = { size?: number; label?: string };

function Frame({
  size,
  color,
  label,
  children,
}: {
  size: number;
  color: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <View style={[s.frame, { width: size, height: size + 18 }]}>
      <Svg width={size} height={size} viewBox="0 0 100 100">
        <Rect x={0} y={0} width={100} height={100} fill="#0A1430" stroke={color} strokeWidth={2} rx={8} />
        {children}
      </Svg>
      <Text style={[s.lbl, { color }]} numberOfLines={1}>
        {label}
      </Text>
    </View>
  );
}

export function AvatarPlaceholderHD({ size = 80, label }: Props) {
  return (
    <Frame size={size} color="#4488FF" label={label ?? 'PLAYER HD (dev)'}>
      <Circle cx={50} cy={32} r={16} fill="#4488FF" />
      <Rect x={28} y={50} width={44} height={42} fill="#4488FF" rx={6} />
    </Frame>
  );
}

export function AvatarPlaceholderWarMini({ size = 80, label }: Props) {
  return (
    <Frame size={size} color="#FFAA22" label={label ?? 'WAR MINI (dev)'}>
      <Polygon points="50,15 80,50 50,85 20,50" fill="#FFAA22" />
      <Circle cx={50} cy={50} r={10} fill="#0A1430" />
    </Frame>
  );
}

export function AvatarPlaceholderGuildWar({ size = 80, label }: Props) {
  return (
    <Frame size={size} color="#AA22FF" label={label ?? 'GUILD WAR (dev)'}>
      <Path d="M50 10 L85 28 L85 60 Q85 85 50 92 Q15 85 15 60 L15 28 Z" fill="#AA22FF" />
      <Polygon points="50,35 60,50 50,65 40,50" fill="#FFD700" />
    </Frame>
  );
}

export function AvatarPlaceholderEvent({ size = 80, label }: Props) {
  return (
    <Frame size={size} color="#22DDAA" label={label ?? 'EVENT (dev)'}>
      <Polygon points="50,8 60,38 92,38 66,58 76,90 50,72 24,90 34,58 8,38 40,38" fill="#22DDAA" />
    </Frame>
  );
}

export function AvatarPlaceholderChibi({ size = 80, label }: Props) {
  return (
    <Frame size={size} color="#FF77CC" label={label ?? 'CHIBI (dev)'}>
      <Circle cx={50} cy={40} r={26} fill="#FF77CC" />
      <Rect x={36} y={66} width={28} height={24} fill="#FF77CC" rx={4} />
      <Circle cx={42} cy={38} r={3} fill="#0A1430" />
      <Circle cx={58} cy={38} r={3} fill="#0A1430" />
    </Frame>
  );
}

export function AvatarPlaceholderRaidBoss({ size = 80, label }: Props) {
  return (
    <Frame size={size} color="#FF4444" label={label ?? 'RAID BOSS (dev)'}>
      <Polygon points="30,8 50,20 70,8 70,30 88,50 70,70 70,92 50,80 30,92 30,70 12,50 30,30" fill="#FF4444" />
      <Circle cx={42} cy={48} r={4} fill="#FFFF00" />
      <Circle cx={58} cy={48} r={4} fill="#FFFF00" />
    </Frame>
  );
}

export function AvatarPlaceholderFactionBoss({ size = 80, label }: Props) {
  return (
    <Frame size={size} color="#CC4488" label={label ?? 'FACTION BOSS (dev)'}>
      <Polygon points="30,12 38,4 50,12 62,4 70,12 70,30 50,40 30,30" fill="#FFD700" />
      <Rect x={22} y={32} width={56} height={56} fill="#CC4488" rx={8} />
    </Frame>
  );
}

export const PLACEHOLDER_REGISTRY: Record<string, React.FC<Props>> = {
  player_avatar_hd_base_dev: AvatarPlaceholderHD,
  player_war_avatar_mini_base_dev: AvatarPlaceholderWarMini,
  guild_war_avatar_base_dev: AvatarPlaceholderGuildWar,
  event_avatar_base_dev: AvatarPlaceholderEvent,
  hero_room_chibi_avatar_base_dev: AvatarPlaceholderChibi,
  raid_boss_avatar_placeholder_dev: AvatarPlaceholderRaidBoss,
  faction_boss_avatar_placeholder_dev: AvatarPlaceholderFactionBoss,
};

const s = StyleSheet.create({
  frame: { alignItems: 'center' },
  lbl: { fontSize: 9, fontWeight: '700', marginTop: 4 },
});
