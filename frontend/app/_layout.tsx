import React, { useEffect, useMemo, useState } from 'react';
import { Stack, useGlobalSearchParams, usePathname, useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { AuthProvider } from '../context/AuthContext';
import { AuthProvider as V96AuthProvider } from '../src/auth/AuthContext';
import { NotificationProvider } from '../context/NotificationContext';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import * as ScreenOrientation from 'expo-screen-orientation';
import { normalizeRoute } from '../src/utils/preQaNavGuard';
import { interceptDeeplink } from '../src/utils/preQaDeeplinkGuard';
import { verifySelectedServerScopeReadOnly } from '../src/hooks/useServerScope';

const SERVER_GATE_EXEMPT_ROUTES = new Set<string>([
  '/',
  '/index',
  '/login',
  '/register',
  '/servers',
]);
const PRE_QA_ROUTE_GUARD_SAFE_REDIRECT = '/story';

function buildPreQaGuardUrl(
  pathname: string | null | undefined,
  params: Record<string, string | string[] | undefined>,
): string {
  const path = pathname || '/';
  const query = Object.keys(params || {})
    .sort()
    .flatMap((key) => {
      const value = params[key];
      const values = Array.isArray(value) ? value : [value];
      return values
        .filter((v): v is string => v !== undefined && v !== null)
        .map((v) => `${encodeURIComponent(key)}=${encodeURIComponent(String(v))}`);
    })
    .join('&');
  return query ? `${path}?${query}` : path;
}

function routeRequiresVerifiedServer(pathname: string | null | undefined): boolean {
  const normalized = normalizeRoute(pathname || '');
  if (!normalized || SERVER_GATE_EXEMPT_ROUTES.has(normalized)) return false;
  if (normalized.startsWith('/_sitemap')) return false;
  return true;
}

function GlobalServerGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const params = useGlobalSearchParams<Record<string, string | string[] | undefined>>();
  const routeGuardUrl = useMemo(
    () => buildPreQaGuardUrl(pathname, params),
    [pathname, params],
  );
  const routeGuard = useMemo(() => interceptDeeplink(routeGuardUrl), [routeGuardUrl]);
  const routeAllowed = routeGuard.decision === 'ALLOW';
  const requiresServer = routeRequiresVerifiedServer(pathname);
  const [gateState, setGateState] = useState({
    pathname: '',
    allowed: false,
  });
  const gateReady =
    !requiresServer ||
    (gateState.allowed && gateState.pathname === pathname);

  useEffect(() => {
    if (routeAllowed) return;
    setGateState({ pathname: pathname || '', allowed: false });
    const safeRedirect = routeGuard.safeRedirect || PRE_QA_ROUTE_GUARD_SAFE_REDIRECT;
    const blockedUrlHasQuery = routeGuardUrl.includes('?');
    if (blockedUrlHasQuery || normalizeRoute(safeRedirect) !== normalizeRoute(pathname || '')) {
      router.replace(safeRedirect as any);
    }
  }, [pathname, routeAllowed, routeGuard.safeRedirect, routeGuardUrl, router]);

  useEffect(() => {
    if (!routeAllowed) {
      setGateState({ pathname: pathname || '', allowed: false });
      return;
    }
    let alive = true;
    async function verify() {
      if (!requiresServer) {
        setGateState({ pathname: pathname || '', allowed: true });
        return;
      }
      setGateState({ pathname: pathname || '', allowed: false });
      const result = await verifySelectedServerScopeReadOnly();
      if (!alive) return;
      if (result.ok) {
        setGateState({ pathname: pathname || '', allowed: true });
      } else {
        router.replace('/servers');
      }
    }
    verify().catch(() => {
      if (alive) router.replace('/servers');
    });
    return () => {
      alive = false;
    };
  }, [pathname, requiresServer, routeAllowed, router]);

  if (!routeAllowed || (requiresServer && !gateReady)) {
    return (
      <View style={styles.gateContainer}>
        <ActivityIndicator color="#FF6B35" />
      </View>
    );
  }

  return <>{children}</>;
}

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
        <V96AuthProvider>
        <NotificationProvider>
        <GlobalServerGate>
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
          {/* v96 — Login screen (Google/Apple/Guest) */}
          <Stack.Screen name="login" options={{ animation: 'fade' }} />
        </Stack>
        </GlobalServerGate>
        </NotificationProvider>
        </V96AuthProvider>
      </AuthProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#080816' },
  gateContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#080816',
  },
});
