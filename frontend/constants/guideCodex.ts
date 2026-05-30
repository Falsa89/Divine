/**
 * frontend/constants/guideCodex.ts
 *
 * PROJECT_GUIDE_CODEX_AND_TUTORIAL_FOUNDATION_PACK
 * Sentinella: v19 PUBLIC_SYNC_TAG_RESYNC_v19_GUIDE_CODEX_AND_TUTORIAL
 *
 * Registry runtime delle categorie e degli entries della Guida/Codex.
 * Content status: test_content. replace_before_release = true.
 * NO mutazioni: read-only data.
 */

export type GuideCategory = {
  id: string;
  order: number;
  label_it: string;
  icon_hint: string;
};

export type GuideSection = {
  heading_it: string;
  body_it: string;
};

export type GuideEntry = {
  id: string;
  category: string;
  order: number;
  title_it: string;
  summary_it: string;
  sections: GuideSection[];
};

export const GUIDE_CONTENT_STATUS = 'test_content';
export const GUIDE_REPLACE_BEFORE_RELEASE = true;

export const GUIDE_CATEGORIES: GuideCategory[] = [
  { id: 'getting_started',              order: 1,  label_it: 'Inizia qui',                            icon_hint: 'book' },
  { id: 'combat_basics',                order: 2,  label_it: 'Basi del combattimento',                icon_hint: 'sword' },
  { id: 'heroes_and_team',              order: 3,  label_it: 'Eroi e Squadra',                        icon_hint: 'team' },
  { id: 'team_columns_and_positioning', order: 4,  label_it: 'Colonne squadra e posizionamento',      icon_hint: 'grid' },
  { id: 'battle_power_and_power_delta', order: 5,  label_it: 'Potere di Battaglia e variazioni',      icon_hint: 'flame' },
  { id: 'items_materials_and_farming',  order: 6,  label_it: 'Oggetti, Materiali e Farming',          icon_hint: 'chest' },
  { id: 'buff_sources',                 order: 7,  label_it: 'Fonti di Buff',                         icon_hint: 'spark' },
  { id: 'modes',                        order: 8,  label_it: 'Modalita\u2019 di gioco',               icon_hint: 'map' },
  { id: 'home_and_avatars',             order: 9,  label_it: 'Home e Avatar',                         icon_hint: 'home' },
  { id: 'guild_and_social',             order: 10, label_it: 'Gilda e Social',                        icon_hint: 'shield' },
  { id: 'events',                       order: 11, label_it: 'Eventi',                                icon_hint: 'calendar' },
  { id: 'economy_shop_bp_vip_iap',      order: 12, label_it: 'Economia, Negozio, BP, VIP, IAP',       icon_hint: 'coin' },
  { id: 'faq',                          order: 13, label_it: 'FAQ',                                   icon_hint: 'help' },
];

