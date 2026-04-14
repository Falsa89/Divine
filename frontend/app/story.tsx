import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const EC: Record<string,string> = { fire:'#ff4444', water:'#4488ff', earth:'#aa8844', wind:'#44cc88', light:'#ffd700', dark:'#9944ff', neutral:'#888' };

export default function StoryScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [battling, setBattling] = useState(false);

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/story/chapters'); setData(d); } catch(e){} finally { setLoading(false); } };

  const doBattle = async (chId: number, stage: number) => {
    setBattling(true);
    try {
      const r = await apiCall('/api/story/battle', { method:'POST', body: JSON.stringify({chapter_id:chId, stage}) });
      await refreshUser(); await load();
      const msg = r.victory
        ? `Vittoria! +${r.rewards?.gold||0} oro, +${r.rewards?.exp||0} EXP${r.rewards?.equipment ? '\nEquip: '+r.rewards.equipment.name : ''}`
        : 'Sconfitta... Potenzia il tuo team!';
      Alert.alert(r.victory ? 'Vittoria!' : 'Sconfitta', msg);
    } catch(e:any) { Alert.alert('Errore', e.message); } finally { setBattling(false); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>←</Text></TouchableOpacity>
        <Text style={s.title}>CAMPAGNA STORIA</Text>
        <Text style={s.sub}>Cap. {data?.progress?.current_chapter || 1}</Text>
      </View>
      <ScrollView contentContainerStyle={s.list}>
        {data?.chapters?.map((ch:any) => {
          const col = EC[ch.element] || '#888';
          return (
            <View key={ch.id} style={[s.card, {borderColor: ch.unlocked ? col : '#333', opacity: ch.unlocked ? 1 : 0.4}]}>
              <View style={[s.chBadge, {backgroundColor:col+'25'}]}><Text style={[s.chNum, {color:col}]}>{ch.id}</Text></View>
              <View style={s.chInfo}>
                <Text style={[s.chName, {color:ch.fully_completed?'#44cc44':col}]}>{ch.name} {ch.fully_completed ? '\u2705' : ''}</Text>
                <Text style={s.chDesc}>{ch.description}</Text>
                <View style={s.progBar}><View style={[s.progFill, {width:`${(ch.completed_stages/ch.stages)*100}%`, backgroundColor:col}]} /></View>
                <Text style={s.progTxt}>{ch.completed_stages}/{ch.stages} stadi</Text>
              </View>
              {ch.unlocked && !ch.fully_completed && (
                <TouchableOpacity style={[s.playBtn, {backgroundColor:col+'30', borderColor:col}]} onPress={() => doBattle(ch.id, ch.completed_stages+1)} disabled={battling}>
                  <Text style={[s.playTxt, {color:col}]}>{battling?'...':'GIOCA'}</Text>
                </TouchableOpacity>
              )}
            </View>
          );
        })}
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(255,107,53,0.2)'},
  back:{color:'#ff6b35',fontSize:20,fontWeight:'700'},
  title:{color:'#fff',fontSize:16,fontWeight:'800',letterSpacing:2,flex:1},
  sub:{color:'#ffd700',fontSize:12},
  list:{padding:10,gap:8},
  card:{flexDirection:'row',alignItems:'center',padding:10,borderRadius:12,backgroundColor:'rgba(255,255,255,0.03)',borderWidth:1.5,gap:10},
  chBadge:{width:40,height:40,borderRadius:10,alignItems:'center',justifyContent:'center'},
  chNum:{fontSize:18,fontWeight:'900'},
  chInfo:{flex:1},
  chName:{fontSize:13,fontWeight:'800'},
  chDesc:{color:'#888',fontSize:9,marginTop:1},
  progBar:{height:4,backgroundColor:'rgba(255,255,255,0.08)',borderRadius:2,marginTop:4,overflow:'hidden'},
  progFill:{height:'100%',borderRadius:2},
  progTxt:{color:'#666',fontSize:8,marginTop:1},
  playBtn:{paddingHorizontal:16,paddingVertical:8,borderRadius:8,borderWidth:1},
  playTxt:{fontSize:11,fontWeight:'800',letterSpacing:1},
});
