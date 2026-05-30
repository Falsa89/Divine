/**
 * frontend/components/TutorialOverlay.tsx
 *
 * PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION_PACK
 * Sentinella: v19 PUBLIC_SYNC_TAG_RESYNC_v19_GUIDE_CODEX_AND_TUTORIAL
 *
 * Overlay riusabile per i tutorial first-unlock/onboarding.
 * Mostra una sequenza di steps (titolo + body) con pulsanti Avanti/Salta/Fine.
 * Marca completion locale via AsyncStorage al termine o allo skip.
 *
 * WIRING: NON e\u2019 wirato in alcuna schermata in questo pack (gameplay touch vietato).
 * Pronto per essere usato in pack futuri.
 *
 * Vincoli:
 *  - read-only props, NESSUNA mutation di gameplay/economy/server.
 *  - touch target >= 44pt (CTA 48pt).
 *  - safe area aware tramite useSafeAreaInsets.
 */
import React, { useCallback, useMemo, useState } from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Platform,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { markTutorialCompleted } from '../utils/tutorialStorage';
import type { TutorialEntry } from '../constants/tutorials';

export type TutorialOverlayProps = {
  /** Entry tutorial da mostrare. */
  entry: TutorialEntry;
  /** Se true, la overlay e\u2019 visibile. */
  visible: boolean;
  /** Callback invocato a chiusura (Fine o Salta). Riceve sempre la stessa overlay marcata come completata localmente. */
  onClose: () => void;
};

export default function TutorialOverlay({ entry, visible, onClose }: TutorialOverlayProps) {
  const insets = useSafeAreaInsets();
  const [stepIndex, setStepIndex] = useState(0);

  const totalSteps = entry.steps.length;
  const currentStep = useMemo(() => entry.steps[stepIndex] ?? entry.steps[0], [entry.steps, stepIndex]);
  const isLast = stepIndex >= totalSteps - 1;

  const handleNext = useCallback(async () => {
    if (isLast) {
      await markTutorialCompleted(entry.id);
      setStepIndex(0);
      onClose();
    } else {
      setStepIndex((i) => Math.min(i + 1, totalSteps - 1));
    }
  }, [isLast, entry.id, onClose, totalSteps]);

  const handleSkip = useCallback(async () => {
    await markTutorialCompleted(entry.id);
    setStepIndex(0);
    onClose();
  }, [entry.id, onClose]);

  return (
    <Modal visible={visible} animationType="fade" transparent statusBarTranslucent onRequestClose={handleSkip}>
      <View style={styles.backdrop}>
        <View style={[styles.card, { marginTop: insets.top + 24, marginBottom: insets.bottom + 24 }]}>
          <Text style={styles.progress} accessibilityLabel={`Step ${stepIndex + 1} di ${totalSteps}`}>
            {`Step ${stepIndex + 1} / ${totalSteps}`}
          </Text>
          <Text style={styles.title}>{currentStep.title_it}</Text>
          <ScrollView style={styles.bodyScroll} contentContainerStyle={styles.bodyContent}>
            <Text style={styles.body}>{currentStep.body_it}</Text>
          </ScrollView>
          <View style={styles.ctaRow}>
            <TouchableOpacity
              onPress={handleSkip}
              style={[styles.btn, styles.btnSecondary]}
              accessibilityRole="button"
              accessibilityLabel="Salta tutorial"
            >
              <Text style={styles.btnTextSecondary}>Salta</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={handleNext}
              style={[styles.btn, styles.btnPrimary]}
              accessibilityRole="button"
              accessibilityLabel={isLast ? 'Fine tutorial' : 'Avanti'}
            >
              <Text style={styles.btnTextPrimary}>{isLast ? 'Fine' : 'Avanti'}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.75)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  card: {
    width: '100%',
    maxWidth: 560,
    backgroundColor: '#141425',
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: '#3a3a55',
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOpacity: 0.4,
        shadowOffset: { width: 0, height: 8 },
        shadowRadius: 16,
      },
      android: { elevation: 12 },
    }),
  },
  progress: { color: '#8a8aaa', fontSize: 12, marginBottom: 8, letterSpacing: 1 },
  title: { color: '#fff', fontSize: 22, fontWeight: '700', marginBottom: 12 },
  bodyScroll: { maxHeight: 220, marginBottom: 16 },
  bodyContent: { paddingRight: 4 },
  body: { color: '#dcdcef', fontSize: 15, lineHeight: 22 },
  ctaRow: { flexDirection: 'row', justifyContent: 'flex-end', gap: 12 },
  btn: {
    minHeight: 48,
    minWidth: 96,
    paddingHorizontal: 18,
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnPrimary: { backgroundColor: '#5b6df0' },
  btnSecondary: { backgroundColor: 'transparent', borderWidth: 1, borderColor: '#5a5a7a' },
  btnTextPrimary: { color: '#fff', fontSize: 15, fontWeight: '700' },
  btnTextSecondary: { color: '#bcbcd8', fontSize: 15, fontWeight: '600' },
});
