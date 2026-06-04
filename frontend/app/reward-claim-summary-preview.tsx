// reward-claim-summary-preview.tsx
//
// PREVIEW SHELL — DEEPLINK-ONLY — NON PRODUCTION UI
// HARDENED v82 — UX hardening, status chips, db_writes vs local_file_writes row,
// observation pass row, rollback state row, live vs staging distinction text.
// ----------------------------------------------------------------------------
// Vincoli rispettati (v81 + v82):
// - NO backend fetch / NO API call / NO process.env
// - NO AsyncStorage / NO account mutation / NO DB
// - NO real claim button / NO live reward grant
// - NO import da story.tsx / combat.tsx / battle_engine
// - Solo dati statici locali derivati dai contratti v80/v81/v82
// - Labels visibili obbligatori:
//     PREVIEW, STAGING, CANARY_LOCAL, NOT LIVE REWARD, DB_WRITES_0, LOCAL_FILE_ONLY
//
// Accesso: deeplink-only (es: /reward-claim-summary-preview)
// ============================================================================

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack, useRouter } from 'expo-router';

// ============================================================================
// Static preview data (locale, no fetch). Allineato a:
// data/design/economy/reward_claim_ui_summary_preview_shell_static_data_v1.json
// data/design/economy/reward_claim_ui_summary_preview_hardening_static_data_v1.json
// ============================================================================
const STATIC_PREVIEW_DATA = {
  reward_preview: {
    route_id: 'story_alpha_slice_preview',
    reward_payload_summary: { gold: 100, account_exp: 10, hero_exp: 20, basic_material: 1 },
    cap_hint: { gold: 500, account_exp: 50, hero_exp: 100, basic_material: 3 },
  },
  claim_result_sample: {
    tx_id: 'canary-wave4-tx-000001',
    applied_to_local_staging: true,
    applied_to_live: false,
    idempotent_replay: false,
    is_preview: true,
  },
  idempotency_status_sample: {
    key_format: 'idem:wave4:<user>:<claim_id>',
    status: 'unique_first_seen',
  },
  rollback_state_sample: {
    rollback_token: 'rb-wave4-token-000001',
    rolled_back: false,
  },
  rejected_examples: [
    { scenario: 'premium_currency_in_payload', reason: 'forbidden_reward_type:premium_currency' },
    { scenario: 'non_allowlisted_user', reason: 'non_allowlisted_user' },
    { scenario: 'over_cap_gold', reason: 'over_cap:gold' },
    { scenario: 'malformed_route', reason: 'malformed_route' },
    { scenario: 'event_arena_ranking_reward', reason: 'forbidden_reward_type:arena_ranking_reward' },
    { scenario: 'duplicate_conflict', reason: 'idempotency_conflict_hash_mismatch' },
  ],
  // v82 hardening: counters separati e stato osservazione
  status_snapshot: {
    wave: 4,
    db_writes: 0,
    local_file_writes: 6,
    observation_pass: true,
    rollback_drill_executed: true,
    rolled_back_count: 2,
    live_db_readiness_design_gate: 'design_only_no_apply',
  },
  local_ledger_summary: {
    wave: 4,
    isolated_from_live: true,
    canary: true,
    entries_displayed: 8,
    db_writes: 0,
    live_reward_grant: false,
  },
};

const LABELS = [
  'PREVIEW',
  'STAGING',
  'CANARY_LOCAL',
  'NOT LIVE REWARD',
  'DB_WRITES_0',
  'LOCAL_FILE_ONLY',
];

// ============================================================================
// Componenti
// ============================================================================
type Expandable = {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  initiallyOpen?: boolean;
};

function ExpandableSection({ title, subtitle, children, initiallyOpen = false }: Expandable) {
  const [open, setOpen] = useState<boolean>(initiallyOpen);
  return (
    <View style={styles.section}>
      <TouchableOpacity
        onPress={() => setOpen((o) => !o)}
        accessibilityRole="button"
        accessibilityLabel={`Espandi ${title}`}
        style={styles.sectionHeader}
        activeOpacity={0.7}
      >
        <View style={{ flex: 1 }}>
          <Text style={styles.sectionTitle}>{title}</Text>
          {subtitle ? <Text style={styles.sectionSubtitle}>{subtitle}</Text> : null}
        </View>
        <Text style={styles.chevron}>{open ? '\u2212' : '+'}</Text>
      </TouchableOpacity>
      {open ? <View style={styles.sectionBody}>{children}</View> : null}
    </View>
  );
}

