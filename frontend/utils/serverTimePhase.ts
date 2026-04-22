/**
 * SERVER TIME → FASE TEMPORALE (dawn/day/sunset/night)
 * ======================================================
 *
 * Regole:
 *  - La fase NON dipende dall'ora locale del device.
 *  - Deriva da un `serverDate` ottenuto via `/api/server-time`.
 *  - Manteniamo un `offset` (serverEpoch - clientEpoch) per continuare a
 *    calcolare la fase in modo fluido senza refetch continuo.
 *  - Le fasce orarie sono CONFIGURABILI in un unico posto (questo file):
 *    `TIME_PHASE_RANGES`. Nessun hardcode sparso in UI/logica.
 */
import { useEffect, useMemo, useState, useRef } from 'react';
import { apiCall } from './api';

export type TimePhase = 'dawn' | 'day' | 'sunset' | 'night';

export type PhaseRange = {
  phase: TimePhase;
  /** ora di inizio, 0-23 (inclusiva) */
  from: number;
  /** ora di fine, 0-24 (esclusiva). Se `from > to` la fascia avvolge la mezzanotte. */
  to: number;
};

/**
 * UNICA FONTE DI VERITÀ per i confini delle fasi.
 * Modificare QUI per ribilanciare alba/giorno/tramonto/notte.
 */
export const TIME_PHASE_RANGES: PhaseRange[] = [
  { phase: 'dawn',   from: 5,  to: 10 }, // 05:00 – 09:59
  { phase: 'day',    from: 10, to: 17 }, // 10:00 – 16:59
  { phase: 'sunset', from: 17, to: 20 }, // 17:00 – 19:59
  { phase: 'night',  from: 20, to: 5  }, // 20:00 – 04:59 (wraps)
];

/** Converte una Date (in UTC server) nella sua TimePhase. */
export function getTimePhase(serverDate: Date): TimePhase {
  const h = serverDate.getUTCHours();
  for (const r of TIME_PHASE_RANGES) {
    if (r.from <= r.to) {
      if (h >= r.from && h < r.to) return r.phase;
    } else {
      // Fascia che attraversa la mezzanotte
      if (h >= r.from || h < r.to) return r.phase;
    }
  }
  return 'night';
}

/**
 * Hook: sincronizza con /api/server-time UNA VOLTA al mount, poi mantiene
 * un offset client↔server e aggiorna la fase ogni `tickSec` secondi
 * (default 60s; più che sufficiente per una rotazione alba/giorno/…).
 *
 * DEV/QA OVERRIDE:
 *   URL query `?phase=dawn|day|sunset|night` forza la fase indicata
 *   ignorando il server time. Utile per screenshot/test visivi.
 */
export function useServerTimePhase(tickSec: number = 60) {
  const offsetMsRef = useRef<number>(0);
  const [serverNow, setServerNow] = useState<Date>(() => new Date());
  const [phase, setPhase] = useState<TimePhase>(() => getTimePhase(new Date()));
  const [synced, setSynced] = useState(false);

  // Dev override via:
  //   1) window.__DW_FORCE_PHASE__ (settato da QA via addInitScript, NON strippato da router)
  //   2) URL query ?phase=... o hash #phase=... (fallback quando 1 non disponibile)
  const overridePhase: TimePhase | null = (() => {
    try {
      const g: any = (globalThis as any)?.__DW_FORCE_PHASE__;
      if (g && ['dawn', 'day', 'sunset', 'night'].includes(g)) return g as TimePhase;
      const loc: any = (globalThis as any)?.location;
      const src = (loc?.search || '') + '&' + (loc?.hash || '').replace(/^#/, '?').slice(1);
      const params = new URLSearchParams(src);
      const p = params.get('phase');
      if (p && ['dawn', 'day', 'sunset', 'night'].includes(p)) return p as TimePhase;
    } catch {}
    return null;
  })();

  // Sync offset su mount
  useEffect(() => {
    let canceled = false;
    (async () => {
      try {
        const res: any = await apiCall('/api/server-time');
        if (canceled) return;
        const serverMs = Number(res?.epoch_ms) || Date.now();
        offsetMsRef.current = serverMs - Date.now();
        const now = new Date(Date.now() + offsetMsRef.current);
        setServerNow(now);
        setPhase(overridePhase || getTimePhase(now));
        setSynced(true);
      } catch {
        // Fallback: UTC del device (coerente su tutti i client)
        offsetMsRef.current = 0;
        const now = new Date();
        setServerNow(now);
        setPhase(overridePhase || getTimePhase(now));
      }
    })();
    return () => { canceled = true; };
  }, [overridePhase]);

  // Tick periodico: aggiorna serverNow + ricalcola phase
  useEffect(() => {
    const id = setInterval(() => {
      const now = new Date(Date.now() + offsetMsRef.current);
      setServerNow(now);
      const newPhase = overridePhase || getTimePhase(now);
      setPhase(prev => (prev === newPhase ? prev : newPhase));
    }, Math.max(1, tickSec) * 1000);
    return () => clearInterval(id);
  }, [tickSec, overridePhase]);

  const formatted = useMemo(() => {
    const d = serverNow;
    const hh = String(d.getUTCHours()).padStart(2, '0');
    const mm = String(d.getUTCMinutes()).padStart(2, '0');
    const ss = String(d.getUTCSeconds()).padStart(2, '0');
    return `${hh}:${mm}:${ss} UTC`;
  }, [serverNow]);

  return { phase, serverNow, formatted, synced };
}
