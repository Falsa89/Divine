import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import useServerScope from '../src/hooks/useServerScope';

// v108_pre — Story Launch Path binding.
// Aggiunge il percorso player-facing "Avvia battaglia" → /pre-battle-lobby
// con i parametri richiesti dal Battle Launch Contract v1 (preview, gated).
// L'auto-resolve legacy /api/story/battle resta disponibile ma viene
// etichettato come QA-AutoResolve gated (non più unico percorso giocabile).
// NO reward live, NO progress write, NO backend delete.

const EC: Record<string,string> = { fire:'#ff4444', water:'#4488ff', earth:'#aa8844', wind:'#44cc88', light:'#ffd700', dark:'#9944ff', neutral:'#888' };

export default function StoryScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  // Pack 92 — server scope sweep su story progress reader player-facing.
  const serverScope = useServerScope();
  const selected_server_id = serverScope.isReady ? serverScope.selected_server_id : null;
  const storyServerReady = !!(!serverScope.loading && serverScope.isReady && selected_server_id);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [battling, setBattling] = useState(false);

  useEffect(() => { load(); }, [serverScope.loading, serverScope.isReady, selected_server_id]);
  const load = async () => {
    if (serverScope.loading) {
      setLoading(true);
      return;
    }
    setLoading(true);
    try {
      // Pre-QA Stabilization 115C — fail-closed se manca server_id (no fallback account-wide).
      if (!storyServerReady || !selected_server_id) {
        setData(null);
        return;
      }
      const url = `/api/story/chapters?server_id=${encodeURIComponent(selected_server_id)}`;
      const d = await apiCall(url);
      setData(d);
    } catch(e){} finally { setLoading(false); }
  };

  const doBattle = async (chId: number, stage: number) => {
    if (!storyServerReady || !selected_server_id) {
      router.replace('/servers' as any);
      return;
    }
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

  // v108_pre — Player-facing battle path: Story → Pre-Battle Lobby → /api/battle/launch.
  // Naviga al lobby con i parametri canonici del Battle Launch Contract v1.
  // PREVIEW_NON_AUTHORITATIVE: nessun reward live, nessun progress write in questo step.
  const launchBattleViaLobby = (chId: number, stage: number) => {
    if (!storyServerReady || !selected_server_id) {
      router.replace('/servers' as any);
      return;
    }
    const encounterId = `story_${chId}_${stage}`;
    router.push({
      pathname: '/pre-battle-lobby',
      params: {
        mode: 'story',
        source_id: encounterId,
        encounter_id: encounterId,
        enemy_source_type: 'authored',
        enemy_source_id: encounterId,
        chapter_id: String(chId),
        stage: String(stage),
        server_id: selected_server_id,
        v108_pre: '1',
      },
    });
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  // Pre-QA Stabilization 115C — stato server-required (no fallback account-wide).
  if (!storyServerReady) {
    return (
      <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1, padding: 24, alignItems: 'center', justifyContent: 'center'}}>
        <Text style={{ color: '#FFD27F', fontSize: 18, fontWeight: '700', marginBottom: 12, textAlign: 'center' }}>Server richiesto</Text>
        <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 14, textAlign: 'center', marginBottom: 24 }}>
          La campagna storia richiede un server selezionato. Le superfici account-wide sono disabilitate in pre-QA.
        </Text>
        <TouchableOpacity onPress={() => router.push('/servers' as any)} activeOpacity={0.85}
          style={{ backgroundColor: '#7B2CBF', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10 }}>
          <Text style={{ color: '#fff', fontWeight: '700' }}>Scegli un server</Text>
        </TouchableOpacity>
      </LinearGradient>
    );
  }

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
                <View style={{ flexDirection: 'column', alignItems: 'stretch', gap: 4 }}>
                  {/* v108_pre — pulsante player-facing primario: porta al Pre-Battle Lobby (Battle Launch Contract v1, preview non-authoritative). */}
                  <TouchableOpacity style={[s.playBtn, {backgroundColor:col+'30', borderColor:col}]} onPress={() => launchBattleViaLobby(ch.id, ch.completed_stages+1)} disabled={battling || !storyServerReady}>
                    <Text style={[s.playTxt, {color:col}]}>Avvia battaglia</Text>
                  </TouchableOpacity>
                  {/* v108_POSTQA_A — QA-AutoResolve nascosto dal player-facing. EXPO_PUBLIC_SHOW_QA_AUTO_RESOLVE Visibile SOLO se EXPO_PUBLIC_SHOW_QA_AUTO_RESOLVE === 'true'. Default OFF. */}
                  {process.env.EXPO_PUBLIC_SHOW_QA_AUTO_RESOLVE === 'true' ? (
                    <TouchableOpacity style={[s.qaBtn, {borderColor:'rgba(255,255,255,0.18)'}]} onPress={() => doBattle(ch.id, ch.completed_stages+1)} disabled={battling || !storyServerReady}>
                      <Text style={s.qaTxt}>{battling?'...':'QA Auto Resolve'}</Text>
                    </TouchableOpacity>
                  ) : null}
                </View>
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
  qaBtn:{paddingHorizontal:10,paddingVertical:4,borderRadius:6,borderWidth:1,backgroundColor:'rgba(255,255,255,0.04)'},
  qaTxt:{color:'#888',fontSize:9,fontWeight:'700',letterSpacing:0.5,textAlign:'center'},
});
