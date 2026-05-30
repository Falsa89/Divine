import React, { useEffect } from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { AuthProvider } from '../context/AuthContext';
import { NotificationProvider } from '../context/NotificationContext';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { StyleSheet, Platform } from 'react-native';
import * as ScreenOrientation from 'expo-screen-orientation';

export default function RootLayout() {
  useEffect(() => {
    async function lockLandscape() {
      try {
        await ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.LANDSCAPE);
      } catch (e) {
        // Web doesn't support orientation lock
      }
    }
    lockLandscape();
  }, []);

  return (
    <GestureHandlerRootView style={styles.container}>
      <AuthProvider>
        <NotificationProvider>
        <StatusBar style="light" hidden />
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: '#080816' },
            animation: 'fade',
          }}
        >
          <Stack.Screen name="index" />
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="combat" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="story" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="tower" options={{ animation: 'slide_from_right' }} />
          {/* PUBLIC_SYNC_TAG_RESYNC_v17_LAYOUT_ROUTE: PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX 2026_05_30 — micro-touch JSX comment no-op-safe per forzare blob resnapshot del file _layout.tsx sul public main. Nessuna modifica a behavior/route/gameplay/economy/AsyncStorage/backend. Tower route registration count rimane = 1. Marker: data/design/tower_of_the_hells/tower_layout_route_sync_fix_marker_v1.json. */}
          {/*
            ============================================================================
            PUBLIC_SYNC_TAG_RESYNC_v18_TOWER_LAYOUT_ROUTE
            ============================================================================
            Pack: PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_V2_PACK
            Sentinella: v18 (secondo tentativo dopo v17 stale sul raw pubblico)
            Data UTC: 2026-05-30
            Scopo: forzare un blob resnapshot più forte (ma no-op-safe) del file
                   frontend/app/_layout.tsx sul public main GitHub.
            Tecnica: (a) commento JSX visibile esteso + (b) Stack.Screen Tower
                     convertita da single-line a multiline equivalente con gli
                     STESSI props (name + options.animation). Semantica invariata.
            Garanzie no-op:
              - route registration count di "tower-of-the-hells" resta = 1
              - props identici: name="tower-of-the-hells", animation='slide_from_right'
              - nessun cambio behavior runtime
              - nessun cambio gameplay/economy/AsyncStorage/backend
              - nessun cambio sulle altre Stack.Screen
              - nessun cambio sul suite runner / validator logic
              - nessun cambio sui 5 file MD5-locked
            Marker JSON: data/design/tower_of_the_hells/tower_layout_route_sync_fix_v2_marker_v1.json
            Doc: docs/divine/198_TOWER_LAYOUT_ROUTE_SYNC_FIX_V2.md
            Se questa V2 resta ancora stale sul raw pubblico:
              PROJECT_TOWER_OF_THE_HELLS_LAYOUT_ROUTE_SYNC_FIX_V2_PUBLIC_LAYOUT_STALE_PLATFORM_BUG_PERSISTENT
            ============================================================================
          */}
          <Stack.Screen
            name="tower-of-the-hells"
            options={{ animation: 'slide_from_right' }}
          />
          <Stack.Screen name="pvp" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="equipment" options={{ animation: 'slide_from_bottom' }} />
          <Stack.Screen name="guild" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="events" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="cosmetics" options={{ animation: 'slide_from_bottom' }} />
          <Stack.Screen name="territory" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="plaza" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="raid" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="exclusive" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="rankings" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="shop" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="mail" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="battlepass" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="servers" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="vip" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="friends" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="gvg" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="artifacts" options={{ animation: 'slide_from_bottom' }} />
          <Stack.Screen name="economy" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="achievements" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="hero-detail" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="hero-viewer" options={{ headerShown: false, animation: 'fade' }} />
          <Stack.Screen name="sprite-test" options={{ headerShown: false, animation: 'slide_from_right' }} />
          <Stack.Screen name="soul-forge" options={{ animation: 'slide_from_bottom' }} />
          {/* CS2-E — Read-only preview screen (design-only, no buttons mutativi). */}
          <Stack.Screen name="collection-synergies-preview" options={{ animation: 'slide_from_right' }} />
        </Stack>
        </NotificationProvider>
      </AuthProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#080816' },
});
