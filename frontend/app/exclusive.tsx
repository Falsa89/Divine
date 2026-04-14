import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const RC: Record<number,string> = { 1:'#888', 2:'#44aa44', 3:'#4488ff', 4:'#aa44ff', 5:'#ff4444', 6:'#ffd700' };
const SLOT_ICONS: Record<string,string> = { weapon:'\uD83D\uDDE1\uFE0F', armor:'\uD83D\uDEE1\uFE0F', accessory:'\uD83D\uDC8D', rune:'\uD83D\uDD2E' };

export default function ExclusiveItemsScreen() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [crafting, setCrafting] = useState('');

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/exclusive-items'); setItems(d); } catch(e){} finally { setLoading(false); } };

  const craft = async (heroName: string) => {
    setCrafting(heroName);
    try {
      const r = await apiCall('/api/exclusive-items/craft', { method:'POST', body: JSON.stringify({hero_name:heroName}) });
      await refreshUser(); await load();
      Alert.alert('Oggetto Creato!', `${r.item?.name} e ora nel tuo inventario!`);
    } catch(e:any) { Alert.alert('Errore', e.message); } finally { setCrafting(''); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ffd700" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>{"\u2190"}</Text></TouchableOpacity>
        <Text style={s.title}>OGGETTI ESCLUSIVI</Text>
        <Text style={s.res}>{"\uD83D\uDCB0"} {(user?.gold||0).toLocaleString()} | {"\uD83D\uDC8E"} {user?.gems}</Text>
      </View>
      <ScrollView contentContainerStyle={s.list}>
        {items.map((ei:any, idx:number) => {
          const col = RC[ei.item.rarity] || '#888';
          return (
            <View key={idx} style={[s.card, {borderColor:col}, !ei.hero_owned && {opacity:0.4}]}>
              <View style={s.cardTop}>
                <Text style={s.itemIcon}>{SLOT_ICONS[ei.item.slot] || '\u2728'}</Text>
                <View style={s.cardInfo}>
                  <Text style={[s.itemName, {color:col}]}>{ei.item.name}</Text>
                  <Text style={s.heroFor}>Esclusivo di: <Text style={{color:'#ff6b35',fontWeight:'700'}}>{ei.hero_name}</Text></Text>
                  <Text style={s.itemDesc}>{ei.item.description}</Text>
                </View>
              </View>
              <View style={s.statsRow}>
                {Object.entries(ei.item.stats||{}).map(([k,v]) => (
                  <View key={k} style={s.statBadge}>
                    <Text style={s.statKey}>{k.toUpperCase()}</Text>
                    <Text style={[s.statVal, {color: Number(v) > 0 ? '#44cc44' : '#ff4444'}]}>{Number(v) > 0 ? '+' : ''}{v}</Text>
                  </View>
                ))}
              </View>
              <View style={s.bottom}>
                <Text style={s.rarityTxt}>{'\u2B50'.repeat(ei.item.rarity)} {ei.item.slot.toUpperCase()}</Text>
                {ei.item_owned ? (
                  <Text style={s.ownedTxt}>\u2705 Posseduto</Text>
                ) : ei.hero_owned ? (
                  <TouchableOpacity style={[s.craftBtn, {borderColor:col}, crafting===ei.hero_name&&{opacity:0.5}]} onPress={() => craft(ei.hero_name)} disabled={crafting===ei.hero_name}>
                    <Text style={[s.craftTxt, {color:col}]}>{crafting===ei.hero_name ? '...' : `FORGIA (${ei.item.rarity>=6?'50K/150':'20K/50'} ${"\uD83D\uDC8E"})`}</Text>
                  </TouchableOpacity>
                ) : (
                  <Text style={s.lockedTxt}>\uD83D\uDD12 Ottieni {ei.hero_name} prima</Text>
                )}
              </View>
            </View>
          );
        })}
      </ScrollView>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(255,215,0,0.3)'},
  back:{color:'#ffd700',fontSize:20,fontWeight:'700'},
  title:{color:'#ffd700',fontSize:16,fontWeight:'800',letterSpacing:2,flex:1},
  res:{color:'#888',fontSize:10},
  list:{padding:10,gap:8},
  card:{padding:10,borderRadius:12,backgroundColor:'rgba(255,255,255,0.03)',borderWidth:1.5,gap:6},
  cardTop:{flexDirection:'row',gap:10},
  itemIcon:{fontSize:28},
  cardInfo:{flex:1},
  itemName:{fontSize:14,fontWeight:'900'},
  heroFor:{color:'#aaa',fontSize:10,marginTop:1},
  itemDesc:{color:'#888',fontSize:9,marginTop:2,fontStyle:'italic'},
  statsRow:{flexDirection:'row',gap:6,flexWrap:'wrap'},
  statBadge:{backgroundColor:'rgba(255,255,255,0.05)',paddingHorizontal:8,paddingVertical:3,borderRadius:6},
  statKey:{color:'#888',fontSize:8,fontWeight:'600'},
  statVal:{fontSize:10,fontWeight:'800'},
  bottom:{flexDirection:'row',justifyContent:'space-between',alignItems:'center'},
  rarityTxt:{color:'#888',fontSize:9},
  ownedTxt:{color:'#44cc44',fontSize:11,fontWeight:'700'},
  craftBtn:{paddingHorizontal:12,paddingVertical:6,borderRadius:6,borderWidth:1.5},
  craftTxt:{fontSize:10,fontWeight:'800'},
  lockedTxt:{color:'#888',fontSize:10},
});
