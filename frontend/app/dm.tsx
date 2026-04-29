/**
 * /dm — Direct Messages route (Phase 2 v16.19)
 * ────────────────────────────────────────────────────────────
 * Schermata combinata Inbox + Thread view per Direct Messaging.
 * Modalità toggleable in base allo state interno:
 *   - 'inbox' → lista thread cliccabili
 *   - 'thread' → conversazione attiva
 *
 * Entry points che possono navigare qui:
 *   - router.push('/dm')                       → inbox
 *   - router.push('/dm?peer=<userId>')         → apre/crea thread con peer
 *   - router.push('/dm?thread=<threadId>')     → apre thread esistente
 */
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { COLORS } from '../constants/theme';
import { useDM } from '../hooks/useDM';
import { useAuth } from '../context/AuthContext';
import ChatComposer from '../components/chat/ChatComposer';

export default function DMScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ peer?: string; thread?: string }>();
  const { user } = useAuth();
  const dm = useDM({ pollingMs: 12000 });
  const scrollRef = useRef<ScrollView>(null);

  const [view, setView] = useState<'inbox' | 'thread'>('inbox');
  const [openingPeer, setOpeningPeer] = useState(false);

  // Apri thread se passato via query param.
  useEffect(() => {
    (async () => {
      if (params?.thread && typeof params.thread === 'string') {
        dm.setActiveThreadId(params.thread);
        setView('thread');
      } else if (params?.peer && typeof params.peer === 'string') {
        setOpeningPeer(true);
        const id = await dm.openWithUser(params.peer);
        setOpeningPeer(false);
        if (id) setView('thread');
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params?.peer, params?.thread]);

  // Auto-scroll su nuovi messaggi nel thread attivo.
  useEffect(() => {
    if (view !== 'thread') return;
    const t = setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 80);
    return () => clearTimeout(t);
  }, [dm.activeMessages.length, view]);

  const activeThread = dm.threads.find(t => t.id === dm.activeThreadId);

  const goBackToInbox = () => {
    setView('inbox');
    dm.setActiveThreadId(null);
    dm.refreshThreads();
  };

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={s.screen}>
      <View style={s.header}>
        <TouchableOpacity
          onPress={() => view === 'thread' ? goBackToInbox() : router.back()}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        >
          <Text style={s.back}>{'\u2190'}</Text>
        </TouchableOpacity>
        <Text style={s.title} numberOfLines={1}>
          {view === 'thread'
            ? (activeThread?.peer_username || 'Conversazione')
            : 'Messaggi privati'}
        </Text>
        <View style={{ width: 26 }} />
      </View>

      {view === 'inbox' ? (
        <View style={s.body}>
          {openingPeer && (
            <View style={s.openingBanner}>
              <ActivityIndicator size="small" color="#ff6b35" />
              <Text style={s.openingTxt}>Apertura conversazione…</Text>
            </View>
          )}
          {dm.loadingThreads && dm.threads.length === 0 ? (
            <View style={s.emptyWrap}><ActivityIndicator color="#ff6b35" /></View>
          ) : dm.threads.length === 0 ? (
            <View style={s.emptyWrap}>
              <Text style={s.emptyIcon}>{'\uD83D\uDCEC'}</Text>
              <Text style={s.emptyTitle}>Nessuna conversazione</Text>
              <Text style={s.emptySub}>
                Apri una chat privata tappando il nome o l'avatar di un giocatore
                in piazza o in chat.
              </Text>
            </View>
          ) : (
            <ScrollView contentContainerStyle={{ paddingBottom: 12 }}>
              {dm.threads.map(t => (
                <TouchableOpacity
                  key={t.id}
                  style={s.threadRow}
                  activeOpacity={0.78}
                  onPress={() => { dm.setActiveThreadId(t.id); setView('thread'); }}
                >
                  <View style={s.threadAvatar}>
                    <Text style={s.threadAvatarTxt}>
                      {(t.peer_username || '?').slice(0, 1).toUpperCase()}
                    </Text>
                  </View>
                  <View style={s.threadBody}>
                    <Text style={s.threadName} numberOfLines={1}>{t.peer_username}</Text>
                    <Text style={s.threadLast} numberOfLines={1}>
                      {t.last_sender_id === user?.id && t.last_message ? 'Tu: ' : ''}
                      {t.last_message || 'Nessun messaggio'}
                    </Text>
                  </View>
                  {t.unread > 0 && (
                    <View style={s.unreadBadge}>
                      <Text style={s.unreadTxt}>{t.unread > 99 ? '99+' : t.unread}</Text>
                    </View>
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}
        </View>
      ) : (
        <View style={s.body}>
          <ScrollView
            ref={scrollRef}
            style={{ flex: 1 }}
            contentContainerStyle={s.threadScroll}
            onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: false })}
          >
            {dm.loadingMessages && dm.activeMessages.length === 0 ? (
              <View style={s.emptyWrap}><ActivityIndicator color="#ff6b35" /></View>
            ) : dm.activeMessages.length === 0 ? (
              <Text style={s.threadEmpty}>
                Inizia la conversazione qui sotto.
              </Text>
            ) : (
              dm.activeMessages.map((m, i) => {
                const mine = m.sender_id === user?.id;
                return (
                  <View key={m.id || i} style={[s.bubble, mine ? s.bubbleMine : s.bubbleTheirs]}>
                    {!mine && <Text style={s.bubbleAuthor}>{m.sender_username}</Text>}
                    <Text style={s.bubbleTxt}>{m.message}</Text>
                  </View>
                );
              })
            )}
          </ScrollView>
          <ChatComposer
            onSend={dm.sendMessage}
            placeholder={`Scrivi a ${activeThread?.peer_username || 'utente'}\u2026`}
            maxLength={500}
          />
        </View>
      )}
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  screen: { flex: 1 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingTop: 14,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.08)',
    gap: 12,
  },
  back: { color: '#ff6b35', fontSize: 22, fontWeight: '900' },
  title: { color: '#fff', fontSize: 16, fontWeight: '900', letterSpacing: 0.5, flex: 1 },
  body: { flex: 1, padding: 10 },

  emptyWrap: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 30 },
  emptyIcon: { fontSize: 42, marginBottom: 10 },
  emptyTitle: { color: '#fff', fontSize: 15, fontWeight: '800', marginBottom: 6 },
  emptySub: { color: 'rgba(255,255,255,0.5)', fontSize: 12, textAlign: 'center', lineHeight: 17 },

  openingBanner: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingHorizontal: 12, paddingVertical: 8,
    backgroundColor: 'rgba(255,107,53,0.14)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.32)',
    marginBottom: 8,
  },
  openingTxt: { color: '#fff', fontSize: 12, fontWeight: '700' },

  threadRow: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    paddingHorizontal: 10, paddingVertical: 10,
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    marginBottom: 6,
  },
  threadAvatar: {
    width: 36, height: 36, borderRadius: 18,
    backgroundColor: 'rgba(255,107,53,0.22)',
    borderWidth: 1, borderColor: 'rgba(255,107,53,0.55)',
    alignItems: 'center', justifyContent: 'center',
  },
  threadAvatarTxt: { color: '#fff', fontWeight: '900', fontSize: 16 },
  threadBody: { flex: 1 },
  threadName: { color: '#fff', fontSize: 13, fontWeight: '800', marginBottom: 2 },
  threadLast: { color: 'rgba(255,255,255,0.55)', fontSize: 11 },
  unreadBadge: {
    minWidth: 22, height: 22, borderRadius: 11,
    paddingHorizontal: 6,
    backgroundColor: COLORS.accent,
    alignItems: 'center', justifyContent: 'center',
  },
  unreadTxt: { color: '#fff', fontSize: 11, fontWeight: '900' },

  threadScroll: { paddingVertical: 6, gap: 6, paddingHorizontal: 4 },
  threadEmpty: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 12,
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 30,
  },
  bubble: {
    maxWidth: '78%',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 12,
    marginBottom: 4,
  },
  bubbleMine: {
    alignSelf: 'flex-end',
    backgroundColor: 'rgba(255,107,53,0.36)',
    borderTopRightRadius: 4,
    borderWidth: 1,
    borderColor: 'rgba(255,107,53,0.5)',
  },
  bubbleTheirs: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderTopLeftRadius: 4,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.10)',
  },
  bubbleAuthor: {
    color: '#FFD7A8',
    fontSize: 10,
    fontWeight: '900',
    marginBottom: 3,
    letterSpacing: 0.5,
  },
  bubbleTxt: { color: '#fff', fontSize: 13, lineHeight: 17 },
});
