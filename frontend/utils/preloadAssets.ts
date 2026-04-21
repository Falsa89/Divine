/**
 * preloadAssets — utility cross-platform per pre-caricare immagini locali
 * (require(...)) o remote (URI string). Funziona su web (Image.prefetch sulla
 * URL bundled) e su native (risolve l'asset source e lo scarica nella cache).
 *
 * Non usa expo-asset (dipendenza opzionale): si basa su Image.resolveAssetSource
 * + Image.prefetch che sono API di React Native core.
 */
import { Image } from 'react-native';

export type AssetRef = any;

/** Risolve un require(...) o URI a un URL/percorso prefetchabile. */
function resolveToUri(ref: AssetRef): string | null {
  if (!ref) return null;
  if (typeof ref === 'string') return ref;
  try {
    const src: any = Image.resolveAssetSource(ref);
    if (src?.uri) return src.uri;
  } catch { /* ignore */ }
  return null;
}

/**
 * Preloada una lista di asset (dedupe automatico).
 * Callback `onProgress` chiamato dopo ogni singolo asset (done/total).
 * Tolerant: ogni singolo fallimento viene ignorato, l'insieme continua.
 */
export async function preloadAssets(
  refs: AssetRef[],
  onProgress?: (done: number, total: number) => void,
): Promise<{ total: number; loaded: number; failed: number }> {
  const uris = Array.from(
    new Set(refs.map(resolveToUri).filter((u): u is string => !!u))
  );
  const total = uris.length;
  if (total === 0) {
    onProgress?.(0, 0);
    return { total: 0, loaded: 0, failed: 0 };
  }

  let done = 0;
  let loaded = 0;
  let failed = 0;

  await Promise.all(
    uris.map(async (uri) => {
      try {
        // Image.prefetch torna true/false o throws.
        const ok = await Image.prefetch(uri);
        if (ok) loaded++; else failed++;
      } catch {
        failed++;
      } finally {
        done++;
        onProgress?.(done, total);
      }
    })
  );

  return { total, loaded, failed };
}
