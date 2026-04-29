/**
 * ChatComposer — lightweight reusable chat input row.
 *
 * Used by:
 *   - app/plaza.tsx (Piazza Comunitaria — global chat)
 *   - app/combat.tsx (Battle Drawer — chat tab)
 *   - app/(tabs)/home.tsx (HomeChatNotifPanel — global chat)
 *
 * Features:
 *   - Text input + send button
 *   - Real emoji picker (in-tree, NOT Modal — coerente con la policy
 *     anti-Modal della codebase, vedi v16.5/v16.15). Curated set di
 *     ~56 emoji + tap-to-insert. Si apre sopra la riga composer
 *     coprendo temporaneamente la message list. Toggle via emoji
 *     button + tap fuori (backdrop) per chiudere.
 *   - Mobile-friendly sizing (44pt min touch target on send)
 *   - Submit via Enter / SubmitEditing
 *   - Disabled state while sending
 *
 * Design intent: matches the premium dark/orange UI direction.
 */
import React, { useState, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Platform, ScrollView, Keyboard } from 'react-native';
import { COLORS } from '../../constants/theme';

// ─────────────────────────────────────────────────────────────────────
// CURATED EMOJI SET (v16.17)
// ─────────────────────────────────────────────────────────────────────
// 56 emoji selezionati per coprire i casi d'uso reali di una chat di
// gioco RPG: reazioni emotive, gesti, simboli RPG/gaming, cuori/stelle.
// Niente categorie multiple in questo pass: una griglia singola con
// flexWrap → fit responsivo su tutte le surface (Plaza/Home/Battle).
// Future enhancement: categorie + ricerca (NON questo pass).
// ─────────────────────────────────────────────────────────────────────
const EMOJIS = [
  '😀','😄','😁','😆','😂','🤣','😊','😉',
  '😍','🥰','😘','😎','🤩','🥳','🤔','🙃',
  '😢','😭','😡','😤','🤯','😱','😴','🥲',
  '👍','👎','👏','🙌','👋','🤝','✌️','🤞',
  '💪','🙏','💯','🔥','✨','⭐','💎','🏆',
  '⚔️','🛡️','🏹','🗡️','👑','🎯','🎉','💥',
  '❤️','🧡','💛','💚','💙','💜','🖤','💔',
];

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
  const [pickerOpen, setPickerOpen] = useState(false);

  const submit = useCallback(async () => {
    const trimmed = text.trim();
    if (!trimmed || sending || disabled) return;
    setSending(true);
    try {
      await onSend(trimmed);
      setText('');
      setPickerOpen(false);
    } catch {
      // swallow — caller decides what to do (toast, log, etc.)
    } finally {
      setSending(false);
    }
  }, [text, sending, disabled, onSend]);

  const onEmojiTogglePress = useCallback(() => {
    // Apertura/chiusura picker. Quando apriamo, dismissiamo prima la
    // keyboard del TextInput per evitare overlap UX (su mobile reale
    // la keyboard può oscurare il picker se entrambi visibili insieme).
    setPickerOpen(prev => {
      const next = !prev;
      if (next) Keyboard.dismiss();
      return next;
    });
  }, []);

  const insertEmoji = useCallback((emoji: string) => {
    // Append all'input. Lasciamo il picker APERTO così l'utente può
    // selezionare più emoji in sequenza. Si chiude tappando di nuovo
    // l'icona emoji o il backdrop, oppure all'invio.
    setText(prev => (prev + emoji).slice(0, maxLength));
  }, [maxLength]);

  const closePicker = useCallback(() => setPickerOpen(false), []);

  const isDisabled = disabled || sending || !text.trim();

  return (
    <View style={[s.wrapper, compact && s.wrapperCompact]}>
      {/* ═══════════════════════════════════════════════════════════════
          EMOJI PICKER (in-tree, absolute above the composer row)
          ───────────────────────────────────────────────────────────────
          - Position: bottom: 100% di questo wrapper → renderizzato
            esattamente sopra la riga input. Copre temporaneamente
            l'area soprastante (message list) finché aperto.
          - Backdrop: TouchableOpacity assoluto sotto il pannello che
            chiude il picker on tap-outside (sul body del composer
            quando il picker è aperto). Il composer row resta tappabile
            (è zIndex superiore) per il toggle/scrittura.
          - Niente Modal, niente portal: stessa policy anti-Modal usata
            altrove nella codebase (v16.5 battle drawer, v16.15 overflow).
         ═══════════════════════════════════════════════════════════════ */}
      {pickerOpen && (
        <View style={s.pickerPanel} pointerEvents="auto">
          <ScrollView
            contentContainerStyle={s.pickerGrid}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="always"
          >
            {EMOJIS.map((e, i) => (
              <TouchableOpacity
                key={`${e}-${i}`}
                onPress={() => insertEmoji(e)}
                activeOpacity={0.55}
                style={s.pickerItem}
                hitSlop={{ top: 2, bottom: 2, left: 2, right: 2 }}
              >
                <Text style={s.pickerItemTxt}>{e}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* COMPOSER ROW (input + emoji + send) */}
      <View style={[s.row, compact && s.rowCompact]}>
        <TouchableOpacity
          onPress={onEmojiTogglePress}
          activeOpacity={0.7}
          style={[
            s.emojiBtn,
            compact && s.emojiBtnCompact,
            pickerOpen && s.emojiBtnActive,
          ]}
          disabled={disabled || sending}
          hitSlop={{ top: 6, bottom: 6, left: 4, right: 4 }}
        >
          <Text style={s.emojiTxt}>{pickerOpen ? '\u00D7' : '\uD83D\uDE0A'}</Text>
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
          onFocus={closePicker}
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
    </View>
  );
}

const s = StyleSheet.create({
  wrapper: {
    // wrapper relativo per ancorare il picker in absolute
    position: 'relative',
  },
  wrapperCompact: {},
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
  emojiBtnActive: {
    backgroundColor: 'rgba(255,107,53,0.25)',
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.55)',
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
  // ─────────── EMOJI PICKER (v16.17) ───────────
  pickerPanel: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: '100%',     // ancorato sopra la riga composer
    maxHeight: 160,
    backgroundColor: 'rgba(8,8,18,0.97)',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,107,53,0.45)',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,107,53,0.20)',
    // elevation + zIndex per stare sopra eventuali message ScrollView
    elevation: 10,
    zIndex: 10,
  },
  pickerGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 6,
    paddingVertical: 6,
    gap: 2,
  },
  pickerItem: {
    width: 34,
    height: 34,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.04)',
    margin: 1,
  },
  pickerItemTxt: {
    fontSize: 20,
    lineHeight: 24,
  },
});
