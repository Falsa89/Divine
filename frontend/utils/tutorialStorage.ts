/**
 * frontend/utils/tutorialStorage.ts
 *
 * PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION_PACK
 * Sentinella: v19
 *
 * Helper AsyncStorage per la persistenza locale della completion dei tutorial.
 * NO server DB writes. NO mutazioni live. Solo storage locale del dispositivo.
 */
import AsyncStorage from '@react-native-async-storage/async-storage';

export const TUTORIAL_COMPLETION_NAMESPACE = '@project_t/tutorial/v1/completion';

function key(tutorialId: string): string {
  return `${TUTORIAL_COMPLETION_NAMESPACE}/${tutorialId}`;
}

export async function isTutorialCompleted(tutorialId: string): Promise<boolean> {
  try {
    const v = await AsyncStorage.getItem(key(tutorialId));
    return v === '1';
  } catch {
    return false;
  }
}

export async function markTutorialCompleted(tutorialId: string): Promise<void> {
  try {
    await AsyncStorage.setItem(key(tutorialId), '1');
  } catch {
    // swallow: storage failure must not break UX
  }
}

export async function resetTutorial(tutorialId: string): Promise<void> {
  try {
    await AsyncStorage.removeItem(key(tutorialId));
  } catch {
    // swallow
  }
}

/** Test-only helper. NON usare in produzione: rimuove TUTTI i flag di completion locali. */
export async function resetAllTutorials(tutorialIds: string[]): Promise<void> {
  try {
    await Promise.all(tutorialIds.map((id) => AsyncStorage.removeItem(key(id))));
  } catch {
    // swallow
  }
}
