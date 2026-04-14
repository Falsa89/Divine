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
          <Stack.Screen name="pvp" options={{ animation: 'slide_from_right' }} />
          <Stack.Screen name="equipment" options={{ animation: 'slide_from_bottom' }} />
          <Stack.Screen name="fusion" options={{ animation: 'slide_from_bottom' }} />
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
          <Stack.Screen name="team-grid" options={{ animation: 'slide_from_bottom' }} />
        </Stack>
        </NotificationProvider>
      </AuthProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#080816' },
});
