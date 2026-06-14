/**
 * useDM — Phase 2 Direct Message hook (v16.19)
 * ────────────────────────────────────────────────────────────
 * Gestisce 1-to-1 direct messaging:
 *   - lista thread dell'utente corrente (inbox)
 *   - apertura/creazione thread con un peer specifico
 *   - lettura/invio messaggi nel thread attivo
 *   - reset unread su apertura
 *
 * Backend:
 *   GET  /api/dm/threads                   → inbox
 *   POST /api/dm/threads {peer_user_id}    → open or create thread
 *   GET  /api/dm/threads/<tid>/messages    → messages
 *   POST /api/dm/threads/<tid>/messages    → send
 *   POST /api/dm/threads/<tid>/read        → mark read
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { apiCall } from '../utils/api';
import { isRouteAllowedInPreQa } from '../src/utils/preQaNavGuard';

// Pre-QA Stabilization 116B — Hook-level fail-close per DM.
// Anche se l'host surface NON e' un PreQaScreenGate, il hook deve rifiutare
// ogni api call verso /api/dm/* finche' /dm e' gated. Defense-in-depth oltre
// lo screen gate.
function _dmPreQaBlocked(): boolean {
  try {
    return !isRouteAllowedInPreQa('/dm');
  } catch (_e) {
    return true;
  }
}

export interface DMThread {
  id: string;
  peer_id: string;
  peer_username: string;
  last_message: string | null;
  last_message_at: string | null;
  last_sender_id: string | null;
  unread: number;
}

export interface DMMessage {
  id: string;
  thread_id: string;
  sender_id: string;
  sender_username: string;
  message: string;
  timestamp: string;
}

export interface UseDMResult {
  threads: DMThread[];
  loadingThreads: boolean;
  refreshThreads: () => Promise<void>;

  activeThreadId: string | null;
  setActiveThreadId: (id: string | null) => void;
  activeMessages: DMMessage[];
  loadingMessages: boolean;

  /** Apre o crea il thread con il peer indicato. Restituisce il thread_id. */
  openWithUser: (peerUserId: string) => Promise<string | null>;
  sendMessage: (msg: string) => Promise<void>;
  refreshMessages: () => Promise<void>;
  markRead: () => Promise<void>;
}

export function useDM(opts?: { pollingMs?: number }): UseDMResult {
  const { pollingMs = 0 } = opts || {};
  const [threads, setThreads] = useState<DMThread[]>([]);
  const [loadingThreads, setLoadingThreads] = useState(false);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [activeMessages, setActiveMessages] = useState<DMMessage[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const reqIdRef = useRef(0);

  const refreshThreads = useCallback(async () => {
    // Pre-QA Stabilization 116B — hook-level fail-close: se /dm e' gated,
    // NESSUNA chiamata /api/dm/* viene effettuata (defense-in-depth).
    if (_dmPreQaBlocked()) { setThreads([]); return; }
    setLoadingThreads(true);
    try {
      const r = await apiCall('/api/dm/threads');
      if (Array.isArray(r)) setThreads(r);
    } catch {}
    finally { setLoadingThreads(false); }
  }, []);

  // Initial threads load
  useEffect(() => { refreshThreads(); }, [refreshThreads]);

  // Soft polling for inbox (when pollingMs > 0)
  useEffect(() => {
    if (!pollingMs) return;
    const t = setInterval(refreshThreads, pollingMs);
    return () => clearInterval(t);
  }, [pollingMs, refreshThreads]);

  // Load messages when active thread changes
  const refreshMessages = useCallback(async () => {
    // Pre-QA Stabilization 116B — hook-level fail-close.
    if (_dmPreQaBlocked()) { setActiveMessages([]); return; }
    const tid = activeThreadId;
    if (!tid) { setActiveMessages([]); return; }
    const myReq = ++reqIdRef.current;
    setLoadingMessages(true);
    try {
      const r = await apiCall(`/api/dm/threads/${tid}/messages`);
      if (myReq !== reqIdRef.current) return;
      if (Array.isArray(r)) setActiveMessages(r);
    } catch {
      if (myReq === reqIdRef.current) setActiveMessages([]);
    } finally {
      if (myReq === reqIdRef.current) setLoadingMessages(false);
    }
  }, [activeThreadId]);

  useEffect(() => {
    if (!activeThreadId) { setActiveMessages([]); return; }
    refreshMessages();
  }, [activeThreadId, refreshMessages]);

  const openWithUser = useCallback(async (peerUserId: string): Promise<string | null> => {
    // Pre-QA Stabilization 116B — hook-level fail-close.
    if (_dmPreQaBlocked()) return null;
    try {
      const r = await apiCall('/api/dm/threads', {
        method: 'POST',
        body: JSON.stringify({ peer_user_id: peerUserId }),
      });
      if (r && r.id) {
        setActiveThreadId(r.id);
        // Best-effort refresh inbox so the thread appears
        refreshThreads();
        return r.id;
      }
      return null;
    } catch {
      return null;
    }
  }, [refreshThreads]);

  const sendMessage = useCallback(async (msg: string) => {
    // Pre-QA Stabilization 116B — hook-level fail-close.
    if (_dmPreQaBlocked()) return;
    if (!activeThreadId) return;
    try {
      await apiCall(`/api/dm/threads/${activeThreadId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ message: msg }),
      });
      await refreshMessages();
      // bump del thread in inbox: refresh leggero
      refreshThreads();
    } catch {}
  }, [activeThreadId, refreshMessages, refreshThreads]);

  const markRead = useCallback(async () => {
    // Pre-QA Stabilization 116B — hook-level fail-close.
    if (_dmPreQaBlocked()) return;
    if (!activeThreadId) return;
    try { await apiCall(`/api/dm/threads/${activeThreadId}/read`, { method: 'POST' }); } catch {}
  }, [activeThreadId]);

  return {
    threads,
    loadingThreads,
    refreshThreads,
    activeThreadId,
    setActiveThreadId,
    activeMessages,
    loadingMessages,
    openWithUser,
    sendMessage,
    refreshMessages,
    markRead,
  };
}
