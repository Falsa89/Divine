/**
 * ChannelSelector — segmented control multi-canale (v16.18 Phase 1)
 * ───────────────────────────────────────────────────────────────────
 * Componente condiviso per selezione canale chat. Renderizza N tab
 * (uno per canale ricevuto in props), evidenzia l'attivo, mostra lo
 * stato 🔒 Locked per i canali non disponibili.
 *
 * Used by: plaza.tsx, home.tsx (HomeChatNotifPanel), combat.tsx.
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import type { ChannelKey, ChannelMeta } from '../../hooks/useChatChannel';
import { COLORS } from '../../constants/theme';

interface Props {
  channels: ChannelMeta[];
  active: ChannelKey;
  onChange: (k: ChannelKey) => void;
  /** Compact mode → label corte, padding ridotti. */
  compact?: boolean;
}

const LABEL_FULL: Record<ChannelKey, string> = {
  global:  'GLOBALE',
  system:  'SISTEMA',
  faction: 'FAZIONE',
  guild:   'GILDA',
};
const LABEL_SHORT: Record<ChannelKey, string> = {
  global:  'GLOB',
  system:  'SYS',
  faction: 'FAZ',
  guild:   'GILD',
};
const ICON: Record<ChannelKey, string> = {
  global:  '\uD83C\uDF10',     // \ud83c\udf10 = 🌐
  system:  '\u2699\uFE0F',      // ⚙
  faction: '\uD83D\uDEE1\uFE0F', // 🛡
  guild:   '\uD83C\uDFF0',      // 🏰
};

export default function ChannelSelector({ channels, active, onChange, compact = false }: Props) {
  return (
    <View style={[s.row, compact && s.rowCompact]}>
      {channels.map(c => {
        const isActive = c.key === active;
        const isLocked = !c.available;
        const label = compact ? LABEL_SHORT[c.key] : LABEL_FULL[c.key];
        return (
          <TouchableOpacity
            key={c.key}
            disabled={isLocked}
            onPress={() => !isLocked && onChange(c.key)}
            activeOpacity={0.7}
            hitSlop={{ top: 4, bottom: 4, left: 2, right: 2 }}
            style={[
              s.tab,
              compact && s.tabCompact,
              isActive && s.tabActive,
              isLocked && s.tabLocked,
            ]}
          >
            <Text style={[
              s.icon,
              compact && s.iconCompact,
              isActive && s.iconActive,
              isLocked && s.iconLocked,
            ]}>
              {isLocked ? '\uD83D\uDD12' : ICON[c.key]}
            </Text>
            <Text
              style={[
                s.txt,
                compact && s.txtCompact,
                isActive && s.txtActive,
                isLocked && s.txtLocked,
              ]}
              numberOfLines={1}
            >
              {label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const s = StyleSheet.create({
  row: {
    flexDirection: 'row',
    gap: 4,
    paddingHorizontal: 4,
    paddingVertical: 4,
    backgroundColor: 'rgba(0,0,0,0.32)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.18)',
  },
  rowCompact: {
    gap: 2,
    paddingHorizontal: 2,
    paddingVertical: 2,
    borderRadius: 6,
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
    paddingHorizontal: 6,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    minHeight: 28,
  },
  tabCompact: {
    paddingHorizontal: 3,
    paddingVertical: 4,
    minHeight: 22,
    gap: 2,
  },
  tabActive: {
    backgroundColor: 'rgba(255,107,53,0.22)',
    borderColor: COLORS.accent,
    shadowColor: COLORS.accent,
    shadowOpacity: 0.35,
    shadowRadius: 3,
    elevation: 2,
  },
  tabLocked: {
    opacity: 0.42,
  },
  icon: {
    fontSize: 12,
  },
  iconCompact: {
    fontSize: 10,
  },
  iconActive: {
    // niente cambio fontSize, solo per chiarezza
  },
  iconLocked: {
    opacity: 0.7,
  },
  txt: {
    color: 'rgba(255,255,255,0.72)',
    fontSize: 10,
    fontWeight: '900',
    letterSpacing: 0.6,
  },
  txtCompact: {
    fontSize: 8.5,
    letterSpacing: 0.3,
  },
  txtActive: {
    color: '#fff',
  },
  txtLocked: {
    color: 'rgba(255,255,255,0.5)',
  },
});