export const GUIDE_ENTRIES: GuideEntry[] = [
  {
    id: 'guide_getting_started',
    category: 'getting_started',
    order: 1,
    title_it: 'Benvenuto in Project T',
    summary_it: 'Inizia da qui per capire come funzionano combattimento, squadra ed economia.',
    sections: [
      { heading_it: 'Obiettivo del gioco', body_it: 'PLACEHOLDER: testo segnaposto. Sostituire prima del rilascio.' },
      { heading_it: 'Primi passi',         body_it: 'PLACEHOLDER: testo segnaposto.' },
    ],
  },
  {
    id: 'guide_combat_basics',
    category: 'combat_basics',
    order: 2,
    title_it: 'Basi del combattimento',
    summary_it: 'Come funzionano turni, abilita\u2019, Active Battle Power.',
    sections: [
      { heading_it: 'Schema turni', body_it: 'PLACEHOLDER.' },
      { heading_it: 'Abilita\u2019 Q/U', body_it: 'PLACEHOLDER.' },
    ],
  },
  {
    id: 'guide_team_columns_positioning',
    category: 'team_columns_and_positioning',
    order: 3,
    title_it: 'Colonne squadra e posizionamento',
    summary_it: 'Avanguardia / DPS / Support: come pensare le tre colonne dal punto di vista della propria squadra.',
    sections: [
      { heading_it: 'Avanguardia', body_it: 'PLACEHOLDER: prima linea, tank/duellanti.' },
      { heading_it: 'DPS',         body_it: 'PLACEHOLDER: dealers principali.' },
      { heading_it: 'Support',     body_it: 'PLACEHOLDER: healer / buffer / debuffer.' },
    ],
  },
  {
    id: 'guide_active_battle_power',
    category: 'battle_power_and_power_delta',
    order: 4,
    title_it: 'Active Battle Power (POWER) e variazioni',
    summary_it: 'Active Battle Power riassume la forza attuale del team. Le variazioni saranno mostrate come +BP / -BP (feature futura).',
    sections: [
      { heading_it: 'Cosa contribuisce a POWER', body_it: 'PLACEHOLDER.' },
      { heading_it: 'Delta overlay +BP/-BP',     body_it: 'FUTURE_FEATURE_DESIGN_ONLY: overlay verra\u2019 agganciato quando cambia la BP attiva del team. Non runtime in questo pack.' },
    ],
  },
  {
    id: 'guide_items_materials_farming',
    category: 'items_materials_and_farming',
    order: 5,
    title_it: 'Oggetti, Materiali e Farming',
    summary_it: 'Cosa farmare, dove e perche\u2019.',
    sections: [{ heading_it: 'Materiali base', body_it: 'PLACEHOLDER.' }],
  },
  {
    id: 'guide_buff_sources',
    category: 'buff_sources',
    order: 6,
    title_it: 'Fonti di Buff',
    summary_it: 'Da dove arrivano i buff: passive, sinergie, artefatti, costellazioni, divine weapon (anteprima).',
    sections: [{ heading_it: 'Sinergie', body_it: 'PLACEHOLDER.' }],
  },
  {
    id: 'guide_tower_of_the_hells',
    category: 'modes',
    order: 7,
    title_it: 'Torre degli Inferi',
    summary_it: '20 piani design-only con boss ogni 5 piani. Progresso locale, primo clear da badge UI.',
    sections: [
      { heading_it: 'Struttura piani', body_it: 'PLACEHOLDER: 20 piani, boss ai piani 5/10/15/20.' },
      { heading_it: 'Niente Stamina',  body_it: 'La Torre non usa stamina/ticket/paid attempts.' },
      { heading_it: 'Persistenza',     body_it: 'Progresso salvato localmente via AsyncStorage in fase di TEST.' },
    ],
  },
  {
    id: 'guide_home_avatars',
    category: 'home_and_avatars',
    order: 8,
    title_it: 'Home e Avatar',
    summary_it: 'Tre famiglie di avatar (anteprima futura): Avatar HD serio, War Avatar chibi/tattico, Hero Room Avatar.',
    sections: [
      { heading_it: 'Avatar HD serio',           body_it: 'FUTURE_FEATURE_DESIGN_ONLY.' },
      { heading_it: 'War Avatar chibi/tattico',  body_it: 'FUTURE_FEATURE_DESIGN_ONLY.' },
      { heading_it: 'Hero Room Avatar',          body_it: 'FUTURE_FEATURE_DESIGN_ONLY.' },
    ],
  },
  {
    id: 'guide_guild_war_fronti_del_valhalla',
    category: 'guild_and_social',
    order: 9,
    title_it: 'Fronti del Valhalla (Guild War)',
    summary_it: 'PLACEHOLDER. Modalita\u2019 futura. Non attiva.',
    sections: [{ heading_it: 'Anteprima', body_it: 'FUTURE_FEATURE_DESIGN_ONLY.' }],
  },
  {
    id: 'guide_artifacts',
    category: 'modes',
    order: 10,
    title_it: 'Artefatti (anteprima)',
    summary_it: 'Catalogo read-only. Mutazioni live attualmente bloccate (HTTP 423).',
    sections: [{ heading_it: 'Stato', body_it: 'DESIGN_ONLY_AND_CATALOG_READ_ONLY.' }],
  },
  {
    id: 'guide_shop_bp_vip_iap',
    category: 'economy_shop_bp_vip_iap',
    order: 11,
    title_it: 'Negozio, Battle Pass, VIP, IAP',
    summary_it: 'Superfici attualmente bloccate / design-only. Non sono attive in questo build.',
    sections: [{ heading_it: 'Stato', body_it: 'LOCKED_DESIGN_ONLY_NO_MONETIZATION_IN_THIS_BUILD.' }],
  },
];
