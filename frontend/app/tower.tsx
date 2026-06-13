// Pre-QA Stabilization 115E — Tower legacy route fail-closed.
//
// PRIMA: tower.tsx chiamava endpoint legacy backend e mostrava reward/stamina
//        live-looking.
// DOPO:  schermata bloccata pre-QA tramite PreQaScreenGate canonico. Nessuna
//        chiamata di rete, nessun refresh utente, nessuna reward UI live.
//
// La route '/tower' viene aggiunta a PRE_QA_BLOCKED_PLAYER_ROUTES in
// preQaNavGuard.ts; PreQaScreenGate.isScreenGated('/tower') -> true.
//
// SAFETY:
//  - zero network calls
//  - zero user refresh
//  - zero reward live UI
//  - zero progression
//  - zero stamina display live

import React from 'react';
import PreQaScreenGate, { isScreenGated } from '../src/components/PreQaScreenGate';

export default function TowerScreen() {
  // Pre-QA Stabilization 115E — fail-closed: la route /tower e' classificata
  // legacy/deferred in pre-QA. Mostriamo direttamente il guard canonico,
  // senza alcuna chiamata backend ne' UI reward live.
  // Default fail-closed: anche se isScreenGated lanciasse, ritornerebbe true.
  if (isScreenGated('/tower')) {
    return <PreQaScreenGate route="/tower" label="Tower" />;
  }
  // Path unreachable in pre-QA (la route '/tower' e' in PRE_QA_BLOCKED_PLAYER_ROUTES).
  // Render comunque il guard come safety net: nessun rendering di reward/UI live.
  return <PreQaScreenGate route="/tower" label="Tower" />;
}
