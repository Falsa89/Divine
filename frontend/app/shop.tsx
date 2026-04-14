import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export default function ShopScreen() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState('');
  const [tab, setTab] = useState('all');

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/shop'); setData(d); } catch(e){} finally { setLoading(false); } };

  const buy = async (itemId: string) => {
    setBuying(itemId);
    try {
      const r = await apiCall('/api/shop/buy', { method:'POST', body: JSON.stringify({item_id:itemId}) });
      await refreshUser(); await load();
      Alert.alert('Acquistato!', `${r.item}`);
    } catch(e:any) { Alert.alert('Errore', e.message); } finally { setBuying(''); }
  };

  const claimDaily = async (itemId: string) => {
    try {
      const r = await apiCall(`/api/shop/claim-daily/${itemId}`, { method:'POST' });
      await refreshUser(); await load();
      Alert.alert('Riscosso!', JSON.stringify(r.reward));
    } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  const CATS = [{id:'all',label:'Tutto'},{id:'gems',label:'Gemme'},{id:'gold',label:'Oro'},{id:'stamina',label:'Stamina'},{id:'gacha',label:'Gacha'},{id:'boost',label:'Boost'}];
  const filtered = tab === 'all' ? data?.items : data?.items?.filter((i:any) => i.category === tab);

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>\u2190</Text></TouchableOpacity>
        <Text style={s.title}>NEGOZIO</Text>
        <Text style={s.res}>\uD83D\uDCB0 {(user?.gold||0).toLocaleString()} | \uD83D\uDC8E {user?.gems?.toLocaleString()}</Text>
      </View>
      {/* Daily Free */}
      <View style={s.dailyRow}>
        <Text style={s.dailyTitle}>Gratuiti Giornalieri:</Text>
        {data?.daily_free?.map((d:any) => (
          <TouchableOpacity key={d.id} style={[s.dailyBtn, d.claimed && s.dailyClaimed]} onPress={() => !d.claimed && claimDaily(d.id)} disabled={d.claimed}>
            <Text style={s.dailyIcon}>{d.icon}</Text>
            <Text style={s.dailyName}>{d.name}</Text>
            {d.claimed ? <Text style={s.claimedTxt}>\u2705</Text> : <Text style={s.claimTxt}>Riscuoti</Text>}
          </TouchableOpacity>
        ))}
      </View>
      {/* Tabs */}
      <View style={s.tabs}>
        {CATS.map(c => (
          <TouchableOpacity key={c.id} style={[s.tab, tab===c.id && s.tabA]} onPress={() => setTab(c.id)}>
            <Text style={[s.tabTxt, tab===c.id && s.tabTxtA]}>{c.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <ScrollView contentContainerStyle={s.grid}>
        {filtered?.map((item:any) => (
          <View key={item.id} style={s.card}>
            <Text style={s.cardIcon}>{item.icon}</Text>
            <Text style={s.cardName}>{item.name}</Text>
            <Text style={s.cardDesc}>{item.description}</Text>
            <TouchableOpacity style={[s.buyBtn, buying===item.id&&{opacity:0.5}]} onPress={() => buy(item.id)} disabled={buying===item.id}>
              <Text style={s.buyTxt}>{item.price_type==='gems'?'\uD83D\uDC8E':'\uD83D\uDCB0'} {item.price.toLocaleString()}</Text>
            </TouchableOpacity>
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
  title:{color:'#fff',fontSize:16,fontWeight:'800',letterSpacing:2,flex:1},
  res:{color:'#888',fontSize:10},
  dailyRow:{flexDirection:'row',alignItems:'center',gap:8,paddingHorizontal:12,paddingVertical:6,borderBottomWidth:1,borderBottomColor:'rgba(255,255,255,0.05)'},
  dailyTitle:{color:'#888',fontSize:10,fontWeight:'600'},
  dailyBtn:{flexDirection:'row',alignItems:'center',gap:4,paddingHorizontal:10,paddingVertical:5,borderRadius:8,backgroundColor:'rgba(68,204,68,0.1)',borderWidth:1,borderColor:'rgba(68,204,68,0.3)'},
  dailyClaimed:{opacity:0.4},
  dailyIcon:{fontSize:14},
  dailyName:{color:'#44cc44',fontSize:10,fontWeight:'600'},
  claimTxt:{color:'#44cc44',fontSize:9,fontWeight:'700'},
  claimedTxt:{fontSize:12},
  tabs:{flexDirection:'row',gap:4,paddingHorizontal:10,paddingVertical:4},
  tab:{paddingHorizontal:10,paddingVertical:4,borderRadius:6,backgroundColor:'rgba(255,255,255,0.04)'},
  tabA:{backgroundColor:'rgba(255,107,53,0.15)',borderWidth:1,borderColor:'#ff6b35'},
  tabTxt:{color:'#666',fontSize:9,fontWeight:'600'},
  tabTxtA:{color:'#ff6b35'},
  grid:{flexDirection:'row',flexWrap:'wrap',padding:8,gap:8},
  card:{width:'22%' as any,padding:10,borderRadius:10,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:1,borderColor:'rgba(255,255,255,0.08)',alignItems:'center'},
  cardIcon:{fontSize:28},
  cardName:{color:'#fff',fontSize:10,fontWeight:'700',marginTop:4,textAlign:'center'},
  cardDesc:{color:'#888',fontSize:8,marginTop:2,textAlign:'center'},
  buyBtn:{marginTop:6,paddingHorizontal:12,paddingVertical:5,borderRadius:6,backgroundColor:'rgba(255,107,53,0.2)',borderWidth:1,borderColor:'#ff6b35'},
  buyTxt:{color:'#ff6b35',fontSize:10,fontWeight:'800'},
});
