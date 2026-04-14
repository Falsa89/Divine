import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export default function BattlePassScreen() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/battlepass'); setData(d); } catch(e){} finally { setLoading(false); } };

  const claim = async (level: number) => {
    try {
      const r = await apiCall(`/api/battlepass/claim/${level}`, { method:'POST' });
      await refreshUser(); await load();
      const rw = Object.entries(r.rewards||{}).map(([k,v]) => `${k}: +${v}`).join(', ');
      Alert.alert('Ricompensa Riscossa!', rw);
    } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  const buyPremium = async () => {
    try {
      await apiCall('/api/battlepass/buy-premium', { method:'POST' });
      await refreshUser(); await load();
      Alert.alert('Pass Premium Attivato!', 'Ora puoi riscuotere tutte le ricompense premium!');
    } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  const level = data?.current_level || 1;
  const exp = data?.current_exp || 0;
  const expNext = data?.exp_to_next || 500;
  const isPremium = data?.is_premium;
  const claimedFree = data?.claimed_free || [];
  const claimedPremium = data?.claimed_premium || [];

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>\u2190</Text></TouchableOpacity>
        <Text style={s.title}>BATTLE PASS</Text>
        <Text style={s.season}>Stagione {data?.season || 1}</Text>
      </View>
      {/* Level & EXP bar */}
      <View style={s.levelBar}>
        <Text style={s.levelTxt}>Lv.{level}</Text>
        <View style={s.expBarBg}>
          <View style={[s.expBarFill, {width:`${Math.min(100,(exp/expNext)*100)}%`}]} />
        </View>
        <Text style={s.expTxt}>{exp}/{expNext} EXP</Text>
        {!isPremium && (
          <TouchableOpacity style={s.premiumBtn} onPress={buyPremium}>
            <Text style={s.premiumTxt}>\uD83D\uDC8E 500 - PREMIUM</Text>
          </TouchableOpacity>
        )}
        {isPremium && <View style={s.premBadge}><Text style={s.premBadgeTxt}>\u2B50 PREMIUM</Text></View>}
      </View>
      {/* Rewards */}
      <ScrollView contentContainerStyle={s.rewards}>
        {data?.rewards?.map((r:any) => {
          const unlocked = r.level <= level;
          const freeClaimed = claimedFree.includes(r.level);
          const premClaimed = claimedPremium.includes(r.level);
          const canClaim = unlocked && (!freeClaimed || (isPremium && !premClaimed));
          return (
            <View key={r.level} style={[s.rewardRow, !unlocked && {opacity:0.35}]}>
              <View style={[s.levelBadge, unlocked && {backgroundColor:'rgba(255,107,53,0.2)',borderColor:'#ff6b35'}]}>
                <Text style={[s.levelNum, unlocked && {color:'#ff6b35'}]}>{r.level}</Text>
              </View>
              {/* Free */}
              <View style={[s.rewardBox, freeClaimed && s.rewardClaimed]}>
                <Text style={s.rewardLabel}>GRATIS</Text>
                {Object.entries(r.free).map(([k,v]) => <Text key={k} style={s.rewardVal}>{k}: +{(v as number).toLocaleString()}</Text>)}
                {freeClaimed && <Text style={s.checkMark}>\u2705</Text>}
              </View>
              {/* Premium */}
              <View style={[s.rewardBox, s.rewardPrem, premClaimed && s.rewardClaimed, !isPremium && {opacity:0.4}]}>
                <Text style={[s.rewardLabel, {color:'#ffd700'}]}>\u2B50 PREMIUM</Text>
                {Object.entries(r.premium).map(([k,v]) => <Text key={k} style={[s.rewardVal, {color:'#ffd700'}]}>{k}: +{(v as number).toLocaleString()}</Text>)}
                {premClaimed && <Text style={s.checkMark}>\u2705</Text>}
                {!isPremium && <Text style={s.lockIcon}>\uD83D\uDD12</Text>}
              </View>
              {/* Claim button */}
              {canClaim && (
                <TouchableOpacity style={s.claimBtn} onPress={() => claim(r.level)}>
                  <Text style={s.claimTxt}>Riscuoti</Text>
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
  season:{color:'#ffd700',fontSize:11,fontWeight:'600'},
  levelBar:{flexDirection:'row',alignItems:'center',gap:8,paddingHorizontal:12,paddingVertical:6,borderBottomWidth:1,borderBottomColor:'rgba(255,255,255,0.05)'},
  levelTxt:{color:'#ff6b35',fontSize:16,fontWeight:'900'},
  expBarBg:{flex:1,height:8,backgroundColor:'rgba(255,255,255,0.08)',borderRadius:4,overflow:'hidden'},
  expBarFill:{height:'100%',backgroundColor:'#ff6b35',borderRadius:4},
  expTxt:{color:'#888',fontSize:10},
  premiumBtn:{paddingHorizontal:12,paddingVertical:4,borderRadius:6,backgroundColor:'rgba(255,215,0,0.2)',borderWidth:1,borderColor:'#ffd700'},
  premiumTxt:{color:'#ffd700',fontSize:9,fontWeight:'800'},
  premBadge:{paddingHorizontal:10,paddingVertical:3,borderRadius:6,backgroundColor:'rgba(255,215,0,0.15)'},
  premBadgeTxt:{color:'#ffd700',fontSize:10,fontWeight:'800'},
  rewards:{padding:8,gap:4},
  rewardRow:{flexDirection:'row',alignItems:'center',gap:6,paddingVertical:4},
  levelBadge:{width:28,height:28,borderRadius:14,backgroundColor:'rgba(255,255,255,0.05)',borderWidth:1,borderColor:'rgba(255,255,255,0.1)',alignItems:'center',justifyContent:'center'},
  levelNum:{color:'#888',fontSize:12,fontWeight:'900'},
  rewardBox:{flex:1,padding:6,borderRadius:8,backgroundColor:'rgba(255,255,255,0.03)',borderWidth:1,borderColor:'rgba(255,255,255,0.06)'},
  rewardPrem:{borderColor:'rgba(255,215,0,0.15)',backgroundColor:'rgba(255,215,0,0.03)'},
  rewardClaimed:{opacity:0.4},
  rewardLabel:{color:'#888',fontSize:7,fontWeight:'700',letterSpacing:0.5},
  rewardVal:{color:'#ccc',fontSize:10,fontWeight:'600'},
  checkMark:{position:'absolute',right:4,top:4,fontSize:12},
  lockIcon:{position:'absolute',right:4,top:4,fontSize:10},
  claimBtn:{paddingHorizontal:10,paddingVertical:6,borderRadius:6,backgroundColor:'#ff6b35'},
  claimTxt:{color:'#fff',fontSize:9,fontWeight:'800'},
});
