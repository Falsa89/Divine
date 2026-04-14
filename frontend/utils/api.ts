import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';
import Constants from 'expo-constants';

function getBaseUrl(): string {
  // On web, use relative URL (nginx proxies /api to backend)
  if (Platform.OS === 'web') {
    return '';
  }
  // On mobile (Expo Go), use the hostname URL which routes to our server
  const hostname = Constants.expoConfig?.extra?.EXPO_PACKAGER_HOSTNAME
    || process.env.EXPO_PACKAGER_HOSTNAME
    || Constants.expoConfig?.extra?.EXPO_PACKAGER_PROXY_URL
    || process.env.EXPO_PACKAGER_PROXY_URL
    || '';
  return hostname;
}

export async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = await AsyncStorage.getItem('token');
  const headers: any = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const base = getBaseUrl();
  const path = endpoint.startsWith('/api') ? endpoint : `/api${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  const url = `${base}${path}`;
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Errore di rete' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}
