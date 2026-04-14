import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const RC: Record<number,string> = { 1:'#888', 2:'#44aa44', 3:'#4488ff', 4:'#aa44ff', 5:'#ff4444', 6:'#ffd700' };
const EC: Record<string,string> = { fire:'#ff4444', water:'#4488ff', earth:'#aa8844', wind:'#44cc88', light:'#ffd700', dark:'#9944ff' };

export default function FusionScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [heroes, setHeroes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [baseHero, setBaseHero] = useState<any>(null);
  const [fodder, setFodder] = useState<string[]>([]);
  const [fusing, setFusing] = useState(false);

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/user/heroes'); setHeroes(d.sort((a:any,b:any)=>(b.hero_rarity||0)-(a.hero_rarity||0))); } catch(e){} finally { setLoading(false); } };

  const toggleFodder = (id: string) => {
    if (id === baseHero?.id) return;
    setFodder(prev => prev.includes(id) ? prev.filter(f=>f!==id) : [...prev, id]);
  };

  const doFusion = async () => {
    if (!baseHero || fodder.length === 0) return;
    setFusing(true);
    try {
      const r = await apiCall('/api/fusion/merge', { method:'POST', body: JSON.stringify({base_hero_id:baseHero.id, fodder_hero_ids:fodder}) });
      await refreshUser(); setBaseHero(null); setFodder([]); await load();
      Alert.alert('Fusione completata!', `Nuovo livello: ${r.new_level}\nStelle: ${'\u2B50'.repeat(r.new_stars)}${r.star_ups>0?'\n+'+r.star_ups+' stelle!':''}\n+${r.exp_gained} EXP`);
    } catch(e:any) { Alert.alert('Errore', e.message); } finally { setFusing(false); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff8844" /></LinearGradient>;

  const availableForFodder = heroes.filter(h => h.id !== baseHero?.id);

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>←</Text></TouchableOpacity>
        <Text style={s.title}>FUSIONE EROI</Text>
      </View>
      <View style={s.body}>
        {/* Base hero selection */}
        <View style={s.panel}>
          <Text style={s.panelTitle}>EROE BASE</Text>
          {baseHero ? (
            <View style={[s.baseCard, {borderColor:RC[baseHero.hero_rarity]}]}>
              <Text style={[s.baseName,{color:RC[baseHero.hero_rarity]}]}>{baseHero.hero_name}</Text>
              <Text style={s.baseStars}>{'\u2B50'.repeat(baseHero.hero_rarity||1)} Lv.{baseHero.level||1}</Text>
              <TouchableOpacity onPress={() => {setBaseHero(null);setFodder([]);}}><Text style={s.clearTxt}>Cambia</Text></TouchableOpacity>
            </View>
          ) : <Text style={s.hint}>Seleziona un eroe da potenziare</Text>}
          {baseHero && (
            <>
              <Text style={s.panelSub}>SACRIFICA ({fodder.length} selezionati)</Text>
              <Text style={s.fusionHint}>Stesso eroe = +1 stella\nEroe diverso = +EXP</Text>
            </>
          )}
          {baseHero && fodder.length > 0 && (
            <TouchableOpacity style={[s.fuseBtn, fusing&&{opacity:0.5}]} onPress={doFusion} disabled={fusing}>
              <Text style={s.fuseTxt}>{fusing?'Fondendo...':'FONDI!'}</Text>
            </TouchableOpacity>
          )}
        </View>
        {/* Hero grid */}
        <ScrollView style={s.grid} contentContainerStyle={s.gridC}>
          {(baseHero ? availableForFodder : heroes).map((h:any) => {
            const isFodder = fodder.includes(h.id);
            return (
              <TouchableOpacity key={h.id} style={[s.heroCard, {borderColor:RC[h.hero_rarity]||'#444'}, isFodder&&s.fodderCard]} onPress={() => baseHero ? toggleFodder(h.id) : setBaseHero(h)}>
                <View style={[s.heroP, {backgroundColor:(EC[h.hero_element]||'#888')+'20'}]}>
                  <Text style={[s.heroI,{color:EC[h.hero_element]}]}>{h.hero_name?.[0]}</Text>
                </View>
                <Text style={s.heroN} numberOfLines={1}>{h.hero_name}</Text>
                <Text style={[s.heroS,{color:RC[h.hero_rarity]}]}>{'\u2B50'.repeat(h.hero_rarity||1)}</Text>
                {isFodder && <View style={s.fodderBadge}><Text style={s.fodderX}>\u2716</Text></View>}
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(255,136,68,0.3)'},
  back:{color:'#ff8844',fontSize:20,fontWeight:'700'},
  title:{color:'#ff8844',fontSize:16,fontWeight:'800',letterSpacing:2},
  body:{flex:1,flexDirection:'row',padding:10,gap:10},
  panel:{width:180,backgroundColor:'rgba(255,255,255,0.04)',borderRadius:14,padding:12,borderWidth:1,borderColor:'rgba(255,136,68,0.2)'},
  panelTitle:{color:'#ff8844',fontSize:13,fontWeight:'800',textAlign:'center',marginBottom:8},
  baseCard:{padding:10,borderRadius:10,borderWidth:2,alignItems:'center',marginBottom:8},
  baseName:{fontSize:14,fontWeight:'800'},
  baseStars:{fontSize:10,marginTop:2},
  clearTxt:{color:'#ff4444',fontSize:10,marginTop:4},
  hint:{color:'#555',fontSize:11,textAlign:'center'},
  panelSub:{color:'#888',fontSize:10,marginTop:8},
  fusionHint:{color:'#666',fontSize:9,marginTop:4},
  fuseBtn:{marginTop:12,padding:12,borderRadius:10,backgroundColor:'#ff8844',alignItems:'center'},
  fuseTxt:{color:'#fff',fontSize:13,fontWeight:'900'},
  grid:{flex:1},
  gridC:{flexDirection:'row',flexWrap:'wrap',gap:6},
  heroCard:{width:75,padding:6,borderRadius:10,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:2,alignItems:'center'},
  fodderCard:{backgroundColor:'rgba(255,68,68,0.15)',borderColor:'#ff4444'},
  heroP:{width:40,height:40,borderRadius:10,alignItems:'center',justifyContent:'center'},
  heroI:{fontSize:18,fontWeight:'900'},
  heroN:{color:'#fff',fontSize:8,fontWeight:'600',marginTop:2,textAlign:'center'},
  heroS:{fontSize:7,marginTop:1},
  fodderBadge:{position:'absolute',top:-2,right:-2,width:16,height:16,borderRadius:8,backgroundColor:'#ff4444',alignItems:'center',justifyContent:'center'},
  fodderX:{color:'#fff',fontSize:9,fontWeight:'900'},
});
