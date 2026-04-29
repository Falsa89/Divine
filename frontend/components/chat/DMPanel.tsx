/**
 * DMPanel — integrated DM widget for the multi-channel chat selector (v16.20)
 * ─────────────────────────────────────────────────────────────────────────────
 * Quando la ChannelSelector è su 'dm', le surface host (Plaza/Home/Battle)
 * renderizzano questo componente al posto del message stream standard.
 *
 * Internal state:
 *   - inbox  → lista thread cliccabili (default)
 *   - thread → conversazione attiva con composer
 *
 * Riusa:
 *   - useDM hook (Phase 2)
 *   - ChatComposer (con emoji picker)
 *
 * Props:
 *   - compact: target Home/Battle (UI ridotta) vs Plaza (UI standard)
 *   - initialPeerId: shortcut → apre/crea thread con peer specifico
 *   - initialThreadId: shortcut → apre thread esistente
 *
 * Used by:
 *   - app/plaza.tsx        (chat sidebar, non-compact)
 *   - app/(tabs)/home.tsx  (HomeChatNotifPanel, compact)
 *   - app/combat.tsx       (battle drawer chat tab, compact)
 *   - app/dm.tsx           (fullscreen route, non-compact)
 */
import React, { useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import ChatComposer from './ChatComposer';
import { useDM, DMThread } from '../../hooks/useDM';
import { useAuth } from '../../context/AuthContext';
import { COLORS } from '../../constants/theme';

export interface DMPanelProps {
  compact?: boolean;
  initialPeerId?: string;
  initialThreadId?: string;
}

export default function DMPanel({ compact = false, initialPeerId, initialThreadId }: DMPanelProps) {
  const { user } = useAuth();
  const dm = useDM({ pollingMs: 12000 });
  const scrollRef = useRef<ScrollView>(null);

  // Apertura iniziale via prop (shortcut esterni: avatar/header/menu).
  useEffect(() => {
    (async () => {
      if (initialThreadId) {
        dm.setActiveThreadId(initialThreadId);
      } else if (initialPeerId) {
        await dm.openWithUser(initialPeerId);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialPeerId, initialThreadId]);

  // Auto-scroll al thread aperto.
  useEffect(() => {
    if (!dm.activeThreadId) return;
    const t = setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 80);
    return () => clearTimeout(t);
  }, [dm.activeMessages.length, dm.activeThreadId]);

  const inThread = !!dm.activeThreadId;
  const activeThread = dm.threads.find(t => t.id === dm.activeThreadId);

  // ═══════════════════════════════════════════════════════════════
  // INBOX VIEW — lista thread cliccabili
  // ═══════════════════════════════════════════════════════════════
  if (!inThread) {
    return (
      <View style={s.container}>
        {dm.loadingThreads && dm.threads.length === 0 ? (
          <View style={s.emptyWrap}><ActivityIndicator color="#ff6b35" /></View>
        ) : dm.threads.length === 0 ? (
          <View style={s.emptyWrap}>
            <Text style={[s.emptyIcon, compact && { fontSize: 26 }]}>{'\uD83D\uDCEC'}</Text>
            <Text style={[s.emptyTitle, compact && { fontSize: 11 }]}>Nessuna conversazione</Text>
            <Text style={[s.emptySub, compact && { fontSize: 9.5, lineHeight: 13 }]}>
              {compact
                ? 'Apri una chat tappando un giocatore in Piazza.'
                : 'Apri una chat privata tappando il nome o l\'avatar di un giocatore in piazza o in chat.'}
            </Text>
          </View>
        ) : (
          <ScrollView contentContainerStyle={{ paddingVertical: compact ? 4 : 6, gap: compact ? 3 : 5 }}>
            {dm.threads.map(t => (
              <ThreadRow
                key={t.id}
                thread={t}
                isMine={t.last_sender_id === user?.id}
                compact={compact}
                onPress={() => dm.setActiveThreadId(t.id)}
              />
            ))}
          </ScrollView>
        )}
      </View>
    );
  }

  // ═══════════════════════════════════════════════════════════════
  // THREAD VIEW — bubble messages + ChatComposer
  // ═══════════════════════════════════════════════════════════════
  return (
    <View style={s.container}>
      <View style={[s.threadHeader, compact && s.threadHeaderCompact]}>
        <TouchableOpacity
          onPress={() => dm.setActiveThreadId(null)}
          activeOpacity={0.7}
          hitSlop={{ top: 6, bottom: 6, left: 6, right: 6 }}
          style={s.backBtn}
        >
          <Text style={[s.backTxt, compact && { fontSize: 13 }]}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={[s.threadName, compact && { fontSize: 11 }]} numberOfLines={1}>
          {activeThread?.peer_username || 'Conversazione'}
        </Text>
      </View>
      <ScrollView
        ref={scrollRef}
        style={{ flex: 1 }}
        contentContainerStyle={{ paddingVertical: 6, paddingHorizontal: 4, gap: compact ? 3 : 5 }}
        onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: false })}
      >
        {dm.loadingMessages && dm.activeMessages.length === 0 ? (
          <ActivityIndicator color="#ff6b35" />
        ) : dm.activeMessages.length === 0 ? (
          <Text style={[s.threadEmpty, compact && { fontSize: 10, marginTop: 16 }]}>
            Inizia la conversazione qui sotto.
          </Text>
        ) : (
          dm.activeMessages.map((m, i) => {
            const mine = m.sender_id === user?.id;
            return (
              <View
                key={m.id || i}
                style={[
                  s.bubble,
                  compact && s.bubbleCompact,
                  mine ? s.bubbleMine : s.bubbleTheirs,
                ]}
              >
                <Text style={[s.bubbleTxt, compact && { fontSize: 11, lineHeight: 14 }]}>
                  {m.message}
                </Text>
              </View>
            );
          })
        )}
      </ScrollView>
      <ChatComposer
        onSend={dm.sendMessage}
        placeholder={`Scrivi a ${activeThread?.peer_username || 'utente'}\u2026`}
        maxLength={500}
        compact={compact}
      />
    </View>
  );
}

