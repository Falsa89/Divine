import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const AURA_COLORS: Record<string,string> = { flame:'#ff4444', ice:'#44aaff', thunder:'#ffd700', shadow:'#9944ff', divine:'#ffd700', celestial:'#ffffff' };
const FRAME_COLORS: Record<string,string> = { bronze:'#cd7f32', silver:'#c0c0c0', gold:'#ffd700', diamond:'#44ddff', legendary:'#ff4444', divine:'#ffd700' };

export default function PlazaScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const [players, setPlayers] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [chatMsg, setChatMsg] = useState('');
  const [sending, setSending] = useState(false);
  const chatRef = useRef<ScrollView>(null);

  useEffect(() => { load(); const iv = setInterval(loadChat, 8000); return () => clearInterval(iv); }, []);

  const load = async () => { try { const [p, c] = await Promise.all([apiCall('/api/plaza'), apiCall('/api/plaza/chat')]); setPlayers(p.players||[]); setMessages(c||[]); } catch(e){} finally { setLoading(false); } };
  const loadChat = async () => { try { const c = await apiCall('/api/plaza/chat'); setMessages(c||[]); } catch(e){} };

  const sendMsg = async () => {
    if (!chatMsg.trim()) return;
    setSending(true);
    try { await apiCall('/api/plaza/chat', { method:'POST', body: JSON.stringify({message:chatMsg}) }); setChatMsg(''); await loadChat(); } catch(e){} finally { setSending(false); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B']} style={{flex: 1, alignItems: 'center', justifyContent: 'center'}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><KeyboardAvoidingView style={{flex: 1}} behavior={Platform.OS==='ios'?'padding':'height'}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>\u2190</Text></TouchableOpacity>
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
            <TextInput style={s.input} placeholder="Scrivi..." placeholderTextColor="#555" value={chatMsg} onChangeText={setChatMsg} onSubmitEditing={sendMsg} />
            <TouchableOpacity style={[s.sendBtn, sending&&{opacity:0.5}]} onPress={sendMsg} disabled={sending}>
              <Text style={s.sendTxt}>Invia</Text>
            </TouchableOpacity>
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
  chat:{width:200,backgroundColor:'rgba(255,255,255,0.03)',borderRadius:12,borderWidth:1,borderColor:'rgba(255,255,255,0.08)',padding:8},
  chatTitle:{color:'#fff',fontSize:12,fontWeight:'700',marginBottom:4},
  chatScroll:{flex:1},
  msg:{flexDirection:'row',gap:4,marginBottom:3,flexWrap:'wrap'},
  msgUser:{color:'#ff6b35',fontSize:10,fontWeight:'700'},
  msgText:{color:'#ccc',fontSize:10,flex:1},
  emptyChat:{color:'#555',fontSize:10,textAlign:'center',marginTop:20},
  chatInput:{flexDirection:'row',gap:4,marginTop:4},
  input:{flex:1,backgroundColor:'rgba(255,255,255,0.06)',borderRadius:6,padding:6,color:'#fff',fontSize:10,borderWidth:1,borderColor:'rgba(255,255,255,0.1)'},
  sendBtn:{paddingHorizontal:10,paddingVertical:6,backgroundColor:'#ff6b35',borderRadius:6,justifyContent:'center'},
  sendTxt:{color:'#fff',fontSize:9,fontWeight:'700'},
});
