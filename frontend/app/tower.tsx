import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export default function TowerScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [battling, setBattling] = useState(false);

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/tower/status'); setStatus(d); } catch(e){} finally { setLoading(false); } };

  const doBattle = async () => {
    setBattling(true);
    try {
      const r = await apiCall('/api/tower/battle', { method:'POST' });
      await refreshUser(); await load();
      const msg = r.victory
        ? `Piano ${r.floor} superato! +${r.rewards?.gold||0} oro, +${r.rewards?.exp||0} EXP${r.rewards?.gems?' +'+r.rewards.gems+' gemme':''}${r.rewards?.equipment?'\nEquip: '+r.rewards.equipment.name:''}`
        : `Sconfitta al piano ${r.floor}! Potenza nemica: ${r.enemy_power.toLocaleString()}`;
      Alert.alert(r.victory?'Vittoria!':'Sconfitta', msg);
    } catch(e:any) { Alert.alert('Errore', e.message); } finally { setBattling(false); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#aa44ff" /></LinearGradient>;

  const floor = status?.floor || 1;
  const highest = status?.highest_floor || 1;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>←</Text></TouchableOpacity>
        <Text style={s.title}>TORRE INFINITA</Text>
      </View>
      <ScrollView contentContainerStyle={s.body} showsVerticalScrollIndicator={false}>
        <View style={s.towerVis}>
          {Array.from({length:5}, (_,i) => {
            const f = floor + 4 - i;
            const isCurrent = f === floor;
            return (
              <View key={i} style={[s.floorRow, isCurrent && s.floorCurrent]}>
                <Text style={[s.floorNum, isCurrent && {color:'#ffd700'}]}>Piano {f}</Text>
                <View style={[s.floorBar, {width: `${Math.min(100, f*3)}%`, backgroundColor: isCurrent ? '#aa44ff' : '#333'}]} />
                {f <= highest && f !== floor && <Text style={s.floorDone}>\u2705</Text>}
              </View>
            );
          })}
        </View>
        <View style={s.infoPanel}>
          <Text style={s.floorBig}>Piano {floor}</Text>
          <Text style={s.highTxt}>Record: Piano {highest}</Text>
          <Text style={s.diffTxt}>Difficolta: {'\u2B50'.repeat(Math.min(5, Math.ceil(floor/10)))}</Text>
          <Text style={s.rewardTxt}>Ricompense: Oro, EXP{floor%5===0?' + Equipaggiamento':''}{floor%10===0?' + 20 Gemme':''}</Text>
          <Text style={s.costTxt}>\u26A1 Costo: 8 Stamina</Text>
          <TouchableOpacity style={[s.battleBtn, battling&&{opacity:0.5}]} onPress={doBattle} disabled={battling}>
            <Text style={s.battleTxt}>{battling ? 'Combattendo...' : 'SFIDA PIANO '+floor}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(170,68,255,0.3)'},
  back:{color:'#aa44ff',fontSize:20,fontWeight:'700'},
  title:{color:'#aa44ff',fontSize:16,fontWeight:'800',letterSpacing:2},
  body:{flex:1,flexDirection:'row',padding:16,gap:16,flexGrow:1},
  towerVis:{flex:1,gap:6,justifyContent:'center'},
  floorRow:{flexDirection:'row',alignItems:'center',gap:8,padding:8,borderRadius:8,backgroundColor:'rgba(255,255,255,0.03)'},
  floorCurrent:{backgroundColor:'rgba(170,68,255,0.15)',borderWidth:1,borderColor:'#aa44ff'},
  floorNum:{color:'#aaa',fontSize:13,fontWeight:'700',width:75},
  floorBar:{height:6,borderRadius:3},
  floorDone:{fontSize:12},
  infoPanel:{width:220,backgroundColor:'rgba(255,255,255,0.04)',borderRadius:14,padding:16,justifyContent:'center',borderWidth:1,borderColor:'rgba(170,68,255,0.3)'},
  floorBig:{color:'#aa44ff',fontSize:28,fontWeight:'900',textAlign:'center'},
  highTxt:{color:'#ffd700',fontSize:12,textAlign:'center',marginTop:4},
  diffTxt:{color:'#ff8844',fontSize:12,textAlign:'center',marginTop:8},
  rewardTxt:{color:'#888',fontSize:10,textAlign:'center',marginTop:8},
  costTxt:{color:'#ff4444',fontSize:11,textAlign:'center',marginTop:8},
  battleBtn:{marginTop:16,padding:14,borderRadius:10,backgroundColor:'#aa44ff',alignItems:'center'},
  battleTxt:{color:'#fff',fontSize:14,fontWeight:'900',letterSpacing:1},
});
