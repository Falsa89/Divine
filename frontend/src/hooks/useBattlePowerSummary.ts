/**
 * Pre-QA Stabilization 116A — useBattlePowerSummary
 *
 * Hook React Native che consuma `GET /api/battle-power/summary?server_id=<sid>`.
 *
 * Stati onesti (mai falso `Power 0`):
 *   - `state === 'idle'`           : selected_server_id non ancora pronto
 *   - `state === 'no_server'`      : nessun server selezionato (UI mostra "Server richiesto")
 *   - `state === 'loading'`        : fetch in corso
 *   - `state === 'no_psp'`         : PSP mancante per il server (UI mostra "Server richiesto" / "Profilo server mancante")
 *   - `state === 'no_team'`        : team_missing=true (UI mostra "Team non impostato")
 *   - `state === 'ok'`             : active_team_power disponibile
 *   - `state === 'error'`          : errore di rete/server (UI mostra "—")
 *
 * SEMANTIC CONTRACT (server-side, mirrored qui):
 *   - formula_version = "battle_power_v1_preqa_derived"
 *   - source = "derived_read_only"
 *   - runtime_attached = false
 *   - combat_authoritative = false
 *   - reward_authoritative = false
 *   - balance_final = false
 *
 * NESSUN DB write. NESSUN reward. NESSUN combat trigger. Solo display.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { apiCall } from '../../utils/api';
import useServerScope from './useServerScope';

export type BattlePowerSummaryState =
  | 'idle'
  | 'no_server'
  | 'loading'
  | 'no_psp'
  | 'no_team'
  | 'ok'
  | 'error';

export type BattlePowerSlot = {
  slot: number;
  user_hero_id: string;
  hero_id: string;
  power: number;
};

export type BattlePowerSummary = {
  status: string;
  server_id: string | null;
  formula_version: string;
  source: string;
  runtime_attached: boolean;
  combat_authoritative: boolean;
  reward_authoritative: boolean;
  balance_final: boolean;
  active_team_power: number;
  team_missing: boolean;
  team_slots: BattlePowerSlot[];
  owned_hero_count: number;
  max_owned_hero_power: number;
  psp_present_for_server: boolean;
  blocker: string | null;
};

export type UseBattlePowerSummaryResult = {
  state: BattlePowerSummaryState;
  summary: BattlePowerSummary | null;
  // Display helpers (mai falso 0 quando non c'e' team):
  displayTeamPower: number | null;        // null = mostra `—`
  displayTeamPowerLabel: string;          // "Server richiesto" / "Team non impostato" / "—" / number
  serverId: string | null;
  errorMessage: string | null;
  reload: () => void;
};

const FORMULA_VERSION_EXPECTED = 'battle_power_v1_preqa_derived';

export default function useBattlePowerSummary(): UseBattlePowerSummaryResult {
  const { selected_server_id, isReady, refreshToken } = useServerScope();
  const [state, setState] = useState<BattlePowerSummaryState>('idle');
  const [summary, setSummary] = useState<BattlePowerSummary | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const reqIdRef = useRef(0);

  const fetchSummary = useCallback(async (sid: string) => {
    const myReqId = ++reqIdRef.current;
    setState('loading');
    setErrorMessage(null);
    try {
      const path = `/api/battle-power/summary?server_id=${encodeURIComponent(sid)}`;
      const res: any = await apiCall(path);
      if (myReqId !== reqIdRef.current) return; // stale
      if (!res || typeof res !== 'object') {
        setState('error');
        setSummary(null);
        setErrorMessage('Risposta non valida');
        return;
      }
      // Truth check: rifiutare risposte che pretendono di essere runtime/live.
      if (res.formula_version && res.formula_version !== FORMULA_VERSION_EXPECTED) {
        setState('error');
        setSummary(null);
        setErrorMessage(`Formula inattesa: ${res.formula_version}`);
        return;
      }
      const sumDoc = res as BattlePowerSummary;
      setSummary(sumDoc);
      if (sumDoc.status === 'blocked_no_psp_for_server' || sumDoc.psp_present_for_server === false) {
        setState('no_psp');
        return;
      }
      if (sumDoc.team_missing === true) {
        setState('no_team');
        return;
      }
      setState('ok');
    } catch (e: any) {
      if (myReqId !== reqIdRef.current) return;
      setState('error');
      setSummary(null);
      setErrorMessage(e?.message || String(e) || 'Errore di rete');
    }
  }, []);

  useEffect(() => {
    if (!isReady) {
      setState('idle');
      return;
    }
    if (!selected_server_id) {
      setState('no_server');
      setSummary(null);
      return;
    }
    void fetchSummary(selected_server_id);
  }, [isReady, selected_server_id, refreshToken, fetchSummary]);

  const reload = useCallback(() => {
    if (selected_server_id) void fetchSummary(selected_server_id);
  }, [selected_server_id, fetchSummary]);

  // Display helpers — mai falso 0.
  let displayTeamPower: number | null = null;
  let displayTeamPowerLabel = '—';
  switch (state) {
    case 'ok':
      displayTeamPower = summary?.active_team_power ?? null;
      displayTeamPowerLabel =
        typeof displayTeamPower === 'number'
          ? displayTeamPower.toLocaleString()
          : '—';
      break;
    case 'no_server':
      displayTeamPower = null;
      displayTeamPowerLabel = 'Server richiesto';
      break;
    case 'no_psp':
      displayTeamPower = null;
      displayTeamPowerLabel = 'Profilo server mancante';
      break;
    case 'no_team':
      displayTeamPower = null;
      displayTeamPowerLabel = 'Team non impostato';
      break;
    case 'loading':
      displayTeamPower = null;
      displayTeamPowerLabel = '…';
      break;
    case 'error':
      displayTeamPower = null;
      displayTeamPowerLabel = '—';
      break;
    default:
      displayTeamPower = null;
      displayTeamPowerLabel = '—';
  }

  return {
    state,
    summary,
    displayTeamPower,
    displayTeamPowerLabel,
    serverId: selected_server_id,
    errorMessage,
    reload,
  };
}
