/**
 * ChatComposer — lightweight reusable chat input row.
 *
 * Used by:
 *   - app/plaza.tsx (Piazza Comunitaria — global chat)
 *   - app/combat.tsx (Battle Drawer — chat tab)
 *
 * Features:
 *   - Text input + send button
 *   - Emoji trigger placeholder (no emoji picker yet — onPress no-op)
 *   - Mobile-friendly sizing (44pt min touch target on send)
 *   - Submit via Enter / SubmitEditing
 *   - Disabled state while sending
 *
 * Design intent: matches the premium dark/orange UI direction.
 */
import React, { useState, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { COLORS } from '../../constants/theme';

export interface ChatComposerProps {
  /** Async send handler. Receives trimmed message. Should resolve when finished. */
  onSend: (msg: string) => Promise<void> | void;
  /** Placeholder text for the input. */
  placeholder?: string;
  /** Max character length (default 200). */
  maxLength?: number;
  /** Compact mode — smaller padding, used inside small drawers. */
  compact?: boolean;
  /** Disabled — block input + send. */
  disabled?: boolean;
}

export default function ChatComposer({
  onSend,
  placeholder = 'Scrivi un messaggio…',
  maxLength = 200,
  compact = false,
  disabled = false,
}: ChatComposerProps) {
  const [text, setText] = useState('');
  const [sending, setSending] = useState(false);

  const submit = useCallback(async () => {
    const trimmed = text.trim();
    if (!trimmed || sending || disabled) return;
    setSending(true);
    try {
      await onSend(trimmed);
      setText('');
    } catch {
      // swallow — caller decides what to do (toast, log, etc.)
    } finally {
      setSending(false);
    }
  }, [text, sending, disabled, onSend]);

  const onEmojiPress = useCallback(() => {
    // Placeholder: future emoji picker. For now, append a quick smile.
    setText(prev => prev + '\uD83D\uDE42');
  }, []);

  const isDisabled = disabled || sending || !text.trim();

  return (
    <View style={[s.row, compact && s.rowCompact]}>
      <TouchableOpacity
        onPress={onEmojiPress}
        activeOpacity={0.7}
        style={[s.emojiBtn, compact && s.emojiBtnCompact]}
        disabled={disabled || sending}
        hitSlop={{ top: 6, bottom: 6, left: 4, right: 4 }}
      >
        <Text style={s.emojiTxt}>{'\uD83D\uDE0A'}</Text>
      </TouchableOpacity>

      <TextInput
        style={[s.input, compact && s.inputCompact]}
        value={text}
        onChangeText={setText}
        placeholder={placeholder}
        placeholderTextColor="rgba(255,255,255,0.32)"
        editable={!disabled && !sending}
        maxLength={maxLength}
        onSubmitEditing={submit}
        returnKeyType="send"
        blurOnSubmit={false}
        autoCorrect={false}
        // multiline=false for single-line; can be elevated later if needed
      />

      <TouchableOpacity
        onPress={submit}
        activeOpacity={0.7}
        disabled={isDisabled}
        style={[
          s.sendBtn,
          compact && s.sendBtnCompact,
          isDisabled && s.sendBtnDisabled,
        ]}
        hitSlop={{ top: 6, bottom: 6, left: 4, right: 4 }}
      >
        <Text style={[s.sendTxt, compact && s.sendTxtCompact]}>
          {sending ? '…' : 'INVIA'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const s = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 8,
    backgroundColor: 'rgba(0,0,0,0.32)',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,107,53,0.22)',
  },
  rowCompact: {
    paddingHorizontal: 6,
    paddingVertical: 5,
    gap: 4,
  },
  emojiBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255,255,255,0.06)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  emojiBtnCompact: {
    width: 30,
    height: 30,
    borderRadius: 15,
  },
  emojiTxt: {
    fontSize: 16,
  },
  input: {
    flex: 1,
    minHeight: 36,
    maxHeight: 80,
    paddingHorizontal: 12,
    paddingVertical: Platform.OS === 'ios' ? 8 : 6,
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.10)',
    color: '#fff',
    fontSize: 13,
  },
  inputCompact: {
    minHeight: 30,
    paddingHorizontal: 10,
    paddingVertical: Platform.OS === 'ios' ? 6 : 4,
    fontSize: 12,
    borderRadius: 8,
  },
  sendBtn: {
    minWidth: 60,
    height: 36,
    paddingHorizontal: 14,
    backgroundColor: COLORS.accent,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#FF6B35',
    shadowOpacity: 0.4,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 3,
  },
  sendBtnCompact: {
    minWidth: 48,
    height: 30,
    paddingHorizontal: 10,
    borderRadius: 8,
  },
  sendBtnDisabled: {
    opacity: 0.4,
    shadowOpacity: 0,
  },
  sendTxt: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '900',
    letterSpacing: 1,
  },
  sendTxtCompact: {
    fontSize: 10,
    letterSpacing: 0.5,
  },
});
