# Frame Animation Safety Standard

**Versione:** v16.12 (introdotta dopo il battle flicker fix)
**Scope:** tutti i frame players, sprite players, rig animati, e qualsiasi
componente che cicla immagini di un eroe in battle, in roster, in preview o
in animazioni shared.
**Owner:** chiunque introduce un nuovo eroe o una nuova animazione.

---

## Perché esiste questa policy

Nel pass v16.12 abbiamo risolto un flicker residuo "appear/disappear" sui
personaggi in battle. La causa proven era una `key` dinamica per-frame su un
`<Image>` di React Native:

```tsx
// ❌ ANTI-PATTERN — causa unmount/mount ad OGNI cambio di frame
<Image key={`hoplite-idle-${idx}`} source={FRAMES[idx]} />
```

A parità di posizione nell'albero, una `key` che cambia fa **distruggere il
componente vecchio e montare uno nuovo**. Su React Native questo significa:

1. Unmount della native `<Image>` view → release texture/view via bridge.
2. Mount di una nuova `<Image>` view → ri-allocazione native + ri-upload texture.

Tra unmount e mount, anche con `fadeDuration={0}`, esiste un draw frame in
cui in quella regione **non c'è nessuna Image renderizzata** → percezione
di flash/disappear breve. Su device fisico è più visibile che in preview web.

---

## Regola d'oro

> **Un layer visivo che deve cambiare nel tempo non deve essere distrutto e
> ricreato per cambiare. Deve restare montato e cambiare le sue props.**

