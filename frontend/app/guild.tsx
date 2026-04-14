import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export default function GuildScreen() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [guildData, setGuildData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [guildName, setGuildName] = useState('');
  const [factions, setFactions] = useState<any>(null);

  useEffect(() => { load(); }, []);
  const load = async () => {
    try {
      const [g, f] = await Promise.all([apiCall('/api/guild/info'), apiCall('/api/factions')]);
      setGuildData(g); setFactions(f);
    } catch(e){} finally { setLoading(false); }
  };

  const createGuild = async () => {
    if (!guildName.trim()) return;
    try { await apiCall('/api/guild/create', {method:'POST', body:JSON.stringify({name:guildName})}); await refreshUser(); await load(); Alert.alert('Gilda creata!'); } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  const joinGuild = async (id:string) => {
    try { await apiCall(`/api/guild/join/${id}`, {method:'POST'}); await refreshUser(); await load(); Alert.alert('Sei entrato nella gilda!'); } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  const leaveGuild = async () => {
    try { await apiCall('/api/guild/leave', {method:'POST'}); await refreshUser(); await load(); } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  const joinFaction = async (id:string) => {
    try { await apiCall('/api/faction/join', {method:'POST', body:JSON.stringify({faction_id:id})}); await refreshUser(); await load(); Alert.alert('Fazione scelta!'); } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#6644ff" /></LinearGradient>;

  const guild = guildData?.guild;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>←</Text></TouchableOpacity>
        <Text style={s.title}>GILDA & FAZIONI</Text>
      </View>
      <ScrollView contentContainerStyle={s.body}>
        {/* Guild */}
        <View style={s.section}>
          <Text style={s.secTitle}>\uD83C\uDFDB\uFE0F GILDA</Text>
          {guild ? (
            <View style={s.guildCard}>
              <Text style={s.guildName}>{guild.name}</Text>
              <Text style={s.guildLvl}>Livello {guild.level} - {guild.member_details?.length||0} membri</Text>
              {guild.member_details?.map((m:any) => (
                <Text key={m.id} style={s.memberTxt}>{m.username} (Lv.{m.level})</Text>
              ))}
              <TouchableOpacity style={s.leaveBtn} onPress={leaveGuild}><Text style={s.leaveTxt}>Abbandona</Text></TouchableOpacity>
            </View>
          ) : (
            <View>
              <View style={s.createRow}>
                <TextInput style={s.input} placeholder="Nome gilda..." placeholderTextColor="#555" value={guildName} onChangeText={setGuildName} />
                <TouchableOpacity style={s.createBtn} onPress={createGuild}><Text style={s.createTxt}>CREA</Text></TouchableOpacity>
              </View>
              {guildData?.available_guilds?.map((g:any) => (
                <TouchableOpacity key={g.id} style={s.guildRow} onPress={() => joinGuild(g.id)}>
                  <Text style={s.gRowName}>{g.name}</Text>
                  <Text style={s.gRowInfo}>Lv.{g.level} - {g.members} membri</Text>
                  <Text style={s.joinTxt}>Unisciti</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>
        {/* Factions */}
        <View style={s.section}>
          <Text style={s.secTitle}>\u2696\uFE0F FAZIONI</Text>
          <View style={s.factGrid}>
            {factions?.factions?.map((f:any) => (
              <TouchableOpacity key={f.id} style={[s.factCard, factions?.user_faction===f.id && s.factActive]} onPress={() => joinFaction(f.id)}>
                <Text style={s.factName}>{f.name}</Text>
                <Text style={s.factDesc}>{f.description}</Text>
                <Text style={s.factBonus}>Bonus: {Object.entries(f.bonus).map(([k,v]) => `+${(Number(v)*100).toFixed(0)}% ${k}`).join(', ')}</Text>
                {factions?.user_faction===f.id && <Text style={s.factActiveTxt}>\u2705 Attiva</Text>}
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(102,68,255,0.3)'},
  back:{color:'#6644ff',fontSize:20,fontWeight:'700'},
  title:{color:'#6644ff',fontSize:16,fontWeight:'800',letterSpacing:2},
  body:{padding:12,gap:16},
  section:{},
  secTitle:{color:'#fff',fontSize:14,fontWeight:'800',marginBottom:8},
  guildCard:{padding:12,borderRadius:12,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:1,borderColor:'rgba(102,68,255,0.3)'},
  guildName:{color:'#6644ff',fontSize:18,fontWeight:'900'},
  guildLvl:{color:'#888',fontSize:11,marginTop:2},
  memberTxt:{color:'#aaa',fontSize:10,marginTop:2},
  leaveBtn:{marginTop:8,padding:6,borderRadius:6,backgroundColor:'rgba(255,68,68,0.15)',alignItems:'center'},
  leaveTxt:{color:'#ff4444',fontSize:10,fontWeight:'700'},
  createRow:{flexDirection:'row',gap:8,marginBottom:8},
  input:{flex:1,backgroundColor:'rgba(255,255,255,0.06)',borderRadius:8,padding:10,color:'#fff',fontSize:13,borderWidth:1,borderColor:'rgba(255,255,255,0.1)'},
  createBtn:{paddingHorizontal:16,paddingVertical:10,backgroundColor:'#6644ff',borderRadius:8,justifyContent:'center'},
  createTxt:{color:'#fff',fontSize:12,fontWeight:'800'},
  guildRow:{flexDirection:'row',alignItems:'center',padding:8,borderRadius:8,backgroundColor:'rgba(255,255,255,0.03)',marginBottom:4,gap:8},
  gRowName:{color:'#fff',fontSize:12,fontWeight:'600',flex:1},
  gRowInfo:{color:'#888',fontSize:10},
  joinTxt:{color:'#6644ff',fontSize:10,fontWeight:'700'},
  factGrid:{flexDirection:'row',flexWrap:'wrap',gap:8},
  factCard:{width:'48%' as any,padding:12,borderRadius:10,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:1,borderColor:'#333'},
  factActive:{borderColor:'#44cc44',backgroundColor:'rgba(68,204,68,0.08)'},
  factName:{color:'#fff',fontSize:13,fontWeight:'800'},
  factDesc:{color:'#888',fontSize:9,marginTop:2},
  factBonus:{color:'#ffd700',fontSize:9,marginTop:4},
  factActiveTxt:{color:'#44cc44',fontSize:10,fontWeight:'700',marginTop:4},
});
