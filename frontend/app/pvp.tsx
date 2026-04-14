import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export default function PvPScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [battling, setBattling] = useState(false);

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/pvp/status'); setStatus(d); } catch(e){} finally { setLoading(false); } };

  const doBattle = async () => {
    setBattling(true);
    try {
      const r = await apiCall('/api/pvp/battle', { method:'POST' });
      await refreshUser(); await load();
      const msg = r.victory
        ? `Hai sconfitto ${r.opponent}! +${r.trophy_change} trofei\n+${r.rewards?.gold||0} oro, +${r.rewards?.exp||0} EXP`
        : `${r.opponent} ti ha sconfitto! ${r.trophy_change} trofei`;
      Alert.alert(r.victory?'Vittoria!':'Sconfitta', msg);
    } catch(e:any) { Alert.alert('Errore', e.message); } finally { setBattling(false); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ffd700" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>←</Text></TouchableOpacity>
        <Text style={s.title}>ARENA PVP</Text>
        <Text style={s.trophies}>\uD83C\uDFC6 {status?.trophies || 0}</Text>
      </View>
      <View style={s.body}>
        {/* Stats */}
        <View style={s.statsPanel}>
          <Text style={s.trophyBig}>\uD83C\uDFC6 {status?.trophies || 0}</Text>
          <Text style={s.statLabel}>Trofei</Text>
          <View style={s.statsRow}>
            <View style={s.statBox}><Text style={[s.statVal,{color:'#44cc44'}]}>{status?.wins||0}</Text><Text style={s.statLbl}>Vittorie</Text></View>
            <View style={s.statBox}><Text style={[s.statVal,{color:'#ff4444'}]}>{status?.losses||0}</Text><Text style={s.statLbl}>Sconfitte</Text></View>
            <View style={s.statBox}><Text style={[s.statVal,{color:'#ffd700'}]}>{status?.streak||0}</Text><Text style={s.statLbl}>Serie</Text></View>
          </View>
          <Text style={s.dailyTxt}>Battaglie oggi: {status?.daily_battles||0}/10</Text>
          <TouchableOpacity style={[s.battleBtn, battling&&{opacity:0.5}]} onPress={doBattle} disabled={battling}>
            <Text style={s.battleTxt}>{battling ? 'Combattendo...' : 'SFIDA ARENA'}</Text>
          </TouchableOpacity>
        </View>
        {/* Leaderboard */}
        <View style={s.lbPanel}>
          <Text style={s.lbTitle}>CLASSIFICA</Text>
          <ScrollView>
            {(status?.leaderboard||[]).map((e:any, i:number) => (
              <View key={i} style={[s.lbRow, i===0&&{borderColor:'#ffd700'}]}>
                <Text style={[s.lbRank, i<3&&{color:['#ffd700','#c0c0c0','#cd7f32'][i]}]}>#{e.rank}</Text>
                <Text style={s.lbName}>{e.username}</Text>
                <Text style={s.lbTr}>\uD83C\uDFC6 {e.trophies}</Text>
              </View>
            ))}
            {(!status?.leaderboard || status.leaderboard.length === 0) && <Text style={s.emptyTxt}>Nessun dato ancora</Text>}
          </ScrollView>
        </View>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(255,215,0,0.3)'},
  back:{color:'#ffd700',fontSize:20,fontWeight:'700'},
  title:{color:'#ffd700',fontSize:16,fontWeight:'800',letterSpacing:2,flex:1},
  trophies:{color:'#ffd700',fontSize:14,fontWeight:'700'},
  body:{flex:1,flexDirection:'row',padding:12,gap:12},
  statsPanel:{flex:1,backgroundColor:'rgba(255,255,255,0.04)',borderRadius:14,padding:16,alignItems:'center',justifyContent:'center',borderWidth:1,borderColor:'rgba(255,215,0,0.2)'},
  trophyBig:{fontSize:36},
  statLabel:{color:'#ffd700',fontSize:14,fontWeight:'700',marginTop:4},
  statsRow:{flexDirection:'row',gap:16,marginTop:12},
  statBox:{alignItems:'center'},
  statVal:{fontSize:20,fontWeight:'900'},
  statLbl:{color:'#888',fontSize:9},
  dailyTxt:{color:'#888',fontSize:11,marginTop:12},
  battleBtn:{marginTop:12,paddingHorizontal:32,paddingVertical:12,borderRadius:10,backgroundColor:'#ffd700'},
  battleTxt:{color:'#080816',fontSize:14,fontWeight:'900',letterSpacing:1},
  lbPanel:{width:200,backgroundColor:'rgba(255,255,255,0.04)',borderRadius:14,padding:12,borderWidth:1,borderColor:'rgba(255,215,0,0.15)'},
  lbTitle:{color:'#ffd700',fontSize:13,fontWeight:'800',letterSpacing:1,textAlign:'center',marginBottom:8},
  lbRow:{flexDirection:'row',alignItems:'center',gap:8,padding:6,borderRadius:6,borderWidth:1,borderColor:'#222',marginBottom:4},
  lbRank:{color:'#fff',fontSize:13,fontWeight:'900',width:28},
  lbName:{color:'#ccc',fontSize:11,flex:1},
  lbTr:{color:'#ffd700',fontSize:10,fontWeight:'600'},
  emptyTxt:{color:'#555',fontSize:11,textAlign:'center',marginTop:20},
});