function KeyValueRow({
  label,
  value,
  emphasis,
}: {
  label: string;
  value: string | number | boolean | null;
  emphasis?: 'good' | 'warn' | 'neutral';
}) {
  const valueStyle =
    emphasis === 'good' ? styles.kvValueGood
      : emphasis === 'warn' ? styles.kvValueWarn
      : styles.kvValue;
  return (
    <View style={styles.kvRow}>
      <Text style={styles.kvLabel}>{label}</Text>
      <Text style={valueStyle}>{String(value)}</Text>
    </View>
  );
}

function LabelChips() {
  return (
    <View style={styles.chipsRow}>
      {LABELS.map((l) => (
        <View key={l} style={styles.chip}>
          <Text style={styles.chipText}>{l}</Text>
        </View>
      ))}
    </View>
  );
}

function StatusChip({ label, tone }: { label: string; tone: 'good' | 'warn' | 'neutral' }) {
  const style =
    tone === 'good' ? styles.statusChipGood
      : tone === 'warn' ? styles.statusChipWarn
      : styles.statusChipNeutral;
  return (
    <View style={[styles.statusChip, style]}>
      <Text style={styles.statusChipText}>{label}</Text>
    </View>
  );
}

// ============================================================================
// Screen
// ============================================================================
export default function RewardClaimSummaryPreview() {
  const router = useRouter();
  const data = STATIC_PREVIEW_DATA;
  const s = data.status_snapshot;

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'bottom']}>
      <Stack.Screen options={{ headerShown: false }} />
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header chiaro */}
        <View style={styles.header}>
          <TouchableOpacity
            onPress={() => router.back()}
            style={styles.backBtn}
            accessibilityRole="button"
            accessibilityLabel="Indietro"
            activeOpacity={0.7}
          >
            <Text style={styles.backText}>{'\u2190'}</Text>
          </TouchableOpacity>
          <View style={styles.headerTitleBlock}>
            <Text style={styles.headerTitle}>Reward Claim Summary</Text>
            <Text style={styles.headerSubtitle}>
              Preview Shell \u00b7 v82 hardened \u00b7 wave-{s.wave}
            </Text>
          </View>
        </View>

        <LabelChips />

        {/* Status chips (v82 hardening) */}
        <View style={styles.statusChipsRow}>
          <StatusChip label="local staging apply" tone="good" />
          <StatusChip label="live claim NOT active" tone="warn" />
          <StatusChip label="future live DB \u2192 dedicated pack" tone="neutral" />
        </View>

        <Text style={styles.banner}>
          Questa \u00e8 una preview deeplink-only. Nessun reward viene assegnato,
          nessuna chiamata API viene eseguita. Tutti i dati sono statici locali.
          Lo stato live-DB \u00e8 design-only: richieder\u00e0 un pack dedicato per essere abilitato.
        </Text>

        {/* v82 status snapshot compatto */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <View style={{ flex: 1 }}>
              <Text style={styles.sectionTitle}>Status Snapshot (v82)</Text>
              <Text style={styles.sectionSubtitle}>
                Counters separati: DB vs local file
              </Text>
            </View>
          </View>
          <View style={styles.sectionBody}>
            <KeyValueRow label="db_writes" value={s.db_writes} emphasis="good" />
            <KeyValueRow label="local_file_writes" value={s.local_file_writes} />
            <KeyValueRow label="observation_pass" value={s.observation_pass} emphasis="good" />
            <KeyValueRow
              label="rollback_drill_executed"
              value={s.rollback_drill_executed}
            />
            <KeyValueRow label="rolled_back_count" value={s.rolled_back_count} />
            <KeyValueRow
              label="live_db_readiness_design_gate"
              value={s.live_db_readiness_design_gate}
              emphasis="warn"
            />
          </View>
        </View>

        {/* Reward Preview */}
        <ExpandableSection
          title="Reward Preview"
          subtitle={`Route: ${data.reward_preview.route_id}`}
          initiallyOpen
        >
          <View style={styles.rewardGrid}>
            {Object.entries(data.reward_preview.reward_payload_summary).map(([k, v]) => {
              const cap = (data.reward_preview.cap_hint as Record<string, number>)[k];
              return (
                <View key={k} style={styles.rewardCard}>
                  <Text style={styles.rewardKey}>{k}</Text>
                  <Text style={styles.rewardValue}>{v}</Text>
                  <Text style={styles.rewardCap}>cap: {cap}</Text>
                </View>
              );
            })}
          </View>
        </ExpandableSection>

        {/* Claim Result */}
        <ExpandableSection
          title="Claim Result (sample)"
          subtitle={data.claim_result_sample.tx_id}
        >
          <KeyValueRow label="tx_id" value={data.claim_result_sample.tx_id} />
          <KeyValueRow
            label="applied_to_local_staging"
            value={data.claim_result_sample.applied_to_local_staging}
            emphasis="good"
          />
          <KeyValueRow
            label="applied_to_live"
            value={data.claim_result_sample.applied_to_live}
            emphasis="warn"
          />
          <KeyValueRow
            label="idempotent_replay"
            value={data.claim_result_sample.idempotent_replay}
          />
          <KeyValueRow label="is_preview" value={data.claim_result_sample.is_preview} />
        </ExpandableSection>

        {/* Idempotency */}
        <ExpandableSection title="Idempotency Status (sample)">
          <KeyValueRow
            label="key_format"
            value={data.idempotency_status_sample.key_format}
          />
          <KeyValueRow label="status" value={data.idempotency_status_sample.status} />
        </ExpandableSection>

        {/* Rollback */}
        <ExpandableSection title="Rollback State (sample)">
          <KeyValueRow
            label="rollback_token"
            value={data.rollback_state_sample.rollback_token}
          />
          <KeyValueRow
            label="rolled_back"
            value={data.rollback_state_sample.rolled_back}
          />
        </ExpandableSection>

        {/* Rejected examples */}
        <ExpandableSection
          title="Blocked / Rejected Examples"
          subtitle={`${data.rejected_examples.length} scenari`}
        >
          {data.rejected_examples.map((r, idx) => (
            <View key={`${r.scenario}-${idx}`} style={styles.rejectRow}>
              <Text style={styles.rejectScenario}>{r.scenario}</Text>
              <Text style={styles.rejectReason}>{r.reason}</Text>
            </View>
          ))}
        </ExpandableSection>

        {/* Local Ledger Summary */}
        <ExpandableSection title="Local Ledger Summary">
          <KeyValueRow label="wave" value={data.local_ledger_summary.wave} />
          <KeyValueRow
            label="isolated_from_live"
            value={data.local_ledger_summary.isolated_from_live}
            emphasis="good"
          />
          <KeyValueRow label="canary" value={data.local_ledger_summary.canary} />
          <KeyValueRow
            label="entries_displayed"
            value={data.local_ledger_summary.entries_displayed}
          />
          <KeyValueRow
            label="db_writes"
            value={data.local_ledger_summary.db_writes}
            emphasis="good"
          />
          <KeyValueRow
            label="live_reward_grant"
            value={data.local_ledger_summary.live_reward_grant}
            emphasis="warn"
          />
        </ExpandableSection>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Nessun reward live viene mai assegnato da questa schermata. Vietato
            uso in produzione. Solo deeplink alpha. Live DB richiede pack dedicato.
          </Text>
          <Text style={styles.footerVersion}>
            preview-shell v82 hardened \u00b7 design-only
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================================================
// Styles
// ============================================================================
const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0B0F19' },
  scroll: { flex: 1 },
  scrollContent: { paddingHorizontal: 16, paddingBottom: 32 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 8,
    paddingBottom: 12,
    gap: 12,
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#1A2030',
    alignItems: 'center',
    justifyContent: 'center',
  },
  backText: { color: '#E6E8EE', fontSize: 22, fontWeight: '600' },
  headerTitleBlock: { flex: 1 },
  headerTitle: {
    color: '#F4F6FB',
    fontSize: 20,
    fontWeight: '700',
    letterSpacing: 0.2,
  },
  headerSubtitle: { color: '#8A93A6', fontSize: 12, marginTop: 2 },

  chipsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    paddingVertical: 8,
  },
  chip: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    backgroundColor: '#2A3550',
    borderWidth: 1,
    borderColor: '#3D4D75',
  },
  chipText: {
    color: '#C9D2E6',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.4,
  },

  statusChipsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    paddingBottom: 8,
  },
  statusChip: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 10,
    borderWidth: 1,
  },
  statusChipGood: {
    backgroundColor: '#0F2A1F',
    borderColor: '#1F5A3D',
  },
  statusChipWarn: {
    backgroundColor: '#2A1F0F',
    borderColor: '#5A3D1F',
  },
  statusChipNeutral: {
    backgroundColor: '#1A2236',
    borderColor: '#293553',
  },
  statusChipText: {
    color: '#E6E8EE',
    fontSize: 11,
    fontWeight: '700',
  },

  banner: {
    color: '#C9D2E6',
    fontSize: 13,
    lineHeight: 18,
    backgroundColor: '#16203A',
    padding: 12,
    borderRadius: 10,
    marginVertical: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#FFB547',
  },

  section: {
    backgroundColor: '#121826',
    borderRadius: 14,
    marginVertical: 6,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#1F2A40',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 12,
    minHeight: 48,
  },
  sectionTitle: {
    color: '#F4F6FB',
    fontSize: 15,
    fontWeight: '700',
  },
  sectionSubtitle: { color: '#8A93A6', fontSize: 12, marginTop: 2 },
  chevron: {
    color: '#8A93A6',
    fontSize: 20,
    fontWeight: '700',
    marginLeft: 8,
  },
  sectionBody: {
    paddingHorizontal: 14,
    paddingBottom: 14,
    paddingTop: 4,
    gap: 6,
  },

  rewardGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  rewardCard: {
    flexGrow: 1,
    minWidth: '45%',
    backgroundColor: '#1A2236',
    borderRadius: 10,
    padding: 10,
    borderWidth: 1,
    borderColor: '#293553',
  },
  rewardKey: { color: '#8A93A6', fontSize: 11, fontWeight: '600' },
  rewardValue: {
    color: '#FFD66B',
    fontSize: 20,
    fontWeight: '800',
    marginTop: 4,
  },
  rewardCap: { color: '#6E7791', fontSize: 10, marginTop: 2 },

  kvRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#1F2A40',
  },
  kvLabel: { color: '#8A93A6', fontSize: 12, flex: 1, marginRight: 8 },
  kvValue: {
    color: '#E6E8EE',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'right',
    flexShrink: 1,
    ...Platform.select({ ios: {}, android: {} }),
  },
  kvValueGood: {
    color: '#7BD89E',
    fontSize: 12,
    fontWeight: '700',
    textAlign: 'right',
    flexShrink: 1,
  },
  kvValueWarn: {
    color: '#FFB547',
    fontSize: 12,
    fontWeight: '700',
    textAlign: 'right',
    flexShrink: 1,
  },

  rejectRow: {
    paddingVertical: 6,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#1F2A40',
  },
  rejectScenario: {
    color: '#F4F6FB',
    fontSize: 13,
    fontWeight: '600',
  },
  rejectReason: { color: '#FF8A8A', fontSize: 11, marginTop: 2 },

  footer: {
    marginTop: 20,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#1F2A40',
    alignItems: 'center',
  },
  footerText: {
    color: '#6E7791',
    fontSize: 11,
    textAlign: 'center',
    lineHeight: 16,
  },
  footerVersion: {
    color: '#3D4D75',
    fontSize: 10,
    marginTop: 6,
    letterSpacing: 0.4,
  },
});
