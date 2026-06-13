/**
 * v96 — Login screen.
 *
 * Pack: MEGA_RELEASE_ACCELERATION_45_v96.
 *
 * Implementa UI per Continue with Google / Sign in with Apple / Guest QA.
 *
 * Safety:
 *  - Apple bottone visibile solo su iOS (Platform.OS === 'ios').
 *  - Provider status mostrato esplicitamente:
 *    - READY
 *    - CREDENTIALS_REQUIRED_FOR_STORE_BUILD (sandbox)
 *  - NESSUN raw OAuth token loggato.
 *  - Token gestito da expo-secure-store via AuthContext.
 *  - Guest visibile solo se gated_qa_only abilitato.
 *  - Branding: testi neutri "Continua con Google" / "Accedi con Apple"
 *    (in produzione reale richiede asset ufficiali Google/Apple per superare lo store review).
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  Platform,
  ActivityIndicator,
  TextInput,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { useAuth } from '../src/auth/AuthContext';

export default function LoginScreen() {
  const router = useRouter();
  const auth = useAuth();
  const [aliasHint, setAliasHint] = useState<string>('');

  const providerStatusGoogle = auth.providerStatus?.google?.status || 'unknown';
  const providerStatusApple = auth.providerStatus?.apple?.status || 'unknown';
  const guestEnabled = !!auth.providerStatus?.guest?.enabled;

  const onLoginGoogle = async () => {
    // Pre-QA Stabilization 115C: post-login route → /servers (server scope unification).
    await auth.login('google', { sandbox_subject: `g_qa_${Date.now()}` });
    if (auth.authenticated) router.replace('/servers' as any);
  };
  const onLoginApple = async () => {
    await auth.login('apple', { sandbox_subject: `a_qa_${Date.now()}` });
    if (auth.authenticated) router.replace('/servers' as any);
  };
  const onLoginGuest = async () => {
    await auth.login('guest', { alias_hint: aliasHint || undefined });
    if (auth.authenticated) router.replace('/servers' as any);
  };

  // Se già loggato, redirect
  if (auth.authenticated && auth.account) {
    return (
      <SafeAreaView style={s.safe}>
        <LinearGradient colors={['#0A1430', '#1F1240']} style={s.bg}>
          <View style={s.center}>
            <Text style={s.title}>Già autenticato</Text>
            <Text style={s.alias}>Alias: {auth.account.alias}</Text>
            <Text style={s.providerLine}>Provider: {auth.account.provider}{auth.account.provider_sandbox ? ' (sandbox)' : ''}</Text>
            <TouchableOpacity style={s.primaryBtn} onPress={() => router.replace('/servers' as any)} activeOpacity={0.85}>
              <Text style={s.btnTxt}>Entra nel gioco</Text>
            </TouchableOpacity>
            <TouchableOpacity style={s.secondaryBtn} onPress={auth.logout} activeOpacity={0.85}>
              <Text style={s.btnTxtSec}>Logout</Text>
            </TouchableOpacity>
          </View>
        </LinearGradient>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={s.safe}>
      <LinearGradient colors={['#0A1430', '#1F1240']} style={s.bg}>
        <ScrollView contentContainerStyle={s.scroll}>
          <View style={s.header}>
            <Text style={s.title}>Accedi</Text>
            <Text style={s.subtitle}>v96 · Auth · Release Candidate Final</Text>
          </View>

          {/* Provider status */}
          <View style={s.card}>
            <Text style={s.cardTitle}>Provider Status</Text>
            <Text style={s.kv}>Google: <Text style={statusColor(providerStatusGoogle)}>{providerStatusGoogle}</Text></Text>
            <Text style={s.kv}>Apple: <Text style={statusColor(providerStatusApple)}>{providerStatusApple}</Text></Text>
            <Text style={s.kv}>Guest QA: <Text style={{ color: guestEnabled ? '#9FE3A2' : '#FF9090' }}>{guestEnabled ? 'enabled' : 'disabled'}</Text></Text>
            {(providerStatusGoogle === 'CREDENTIALS_REQUIRED_FOR_STORE_BUILD' || providerStatusApple === 'CREDENTIALS_REQUIRED_FOR_STORE_BUILD') && (
              <Text style={s.warnLine}>
                ⚠ Provider in modalità sandbox. Per build store reale servono GOOGLE_CLIENT_ID e APPLE_CLIENT_ID nel backend.
              </Text>
            )}
          </View>

          {/* Loading */}
          {auth.loading && (
            <View style={s.loadingBox}>
              <ActivityIndicator color="#FFD700" />
              <Text style={s.loadingTxt}>Autenticazione in corso…</Text>
            </View>
          )}

          {/* Error */}
          {auth.error && (
            <View style={s.errorBox}>
              <Text style={s.errorTxt}>Errore: {auth.error}</Text>
            </View>
          )}

          {/* Google */}
          <TouchableOpacity
            style={[s.providerBtn, s.googleBtn]}
            onPress={onLoginGoogle}
            disabled={auth.loading}
            activeOpacity={0.85}
          >
            <Text style={s.providerEmoji}>🟢</Text>
            <Text style={s.providerBtnTxt}>Continua con Google</Text>
          </TouchableOpacity>

          {/* Apple — iOS only */}
          {Platform.OS === 'ios' && (
            <TouchableOpacity
              style={[s.providerBtn, s.appleBtn]}
              onPress={onLoginApple}
              disabled={auth.loading}
              activeOpacity={0.85}
            >
              <Text style={s.providerEmoji}> </Text>
              <Text style={s.providerBtnTxt}>Accedi con Apple</Text>
            </TouchableOpacity>
          )}
          {Platform.OS !== 'ios' && (
            <View style={s.appleAndroidNote}>
              <Text style={s.appleAndroidTxt}>
                Sign in with Apple disponibile solo su iOS (policy ufficiale).
              </Text>
            </View>
          )}

          {/* Guest QA */}
          {guestEnabled && (
            <View style={s.guestBox}>
              <Text style={s.guestTitle}>Guest / QA Login</Text>
              <Text style={s.guestNote}>Per test interni. Marker provider_sandbox=true.</Text>
              <TextInput
                style={s.input}
                placeholder="alias (opzionale, max 24)"
                placeholderTextColor="#777"
                maxLength={24}
                value={aliasHint}
                onChangeText={setAliasHint}
              />
              <TouchableOpacity style={s.guestBtn} onPress={onLoginGuest} disabled={auth.loading} activeOpacity={0.85}>
                <Text style={s.btnTxt}>Entra come Guest</Text>
              </TouchableOpacity>
            </View>
          )}

          {/* Safety */}
          <View style={s.safetyBox}>
            <Text style={s.safetyTitle}>🔒 Safety Notes</Text>
            <Text style={s.safetyLine}>• Nessun token raw OAuth viene loggato.</Text>
            <Text style={s.safetyLine}>• Provider secret NON committati nel repo.</Text>
            <Text style={s.safetyLine}>• Session token in expo-secure-store.</Text>
            <Text style={s.safetyLine}>• Provider sandbox marcato esplicitamente.</Text>
          </View>
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

