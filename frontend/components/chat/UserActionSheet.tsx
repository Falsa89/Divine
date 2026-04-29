/**
 * UserActionSheet — in-tree popover with quick user actions (v16.19)
 * ──────────────────────────────────────────────────────────
 * Mostrato quando l'utente tappa un username/avatar in chat o nella mappa
 * Plaza. Espone azioni quick (Phase 2: "Parla in privato").
 * In-tree overlay (no Modal nativo — coerente con la policy della codebase
 * vedi v16.5/v16.15).
 *
 * Future Phase 3+: aggiungere "Aggiungi amico", "Vedi profilo", "Sfida arena",
 * "Blocca", "Segnala".
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../../constants/theme';

export interface UserActionSheetProps {
  visible: boolean;
  username: string;
  onClose: () => void;
  /** L'azione DM. Quando assente, il bottone è nascosto. */
  onPrivateChat?: () => void;
  /** Eventuale subtitle (es: livello, fazione). */
  subtitle?: string;
  /** Disabilita azioni — es. NPC o utente non DM-able. */
  isNpc?: boolean;
}

export default function UserActionSheet({
  visible,
  username,
  onClose,
  onPrivateChat,
  subtitle,
  isNpc,
}: UserActionSheetProps) {
  if (!visible) return null;
  return (
    <View style={s.overlay} pointerEvents="auto">
      <TouchableOpacity
        style={StyleSheet.absoluteFill}
        activeOpacity={1}
        onPress={onClose}
      />
      <View style={s.sheetWrap}>
        <LinearGradient
          colors={['rgba(11,23,60,0.98)', 'rgba(5,9,26,0.98)']}
          style={s.sheet}
        >
          <View style={s.header}>
            <Text style={s.username} numberOfLines={1}>{username || 'Utente'}</Text>
            {!!subtitle && <Text style={s.subtitle} numberOfLines={1}>{subtitle}</Text>}
          </View>
          {isNpc ? (
            <Text style={s.npcHint}>Questo è un personaggio non giocante.</Text>
          ) : (
            <>
              {onPrivateChat && (
                <TouchableOpacity
                  onPress={() => { onClose(); onPrivateChat(); }}
                  activeOpacity={0.78}
                  style={s.action}
                >
                  <Text style={s.actionIcon}>{'\uD83D\uDCAC'}</Text>
                  <Text style={s.actionLabel}>Parla in privato</Text>
                  <Text style={s.actionArrow}>{'\u203A'}</Text>
                </TouchableOpacity>
              )}
              {/* Future Phase 3+: aggiungi qui altre azioni (amico, profilo, sfida) */}
            </>
          )}
          <TouchableOpacity onPress={onClose} activeOpacity={0.7} style={s.cancel}>
            <Text style={s.cancelTxt}>Annulla</Text>
          </TouchableOpacity>
        </LinearGradient>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0, bottom: 0, left: 0, right: 0,
    backgroundColor: 'rgba(0,0,0,0.62)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9500,
    elevation: 9500,
  },
  sheetWrap: {
    width: 320,
    maxWidth: '90%',
  },
  sheet: {
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: 'rgba(255,107,53,0.42)',
    padding: 16,
  },
  header: {
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.08)',
    marginBottom: 12,
  },
  username: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '900',
    letterSpacing: 0.4,
  },
  subtitle: {
    color: 'rgba(255,255,255,0.55)',
    fontSize: 11,
    marginTop: 3,
    fontWeight: '600',
  },
  action: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: 'rgba(255,107,53,0.18)',
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.42)',
    marginBottom: 8,
    gap: 10,
  },
  actionIcon: {
    fontSize: 18,
  },
  actionLabel: {
    flex: 1,
    color: '#fff',
    fontSize: 14,
    fontWeight: '800',
    letterSpacing: 0.3,
  },
  actionArrow: {
    color: COLORS.accent,
    fontSize: 18,
    fontWeight: '900',
  },
  npcHint: {
    color: 'rgba(255,255,255,0.55)',
    fontSize: 12,
    fontStyle: 'italic',
    paddingVertical: 8,
    textAlign: 'center',
  },
  cancel: {
    marginTop: 4,
    paddingVertical: 10,
    alignItems: 'center',
  },
  cancelTxt: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
});
