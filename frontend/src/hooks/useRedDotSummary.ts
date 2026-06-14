/**
 * Pre-QA Stabilization 116C — useRedDotSummary
 *
 * GET-only hook. No polling aggressivo (refresh on focus/manual reload only).
 * No claim. No spend. No read-all. Visual-only.
 *
 * SEMANTIC CONTRACT:
 *   - red_dot_summary_version = "red_dot_v1_preqa_read_only_foundation"
 *   - no_db_writes = true
 *   - no_claim_activation = true
 *   - no_push_notification = true
 *   - no_toast = true
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { apiCall } from '../../utils/api';
import useServerScope from './useServerScope';

export type RedDotNode = {
  has_dot: boolean;
  count: number;
  severity: 'none' | 'info' | 'warning';
  reason: string | null;
  route: string;
  locked_by_pre_qa: boolean;
  actionable_now: boolean;
};

export type RedDotSummary = {
  status: string;
  server_id: string | null;
  red_dot_summary_version: string;
  psp_present_for_server: boolean;
  sources: Array<RedDotNode & { source_id: string }>;
  by_screen: Record<string, RedDotNode>;
  home_total: RedDotNode;
  active_sources_count: number;
};

const FORMULA_VERSION_EXPECTED = 'red_dot_v1_preqa_read_only_foundation';

export default function useRedDotSummary() {
  const { selected_server_id, isReady, refreshToken } = useServerScope();
  const [summary, setSummary] = useState<RedDotSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const reqIdRef = useRef(0);

  const fetchSummary = useCallback(async (sid: string) => {
    const my = ++reqIdRef.current;
    setLoading(true);
    try {
      const res: any = await apiCall(`/api/red-dot/summary?server_id=${encodeURIComponent(sid)}`);
      if (my !== reqIdRef.current) return;
      if (!res || typeof res !== 'object') { setSummary(null); return; }
      if (res.red_dot_summary_version && res.red_dot_summary_version !== FORMULA_VERSION_EXPECTED) {
        setSummary(null); return;
      }
      setSummary(res as RedDotSummary);
    } catch {
      if (my !== reqIdRef.current) return;
      setSummary(null);
    } finally {
      if (my === reqIdRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isReady || !selected_server_id) { setSummary(null); return; }
    void fetchSummary(selected_server_id);
  }, [isReady, selected_server_id, refreshToken, fetchSummary]);

  const reload = useCallback(() => {
    if (selected_server_id) void fetchSummary(selected_server_id);
  }, [selected_server_id, fetchSummary]);

  const getDotForRoute = useCallback((route: string): RedDotNode | null => {
    if (!summary) return null;
    return summary.by_screen[route] || null;
  }, [summary]);

  return { summary, loading, reload, getDotForRoute };
}
