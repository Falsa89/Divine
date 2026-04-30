import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiCall } from '../utils/api';

interface User {
  id: string;
  email: string;
  username: string;
  level: number;
  gold: number;
  gems: number;
  stamina: number;
  max_stamina: number;
  titles: string[];
  active_title: string;
  guild_id?: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  /**
   * Versione monotona del roster utente. Bumpata dopo eventi che alterano
   * /api/user/heroes (gacha pull, ascension, fusion, ecc.).
   * Le schermate consumer la usano come dependency in useFocusEffect /
   * useEffect per invalidare la cache stale (TASK RM1.16-B).
   */
  userHeroesVersion: number;
  bumpUserHeroesVersion: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, username: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  loading: true,
  userHeroesVersion: 0,
  bumpUserHeroesVersion: () => {},
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  refreshUser: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  // RM1.16-B: cache invalidation counter per il roster utente.
  const [userHeroesVersion, setUserHeroesVersion] = useState(0);

  const bumpUserHeroesVersion = () => setUserHeroesVersion((v) => v + 1);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('token');
      if (storedToken) {
        setToken(storedToken);
        const profile = await apiCall('/api/user/profile');
        setUser(profile);
      }
    } catch (e) {
      await AsyncStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const data = await apiCall('/api/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    await AsyncStorage.setItem('token', data.token);
    setToken(data.token);
    setUser(data.user);
  };

  const register = async (email: string, password: string, username: string) => {
    const data = await apiCall('/api/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, username }),
    });
    await AsyncStorage.setItem('token', data.token);
    setToken(data.token);
    setUser(data.user);
  };

  const logout = async () => {
    await AsyncStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const profile = await apiCall('/api/user/profile');
      setUser(profile);
    } catch (e) {}
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, userHeroesVersion, bumpUserHeroesVersion, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
