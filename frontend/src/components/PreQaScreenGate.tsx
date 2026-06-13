// Pre-QA Stabilization 115D — Screen-Entry / Deeplink Guard component.
//
// Componente riutilizzabile che blocca l'ingresso a una schermata player-facing
// se la sua route e' classificata come unsafe/deferred dal guard centrale
// (`isRouteAllowedInPreQa` + `PRE_QA_BLOCKED_PLAYER_ROUTES`).
//
// Uso (early-return pattern, PRIMA di qualunque fetch/useEffect API):
//
//   import PreQaScreenGate, { isScreenGated } from '../src/components/PreQaScreenGate';
//
//   export default function MyScreen() {
//     if (isScreenGated('/myroute')) return <PreQaScreenGate route="/myroute" />;
//     // ... resto della schermata (safe quando route allowed)
//   }
//
// SAFETY:
// - Fail-closed: se in dubbio, blocca.
// - Nessuna API call, nessun mutation button.
// - Mostra solo navigazione safe: Indietro, Home, Server.
// - Non importa router globalmente per evitare cicli.

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView } from 'react-native';
import { router } from 'expo-router';
import { isRouteAllowedInPreQa, PRE_QA_ROUTE_BLOCKED_TOKEN } from '../utils/preQaNavGuard';

/**
 * Wrapper di convenienza: ritorna true se la route NON e' permessa in pre-QA.
 * Default fail-closed: se la funzione lancia eccezione, ritorna true (gated).
 */
export function isScreenGated(route: string): boolean {
  try {
    return !isRouteAllowedInPreQa(route);
  } catch (_e) {
    return true;
  }
}

export interface PreQaScreenGateProps {
  /** Route canonica della schermata gated (es. '/shop', '/vip'). */
  route: string;
  /** Etichetta human-readable della schermata (opzionale). */
  label?: string;
  /** Mostra opzione "vai ai Server" (default: false). */
  showServersCta?: boolean;
}

export const PreQaScreenGate: React.FC<PreQaScreenGateProps> = ({
  route,
  label,
  showServersCta = false,
}) => {
  const goBack = () => {
    try {
      if (router.canGoBack?.()) {
        router.back();
      } else {
        router.replace('/(tabs)/home' as any);
      }
    } catch (_e) {
      try { router.replace('/(tabs)/home' as any); } catch (_e2) {}
    }
  };
  const goHome = () => {
    try { router.replace('/(tabs)/home' as any); } catch (_e) {}
  };
  const goServers = () => {
    try { router.push('/servers' as any); } catch (_e) {}
  };

  return (
    <SafeAreaView style={st.root}>
      <View style={st.inner}>
        <Text style={st.icon}>{'\uD83D\uDD12'}</Text>
        <Text style={st.title}>Schermata temporaneamente bloccata</Text>
        <Text style={st.subtitle}>
          Questa schermata{label ? ` (${label})` : ''} è classificata come{' '}
          <Text style={st.deferred}>deferred / unsafe</Text> in pre-QA.
          Le funzioni mutanti, gli store live, le ricompense e gli accessi
          account-wide sono disattivati.
        </Text>
        <Text style={st.token}>{PRE_QA_ROUTE_BLOCKED_TOKEN}</Text>
        <Text style={st.routeHint}>route: {route}</Text>

        <View style={st.btnRow}>
          <TouchableOpacity onPress={goBack} style={[st.btn, st.btnPrimary]} activeOpacity={0.85}>
            <Text style={st.btnTxt}>{'\u2190'} Indietro</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={goHome} style={[st.btn, st.btnSecondary]} activeOpacity={0.85}>
            <Text style={st.btnTxt}>Home</Text>
          </TouchableOpacity>
          {showServersCta ? (
            <TouchableOpacity onPress={goServers} style={[st.btn, st.btnSecondary]} activeOpacity={0.85}>
              <Text style={st.btnTxt}>Server</Text>
            </TouchableOpacity>
          ) : null}
        </View>
      </View>
    </SafeAreaView>
  );
};

const st = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0A0820' },
  inner: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
  icon: { fontSize: 48, marginBottom: 16 },
  title: { color: '#FFD27F', fontSize: 20, fontWeight: '700', marginBottom: 16, textAlign: 'center' },
  subtitle: { color: 'rgba(255,255,255,0.78)', fontSize: 14, textAlign: 'center', lineHeight: 20, marginBottom: 14 },
  deferred: { color: '#FF8A4C', fontWeight: '700' },
  token: { color: '#7B2CBF', fontSize: 12, fontFamily: 'monospace', marginBottom: 4, textAlign: 'center' },
  routeHint: { color: 'rgba(255,255,255,0.4)', fontSize: 11, fontFamily: 'monospace', marginBottom: 28, textAlign: 'center' },
  btnRow: { flexDirection: 'row', gap: 12, marginTop: 8, flexWrap: 'wrap', justifyContent: 'center' },
  btn: { paddingHorizontal: 18, paddingVertical: 12, borderRadius: 10, minWidth: 110, alignItems: 'center' },
  btnPrimary: { backgroundColor: '#7B2CBF' },
  btnSecondary: { backgroundColor: 'rgba(255,255,255,0.12)' },
  btnTxt: { color: '#fff', fontWeight: '700' },
});

export default PreQaScreenGate;
