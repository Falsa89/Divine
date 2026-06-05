// v107B — Combat Launch Parser.
// Non-destructive parser for Battle Launch Contract payloads handed to combat renderer.
// Does NOT mutate combat.tsx behavior. Pure helper.
import { parseLaunchContextFromParams, BattleLaunchContractV1, validateLaunchContext } from '../buildLaunchContext';

export interface CombatLaunchEnvelope {
  contract: BattleLaunchContractV1 | null;
  is_valid: boolean;
  errors: string[];
  source: 'router_params' | 'post_response' | 'missing';
  is_preview: boolean;
}

export function readLaunchContextFromRouterParams(params: Record<string, unknown>): CombatLaunchEnvelope {
  const ctx = parseLaunchContextFromParams(params);
  if (!ctx) return { contract: null, is_valid: false, errors: ['parse_failed'], source: 'missing', is_preview: true };
  const v = validateLaunchContext(ctx);
  return {
    contract: ctx,
    is_valid: v.ok,
    errors: v.errors,
    source: 'router_params',
    is_preview: ctx.battle_engine_mode === 'preview',
  };
}

export function readLaunchContextFromPostResponse(echo: { echoed_payload?: BattleLaunchContractV1; status?: string }): CombatLaunchEnvelope {
  if (!echo || !echo.echoed_payload) return { contract: null, is_valid: false, errors: ['no_payload'], source: 'missing', is_preview: true };
  const ctx = echo.echoed_payload;
  const v = validateLaunchContext(ctx);
  return {
    contract: ctx,
    is_valid: v.ok,
    errors: v.errors,
    source: 'post_response',
    is_preview: echo.status === 'PREVIEW_ECHO_NON_AUTHORITATIVE' || ctx.battle_engine_mode === 'preview',
  };
}
