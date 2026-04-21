/**
 * preloadAssets — utility cross-platform per pre-caricare asset della UI.
 *
 * Regole (richieste esplicitamente dall'utente):
 *  1. Distinzione rigorosa tra asset LOCALI (require(...) → number) e
 *     asset REMOTI (URL string).
 *       • Locali  → Asset.fromModule(mod).downloadAsync()  [expo-asset]
 *       • Remoti  → Image.prefetch(uri)                    [react-native]
 *  2. Nessun singolo fallimento può bloccare l'insieme: usiamo
 *     Promise.allSettled + try/catch per-asset.
 *  3. Timeout per-asset (default 3000ms): un asset "lento" non blocca il gate.
 *  4. Progresso incrementale REALE: `onProgress(done, total)` viene
 *     chiamato dopo OGNI singolo asset che si risolve/rigetta/timeout,
 *     così la progress bar avanza davvero step-by-step.
 *  5. La funzione ritorna sempre (mai rigetta).
 */
import { Image } from 'react-native';
import { Asset } from 'expo-asset';

export type AssetRef = any;

export interface PreloadResult {
  total: number;
  loaded: number;
  failed: number;
}

/** Promise che si risolve dopo `ms` con valore `fallback`. */
function withTimeout<T>(p: Promise<T>, ms: number, fallback: T): Promise<T> {
  return new Promise<T>((resolve) => {
    let settled = false;
    const t = setTimeout(() => {
      if (settled) return;
      settled = true;
      resolve(fallback);
    }, ms);
    p.then(
      (v) => {
        if (settled) return;
        settled = true;
        clearTimeout(t);
        resolve(v);
      },
      () => {
        if (settled) return;
        settled = true;
        clearTimeout(t);
        resolve(fallback);
      },
    );
  });
}

/** Preload singolo — routing per tipo, mai throwa. */
async function preloadOne(
  ref: AssetRef,
  perAssetTimeoutMs: number,
): Promise<boolean> {
  if (ref == null) return false;

  // LOCAL ASSET (require(...) → number su native, object su web)
  if (typeof ref === 'number' || (typeof ref === 'object' && ref !== null)) {
    try {
      const asset = Asset.fromModule(ref);
      await withTimeout(asset.downloadAsync(), perAssetTimeoutMs, null);
      return !!asset.localUri || !!asset.uri;
    } catch {
      return false;
    }
  }

  // REMOTE URL (string http(s)://... o data:)
  if (typeof ref === 'string' && ref.length > 0) {
    // data: URI sono già in memoria → skip prefetch (conta come loaded)
    if (ref.startsWith('data:')) return true;
    try {
      const ok = await withTimeout(Image.prefetch(ref), perAssetTimeoutMs, false);
      return !!ok;
    } catch {
      return false;
    }
  }

  return false;
}

/**
 * Preload di una lista eterogenea di asset.
 * - dedupe interno
 * - tollera errori singoli (Promise.allSettled)
 * - timeout per-asset
 * - progresso incrementale reale
 */
export async function preloadAssets(
  refs: AssetRef[],
  onProgress?: (done: number, total: number) => void,
  perAssetTimeoutMs: number = 3000,
): Promise<PreloadResult> {
  // Dedupe: locali per reference (number), remoti per stringa.
  const seen = new Set<any>();
  const unique: AssetRef[] = [];
  for (const r of refs) {
    if (r == null) continue;
    const key = typeof r === 'string' ? `u:${r}` : typeof r === 'number' ? `l:${r}` : r;
    if (seen.has(key)) continue;
    seen.add(key);
    unique.push(r);
  }

  const total = unique.length;
  if (total === 0) {
    onProgress?.(0, 0);
    return { total: 0, loaded: 0, failed: 0 };
  }

  let done = 0;
  let loaded = 0;
  let failed = 0;

  const tasks = unique.map(async (ref) => {
    const ok = await preloadOne(ref, perAssetTimeoutMs);
    done++;
    if (ok) loaded++; else failed++;
    try { onProgress?.(done, total); } catch { /* ignore */ }
    return ok;
  });

  // allSettled: nessun singolo reject può bloccare. Inoltre preloadOne
  // non throwa mai, quindi è doppio-safe.
  await Promise.allSettled(tasks);

  return { total, loaded, failed };
}
