/**
 * PROJECT_TOWER_OF_THE_HELLS_RUNTIME — Schermata TEST MVP
 *
 * Modalità: Torre degli Inferi (mode_id = tower_of_the_hells)
 * Stato: frontend TEST MVP only. Nessun backend runtime. Nessun DB write.
 *        Nessuna economy mutation. Asset e audio = test_placeholder.
 *        Replace_before_release = true.
 *
 * Vincoli rispettati:
 *  - NO stamina (pack 183)
 *  - NO IAP / VIP / BP / Shop activation
 *  - NO Artifact / Divine Weapon / Synergy V2 / Status / VFX runtime
 *  - NO Combat engine call (simulazione TEST inline)
 *  - NO server profile live
 *  - NO audio engine
 */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Modal,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useRouter } from 'expo-router';
import {
  TOWER_OF_THE_HELLS_BOSS_EVERY,
  TOWER_OF_THE_HELLS_FLOORS,
  TOWER_OF_THE_HELLS_LOCAL_PROGRESS_KEY,
  TOWER_OF_THE_HELLS_MODE_ID,
} from '../constants/towerOfTheHellsFloors';
import type { TowerFloorTestPlaceholder } from '../constants/towerOfTheHellsFloors';
// Pack 123 — Preview lobby URL builder (no-write, no-DB, no-grant).
// Garantisce navigazione deterministica `mode=tower&floor_id=X` senza crash
// e senza chiamate live al backend.
import { buildPreviewLobbyUrl } from '../src/utils/previewBattleTeam';

type FloorState = 'locked' | 'unlocked' | 'completed';

const BG = '#10031d';
const CARD_BG = '#1d0935';
const CARD_BG_LOCKED = '#170825';
const CARD_BG_COMPLETED = '#2c1556';
const ACCENT = '#ff6b3d';
const ACCENT_BOSS = '#ff3d6b';
const TEXT = '#f5e9ff';
const TEXT_DIM = '#9b86b8';
const BORDER = '#3a1b66';
const BORDER_BOSS = '#7a1b44';
const TEST_BANNER = '#ffb454';

interface LocalProgress {
  highest_cleared_floor: number;
  updated_at: string;
}

const INITIAL_PROGRESS: LocalProgress = {
  highest_cleared_floor: 0,
  updated_at: new Date(0).toISOString(),
};

function floorStateFor(floorId: number, highestCleared: number): FloorState {
  if (floorId <= highestCleared) return 'completed';
  if (floorId === highestCleared + 1) return 'unlocked';
  return 'locked';
}

