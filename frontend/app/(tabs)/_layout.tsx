import React from 'react';
import { Tabs } from 'expo-router';
import { View, Text, StyleSheet, Platform } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
  useAnimatedStyle, withTiming, useSharedValue, withSpring,
} from 'react-native-reanimated';
import { COLORS } from '../../constants/theme';

function TabIcon({ label, icon, focused }: { label: string; icon: string; focused: boolean }) {
  return (
    <View style={[st.tabItem]}>
      {focused && (
        <LinearGradient
          colors={['rgba(255,107,53,0.25)', 'rgba(255,107,53,0.0)']}
          style={st.tabGlow}
          start={{ x: 0.5, y: 0 }}
          end={{ x: 0.5, y: 1 }}
        />
      )}
      <View style={[st.iconWrap, focused && st.iconWrapActive]}>
        <Text style={[st.tabIcon, focused && st.tabIconActive]}>{icon}</Text>
      </View>
      <Text style={[st.tabLabel, focused && st.tabLabelActive]}>{label}</Text>
      {focused && <View style={st.activeIndicator} />}
    </View>
  );
}

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarShowLabel: false,
        tabBarActiveTintColor: COLORS.accent,
        tabBarInactiveTintColor: '#555',
        tabBarStyle: st.tabBar,
        tabBarBackground: () => (
          <LinearGradient
            colors={[COLORS.gradientTabBar[0], COLORS.gradientTabBar[1]]}
            style={StyleSheet.absoluteFill}
            start={{ x: 0, y: 0 }}
            end={{ x: 0, y: 1 }}
          />
        ),
      }}
    >
      <Tabs.Screen name="home" options={{ tabBarIcon: ({ focused }) => <TabIcon label="Home" icon={"\u2302"} focused={focused} /> }} />
      <Tabs.Screen name="heroes" options={{ tabBarIcon: ({ focused }) => <TabIcon label="Eroi" icon={"\u2694\uFE0F"} focused={focused} /> }} />
      <Tabs.Screen name="battle" options={{ tabBarIcon: ({ focused }) => <TabIcon label="Battaglia" icon={"\uD83D\uDD25"} focused={focused} /> }} />
      <Tabs.Screen name="gacha" options={{ tabBarIcon: ({ focused }) => <TabIcon label="Evoca" icon={"\u2B50"} focused={focused} /> }} />
      <Tabs.Screen name="menu" options={{ tabBarIcon: ({ focused }) => <TabIcon label="Menu" icon={"\u2630"} focused={focused} /> }} />
    </Tabs>
  );
}

const st = StyleSheet.create({
  tabBar: {
    position: 'absolute',
    borderTopWidth: 0,
    elevation: 0,
    height: 58,
    paddingBottom: 2,
    paddingTop: 2,
    backgroundColor: 'transparent',
  },
  tabItem: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 2,
    minWidth: 64,
    position: 'relative',
  },
  tabGlow: {
    position: 'absolute',
    top: -8,
    width: 56,
    height: 40,
    borderRadius: 20,
  },
  iconWrap: {
    width: 36,
    height: 28,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 10,
  },
  iconWrapActive: {
    backgroundColor: 'rgba(255,107,53,0.15)',
  },
  tabIcon: {
    fontSize: 18,
    color: '#4A4A6A',
  },
  tabIconActive: {
    color: COLORS.accent,
    fontSize: 20,
  },
  tabLabel: {
    fontSize: 8,
    color: '#4A4A6A',
    fontWeight: '700',
    marginTop: 2,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  tabLabelActive: {
    color: COLORS.accent,
    fontWeight: '900',
  },
  activeIndicator: {
    width: 16,
    height: 2,
    borderRadius: 1,
    backgroundColor: COLORS.accent,
    marginTop: 2,
  },
});
