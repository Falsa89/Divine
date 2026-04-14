import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export default function FriendsScreen() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searchName, setSearchName] = useState('');
  const [tab, setTab] = useState<'friends'|'requests'>('friends');

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/friends'); setData(d); } catch(e){} finally { setLoading(false); } };

  const sendRequest = async () => {
    if (!searchName.trim()) return;
    try {
      await apiCall('/api/friends/request', { method:'POST', body: JSON.stringify({target_username:searchName}) });
      Alert.alert('Richiesta inviata!'); setSearchName(''); await load();
    } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  const accept = async (id: string) => {
    try { await apiCall('/api/friends/accept', { method:'POST', body: JSON.stringify({requester_id:id}) }); await load(); } catch(e:any) {}
  };

  const remove = async (id: string) => {
    try { await apiCall(`/api/friends/remove/${id}`, { method:'POST' }); await load(); } catch(e:any) {}
  };

  const gift = async (id: string) => {
    try {
      const r = await apiCall(`/api/friends/gift/${id}`, { method:'POST' });
      await refreshUser(); Alert.alert('Regalo inviato!', `1000 oro e 5 gemme a ${r.recipient}`);
    } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#4488ff" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>{"\u2190"}</Text></TouchableOpacity>
        <Text style={s.title}>AMICI</Text>
        <Text style={s.cnt}>{data?.friends?.length || 0}/{data?.max_friends || 30}</Text>
      </View>
      {/* Search */}
      <View style={s.searchRow}>
        <TextInput style={s.searchInput} placeholder="Nome giocatore..." placeholderTextColor="#555" value={searchName} onChangeText={setSearchName} onSubmitEditing={sendRequest} />
        <TouchableOpacity style={s.searchBtn} onPress={sendRequest}><Text style={s.searchTxt}>Aggiungi</Text></TouchableOpacity>
      </View>
      {/* Tabs */}
      <View style={s.tabs}>
        <TouchableOpacity style={[s.tab, tab==='friends'&&s.tabA]} onPress={() => setTab('friends')}>
          <Text style={[s.tabTxt, tab==='friends'&&s.tabTxtA]}>Amici ({data?.friends?.length||0})</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[s.tab, tab==='requests'&&s.tabA]} onPress={() => setTab('requests')}>
          <Text style={[s.tabTxt, tab==='requests'&&s.tabTxtA]}>Richieste ({data?.requests_in?.length||0})</Text>
        </TouchableOpacity>
      </View>
      <ScrollView contentContainerStyle={s.list}>
        {tab === 'friends' && data?.friends?.map((f:any) => (
          <View key={f.id} style={s.card}>
            <View style={[s.avatar, f.is_online && {borderColor:'#44cc44'}]}>
              <Text style={s.avatarTxt}>{f.username?.[0]?.toUpperCase()}</Text>
            </View>
            <View style={s.info}>
              <Text style={s.name}>{f.username}</Text>
              <Text style={s.sub}>Lv.{f.level} {f.title ? '\u2022 '+f.title : ''} {f.faction ? '\u2022 '+f.faction : ''}</Text>
              <Text style={s.power}>{"\u2694\uFE0F"} {f.power?.toLocaleString()}</Text>
            </View>
            <View style={s.onlineDot}>{f.is_online && <View style={s.dot}/>}</View>
            <TouchableOpacity style={s.giftBtn} onPress={() => gift(f.id)}><Text style={s.giftTxt}>{"\uD83C\uDF81"} Regalo</Text></TouchableOpacity>
            <TouchableOpacity style={s.removeBtn} onPress={() => remove(f.id)}><Text style={s.removeTxt}>{"\u2716"}</Text></TouchableOpacity>
          </View>
        ))}
        {tab === 'friends' && (!data?.friends || data.friends.length === 0) && <Text style={s.empty}>Nessun amico. Cerca e aggiungi giocatori!</Text>}

        {tab === 'requests' && data?.requests_in?.map((r:any) => (
          <View key={r.id} style={s.card}>
            <View style={s.avatar}><Text style={s.avatarTxt}>{r.username?.[0]?.toUpperCase()}</Text></View>
            <View style={s.info}>
              <Text style={s.name}>{r.username}</Text>
              <Text style={s.sub}>Lv.{r.level}</Text>
            </View>
            <TouchableOpacity style={s.acceptBtn} onPress={() => accept(r.id)}><Text style={s.acceptTxt}>Accetta</Text></TouchableOpacity>
          </View>
        ))}
        {tab === 'requests' && (!data?.requests_in || data.requests_in.length === 0) && <Text style={s.empty}>Nessuna richiesta in attesa</Text>}
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(68,136,255,0.2)'},
  back:{color:'#4488ff',fontSize:20,fontWeight:'700'},
  title:{color:'#4488ff',fontSize:16,fontWeight:'800',letterSpacing:2,flex:1},
  cnt:{color:'#888',fontSize:11},
  searchRow:{flexDirection:'row',gap:6,paddingHorizontal:12,paddingVertical:6},
  searchInput:{flex:1,backgroundColor:'rgba(255,255,255,0.06)',borderRadius:8,padding:8,color:'#fff',fontSize:12,borderWidth:1,borderColor:'rgba(255,255,255,0.1)'},
  searchBtn:{paddingHorizontal:14,paddingVertical:8,backgroundColor:'#4488ff',borderRadius:8,justifyContent:'center'},
  searchTxt:{color:'#fff',fontSize:11,fontWeight:'700'},
  tabs:{flexDirection:'row',gap:6,paddingHorizontal:12,paddingVertical:4},
  tab:{flex:1,padding:6,borderRadius:6,backgroundColor:'rgba(255,255,255,0.04)',alignItems:'center'},
  tabA:{backgroundColor:'rgba(68,136,255,0.15)',borderWidth:1,borderColor:'#4488ff'},
  tabTxt:{color:'#666',fontSize:11,fontWeight:'600'},
  tabTxtA:{color:'#4488ff'},
  list:{padding:10,gap:6},
  card:{flexDirection:'row',alignItems:'center',padding:8,borderRadius:10,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:1,borderColor:'rgba(255,255,255,0.06)',gap:8},
  avatar:{width:36,height:36,borderRadius:18,backgroundColor:'rgba(68,136,255,0.15)',borderWidth:2,borderColor:'#333',alignItems:'center',justifyContent:'center'},
  avatarTxt:{color:'#4488ff',fontSize:14,fontWeight:'900'},
  info:{flex:1},
  name:{color:'#fff',fontSize:12,fontWeight:'700'},
  sub:{color:'#888',fontSize:9,marginTop:1},
  power:{color:'#ffd700',fontSize:9,marginTop:1},
  onlineDot:{width:12},
  dot:{width:8,height:8,borderRadius:4,backgroundColor:'#44cc44'},
  giftBtn:{paddingHorizontal:8,paddingVertical:5,borderRadius:6,backgroundColor:'rgba(255,215,0,0.15)',borderWidth:1,borderColor:'rgba(255,215,0,0.3)'},
  giftTxt:{color:'#ffd700',fontSize:9,fontWeight:'700'},
  removeBtn:{padding:6},
  removeTxt:{color:'#ff4444',fontSize:12},
  acceptBtn:{paddingHorizontal:12,paddingVertical:6,borderRadius:6,backgroundColor:'#44cc44'},
  acceptTxt:{color:'#fff',fontSize:10,fontWeight:'700'},
  empty:{color:'#555',fontSize:12,textAlign:'center',marginTop:30},
});
