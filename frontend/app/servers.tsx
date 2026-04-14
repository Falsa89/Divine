import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';

export default function ServerSelectScreen() {
  const router = useRouter();
  const [servers, setServers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selecting, setSelecting] = useState('');

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/servers'); setServers(d); } catch(e){} finally { setLoading(false); } };

  const select = async (id: string) => {
    setSelecting(id);
    try {
      await apiCall('/api/server/select', { method:'POST', body: JSON.stringify({server_id:id}) });
      Alert.alert('Server Selezionato!', 'Benvenuto!');
      router.back();
    } catch(e:any) { Alert.alert('Errore', e.message); } finally { setSelecting(''); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  const regions = [...new Set(servers.map(s => s.region))];

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>{"\u2190"}</Text></TouchableOpacity>
        <Text style={s.title}>SELEZIONE SERVER</Text>
      </View>
      <ScrollView contentContainerStyle={s.list}>
        {regions.map(region => (
          <View key={region}>
            <Text style={s.regionTitle}>{region === 'EU' ? '\uD83C\uDDEA\uD83C\uDDFA Europa' : region === 'ASIA' ? '\uD83C\uDDF0\uD83C\uDDF7 Asia' : '\uD83C\uDDFA\uD83C\uDDF8 America'}</Text>
            {servers.filter(s => s.region === region).map(srv => {
              const loadColor = srv.load_percent > 80 ? '#ff4444' : srv.load_percent > 50 ? '#ffaa00' : '#44cc44';
              return (
                <TouchableOpacity key={srv.id} style={[s.card, srv.status==='new'&&{borderColor:'#44cc44'}]} onPress={() => select(srv.id)} disabled={selecting===srv.id}>
                  <View style={s.cardLeft}>
                    <Text style={s.srvName}>{srv.name}</Text>
                    <Text style={s.srvPlayers}>{srv.players_online}/{srv.max_players} giocatori</Text>
                    {srv.status === 'new' && <Text style={s.newBadge}>NUOVO!</Text>}
                  </View>
                  <View style={s.cardRight}>
                    <View style={s.loadBarBg}><View style={[s.loadBarFill, {width:`${srv.load_percent}%`, backgroundColor:loadColor}]} /></View>
                    <Text style={[s.loadTxt, {color:loadColor}]}>{srv.load_percent}%</Text>
                    <View style={[s.statusDot, {backgroundColor: srv.status==='online'?'#44cc44':'#ffaa00'}]} />
                  </View>
                </TouchableOpacity>
              );
            })}
          </View>
        ))}
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(255,107,53,0.2)'},
  back:{color:'#ff6b35',fontSize:20,fontWeight:'700'},
  title:{color:'#fff',fontSize:16,fontWeight:'800',letterSpacing:2},
  list:{padding:12,gap:4},
  regionTitle:{color:'#ffd700',fontSize:13,fontWeight:'800',marginTop:8,marginBottom:4,letterSpacing:1},
  card:{flexDirection:'row',alignItems:'center',justifyContent:'space-between',padding:12,borderRadius:10,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:1,borderColor:'rgba(255,255,255,0.08)',marginBottom:6},
  cardLeft:{flex:1},
  srvName:{color:'#fff',fontSize:13,fontWeight:'700'},
  srvPlayers:{color:'#888',fontSize:10,marginTop:2},
  newBadge:{color:'#44cc44',fontSize:9,fontWeight:'800',marginTop:2},
  cardRight:{alignItems:'flex-end',width:80},
  loadBarBg:{width:60,height:6,backgroundColor:'rgba(255,255,255,0.08)',borderRadius:3,overflow:'hidden'},
  loadBarFill:{height:'100%',borderRadius:3},
  loadTxt:{fontSize:10,fontWeight:'700',marginTop:2},
  statusDot:{width:8,height:8,borderRadius:4,marginTop:4},
});