Detto altrimenti: una `<Image>` che gioca un'animazione di N frame deve
vivere come **una singola istanza** per tutta la durata della sequenza.
Cambia solo il `source` (o l'`offset` se è un atlas). React Native swappa
la texture in-place — questo è il path nativo veloce, atomico, zero-flash.

---

## ✅ Pattern SAFE (da seguire)

### A. Frame-by-frame players (`<Image>` distinte per frame)

```tsx
const [idx, setIdx] = useState(0);
// ...timer/ticker che aggiorna idx...

return (
  // ✅ NESSUNA key dinamica. Image stabile, source che cambia.
  <Image
    source={FRAMES[idx]}
    style={{ width, height }}
    resizeMode="contain"
    fadeDuration={0}     // su Android evita micro-crossfade di 300ms
  />
);
```

### B. Sprite-sheet atlas (frame singoli ritagliati)

```tsx
// ✅ Image più larga del viewport, transform translateX o marginLeft
//    per "scrollare" all'offset del frame corrente.
<View style={{ width: frameW, height: frameH, overflow: 'hidden' }}>
  <Image
    source={atlasUri}
    style={{
      width: frameW * totalFrames,
      height: frameH,
      transform: [{ translateX: -currentFrame * frameW }],
    }}
    resizeMode="stretch"
  />
</View>
```

Vedi `AnimatedSprite.tsx` come reference implementation.

### C. Multiplexer multi-state (idle / attack / skill)

Tutti i player sono **sempre montati**, la visibilità è gestita via `opacity`
+ `pointerEvents` (vedi `HeroHopliteRig.tsx`):

```tsx
// ✅ I 3 layer vivono per tutta la sessione di battle.
<View style={[abs, { opacity: showIdle ? 1 : 0 }]}>
  <IdleLoop active={showIdle} />
</View>
<View style={[abs, { opacity: attackActive ? 1 : 0 }]}>
  <AttackPlayer active={attackActive} />
</View>
<View style={[abs, { opacity: skillActive ? 1 : 0 }]}>
  <SkillPlayer active={skillActive} />
</View>
```

### D. Animated wrapper con flag toggle

Se uno stesso layer può essere "animato" o "fermo", **non cambiare il tipo di
componente** in base al flag. Resta sempre `Animated.View`, lascia che lo
style animato cada su `undefined` quando il flag è off:

```tsx
// ✅ Tipo stabile, child <Image> non si rimonta su toggle.
<Animated.View style={[base, animated ? animStyle : null]}>
  <Image source={layer.src} ... />
</Animated.View>
```

---

## ❌ Anti-pattern PROIBITI

### 1. Key dinamica per-frame su `<Image>`

```tsx
// ❌ NO. Causa unmount/mount ad ogni frame change → flicker.
<Image key={`anim-${frameIdx}`} source={FRAMES[frameIdx]} />
<Image key={state} source={SPRITES[state]} />          // anche state-based
<Image key={frameName} source={FRAMES[frameName]} />   // anche name-based
```

### 2. Branching di tipo a parità di posizione

```tsx
// ❌ NO. <View> vs <Animated.View> in stessa posizione = unmount al toggle.
{animated
  ? <Animated.View><Image .../></Animated.View>
  : <View><Image .../></View>
}
```

### 3. Frame player che monta/smonta la `<Image>` su cambio sequenza

```tsx
// ❌ NO. Ogni nuovo playKey distrugge la player precedente.
{playKey % 2 === 0
  ? <PlayerA key="a" />
  : <PlayerB key="b" />
}
```

### 4. Componente definito inline nel render del parent

```tsx
// ❌ NO. Ogni render del parent crea un nuovo "tipo" di componente
//        → React reinizializza l'intero sottoalbero.
function ParentScreen() {
  const Wrapper = ({ children }) => <View>{children}</View>;  // ❌
  return <Wrapper><Sprite /></Wrapper>;
}
```

(Già documentato in v16.5 BattleWrapper Remount Fix.)

### 5. Conditional render che alterna `null` e componente visibile

```tsx
// ❌ Cattivo per un frame player attivo: ogni nascondi/mostra è unmount.
{visible && <Sprite frames={FRAMES} />}

// ✅ Meglio: opacity-toggle, sprite sempre montato.
<View style={{ opacity: visible ? 1 : 0 }}>
  <Sprite frames={FRAMES} />
</View>
```

---

## Checklist obbligatoria per ogni nuovo eroe

Quando si introduce un nuovo eroe con animazioni, verificare:

- [ ] Nessuna `<Image>` ha `key` legata a frame index, frame name, sprite
      state, o ad altri valori che cambiano durante l'animazione.
- [ ] Le sequenze di frame avanzano cambiando `source` (o `transform`/
      `marginLeft` per atlas), **non** rimontando il componente.
- [ ] Il multiplexer di stato (idle/attack/skill/...) tiene tutti i layer
      sempre montati, con visibilità via `opacity`.
- [ ] Eventuali toggle "animato/statico" non cambiano il tipo di componente
      (sempre `Animated.View`, animStyle a `null` quando inattivo).
- [ ] `fadeDuration={0}` su tutte le `<Image>` Android-side dei frame
      players (evita il crossfade default di 300ms tra source consecutivi).
- [ ] Nessun componente definito inline nel render del parent.
- [ ] Eventuale pause si propaga **fermando il tick** (cancelAnimation,
      pausedConsumerCount counter, paused prop), **non** smontando il
      sottoalbero.

---

## Reference implementations approvate

| File                                | Pattern        | Note                         |
| ----------------------------------- | -------------- | ---------------------------- |
| `HeroHopliteIdleLoop.tsx`           | A (frame-by-frame) | Global ticker + stagger phase |
| `HeroHopliteAffondo.tsx`            | A              | 8 frame attack sequence       |
| `HeroHopliteGuardiaFerrea.tsx`      | A              | 6 frame skill sequence        |
| `HeroHopliteRig.tsx`                | C (multiplexer) | 3 layer always mounted        |
| `AnimatedSprite.tsx`                | B (atlas)      | translateX horizontal sheet   |
| `BattleSprite.tsx` (sprite-sheet)   | B              | marginLeft offset path        |
| `HeroHopliteIdle.tsx` (legacy rig)  | D (toggle)     | Animated.View always          |

Tutti i file sopra sono stati audit-approved nel pass v16.12.

---

## Quando in dubbio

Chiedi: "se il flag/index cambia, **chi viene smontato**?" Se la risposta è
"un componente Image" o "un sottoalbero che contiene un'Image" → stai
introducendo un potenziale flicker. Riformula con uno dei pattern SAFE sopra.