// ─────────────────────────────────────────────────────────────────
// Sub-component — ThreadRow
// ─────────────────────────────────────────────────────────────────
function ThreadRow({
  thread, isMine, compact, onPress,
}: { thread: DMThread; isMine: boolean; compact: boolean; onPress: () => void }) {
  return (
    <TouchableOpacity
      style={[s.threadRow, compact && s.threadRowCompact]}
      activeOpacity={0.78}
      onPress={onPress}
    >
      <View style={[s.threadAvatar, compact && s.threadAvatarCompact]}>
        <Text style={[s.threadAvatarTxt, compact && { fontSize: 12 }]}>
          {(thread.peer_username || '?').slice(0, 1).toUpperCase()}
        </Text>
      </View>
      <View style={{ flex: 1, minWidth: 0 }}>
        <Text style={[s.threadName, compact && { fontSize: 11 }]} numberOfLines={1}>
          {thread.peer_username}
        </Text>
        <Text style={[s.threadLast, compact && { fontSize: 9.5 }]} numberOfLines={1}>
          {isMine && thread.last_message ? 'Tu: ' : ''}
          {thread.last_message || 'Nessun messaggio'}
        </Text>
      </View>
      {thread.unread > 0 && (
        <View style={[s.unreadBadge, compact && s.unreadBadgeCompact]}>
          <Text style={[s.unreadTxt, compact && { fontSize: 9 }]}>
            {thread.unread > 99 ? '99+' : thread.unread}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const s = StyleSheet.create({
  container: { flex: 1 },

  emptyWrap: {
    flex: 1, alignItems: 'center', justifyContent: 'center',
    paddingHorizontal: 20, paddingVertical: 16,
  },
  emptyIcon: { fontSize: 36, marginBottom: 8 },
  emptyTitle: { color: '#fff', fontSize: 13, fontWeight: '800', marginBottom: 5 },
  emptySub: { color: 'rgba(255,255,255,0.5)', fontSize: 11, textAlign: 'center', lineHeight: 15 },

  threadRow: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingHorizontal: 9, paddingVertical: 8,
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    marginHorizontal: 2,
  },
  threadRowCompact: {
    paddingHorizontal: 6, paddingVertical: 5,
    gap: 6,
    borderRadius: 6,
  },
  threadAvatar: {
    width: 30, height: 30, borderRadius: 15,
    backgroundColor: 'rgba(255,107,53,0.22)',
    borderWidth: 1, borderColor: 'rgba(255,107,53,0.55)',
    alignItems: 'center', justifyContent: 'center',
  },
  threadAvatarCompact: {
    width: 22, height: 22, borderRadius: 11,
  },
  threadAvatarTxt: { color: '#fff', fontWeight: '900', fontSize: 14 },

  threadName: { color: '#fff', fontSize: 12, fontWeight: '800' },
  threadLast: { color: 'rgba(255,255,255,0.55)', fontSize: 10, marginTop: 1 },

  unreadBadge: {
    minWidth: 20, height: 20, borderRadius: 10,
    paddingHorizontal: 5,
    backgroundColor: COLORS.accent,
    alignItems: 'center', justifyContent: 'center',
  },
  unreadBadgeCompact: { minWidth: 16, height: 16, borderRadius: 8, paddingHorizontal: 3 },
  unreadTxt: { color: '#fff', fontSize: 10, fontWeight: '900' },

  threadHeader: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    paddingHorizontal: 4, paddingVertical: 6,
    borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.07)',
  },
  threadHeaderCompact: { paddingVertical: 4 },
  backBtn: {
    width: 28, height: 24,
    alignItems: 'center', justifyContent: 'center',
    borderRadius: 6,
    backgroundColor: 'rgba(255,107,53,0.18)',
  },
  backTxt: { color: '#FFD7A8', fontSize: 15, fontWeight: '900' },

  threadEmpty: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 11,
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 24,
  },

  bubble: {
    maxWidth: '82%',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 10,
  },
  bubbleCompact: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  bubbleMine: {
    alignSelf: 'flex-end',
    backgroundColor: 'rgba(255,107,53,0.36)',
    borderTopRightRadius: 3,
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.5)',
  },
  bubbleTheirs: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderTopLeftRadius: 3,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.10)',
  },
  bubbleTxt: { color: '#fff', fontSize: 12, lineHeight: 16 },
});