function statusColor(status: string) {
  if (status === 'READY') return { color: '#9FE3A2' };
  if (status === 'CREDENTIALS_REQUIRED_FOR_STORE_BUILD') return { color: '#FFB347' };
  return { color: '#999' };
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0A1430' },
  bg: { flex: 1 },
  scroll: { padding: 20, paddingBottom: 48 },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  header: { marginBottom: 18, alignItems: 'center' },
  title: { color: '#FFD700', fontSize: 28, fontWeight: '800' },
  subtitle: { color: '#AAB', fontSize: 12, marginTop: 4 },
  alias: { color: '#FFF', fontSize: 18, marginTop: 8 },
  providerLine: { color: '#9FE3A2', marginTop: 4 },
  card: { backgroundColor: 'rgba(20,40,80,0.7)', borderRadius: 12, padding: 14, marginBottom: 14, borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)' },
  cardTitle: { color: '#FFD700', fontSize: 14, fontWeight: '700', marginBottom: 8 },
  kv: { color: '#DDE', fontSize: 13, marginVertical: 2 },
  warnLine: { color: '#FFB347', fontSize: 12, marginTop: 8 },
  loadingBox: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginVertical: 8 },
  loadingTxt: { color: '#FFD700', marginLeft: 8 },
  errorBox: { backgroundColor: 'rgba(120,30,30,0.6)', padding: 10, borderRadius: 8, marginBottom: 8 },
  errorTxt: { color: '#FFB0B0', fontSize: 12 },
  providerBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderRadius: 10, paddingVertical: 14, marginBottom: 10, borderWidth: 1, borderColor: 'rgba(255,255,255,0.18)', minHeight: 48 },
  googleBtn: { backgroundColor: '#FFFFFF' },
  appleBtn: { backgroundColor: '#000000' },
  providerEmoji: { fontSize: 18, marginRight: 8 },
  providerBtnTxt: { color: '#222', fontSize: 16, fontWeight: '600' },
  appleAndroidNote: { backgroundColor: 'rgba(30,30,40,0.7)', borderRadius: 8, padding: 10, marginBottom: 10 },
  appleAndroidTxt: { color: '#AAB', fontSize: 12, textAlign: 'center' },
  guestBox: { backgroundColor: 'rgba(60,40,80,0.5)', borderRadius: 10, padding: 12, marginTop: 6 },
  guestTitle: { color: '#FFD700', fontSize: 14, fontWeight: '700' },
  guestNote: { color: '#BBC', fontSize: 11, marginVertical: 4 },
  input: { backgroundColor: 'rgba(0,0,0,0.4)', color: '#FFF', borderRadius: 8, padding: 10, marginVertical: 8, fontSize: 14 },
  guestBtn: { backgroundColor: '#7050A0', padding: 12, borderRadius: 8, alignItems: 'center', minHeight: 48 },
  primaryBtn: { backgroundColor: '#FFD700', padding: 14, borderRadius: 8, marginTop: 16, paddingHorizontal: 32 },
  secondaryBtn: { padding: 12, marginTop: 8 },
  btnTxt: { color: '#222', fontWeight: '700' },
  btnTxtSec: { color: '#AAB' },
  safetyBox: { marginTop: 24, padding: 12, backgroundColor: 'rgba(10,20,40,0.6)', borderRadius: 8 },
  safetyTitle: { color: '#9FE3A2', fontSize: 12, fontWeight: '700' },
  safetyLine: { color: '#AAB', fontSize: 11, marginTop: 4 },
});
