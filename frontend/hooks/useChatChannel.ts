/**
 * useChatChannel — Phase 1 multi-channel chat hook (v16.18)
 * ────────────────────────────────────────────────────────────
 * Centralizza la logica di lettura/scrittura per il sistema chat
 * multi-canale. Sostituisce la logica locale duplicata che era
 * presente in plaza.tsx, home.tsx (HomeChatNotifPanel) e combat.tsx.
 *
 * Channels supportati in Phase 1:
 *   - global   — chat globale pubblica (sempre disponibile)
 *   - system   — notifiche di sistema (read-only, eventualmente vuoto)
 *   - faction  — chat solo per la fazione dell'utente (locked se l'utente
 *                non appartiene ad una fazione)
 *   - guild    — chat solo per la gilda dell'utente (locked se senza gilda)
 *
 * Backend:
 *   GET  /api/plaza/chat?channel=...    → array messaggi del canale
 *   POST /api/plaza/chat                → body {message, channel}
 *   GET  /api/plaza/channels            → metadata availability per utente
 *
 * Phase 2 (futura, NON in scope qui):
 *   - private/direct messaging
 *   - inbox conversazioni
 *   - entry point da username/profile
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { apiCall } from '../utils/api';
import { useAuth } from '../context/AuthContext';

export type ChannelKey = 'global' | 'system' | 'faction' | 'guild' | 'dm';

export interface ChannelMeta {
  key: ChannelKey;
  label: string;
  available: boolean;
  readonly?: boolean;
  /** Es: 'greek' per faction, guild_id per guild, null altrove. */
  context?: string | null;
  /** Motivo di lock se !available (mostrato nell'empty-state). */
  lockedReason?: string;
}

export interface UseChatChannelOptions {
  /** Canale iniziale (default 'global'). */
  initial?: ChannelKey;
  /** Polling soft per il canale attivo (ms). 0 = disabilitato. */
  pollingMs?: number;
  /** Quando false, non carica e non polla (utile per pannelli chiusi). */
  enabled?: boolean;
}

export interface UseChatChannelResult {
  channels: ChannelMeta[];
  active: ChannelKey;
  setActive: (k: ChannelKey) => void;
  messages: any[];
  loading: boolean;
  send: (msg: string) => Promise<void>;
  refresh: () => Promise<void>;
  /** True se il canale attivo è solo lettura (es. 'system'). */
  isReadonly: boolean;
  /** True se il canale attivo è disponibile per l'utente. */
  isAvailable: boolean;
  /** Metadati del canale attivo. */
  activeMeta: ChannelMeta | undefined;
}

function buildChannelsFromUser(user: any): ChannelMeta[] {
  const hasFaction = !!user?.faction;
  const hasGuild = !!user?.guild_id;
  const isLogged = !!user?.id;
  return [
    { key: 'global',  label: 'Globale', available: true },
    { key: 'system',  label: 'Sistema', available: true, readonly: true },
    {
      key: 'faction',
      label: 'Fazione',
      available: hasFaction,
      context: user?.faction || null,
      lockedReason: hasFaction ? undefined : 'Nessuna fazione',
    },
    {
      key: 'guild',
      label: 'Gilda',
      available: hasGuild,
      context: user?.guild_id || null,
      lockedReason: hasGuild ? undefined : 'Nessuna gilda',
    },
    // v16.20 — DM canale "speciale": non è uno stream broadcast, ma un
    // entry point integrato al sistema selector. Quando attivo, la surface
    // host renderizza <DMPanel> invece di una message list standard.
    // useChatChannel rileva questo caso e non esegue fetch API per messages
    // (load() short-circuit su 'dm').
    {
      key: 'dm',
      label: 'Privati',
      available: isLogged,
      lockedReason: isLogged ? undefined : 'Effettua il login',
    },
  ];
}

export function useChatChannel(opts?: UseChatChannelOptions): UseChatChannelResult {
  const { initial = 'global', pollingMs = 0, enabled = true } = opts || {};
  const { user } = useAuth();

  const [active, setActive] = useState<ChannelKey>(initial);
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const channels = useMemo(() => buildChannelsFromUser(user), [user]);
  const activeMeta = useMemo(() => channels.find(c => c.key === active), [channels, active]);

  const reqIdRef = useRef(0);

  const load = useCallback(async (ch: ChannelKey) => {
    // v16.20 — DM è un canale speciale gestito da DMPanel/useDM, non
    // dallo stream broadcast. Short-circuit: nessuna chiamata GET, nessun
    // setMessages → l'host surface saprà renderizzare <DMPanel/> al posto
    // della message list standard.
    if (ch === 'dm') {
      setMessages([]);
      return;
    }
    const myReq = ++reqIdRef.current;
    try {
      const c = await apiCall(`/api/plaza/chat?channel=${ch}`);
      // Se nel frattempo il canale è cambiato, scarta la risposta stale.
      if (myReq !== reqIdRef.current) return;
      if (Array.isArray(c)) setMessages(c);
      else setMessages([]);
    } catch {
      if (myReq === reqIdRef.current) setMessages([]);
    }
  }, []);

  // Active channel change → fetch fresh
  useEffect(() => {
    if (!enabled) return;
    setMessages([]);
    setLoading(true);
    load(active).finally(() => setLoading(false));
  }, [active, enabled, load]);

  // Polling soft sul canale attivo
  useEffect(() => {
    if (!enabled || !pollingMs) return;
    const t = setInterval(() => load(active), pollingMs);
    return () => clearInterval(t);
  }, [enabled, pollingMs, active, load]);

  const send = useCallback(async (msg: string) => {
    if (!activeMeta?.available || activeMeta?.readonly) return;
    try {
      await apiCall('/api/plaza/chat', {
        method: 'POST',
        body: JSON.stringify({ message: msg, channel: active }),
      });
      await load(active);
    } catch {
      // network ko → silenzioso, l'UI mostrerà solo che il messaggio non è apparso.
    }
  }, [active, activeMeta, load]);

  const refresh = useCallback(() => load(active), [active, load]);

  return {
    channels,
    active,
    setActive,
    messages,
    loading,
    send,
    refresh,
    isReadonly: !!activeMeta?.readonly,
    isAvailable: !!activeMeta?.available,
    activeMeta,
  };
}
