import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const RC: Record<number,string> = { 1:'#888', 2:'#44aa44', 3:'#4488ff', 4:'#aa44ff', 5:'#ff4444', 6:'#ffd700' };
const SLOT_ICONS: Record<string,string> = { weapon:'\uD83D\uDDE1\uFE0F', armor:'\uD83D\uDEE1\uFE0F', accessory:'\uD83D\uDC8D', rune:'\uD83D\uDD2E' };

export default function EquipmentScreen() {
  const router = useRouter();
  const [equips, setEquips] = useState<any[]>([]);
  const [heroes, setHeroes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEquip, setSelectedEquip] = useState<any>(null);
  const [selectedHero, setSelectedHero] = useState<any>(null);

  useEffect(() => { load(); }, []);
  const load = async () => {
    try {
      const [eq, h] = await Promise.all([apiCall('/api/user/equipment'), apiCall('/api/user/heroes')]);
      setEquips(eq); setHeroes(h);
    } catch(e){} finally { setLoading(false); }
  };

  const doEquip = async () => {
    if (!selectedEquip || !selectedHero) return;
    try {
      await apiCall('/api/equipment/equip', { method:'POST', body: JSON.stringify({equipment_id:selectedEquip.id, user_hero_id:selectedHero.id}) });
      Alert.alert('Fatto!', `${selectedEquip.name} equipaggiato a ${selectedHero.hero_name}`);
      setSelectedEquip(null); setSelectedHero(null); await load();
    } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#44cc88" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>←</Text></TouchableOpacity>
        <View style={{ flex: 1 }}>
          <Text style={s.title}>FUCINA DI EFESTO</Text>
          <Text style={s.subtitle}>Equipaggiamento {'\u2022'} Fusione {'\u2022'} Potenziamento</Text>
        </View>
        <Text style={s.cnt}>{equips.length} oggetti</Text>
      </View>

      {/* TASK 4.5-E — Read-only note: il backend Forge supporta upgrade+fuse;
          la UI dedicata arriverà in un task successivo. Niente acquisto/vendita
          qui: l'equipment in eccesso si fonde, non si scarta. */}
      <View style={s.forgeNote}>
        <Text style={s.forgeNoteIco}>{'\u2692\uFE0F'}</Text>
        <View style={{ flex: 1 }}>
          <Text style={s.forgeNoteTitle}>Fucina attiva</Text>
          <Text style={s.forgeNoteTxt}>
            Gli oggetti in eccesso si fondono per aumentare la rarità (non si vendono).
            UI dedicata di Upgrade & Fusione in arrivo.
          </Text>
        </View>
      </View>

      <View style={s.body}>
        <ScrollView style={s.eqList} contentContainerStyle={s.eqListC}>
          {equips.length === 0 && <Text style={s.empty}>Nessun equipaggiamento! Gioca Storia o Torre per ottenerne.</Text>}
          {equips.map((eq:any) => (
            <TouchableOpacity key={eq.id} style={[s.eqCard, {borderColor:RC[eq.rarity]||'#444'}, selectedEquip?.id===eq.id && s.eqSel]} onPress={() => setSelectedEquip(eq)}>
              <Text style={s.eqIcon}>{SLOT_ICONS[eq.slot]||'\u2728'}</Text>
              <View style={s.eqInfo}>
                <Text style={[s.eqName,{color:RC[eq.rarity]}]}>{eq.name}</Text>
                <Text style={s.eqSlot}>{eq.slot?.toUpperCase()} {'\u2B50'.repeat(eq.rarity||1)}</Text>
                <Text style={s.eqStats}>{Object.entries(eq.stats||{}).map(([k,v]) => `${k}: +${v}`).join(', ')}</Text>
                {eq.equipped_to && <Text style={s.eqEquipped}>Equipaggiato</Text>}
              </View>
            </TouchableOpacity>
          ))}
        </ScrollView>
        {/* Equip panel */}
        <View style={s.panel}>
          <Text style={s.panelTitle}>EQUIPAGGIA</Text>
          {selectedEquip ? (
            <View style={s.selInfo}>
              <Text style={[s.selName,{color:RC[selectedEquip.rarity]}]}>{selectedEquip.name}</Text>
              <Text style={s.selSlot}>{SLOT_ICONS[selectedEquip.slot]} {selectedEquip.slot}</Text>
              <Text style={s.selStats}>{Object.entries(selectedEquip.stats||{}).map(([k,v]) => `${k}: +${v}`).join('\n')}</Text>
            </View>
          ) : <Text style={s.hint}>Seleziona un oggetto</Text>}
          <Text style={s.panelSub}>Seleziona eroe:</Text>
          <ScrollView style={s.heroScroll}>
            {heroes.map((h:any) => (
              <TouchableOpacity key={h.id} style={[s.heroRow, selectedHero?.id===h.id && s.heroSel]} onPress={() => setSelectedHero(h)}>
                <Text style={s.heroN}>{h.hero_name}</Text>
                <Text style={s.heroS}>{'\u2B50'.repeat(h.hero_rarity||1)}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
          {selectedEquip && selectedHero && (
            <TouchableOpacity style={s.equipBtn} onPress={doEquip}>
              <Text style={s.equipTxt}>EQUIPAGGIA</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(255,170,68,0.3)'},
  back:{color:'#FFAA44',fontSize:20,fontWeight:'700'},
  title:{color:'#FFAA44',fontSize:16,fontWeight:'900',letterSpacing:2},
  subtitle:{color:'#888',fontSize:9,fontWeight:'700',letterSpacing:1.5,marginTop:2},
  cnt:{color:'#888',fontSize:12},
  forgeNote:{flexDirection:'row',alignItems:'center',gap:10,padding:10,marginHorizontal:10,marginTop:8,borderRadius:10,borderWidth:1,borderColor:'rgba(255,170,68,0.35)',backgroundColor:'rgba(255,170,68,0.08)'},
  forgeNoteIco:{fontSize:22},
  forgeNoteTitle:{color:'#FFAA44',fontSize:11,fontWeight:'900',letterSpacing:1.5},
  forgeNoteTxt:{color:'#B8B8D0',fontSize:10,marginTop:2,lineHeight:13},
  body:{flex:1,flexDirection:'row',padding:10,gap:10},
  eqList:{flex:1},
  eqListC:{gap:6},
  eqCard:{flexDirection:'row',alignItems:'center',padding:8,borderRadius:10,backgroundColor:'rgba(255,255,255,0.03)',borderWidth:1.5,gap:8},
  eqSel:{backgroundColor:'rgba(68,204,136,0.12)'},
  eqIcon:{fontSize:22},
  eqInfo:{flex:1},
  eqName:{fontSize:12,fontWeight:'700'},
  eqSlot:{color:'#888',fontSize:9},
  eqStats:{color:'#aaa',fontSize:9,marginTop:1},
  eqEquipped:{color:'#44cc44',fontSize:8,fontWeight:'600'},
  empty:{color:'#555',fontSize:12,textAlign:'center',marginTop:40},
  panel:{width:190,backgroundColor:'rgba(255,255,255,0.04)',borderRadius:14,padding:12,borderWidth:1,borderColor:'rgba(68,204,136,0.2)'},
  panelTitle:{color:'#44cc88',fontSize:13,fontWeight:'800',textAlign:'center',marginBottom:8},
  selInfo:{marginBottom:8},
  selName:{fontSize:14,fontWeight:'800'},
  selSlot:{color:'#888',fontSize:10,marginTop:2},
  selStats:{color:'#aaa',fontSize:10,marginTop:4},
  hint:{color:'#555',fontSize:11,textAlign:'center'},
  panelSub:{color:'#888',fontSize:10,marginTop:8,marginBottom:4},
  heroScroll:{flex:1},
  heroRow:{flexDirection:'row',justifyContent:'space-between',padding:6,borderRadius:6,backgroundColor:'rgba(255,255,255,0.03)',marginBottom:3},
  heroSel:{backgroundColor:'rgba(68,204,136,0.15)',borderWidth:1,borderColor:'#44cc88'},
  heroN:{color:'#fff',fontSize:10,fontWeight:'600'},
  heroS:{fontSize:8},
  equipBtn:{marginTop:8,padding:10,borderRadius:8,backgroundColor:'#44cc88',alignItems:'center'},
  equipTxt:{color:'#080816',fontSize:12,fontWeight:'900'},
});
