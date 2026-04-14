import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const EVENT_ICONS: Record<string,string> = { coin:'\uD83D\uDCB0', dumbbell:'\uD83C\uDFCB\uFE0F', sword:'\uD83D\uDDE1\uFE0F', gem:'\uD83D\uDC8E', skull:'\uD83D\uDC80' };

export default function EventsScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [battling, setBattling] = useState('');

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/events/daily'); setData(d); } catch(e){} finally { setLoading(false); } };

  const doBattle = async (eventId: string) => {
    setBattling(eventId);
    try {
      const r = await apiCall('/api/events/battle', { method:'POST', body: JSON.stringify({event_id:eventId}) });
      await refreshUser(); await load();
      const rw = Object.entries(r.rewards||{}).map(([k,v]) => `${k}: ${typeof v === 'object' ? (v as any).name : v}`).join(', ');
      Alert.alert(r.victory?'Vittoria!':'Sconfitta', r.victory ? `Ricompense: ${rw}` : 'Ritenta!');
    } catch(e:any) { Alert.alert('Errore', e.message); } finally { setBattling(''); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#44aaff" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>←</Text></TouchableOpacity>
        <Text style={s.title}>EVENTI GIORNALIERI</Text>
        <Text style={s.date}>{data?.date}</Text>
      </View>
      <ScrollView contentContainerStyle={s.list}>
        {data?.events?.map((ev:any) => (
          <View key={ev.id} style={[s.card, ev.completed_today && s.cardDone]}>
            <Text style={s.evIcon}>{EVENT_ICONS[ev.icon]||'\uD83C\uDF1F'}</Text>
            <View style={s.evInfo}>
              <Text style={s.evName}>{ev.name}</Text>
              <Text style={s.evDesc}>{ev.description}</Text>
              <Text style={s.evCost}>\u26A1 {ev.stamina_cost} Stamina</Text>
            </View>
            {ev.completed_today ? (
              <Text style={s.doneTxt}>\u2705 Completato</Text>
            ) : (
              <TouchableOpacity style={[s.playBtn, battling===ev.id&&{opacity:0.5}]} onPress={() => doBattle(ev.id)} disabled={battling===ev.id}>
                <Text style={s.playTxt}>{battling===ev.id?'...':'GIOCA'}</Text>
              </TouchableOpacity>
            )}
          </View>
        ))}
        {(!data?.events || data.events.length === 0) && <Text style={s.empty}>Nessun evento oggi!</Text>}
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(68,170,255,0.3)'},
  back:{color:'#44aaff',fontSize:20,fontWeight:'700'},
  title:{color:'#44aaff',fontSize:16,fontWeight:'800',letterSpacing:2,flex:1},
  date:{color:'#888',fontSize:11},
  list:{padding:12,gap:8},
  card:{flexDirection:'row',alignItems:'center',padding:12,borderRadius:12,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:1,borderColor:'rgba(68,170,255,0.2)',gap:10},
  cardDone:{opacity:0.5},
  evIcon:{fontSize:28},
  evInfo:{flex:1},
  evName:{color:'#fff',fontSize:14,fontWeight:'700'},
  evDesc:{color:'#888',fontSize:10,marginTop:1},
  evCost:{color:'#ff8844',fontSize:10,marginTop:2},
  doneTxt:{color:'#44cc44',fontSize:11,fontWeight:'600'},
  playBtn:{paddingHorizontal:16,paddingVertical:8,borderRadius:8,backgroundColor:'#44aaff'},
  playTxt:{color:'#fff',fontSize:12,fontWeight:'800'},
  empty:{color:'#555',fontSize:13,textAlign:'center',marginTop:40},
});
