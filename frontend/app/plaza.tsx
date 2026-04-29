import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import ChatComposer from '../components/chat/ChatComposer';

const AURA_COLORS: Record<string,string> = { flame:'#ff4444', ice:'#44aaff', thunder:'#ffd700', shadow:'#9944ff', divine:'#ffd700', celestial:'#ffffff' };
const FRAME_COLORS: Record<string,string> = { bronze:'#cd7f32', silver:'#c0c0c0', gold:'#ffd700', diamond:'#44ddff', legendary:'#ff4444', divine:'#ffd700' };

export default function PlazaScreen() {
  const router = useRouter();
  // v16.14 — RIMOSSO `useAuth()` non utilizzato (era importato ma `user`
  // non veniva mai letto). In edge-case di navigazione rapida verso /plaza
  // mentre l'AuthContext non è ancora pronto, l'hook può throw e provocare
  // un crash navtive su Hermes. Safe removal: zero impatto funzionale.
  const [players, setPlayers] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const chatRef = useRef<ScrollView>(null);

  useEffect(() => { load(); const iv = setInterval(loadChat, 8000); return () => clearInterval(iv); }, []);

  const load = async () => { try { const [p, c] = await Promise.all([apiCall('/api/plaza'), apiCall('/api/plaza/chat')]); setPlayers(p.players||[]); setMessages(c||[]); } catch(e){} finally { setLoading(false); } };
  const loadChat = async () => { try { const c = await apiCall('/api/plaza/chat'); setMessages(c||[]); } catch(e){} };

  const sendMsg = async (msg: string) => {
    await apiCall('/api/plaza/chat', { method: 'POST', body: JSON.stringify({ message: msg }) });
    await loadChat();
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={{flex: 1, alignItems: 'center', justifyContent: 'center'}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><KeyboardAvoidingView style={{flex: 1}} behavior={Platform.OS==='ios'?'padding':'height'}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>{'\u2190'}</Text></TouchableOpacity>
        <Text style={s.title}>PIAZZA COMUNITARIA</Text>
        <Text style={s.online}>{players.length} presenti</Text>
      </View>
      <View style={s.body}>
        {/* Player Map */}
        <View style={s.map}>
          {players.map((p:any) => {
            const frameCol = FRAME_COLORS[p.frame] || '#888';
            const auraCol = AURA_COLORS[p.aura] || 'transparent';
            return (
              <View key={p.id} style={[s.player, {left:p.x % 500, top: p.y % 280}]}>
                {p.aura && <View style={[s.aura, {backgroundColor:auraCol, shadowColor:auraCol}]} />}
                <View style={[s.avatar, {borderColor:frameCol}]}>
                  <Text style={[s.avatarTxt, p.is_npc && {color:'#ffd700'}]}>{p.username?.[0]?.toUpperCase()}</Text>
                </View>
                <Text style={[s.playerName, p.is_you && {color:'#ff6b35'}, p.is_npc && {color:'#ffd700'}]} numberOfLines={1}>{p.username}</Text>
                <Text style={s.playerTitle}>{p.title}</Text>
              </View>
            );
          })}
        </View>
        {/* Chat */}
        <View style={s.chat}>
          <Text style={s.chatTitle}>Chat</Text>
          <ScrollView style={s.chatScroll} ref={chatRef} onContentSizeChange={() => chatRef.current?.scrollToEnd()}>
            {messages.map((m:any) => (
              <View key={m.id || m._id} style={s.msg}>
                <Text style={s.msgUser}>{m.username}:</Text>
                <Text style={s.msgText}>{m.message}</Text>
              </View>
            ))}
            {messages.length === 0 && <Text style={s.emptyChat}>Nessun messaggio ancora</Text>}
          </ScrollView>
          <View style={s.chatInput}>
            {/* v16.16 — PLAZA COMPOSER USABILITY FIX
                Rimosso `compact`: la modalità compact (input 30h / font 12 /
                emoji 30 / send 30h) è pensata per il drawer battle ristretto
                e per il pannello home in basso, dove lo spazio verticale è
                forzato. In Plaza c'è una sidebar dedicata: usiamo il preset
                NON-compact (input 36h / font 13 / emoji 36 / send 36h+)
                molto più comodo da tappare e leggere su mobile reale. */}
            <ChatComposer
              onSend={sendMsg}
              placeholder={'Scrivi alla piazza\u2026'}
              maxLength={200}
            />
          </View>
        </View>
      </View>
    </KeyboardAvoidingView></LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(255,107,53,0.2)'},
  back:{color:'#ff6b35',fontSize:20,fontWeight:'700'},
  title:{color:'#fff',fontSize:16,fontWeight:'800',letterSpacing:2,flex:1},
  online:{color:'#44cc44',fontSize:11},
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
