import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../constants/theme';
import { useRouter } from 'expo-router';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export default function MailScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [mails, setMails] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);
  const load = async () => { try { const d = await apiCall('/api/mail'); setMails(d); } catch(e){} finally { setLoading(false); } };

  const claim = async (mailId: string) => {
    try {
      const r = await apiCall(`/api/mail/claim/${mailId}`, { method:'POST' });
      await refreshUser(); await load();
      const rw = Object.entries(r.rewards||{}).map(([k,v]) => `${k}: +${v}`).join(', ');
      Alert.alert('Ricompense Riscossse!', rw || 'Nessuna ricompensa');
    } catch(e:any) { Alert.alert('Errore', e.message); }
  };

  if (loading) return <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}><ActivityIndicator size="large" color="#ff6b35" /></LinearGradient>;

  return (
    <LinearGradient colors={[COLORS.bgPrimary, '#0D0D2B', '#0A0820']} style={{flex: 1}}>
      <View style={s.hdr}>
        <TouchableOpacity onPress={() => router.back()}><Text style={s.back}>\u2190</Text></TouchableOpacity>
        <Text style={s.title}>POSTA</Text>
        <Text style={s.cnt}>{mails.filter(m=>!m.claimed).length} non lette</Text>
      </View>
      <ScrollView contentContainerStyle={s.list}>
        {mails.length === 0 && <Text style={s.empty}>Nessuna mail. Gioca per ricevere ricompense!</Text>}
        {mails.map((m:any) => (
          <View key={m.id||m._id} style={[s.card, m.claimed && s.cardClaimed]}>
            <View style={s.mailIcon}><Text style={s.mailEmoji}>{m.claimed ? '\uD83D\uDCE8' : '\uD83D\uDCE9'}</Text></View>
            <View style={s.mailInfo}>
              <Text style={s.mailSubject}>{m.subject || 'Ricompensa'}</Text>
              <Text style={s.mailBody}>{m.body || ''}</Text>
              {m.rewards && Object.keys(m.rewards).length > 0 && (
                <Text style={s.mailRewards}>Ricompense: {Object.entries(m.rewards).map(([k,v]) => `${k}: ${v}`).join(', ')}</Text>
              )}
              <Text style={s.mailDate}>{m.timestamp ? new Date(m.timestamp).toLocaleDateString('it') : ''}</Text>
            </View>
            {!m.claimed && m.rewards && Object.keys(m.rewards).length > 0 && (
              <TouchableOpacity style={s.claimBtn} onPress={() => claim(m.id)}>
                <Text style={s.claimTxt}>Riscuoti</Text>
              </TouchableOpacity>
            )}
            {m.claimed && <Text style={s.claimedTxt}>\u2705</Text>}
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
  cnt:{color:'#ff6b35',fontSize:11,fontWeight:'600'},
  list:{padding:10,gap:6},
  empty:{color:'#555',fontSize:12,textAlign:'center',marginTop:40},
  card:{flexDirection:'row',alignItems:'center',padding:10,borderRadius:10,backgroundColor:'rgba(255,255,255,0.04)',borderWidth:1,borderColor:'rgba(255,255,255,0.08)',gap:10},
  cardClaimed:{opacity:0.5},
  mailIcon:{width:36,height:36,borderRadius:8,backgroundColor:'rgba(255,107,53,0.1)',alignItems:'center',justifyContent:'center'},
  mailEmoji:{fontSize:20},
  mailInfo:{flex:1},
  mailSubject:{color:'#fff',fontSize:12,fontWeight:'700'},
  mailBody:{color:'#aaa',fontSize:10,marginTop:1},
  mailRewards:{color:'#ffd700',fontSize:9,marginTop:2},
  mailDate:{color:'#555',fontSize:8,marginTop:2},
  claimBtn:{paddingHorizontal:12,paddingVertical:6,borderRadius:6,backgroundColor:'#ff6b35'},
  claimTxt:{color:'#fff',fontSize:10,fontWeight:'800'},
  claimedTxt:{fontSize:16},
});
