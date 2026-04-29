import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import ChatComposer from '../components/chat/ChatComposer';
import ChannelSelector from '../components/chat/ChannelSelector';
import UserActionSheet from '../components/chat/UserActionSheet';
import { useChatChannel } from '../hooks/useChatChannel';
import { useAuth } from '../context/AuthContext';

const AURA_COLORS: Record<string,string> = { flame:'#ff4444', ice:'#44aaff', thunder:'#ffd700', shadow:'#9944ff', divine:'#ffd700', celestial:'#ffffff' };
const FRAME_COLORS: Record<string,string> = { bronze:'#cd7f32', silver:'#c0c0c0', gold:'#ffd700', diamond:'#44ddff', legendary:'#ff4444', divine:'#ffd700' };

export default function PlazaScreen() {
  const router = useRouter();
  // v16.14: rimosso useAuth() non utilizzato.
  // v16.18 Phase 1: chat ora multi-canale via useChatChannel hook condiviso.
  // v16.19 Phase 2: useAuth riusato per filtrare self-DM e identificare own messages.
  const { user } = useAuth();
  const [players, setPlayers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const chatRef = useRef<ScrollView>(null);

  const ch = useChatChannel({ pollingMs: 8000 });

  // v16.19 Phase 2 — UserActionSheet entry point per DM
  const [actionTarget, setActionTarget] = useState<any | null>(null);
  const openDMWithUser = (peerId: string) => {
    router.push(`/dm?peer=${encodeURIComponent(peerId)}` as any);
  };

  useEffect(() => {
    (async () => {
      try {
        const p = await apiCall('/api/plaza');
        setPlayers(p.players || []);
      } catch {}
      finally { setLoading(false); }
    })();
  }, []);

  // Auto-scroll quando arrivano nuovi messaggi sul canale attivo.
  useEffect(() => {
    const t = setTimeout(() => chatRef.current?.scrollToEnd({ animated: true }), 80);
    return () => clearTimeout(t);
  }, [ch.messages.length, ch.active]);

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={{flex: 1, alignItems: 'center', justifyContent: 'center'}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><KeyboardAvoidingView style={{flex: 1}} behavior={Platform.OS==='ios'?'padding':'height'}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>{'\u2190'}</Text></TouchableOpacity>
        <Text style={s.title}>PIAZZA COMUNITARIA</Text>
        {/* v16.19 — DM inbox quick-access */}
        <TouchableOpacity
          onPress={() => router.push('/dm' as any)}
          style={s.dmBtn}
          hitSlop={{ top: 6, bottom: 6, left: 6, right: 6 }}
          activeOpacity={0.7}
        >
          <Text style={s.dmIcon}>{'\uD83D\uDCEC'}</Text>
          <Text style={s.dmLabel}>DM</Text>
        </TouchableOpacity>
        <Text style={s.online}>{players.length} presenti</Text>
      </View>
      <View style={s.body}>
        {/* Player Map */}
        <View style={s.map}>
          {players.map((p:any) => {
            const frameCol = FRAME_COLORS[p.frame] || '#888';
            const auraCol = AURA_COLORS[p.aura] || 'transparent';
            return (
              <TouchableOpacity
                key={p.id}
                style={[s.player, {left:p.x % 500, top: p.y % 280}]}
                activeOpacity={0.78}
                disabled={!!p.is_you}
                onPress={() => !p.is_you && setActionTarget(p)}
              >
                {p.aura && <View style={[s.aura, {backgroundColor:auraCol, shadowColor:auraCol}]} />}
                <View style={[s.avatar, {borderColor:frameCol}]}>
                  <Text style={[s.avatarTxt, p.is_npc && {color:'#ffd700'}]}>{p.username?.[0]?.toUpperCase()}</Text>
                </View>
                <Text style={[s.playerName, p.is_you && {color:'#ff6b35'}, p.is_npc && {color:'#ffd700'}]} numberOfLines={1}>{p.username}</Text>
                <Text style={s.playerTitle}>{p.title}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
        {/* Chat (v16.18 — multi-channel: selector + active channel messages) */}
        <View style={s.chat}>
          <ChannelSelector
            channels={ch.channels}
            active={ch.active}
            onChange={ch.setActive}
            compact
          />
          <ScrollView style={s.chatScroll} ref={chatRef} onContentSizeChange={() => chatRef.current?.scrollToEnd()}>
            {ch.messages.map((m:any) => (
              <View key={m.id || m._id} style={s.msg}>
                {/* v16.19 — tap su username → UserActionSheet (entry DM) */}
                <TouchableOpacity
                  onPress={() => {
                    if (!m.user_id || m.user_id === user?.id) return;
                    setActionTarget({
                      id: m.user_id,
                      username: m.username || 'utente',
                      level: undefined,
                      title: undefined,
                      is_npc: false,
                      is_you: false,
                    });
                  }}
                  hitSlop={{ top: 4, bottom: 4, left: 2, right: 2 }}
                  activeOpacity={0.65}
                  disabled={m.user_id === user?.id}
                >
                  <Text style={s.msgUser}>{m.username}:</Text>
                </TouchableOpacity>
                <Text style={s.msgText}>{m.message}</Text>
              </View>
            ))}
            {ch.messages.length === 0 && (
              <Text style={s.emptyChat}>
                {!ch.isAvailable
                  ? `\uD83D\uDD12 ${ch.activeMeta?.lockedReason || 'Canale non disponibile'}`
                  : ch.isReadonly
                    ? 'Nessuna notifica di sistema.'
                    : 'Nessun messaggio ancora'}
              </Text>
            )}
          </ScrollView>
          <View style={s.chatInput}>
            {/* v16.18 — composer disabilitato su canali read-only o lock. */}
            <ChatComposer
              onSend={ch.send}
              placeholder={
                !ch.isAvailable ? 'Canale bloccato' :
                ch.isReadonly   ? 'Sola lettura'    :
                                  'Scrivi alla piazza\u2026'
              }
              maxLength={200}
              disabled={!ch.isAvailable || ch.isReadonly}
            />
          </View>
        </View>
      </View>
      {/* v16.19 Phase 2 — User Action Sheet (entry point DM) */}
      <UserActionSheet
        visible={!!actionTarget}
        username={actionTarget?.username || ''}
        subtitle={actionTarget ? `Lv ${actionTarget.level || '?'} \u00B7 ${actionTarget.title || 'Avventuriero'}` : undefined}
        isNpc={!!actionTarget?.is_npc}
        onClose={() => setActionTarget(null)}
        onPrivateChat={
          actionTarget && !actionTarget.is_npc && !actionTarget.is_you
            ? () => openDMWithUser(actionTarget.id)
            : undefined
        }
      />
    </KeyboardAvoidingView></LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(255,107,53,0.2)'},
  back:{color:'#ff6b35',fontSize:20,fontWeight:'700'},
  title:{color:'#fff',fontSize:16,fontWeight:'800',letterSpacing:2,flex:1},
  online:{color:'#44cc44',fontSize:11},
  // v16.19 — DM quick-access button in header
  dmBtn:{flexDirection:'row',alignItems:'center',gap:4,paddingHorizontal:8,paddingVertical:5,backgroundColor:'rgba(255,107,53,0.16)',borderRadius:6,borderWidth:1,borderColor:'rgba(255,107,53,0.45)'},
  dmIcon:{fontSize:13},
  dmLabel:{color:'#fff',fontSize:10,fontWeight:'900',letterSpacing:0.5},
  body:{flex:1,flexDirection:'row',padding:8,gap:8},
  // Map
  map:{flex:1,backgroundColor:'rgba(255,255,255,0.02)',borderRadius:12,borderWidth:1,borderColor:'rgba(255,107,53,0.1)',overflow:'hidden',position:'relative'},
  player:{position:'absolute'},
  aura:{position:'absolute',width:36,height:36,borderRadius:18,top:-4,left:-4,opacity:0.3,shadowOffset:{width:0,height:0},shadowOpacity:0.8,shadowRadius:8},
  avatar:{width:28,height:28,borderRadius:14,backgroundColor:'rgba(255,255,255,0.1)',borderWidth:2,alignItems:'center',justifyContent:'center'},
  avatarTxt:{color:'#fff',fontSize:11,fontWeight:'900'},
  playerName:{color:'#ccc',fontSize:7,fontWeight:'600',textAlign:'center',maxWidth:60},
  playerTitle:{color:'#888',fontSize:6,textAlign:'center'},
  // Chat
  // v16.16 — width 200 → 260: il composer non-compact (emoji 36 + gap +
  // input flex:1 + gap + send 60) ha bisogno di ~110px di chrome fissa.
  // A 200 il TextInput finiva strozzato a ~70px, scomodissimo da tappare.
  // A 260 il TextInput respira ~140px → comodo per scrivere messaggi reali.
  chat:{width:260,backgroundColor:'rgba(255,255,255,0.03)',borderRadius:12,borderWidth:1,borderColor:'rgba(255,255,255,0.08)',padding:10},
  chatTitle:{color:'#fff',fontSize:13,fontWeight:'800',marginBottom:6,letterSpacing:0.5},
  chatScroll:{flex:1},
  // v16.16 — bumpate font da 10 → 12 (msg) per readability mobile reale.
  msg:{flexDirection:'row',gap:5,marginBottom:5,flexWrap:'wrap'},
  msgUser:{color:'#ff6b35',fontSize:12,fontWeight:'800'},
  msgText:{color:'#e2e2e6',fontSize:12,flex:1,lineHeight:16},
  emptyChat:{color:'#666',fontSize:11,textAlign:'center',marginTop:24,fontStyle:'italic'},
  // v16.16 — chatInput: aumentato gap top per separare visualmente la
  // ScrollView dal composer, evita il "tutto attaccato" pre-fix.
  chatInput:{marginTop:8},
  input:{flex:1,backgroundColor:'rgba(255,255,255,0.06)',borderRadius:6,padding:6,color:'#fff',fontSize:10,borderWidth:1,borderColor:'rgba(255,255,255,0.1)'},
  sendBtn:{paddingHorizontal:10,paddingVertical:6,backgroundColor:'#ff6b35',borderRadius:6,justifyContent:'center'},
  sendTxt:{color:'#fff',fontSize:9,fontWeight:'700'},
});
