import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export default function VIPScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // BATCH_1_V2 Track E \u2014 VIP spend-based senza IAP \u2192 lock claim. Mode preservato
  // come anteprima informativa fino a design IAP completo.
  const VIP_LOCKED_V2 = true;

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/vip'); setData(d); } catch(e){} finally { setLoading(false); } };

  const claimDaily = async () => {
    if (VIP_LOCKED_V2) return; // lock UI safe
    try {
      const r = await apiCall('/api/vip/claim-daily', { method:'POST' });
      await refreshUser(); await load();
    } catch(e:any) {}
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ffd700" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>{"\u2190"}</Text></TouchableOpacity>
        <Text style={s.title}>SISTEMA VIP</Text>
      </View>
      {/* BATCH_1_V2 Track E \u2014 banner lock VIP */}
      {VIP_LOCKED_V2 && (
        <View style={s.lockBannerV2}>
          <Text style={s.lockBannerIconV2}>{'\uD83D\uDD12'}</Text>
          <Text style={s.lockBannerTxtV2}>
            VIP in revisione \u2014 sistema spesa reale (IAP) non ancora implementato.
            Riscossioni VIP temporaneamente disabilitate. Anteprima informativa.
          </Text>
        </View>
      )}
      <View style={s.body}>
        {/* Current VIP */}
        <View style={[s.currentVip, {borderColor:data?.vip_color||'#888'}]}>
          <Text style={[s.vipName, {color:data?.vip_color}]}>{data?.vip_name || 'Free'}</Text>
          <Text style={s.spendTxt}>Spesa totale: {data?.total_spend?.toLocaleString() || 0}</Text>
          {data?.next_level && <Text style={s.nextTxt}>Prossimo: {data.next_level.name} (mancano {data.spend_to_next})</Text>}
          {data?.perks && Object.keys(data.perks).length > 0 && (
            <View style={s.perksList}>
              <Text style={s.perksTitle}>I tuoi bonus:</Text>
              {Object.entries(data.perks).map(([k,v]) => (
                <Text key={k} style={s.perkItem}>{k.replace(/_/g,' ')}: {typeof v === 'boolean' ? '\u2705' : typeof v === 'number' && v < 1 ? `+${(Number(v)*100).toFixed(0)}%` : `+${v}`}</Text>
              ))}
            </View>
          )}
          {data?.can_claim_daily && data?.vip_level > 0 && !VIP_LOCKED_V2 && (
            <TouchableOpacity style={s.claimBtn} onPress={claimDaily}>
              <Text style={s.claimTxt}>Riscuoti Gemme VIP Giornaliere</Text>
            </TouchableOpacity>
          )}
        </View>
        {/* All VIP Levels */}
        <ScrollView style={s.levels}>
          {data?.all_levels?.map((vl:any) => (
            <View key={vl.level} style={[s.lvlCard, {borderColor:vl.color}, data?.vip_level===vl.level && s.lvlActive]}>
              <View style={[s.lvlBadge, {backgroundColor:vl.color+'25'}]}>
                <Text style={[s.lvlNum, {color:vl.color}]}>{vl.level}</Text>
              </View>
              <View style={s.lvlInfo}>
                <Text style={[s.lvlName, {color:vl.color}]}>{vl.name}</Text>
                <Text style={s.lvlReq}>Spesa minima: {vl.min_spend.toLocaleString()}</Text>
              </View>
              <View style={s.lvlPerks}>
                {Object.entries(vl.perks).slice(0,3).map(([k,v]) => (
                  <Text key={k} style={s.perkSmall}>{k.replace(/_/g,' ')}: {typeof v === 'boolean' ? '\u2705' : typeof v === 'number' && Number(v) < 1 ? `+${(Number(v)*100).toFixed(0)}%` : `+${v}`}</Text>
                ))}
              </View>
              {data?.vip_level === vl.level && <Text style={s.youBadge}>TU</Text>}
            </View>
          ))}
        </ScrollView>
      </View>
    </LinearGradient>
  );
}

const s = StyleSheet.create({
  c:{flex:1,backgroundColor:'transparent'},
  hdr:{flexDirection:'row',alignItems:'center',gap:12,paddingHorizontal:16,paddingVertical:8,borderBottomWidth:1,borderBottomColor:'rgba(255,215,0,0.2)'},
  back:{color:'#ffd700',fontSize:20,fontWeight:'700'},
  title:{color:'#ffd700',fontSize:16,fontWeight:'800',letterSpacing:2},
  body:{flex:1,flexDirection:'row',padding:10,gap:10},
  currentVip:{width:200,padding:14,borderRadius:12,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:2,alignItems:'center'},
  vipName:{fontSize:22,fontWeight:'900',letterSpacing:2},
  spendTxt:{color:'#888',fontSize:11,marginTop:4},
  nextTxt:{color:'#ffd700',fontSize:10,marginTop:4},
  perksList:{marginTop:10,width:'100%'},
  perksTitle:{color:'#fff',fontSize:11,fontWeight:'700',marginBottom:4},
  perkItem:{color:'#44cc44',fontSize:10,marginTop:1},
  claimBtn:{marginTop:10,padding:8,borderRadius:8,backgroundColor:'rgba(255,215,0,0.2)',borderWidth:1,borderColor:'#ffd700'},
  claimTxt:{color:'#ffd700',fontSize:10,fontWeight:'700'},
  levels:{flex:1},
  lvlCard:{flexDirection:'row',alignItems:'center',padding:8,borderRadius:8,backgroundColor:'rgba(255,255,255,0.03)',borderWidth:1,marginBottom:4,gap:8},
  lvlActive:{backgroundColor:'rgba(255,215,0,0.08)'},
  lvlBadge:{width:32,height:32,borderRadius:16,alignItems:'center',justifyContent:'center'},
  lvlNum:{fontSize:14,fontWeight:'900'},
  lvlInfo:{flex:1},
  lvlName:{fontSize:12,fontWeight:'800'},
  lvlReq:{color:'#888',fontSize:9},
  lvlPerks:{width:120},
  perkSmall:{color:'#aaa',fontSize:8},
  youBadge:{color:'#ff6b35',fontSize:10,fontWeight:'900',backgroundColor:'rgba(255,107,53,0.2)',paddingHorizontal:6,paddingVertical:2,borderRadius:4},
  // BATCH_1_V2 Track E
  lockBannerV2:{flexDirection:'row',gap:8,alignItems:'center',paddingHorizontal:12,paddingVertical:10,marginHorizontal:12,marginTop:8,marginBottom:4,borderRadius:8,backgroundColor:'rgba(255,165,0,0.10)',borderWidth:1,borderColor:'rgba(255,165,0,0.45)'},
  lockBannerIconV2:{fontSize:18},
  lockBannerTxtV2:{flex:1,color:'#FFD089',fontSize:11,lineHeight:16,fontWeight:'600'},
});
