import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export default function CosmeticsScreen() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'aura'|'frame'>('aura');

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/cosmetics'); setData(d); } catch(e){} finally { setLoading(false); } };

  const buy = async (type: string, id: string) => {
    try {
      await apiCall('/api/cosmetics/buy', { method:'POST', body: JSON.stringify({type, item_id:id}) });
      await refreshUser(); await load();
      Alert.alert('Acquistato!');
    } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  const equip = async (type: string, id: string) => {
    try {
      await apiCall('/api/cosmetics/equip', { method:'POST', body: JSON.stringify({type, item_id:id}) });
      await load();
      Alert.alert('Equipaggiato!');
    } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  const items = tab === 'aura' ? data?.auras : data?.frames;
  const owned = tab === 'aura' ? data?.owned_auras : data?.owned_frames;
  const active = tab === 'aura' ? data?.active_aura : data?.active_frame;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>\u2190</Text></TouchableOpacity>
        <Text style={s.title}>AURE & AVATAR</Text>
        <Text style={s.res}>\uD83D\uDCB0 {(user?.gold||0).toLocaleString()} | \uD83D\uDC8E {user?.gems||0}</Text>
      </View>
      <View style={s.tabs}>
        <TouchableOpacity style={[s.tabBtn, tab==='aura'&&s.tabActive]} onPress={() => setTab('aura')}>
          <Text style={[s.tabTxt, tab==='aura'&&s.tabTxtActive]}>\u2728 Aure</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[s.tabBtn, tab==='frame'&&s.tabActive]} onPress={() => setTab('frame')}>
          <Text style={[s.tabTxt, tab==='frame'&&s.tabTxtActive]}>\uD83D\uDDBC\uFE0F Cornici</Text>
        </TouchableOpacity>
      </View>
      <ScrollView contentContainerStyle={s.grid}>
        {items?.map((item:any) => {
          const isOwned = owned?.includes(item.id);
          const isActive = active === item.id;
          return (
            <View key={item.id} style={[s.card, {borderColor:item.color||'#888'}, isActive&&s.cardActive]}>
              <View style={[s.iconCircle, {backgroundColor:(item.color||'#888')+'25'}]}>
                <Text style={s.icon}>{item.icon || '\uD83D\uDDBC\uFE0F'}</Text>
              </View>
              <Text style={[s.name, {color:item.color}]}>{item.name}</Text>
              {isActive && <Text style={s.activeTxt}>\u2705 ATTIVO</Text>}
              {isOwned && !isActive && (
                <TouchableOpacity style={s.equipBtn} onPress={() => equip(tab, item.id)}>
                  <Text style={s.equipTxt}>Equipaggia</Text>
                </TouchableOpacity>
              )}
              {!isOwned && (
                <TouchableOpacity style={[s.buyBtn, {borderColor:item.color}]} onPress={() => buy(tab, item.id)}>
                  <Text style={s.buyTxt}>{item.currency==='gems'?'\uD83D\uDC8E':'\uD83D\uDCB0'} {item.cost}</Text>
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
  res:{color:'#888',fontSize:10},
  tabs:{flexDirection:'row',paddingHorizontal:12,paddingVertical:6,gap:8},
  tabBtn:{paddingHorizontal:16,paddingVertical:6,borderRadius:8,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:1,borderColor:'rgba(255,255,255,0.1)'},
  tabActive:{backgroundColor:'rgba(255,107,53,0.15)',borderColor:'#ff6b35'},
  tabTxt:{color:'#888',fontSize:12,fontWeight:'600'},
  tabTxtActive:{color:'#ff6b35'},
  grid:{flexDirection:'row',flexWrap:'wrap',padding:10,gap:8},
  card:{width:130,padding:10,borderRadius:10,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:1.5,alignItems:'center'},
  cardActive:{backgroundColor:'rgba(68,204,68,0.08)'},
  iconCircle:{width:48,height:48,borderRadius:24,alignItems:'center',justifyContent:'center'},
  icon:{fontSize:24},
  name:{fontSize:11,fontWeight:'700',marginTop:6,textAlign:'center'},
  activeTxt:{color:'#44cc44',fontSize:9,fontWeight:'700',marginTop:4},
  equipBtn:{marginTop:4,paddingHorizontal:10,paddingVertical:4,borderRadius:6,backgroundColor:'rgba(68,136,255,0.2)'},
  equipTxt:{color:'#4488ff',fontSize:9,fontWeight:'700'},
  buyBtn:{marginTop:4,paddingHorizontal:10,paddingVertical:4,borderRadius:6,borderWidth:1,backgroundColor:'rgba(255,255,255,0.03)'},
  buyTxt:{color:'#fff',fontSize:10,fontWeight:'700'},
});