export default function TowerOfTheHellsScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(true);
  const [progress, setProgress] = useState<LocalProgress>(INITIAL_PROGRESS);
  const [selectedFloor, setSelectedFloor] = useState<TowerFloorTestPlaceholder | null>(null);
  const [showFirstClearBanner, setShowFirstClearBanner] = useState<boolean>(false);

  const loadProgress = useCallback(async () => {
    try {
      const raw = await AsyncStorage.getItem(TOWER_OF_THE_HELLS_LOCAL_PROGRESS_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as LocalProgress;
        if (typeof parsed.highest_cleared_floor === 'number') {
          setProgress(parsed);
        }
      }
    } catch {
      // ignore corrupted local store; revert to INITIAL_PROGRESS
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProgress();
  }, [loadProgress]);

  const saveProgress = useCallback(async (next: LocalProgress) => {
    setProgress(next);
    try {
      await AsyncStorage.setItem(
        TOWER_OF_THE_HELLS_LOCAL_PROGRESS_KEY,
        JSON.stringify(next),
      );
    } catch {
      // best effort, this is a TEST MVP
    }
  }, []);

  const handleTestClear = useCallback(
    async (floor: TowerFloorTestPlaceholder) => {
      // TEST simulation only: no backend call, no economy mutation
      const currentHighest = progress.highest_cleared_floor;
      // Only advance highest_cleared_floor; replay of already-cleared floors
      // does NOT change anything (anti-farming policy enforced client-side).
      if (floor.id === currentHighest + 1) {
        const next: LocalProgress = {
          highest_cleared_floor: floor.id,
          updated_at: new Date().toISOString(),
        };
        await saveProgress(next);
        setShowFirstClearBanner(true);
      }
      setSelectedFloor(null);
    },
    [progress.highest_cleared_floor, saveProgress],
  );

  // Pack 123 — Fix crash al tap del piano.
  // Apre la pre-battle-lobby in modalita' preview deterministica con
  // mode=tower e floor_id propagato. NESSUN reward, NESSUN DB write.
  const handleOpenPreviewLobby = useCallback(
    (floor: TowerFloorTestPlaceholder) => {
      try {
        const url = buildPreviewLobbyUrl({
          mode: 'tower',
          encounter_id: `enc_tower_floor_${floor.id}`,
          enemy_source_id: `tower_floor_${floor.id}_preview`,
          enemy_source_type: 'authored',
          floor_id: floor.id,
        });
        setSelectedFloor(null);
        router.push(url as any);
      } catch (_e) {
        // fail-closed: in caso di errore non navigare, semplicemente chiudi
        // il modal per evitare crash UI.
        setSelectedFloor(null);
      }
    },
    [router],
  );

  const handleResetProgress = useCallback(async () => {
    await saveProgress(INITIAL_PROGRESS);
    setShowFirstClearBanner(false);
  }, [saveProgress]);

  const totalCleared = progress.highest_cleared_floor;
  const totalFloors = TOWER_OF_THE_HELLS_FLOORS.length;

  const renderFloorItem = useCallback(
    ({ item }: { item: TowerFloorTestPlaceholder }) => {
      const state = floorStateFor(item.id, totalCleared);
      const isBoss = item.is_boss;
      const cardBg =
        state === 'completed'
          ? CARD_BG_COMPLETED
          : state === 'locked'
            ? CARD_BG_LOCKED
            : CARD_BG;
      const borderColor = isBoss ? BORDER_BOSS : BORDER;
      const icon =
        state === 'completed'
          ? '\u2705'
          : state === 'locked'
            ? '\uD83D\uDD12'
            : isBoss
              ? '\uD83D\uDC79'
              : '\u2694\uFE0F';
      const disabled = state === 'locked';
      return (
        <TouchableOpacity
          accessibilityRole="button"
          accessibilityLabel={`Floor ${item.id} ${state} (TEST) — apri preview lobby`}
          activeOpacity={0.8}
          disabled={disabled}
          // Pack 123 — Tap principale: apri il dettaglio (modal sicuro).
          // Il modal contiene il bottone "Avvia Preview (Lobby)" che effettua
          // il routing a /pre-battle-lobby?mode=tower&floor_id=X (no crash).
          onPress={() => setSelectedFloor(item)}
          style={[
            styles.floorCard,
            { backgroundColor: cardBg, borderColor },
            disabled ? styles.floorCardDisabled : null,
          ]}
        >
          <View style={styles.floorIconWrap}>
            <Text style={styles.floorIcon}>{icon}</Text>
            {isBoss ? (
              <Text style={styles.floorIconHellfire}>{'\uD83D\uDD25'}</Text>
            ) : null}
          </View>
          <View style={styles.floorTextWrap}>
            <Text style={styles.floorName}>{item.name}</Text>
            <Text style={styles.floorMeta}>
              {`Power TEST: ${item.recommended_team_power_test} \u00b7 ${state.toUpperCase()}`}
            </Text>
            {isBoss ? (
              <Text style={styles.floorBossTag}>{'BOSS \u00b7 PLACEHOLDER'}</Text>
            ) : null}
          </View>
          <View style={styles.floorIdWrap}>
            <Text style={styles.floorIdText}>{item.id}</Text>
          </View>
        </TouchableOpacity>
      );
    },
    [totalCleared],
  );

  const headerNode = useMemo(
    () => (
      <View style={styles.headerWrap}>
        <Text style={styles.title}>{'Torre degli Inferi (TEST)'}</Text>
        <Text style={styles.subtitle}>
          {`mode_id: ${TOWER_OF_THE_HELLS_MODE_ID} \u00b7 Boss ogni ${TOWER_OF_THE_HELLS_BOSS_EVERY} floors`}
        </Text>
        <View style={styles.testBanner}>
          <Text style={styles.testBannerText}>
            {'TEST PLACEHOLDER \u00b7 asset/audio non finali \u00b7 nessuna ricompensa economy'}
          </Text>
        </View>
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{totalCleared}</Text>
            <Text style={styles.statLabel}>{'Cleared'}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{totalFloors}</Text>
            <Text style={styles.statLabel}>{'Floors (TEST)'}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{'0'}</Text>
            <Text style={styles.statLabel}>{'Stamina'}</Text>
          </View>
        </View>
      </View>
    ),
    [totalCleared, totalFloors],
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.loadingWrap}>
          <ActivityIndicator color={ACCENT} size="large" />
          <Text style={styles.loadingText}>{'Caricamento progresso TEST...'}</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.topBar}>
        <TouchableOpacity
          accessibilityRole="button"
          accessibilityLabel="Torna indietro"
          onPress={() => router.back()}
          style={styles.backBtn}
          hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
        >
          <Text style={styles.backBtnText}>{'\u2190 Indietro'}</Text>
        </TouchableOpacity>
        <Text style={styles.topBarTitle}>{'Torre degli Inferi'}</Text>
        <TouchableOpacity
          accessibilityRole="button"
          accessibilityLabel="Reset progress TEST"
          onPress={handleResetProgress}
          style={styles.resetBtn}
          hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
        >
          <Text style={styles.resetBtnText}>{'Reset (TEST)'}</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={[...TOWER_OF_THE_HELLS_FLOORS]}
        keyExtractor={(it) => `tower-floor-${it.id}`}
        renderItem={renderFloorItem}
        ListHeaderComponent={headerNode}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator
      />

      <Modal
        animationType="fade"
        transparent
        visible={selectedFloor != null}
        onRequestClose={() => setSelectedFloor(null)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <ScrollView contentContainerStyle={styles.modalScrollContent}>
              <Text style={styles.modalTitle}>{selectedFloor?.name ?? ''}</Text>
              <Text style={styles.modalSubtitle}>
                {selectedFloor?.is_boss
                  ? `BOSS FLOOR \u00b7 PLACEHOLDER`
                  : `Normal floor \u00b7 PLACEHOLDER`}
              </Text>
              <View style={styles.modalRow}>
                <Text style={styles.modalLabel}>{'Power TEST'}</Text>
                <Text style={styles.modalValue}>
                  {selectedFloor?.recommended_team_power_test ?? '\u2014'}
                </Text>
              </View>
              <View style={styles.modalRow}>
                <Text style={styles.modalLabel}>{'Reward (TEST)'}</Text>
                <Text style={styles.modalValue}>
                  {selectedFloor?.first_clear_reward_design_label ?? '\u2014'}
                </Text>
              </View>
              <View style={styles.modalRow}>
                <Text style={styles.modalLabel}>{'Stamina'}</Text>
                <Text style={styles.modalValue}>{'0 (no_stamina)'}</Text>
              </View>
              <View style={styles.modalRow}>
                <Text style={styles.modalLabel}>{'IAP / Ticket'}</Text>
                <Text style={styles.modalValue}>{'NESSUNO'}</Text>
              </View>
              <View style={styles.modalRow}>
                <Text style={styles.modalLabel}>{'Combat'}</Text>
                <Text style={styles.modalValue}>{'Simulazione TEST'}</Text>
              </View>
              <View style={styles.modalNoteBox}>
                <Text style={styles.modalNoteText}>
                  {'Questa \u00e8 una simulazione TEST. Nessuna ricompensa economy verr\u00e0 concessa. Nessuna chiamata al battle engine. asset_status = test_placeholder.'}
                </Text>
              </View>
            </ScrollView>
            <View style={styles.modalActions}>
              <Pressable
                accessibilityRole="button"
                accessibilityLabel="Annulla"
                onPress={() => setSelectedFloor(null)}
                style={({ pressed }) => [
                  styles.modalBtn,
                  styles.modalBtnGhost,
                  pressed ? { opacity: 0.7 } : null,
                ]}
              >
                <Text style={styles.modalBtnGhostText}>{'Annulla'}</Text>
              </Pressable>
              {/* Pack 123 — Avvia Preview Lobby (no crash, no DB write). */}
              <Pressable
                accessibilityRole="button"
                accessibilityLabel="Avvia preview lobby per questo piano"
                onPress={() => selectedFloor && handleOpenPreviewLobby(selectedFloor)}
                style={({ pressed }) => [
                  styles.modalBtn,
                  styles.modalBtnPrimary,
                  pressed ? { opacity: 0.7 } : null,
                ]}
              >
                <Text style={styles.modalBtnPrimaryText}>{'Avvia Preview Lobby'}</Text>
              </Pressable>
              <Pressable
                accessibilityRole="button"
                accessibilityLabel="Test Clear floor"
                onPress={() => selectedFloor && handleTestClear(selectedFloor)}
                style={({ pressed }) => [
                  styles.modalBtn,
                  styles.modalBtnGhost,
                  pressed ? { opacity: 0.7 } : null,
                ]}
              >
                <Text style={styles.modalBtnGhostText}>{'Test Clear (TEST)'}</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>

      <Modal
        animationType="fade"
        transparent
        visible={showFirstClearBanner}
        onRequestClose={() => setShowFirstClearBanner(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.bannerCard}>
            <Text style={styles.bannerEmoji}>{'\u2728'}</Text>
            <Text style={styles.bannerTitle}>{'First Clear (TEST)'}</Text>
            <Text style={styles.bannerText}>
              {'Badge UI design-only. Nessuna ricompensa economy concessa. asset_status = test_placeholder.'}
            </Text>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Chiudi banner"
              onPress={() => setShowFirstClearBanner(false)}
              style={({ pressed }) => [
                styles.modalBtn,
                styles.modalBtnPrimary,
                pressed ? { opacity: 0.7 } : null,
              ]}
            >
              <Text style={styles.modalBtnPrimaryText}>{'OK'}</Text>
            </Pressable>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: BG,
  },
  loadingWrap: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    color: TEXT_DIM,
    marginTop: 12,
    fontSize: 14,
  },
  topBar: {
    height: 52,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  topBarTitle: {
    color: TEXT,
    fontSize: 16,
    fontWeight: '700',
  },
  backBtn: {
    paddingVertical: 6,
    paddingHorizontal: 8,
  },
  backBtnText: {
    color: ACCENT,
    fontSize: 14,
    fontWeight: '600',
  },
  resetBtn: {
    paddingVertical: 6,
    paddingHorizontal: 8,
  },
  resetBtnText: {
    color: TEXT_DIM,
    fontSize: 12,
    fontWeight: '600',
  },
  headerWrap: {
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  title: {
    color: TEXT,
    fontSize: 22,
    fontWeight: '800',
  },
  subtitle: {
    color: TEXT_DIM,
    fontSize: 12,
    marginTop: 4,
  },
  testBanner: {
    marginTop: 12,
    backgroundColor: TEST_BANNER,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  testBannerText: {
    color: '#3a1500',
    fontSize: 12,
    fontWeight: '700',
  },
  statsRow: {
    marginTop: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statBox: {
    flex: 1,
    marginHorizontal: 4,
    backgroundColor: CARD_BG,
    borderRadius: 8,
    paddingVertical: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: BORDER,
  },
  statValue: {
    color: ACCENT,
    fontSize: 18,
    fontWeight: '800',
  },
  statLabel: {
    color: TEXT_DIM,
    fontSize: 11,
    marginTop: 2,
  },
  listContent: {
    paddingBottom: 24,
  },
  floorCard: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 16,
    marginTop: 10,
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderRadius: 10,
    borderWidth: 1,
    minHeight: 64,
  },
  floorCardDisabled: {
    opacity: 0.55,
  },
  floorIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#000000',
    alignItems: 'center',
    justifyContent: 'center',
  },
  floorIcon: {
    fontSize: 22,
  },
  floorIconHellfire: {
    position: 'absolute',
    bottom: -4,
    right: -4,
    fontSize: 14,
  },
  floorTextWrap: {
    flex: 1,
    marginLeft: 12,
  },
  floorName: {
    color: TEXT,
    fontSize: 14,
    fontWeight: '700',
  },
  floorMeta: {
    color: TEXT_DIM,
    fontSize: 12,
    marginTop: 2,
  },
  floorBossTag: {
    color: ACCENT_BOSS,
    fontSize: 11,
    fontWeight: '700',
    marginTop: 2,
  },
  floorIdWrap: {
    width: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  floorIdText: {
    color: TEXT_DIM,
    fontSize: 12,
    fontWeight: '700',
  },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  modalCard: {
    width: '100%',
    maxWidth: 480,
    backgroundColor: '#1a0a30',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: BORDER,
    overflow: 'hidden',
  },
  modalScrollContent: {
    padding: 18,
  },
  modalTitle: {
    color: TEXT,
    fontSize: 18,
    fontWeight: '800',
  },
  modalSubtitle: {
    color: ACCENT_BOSS,
    fontSize: 12,
    fontWeight: '700',
    marginTop: 2,
    marginBottom: 12,
  },
  modalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  modalLabel: {
    color: TEXT_DIM,
    fontSize: 12,
  },
  modalValue: {
    color: TEXT,
    fontSize: 12,
    fontWeight: '700',
    maxWidth: '60%',
    textAlign: 'right',
  },
  modalNoteBox: {
    marginTop: 12,
    backgroundColor: TEST_BANNER,
    borderRadius: 8,
    padding: 8,
  },
  modalNoteText: {
    color: '#3a1500',
    fontSize: 11,
    fontWeight: '700',
  },
  modalActions: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: BORDER,
  },
  modalBtn: {
    flex: 1,
    paddingVertical: 14,
    alignItems: 'center',
  },
  modalBtnGhost: {
    borderRightWidth: 1,
    borderRightColor: BORDER,
  },
  modalBtnGhostText: {
    color: TEXT_DIM,
    fontSize: 14,
    fontWeight: '700',
  },
  modalBtnPrimary: {
    backgroundColor: ACCENT,
  },
  modalBtnPrimaryText: {
    color: '#1a0500',
    fontSize: 14,
    fontWeight: '800',
  },
  bannerCard: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: '#1a0a30',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: BORDER,
    alignItems: 'center',
    padding: 24,
  },
  bannerEmoji: {
    fontSize: 44,
  },
  bannerTitle: {
    color: TEXT,
    fontSize: 18,
    fontWeight: '800',
    marginTop: 8,
  },
  bannerText: {
    color: TEXT_DIM,
    fontSize: 12,
    marginTop: 8,
    marginBottom: 16,
    textAlign: 'center',
  },
});
