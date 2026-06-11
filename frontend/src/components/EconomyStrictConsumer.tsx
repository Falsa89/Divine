/**
 * Pack 104 — Economy Strict UI consumer (read-only, server-scoped, guarded).
 *
 * Triple gate di sicurezza:
 *  1. Flag UI `EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED` === 'true' (default OFF).
 *  2. `useServerScope().serverId` presente (no fallback s1).
 *  3. `useAuth().token` presente.
 *
 * Comportamento:
 *  - Mostra solo lo health stato e il catalog shop pubblico server-side (read-only).
 *  - Nessuna chiamata di POST mutating dal client UI. I path mutating (buy/retire/equip/unequip)
 *    sono test-only via marker `pack_104_test_artifact`; non vengono mai chiamati dall'UI utente.
 *  - Etichetta esplicita "Reward in modalita controlled gated" + "Forge/Fusion deferred".
 *  - Refetch automatico dopo focus.
 *
 * NON consuma `EXPO_PUBLIC_TOWER_STRICT_UI_ENABLED` (resta indipendente).
 */
import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { useAuth } from '../auth/AuthContext';
import { useServerScope } from '../hooks/useServerScope';

const BACKEND = (process.env.EXPO_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL || '').toString();
const UI_FLAG = (process.env.EXPO_PUBLIC_ECONOMY_STRICT_UI_ENABLED || 'false').toString().toLowerCase();
const UI_ENABLED = UI_FLAG === 'true';

type Health = {
  endpoint_group: string;
  pack_origin: string;
  kill_switches: Record<string, boolean>;
  sources: Record<string, string>;
  shop_catalog_version: string;
  reward_live_general: boolean;
  premium_grants: boolean;
  release_readiness_claimed: boolean;
  no_users_gold_gems_experience_mutation: boolean;
  no_account_wide_writes: boolean;
  no_cross_server: boolean;
  no_iap_gacha_payment: boolean;
};

type CatalogItem = {
  id: string;
  name: string;
  cost: Record<string, number>;
  grant: Record<string, number>;
  daily_purchase_limit: number;
};

type CatalogShop = {
  shop_id: string;
  name: string;
  description: string;
  items: CatalogItem[];
};

type Catalog = {
  catalog_version: string;
  shops: CatalogShop[];
};

type State =
  | { kind: 'loading' }
  | { kind: 'ready'; health: Health; catalog: Catalog }
  | { kind: 'error'; message: string };

export type EconomyStrictConsumerProps = {
  forceVisible?: boolean;
};

export const EconomyStrictConsumer: React.FC<EconomyStrictConsumerProps> = ({ forceVisible = false }) => {
  if (!UI_ENABLED && !forceVisible) return null;

  const { token } = useAuth();
  const { serverId } = useServerScope();
  const [state, setState] = useState<State>({ kind: 'loading' });

  const fetchData = useCallback(async () => {
    if (!token || !serverId) return;
    setState({ kind: 'loading' });
    try {
      const [hRes, cRes] = await Promise.all([
        fetch(`${BACKEND}/api/economy/strict/health`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${BACKEND}/api/economy/strict/shop/catalog`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);
      if (!hRes.ok) throw new Error(`health http ${hRes.status}`);
      if (!cRes.ok) throw new Error(`catalog http ${cRes.status}`);
      const health: Health = await hRes.json();
      const catalog: Catalog = await cRes.json();
      setState({ kind: 'ready', health, catalog });
    } catch (e: any) {
      setState({ kind: 'error', message: e?.message || 'unknown error' });
    }
  }, [token, serverId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (!UI_ENABLED && !forceVisible) return null;

  if (state.kind === 'loading') {
    return (
      <View style={styles.container}>
        <ActivityIndicator />
        <Text style={styles.label}>Caricamento Economy Strict...</Text>
      </View>
    );
  }
  if (state.kind === 'error') {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>Errore: {state.message}</Text>
        <Pressable style={styles.btn} onPress={fetchData}>
          <Text style={styles.btnText}>Riprova</Text>
        </Pressable>
      </View>
    );
  }
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Economy Strict (server-scoped, gated)</Text>
      <Text style={styles.label}>Server: {serverId}</Text>
      <Text style={styles.label}>Catalog version: {state.catalog.catalog_version}</Text>
      <Text style={styles.warn}>Reward live general: {String(state.health.reward_live_general)}</Text>
      <Text style={styles.warn}>Premium grants: {String(state.health.premium_grants)}</Text>
      <Text style={styles.warn}>No IAP/gacha/payment: {String(state.health.no_iap_gacha_payment)}</Text>
      <Text style={styles.label}>Sources status:</Text>
      {Object.entries(state.health.sources).map(([k, v]) => (
        <Text key={k} style={styles.subLabel}>  - {k}: {v}</Text>
      ))}
      <Text style={styles.label}>Shop catalog (preview, read-only):</Text>
      {state.catalog.shops.map((shop) => (
        <View key={shop.shop_id} style={styles.shopBlock}>
          <Text style={styles.shopName}>{shop.name}</Text>
          <Text style={styles.shopDesc}>{shop.description}</Text>
          {shop.items.map((it) => (
            <Text key={it.id} style={styles.itemLine}>
              • {it.name} — cost: {JSON.stringify(it.cost)} → grant: {JSON.stringify(it.grant)} (limit/day: {it.daily_purchase_limit})
            </Text>
          ))}
        </View>
      ))}
      <Pressable style={styles.btn} onPress={fetchData}>
        <Text style={styles.btnText}>Refresh</Text>
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 12, backgroundColor: '#1a1a1a', borderRadius: 8, margin: 8 },
  title: { color: '#ffd700', fontSize: 16, fontWeight: 'bold', marginBottom: 6 },
  label: { color: '#fff', fontSize: 13, marginTop: 4 },
  subLabel: { color: '#aaa', fontSize: 12 },
  warn: { color: '#90ee90', fontSize: 12, marginTop: 2 },
  error: { color: '#ff6464', fontSize: 13, marginVertical: 8 },
  shopBlock: { marginTop: 8, paddingLeft: 8, borderLeftWidth: 2, borderLeftColor: '#444' },
  shopName: { color: '#fff', fontWeight: 'bold' },
  shopDesc: { color: '#bbb', fontSize: 11, marginBottom: 4 },
  itemLine: { color: '#ddd', fontSize: 11 },
  btn: { marginTop: 10, backgroundColor: '#2a4', paddingVertical: 8, paddingHorizontal: 12, borderRadius: 6, alignSelf: 'flex-start' },
  btnText: { color: '#fff', fontWeight: 'bold' },
});

export default EconomyStrictConsumer;
