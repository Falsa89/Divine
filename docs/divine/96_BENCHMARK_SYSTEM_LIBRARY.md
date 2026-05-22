# Canonical Source — Benchmark-Derived System Library

This file covers every important system or improvement derived from the benchmark wiki analysis. It is not limited to the 16 modes.

All systems below are SOURCE-OF-TRUTH DESIGN NOTES unless a later pack explicitly authorizes runtime.

## A. Server Lifecycle / Calendar / Merge Recovery

Sources:
- Whiteout Survival: State Merger, State Transfer, SVS, Foundry Battle, Alliance Territory.
- Rise of Kingdoms: Kingdom timeline, zone unlocks, Mightiest Governor, Alliance Technology.
- Bleach Online: daily schedule, live windows, guild war, protect city.
- Nikke/Omniheroes: event archive, seasons, union/guild cycles.

Divine decisions:
- Account is global.
- Server profile is server-bound.
- New server means a new competitive start for the same account.
- Paid currency can be account-wide.
- Free currency, roster, inventory, progress, guild, arena, affinity, gift ledger and event state are server-bound.
- New player routing defaults to newest open server.
- Existing player routing defaults to last active server.
- Server-age calendar controls most non-real-world events.
- Real-world events override server-age when calendar logic requires it.
- Merge recovery must recover critical missed milestones, not skipped weeks.

Do import:
- merge relocation/shield equivalent;
- guild territory reset/refund logic;
- duplicate name/tag resolution;
- leaderboard reset/settlement;
- post-merge recovery missions;
- merge recovery season 5–14 days;
- compatibility matrix for future transfer.

Do not import:
- destructive troop loss;
- paid transfer-only access;
- pack reset monetization abuse;
- president powers that harm player freedom;
- whale power-cap manipulation.

## B. Event Hub / Daily Guide / Activity Board

Sources:
- Honkai Star Rail: Interastral-style guide, event hub, activity guidance.
- Genshin: Events Overview, Quick Start, Battle Pass mission structure.
- Nikke: Event Archive and Grand Events.
- Bleach Online: daily schedule and live timed activities.
- Epic Seven/Raid/Bleach Brave Souls: challenge orders, reputation boards, progression guides.

Divine target system:
- Event Hub must organize Current, Upcoming, Permanent, Server-Age, Real-World, Merge Recovery, Guild/Server and Archive.
- Daily Guide must tell the player what matters today without creating a second job.
- Hero Growth Target / Material Finder should guide progression.

Do import:
- clear event tabs;
- current/upcoming/permanent archive;
- server-age calendar view;
- quick-start only when story context is not critical;
- daily/weekly/period missions with caps.

Do not import:
- overwhelming UI;
- time-gated weekly caps that feel punitive;
- event archive with active shop/currency duplication.

## C. Summon / Pity / Wishlist / Fragments

Sources:
- Honkai Star Rail/Genshin/Epic Seven: pity clarity.
- Nikke: wishlist, social summon, molds, manufacturer/faction summon.
- Figure Fantasy: starter roll, faction rotating banners.
- Raid/Naruto Blazing/Summoners War: fragments, fusion, Hall of Heroes, limited reruns.

Divine target system:
- Permanent Summon.
- Starter Server Summon.
- Limited Hero Banner.
- Faction Day Banner.
- Divine Weapon Banner only when safe.
- Fragment Hall / Hero Fragment Event.
- Merge Catch-Up Banner for missed critical hero/counter milestones.

Do import:
- explicit pity/mercy tracking;
- wishlist after threshold;
- social/friend summon low-rate;
- fragment rerun for older non-limited heroes;
- starter selector/discounted roll for new server profiles;
- pity inheritance rules for merge catch-up banners.

Do not import:
- rank-only critical meta heroes;
- whale-only faction currency;
- hidden pity;
- fragment events that are impossible for casuals;
- paid-only hard counters.

## D. Cosmetics / Skins / Titles / Frames / Furniture Power

Sources:
- Nikke: costumes and mission/event pass.
- Genshin/AFK: profile frames/namecards/seasonal cosmetics.
- Bleach Online: temporary ranking titles.
- Heroes of Camelot: evolved/animated card presentation.
- Marvel Future Fight: uniform power risk.
- Divine COSMETIC-A: already approved foundation.

Divine target system:
- Skins can grant minimal hero-bound bonuses.
- Titles can grant team/player/account-server bonuses.
- Furniture can grant very small global/team bonuses through housing.
- Higher rarity gives higher effect, but every category is capped.
- PvP/Guild War caps must be stricter than PvE caps.

Do import:
- skins from top-up, paid gems, achievements, intimacy, PvP rank, tower, castle, guild war, titan kills, hero stars;
- temporary seasonal titles;
- server-first titles as server-bound and no-rerun;
- animated card frames / evolved presentation for high ascension or rare skins.

Do not import:
- Marvel-style mandatory uniforms;
- uncapped collection bonuses;
- paid furniture as required PvP power;
- cosmetics that become dominant power creep.

## E. Sanctuary Housing / Dimora Divina

Sources:
- Figure Fantasy Otaku Zone.
- Nikke Outpost.
- Genshin Serenitea Pot.
- AFK Arena Oak Inn.
- League of Angels Homestead/Garden.
- Omniheroes Valkyrie Manor.

Divine target system:
- Sanctuary section called Dimora Divina.
- Player decorates rooms/altars/furniture.
- Favorite heroes can be displayed.
- Comfort/prestige score unlocks quality or convenience.
- Furniture equipment slots give tiny capped global/team bonuses.
- Paid furniture ownership may be account-wide, but equipped state and bonus are server-bound.

Possible bonuses:
- Team HP flat small bonus.
- Team ATK +0.5%.
- PvE healing received +0.5%.
- Guild War damage +0.5% capped.
- Account EXP/material gain +1% capped.
- Initial Rage +2 PvE-only for high rarity furniture.

Do not import:
- large global stat bonuses;
- housing mandatory for PvP;
- social themes inappropriate for Divine;
- paid-only furniture power.

## F. Guild / Social / Co-op

Sources:
- Nikke Union, Union Raid.
- Mythic Heroes Guild Daemons/Showdown.
- Omniheroes Guild/Grayshroom Realm.
- Summoners War Guild Battle/Siege/Rift Raid.
- Marvel Future Fight co-op/Giant Boss/Alliance Conquest.
- SAO Memory Defrag party/co-op.
- Bleach Online guild/live phases.

Divine target system:
- Guild chat, activity, donation, shop, weekly chest.
- Guild boss with test battle and limited attempts.
- Guild raids: Fame del Behemoth, Furie del Pantheon, Fronti del Valhalla, Titanomachia, Guerra dei Tre Troni.
- Co-op Scrigni dell’Elisio.
- Future social plaza / party finder.

Do import:
- test battle that does not consume attempt;
- no leave/kick during major guild event;
- roster/hero lock where needed;
- contribution ranking;
- personal + collective reward;
- substitutes/defensive roster prep for territory modes.

Do not import:
- uncapped guild donations;
- paid morale/cooldown in competitive;
- leader abuse without inactivity transfer;
- timezone-heavy schedules without fallback.

## G. Tower / Castle / Roguelike / Labyrinth

Sources:
- SAO Memory Defrag Floor Clearing Castle.
- Bleach Brave Souls Senkaimon.
- Summoners War Trial of Ascension.
- AFK Arcane Labyrinth / Abyssal Expedition.
- Mythic Heroes Pantheon.
- HSR Simulated Universe.
- Omniheroes Labyrinth/Rift Odyssey.

Divine target systems:
- Torre degli Inferi: seasonal lock tower.
- Scala dell’Olimpo: wave/endurance progression.
- Cammino dell’Ade: branching survival run.
- Abisso del Colosso: boss survival ladder.
- Prove del Pantheon / Sigilli degli Dei: tactical challenges.

Do import:
- 100-floor structure;
- milestone rewards;
- boss floors;
- special rules;
- clear time tracking;
- medal exchange;
- internal-only blessings/relics;
- rare treasure floors.

Do not import:
- relic/buff leakage into global battle runtime;
- impossible roster lock;
- missable critical counters;
- excessive daily reset pressure.

## H. Equipment / Relic / Forge / Gear QoL

Sources:
- Summoners War runes.
- Raid artifacts/forge/charms.
- Epic Seven gear conversion/forge events.
- Genshin artifacts/strongbox.
- Bleach accessories/fusion/reroll.

Divine target system:
- Future Forge/Relic system should be controlled RNG.
- Target set, slot and limited main stat selection should exist.
- Bad gear should recycle into cores.
- Reroll/lock materials should exist.
- Auto-sell/lock filters require strong safety toggles.

Do import:
- set bonuses 2/4 or simplified equivalent;
- recycle/strongbox;
- targeted crafting;
- conversion/reroll stones;
- safe auto-sell filters with confirmation.

Do not import:
- expensive removal costs;
- infinite RNG without pity;
- PvP-dominant Speed/extra-turn meta;
- accidental sell risk.

## I. Battle Stats / Damage Reporting

Sources:
- Bleach Online attributes/damage/stat reports.
- Raid/Epic/Summoners boss reports.
- Divine approved Battle Report foundation.

Divine target system:
- Existing report should include damage dealt, received, healing, MVP.
- Future advanced report should include damage mitigated, shields, healing prevented, support contribution, gate/wall damage, boss contribution, kills, deaths, revives, final blow capped, streaks.
- Use skill growth rates internally but expose user-friendly tooltips.

Do import:
- damage contribution;
- gate/wall damage for Titanomachia/Guerra modes;
- streak score for Fronti del Valhalla;
- boss contribution for Crepuscolo/Fame/Furie;
- objective clear stats for Prove/Sigilli.

Do not import:
- high unbounded Damage Rate/Immune power creep;
- Combo/Aid/Speed mechanics directly into runtime without design schema;
- final blow as major reward.

## J. Monetized Events / Lucky Wheel / Treasury / Top-up

Sources:
- Bleach Online Lucky Turntable, top-up events, Ultimate BP.
- Idle Angels Lucky Valley / Lost Sanctuary.
- League of Angels Lucky Tree / House of Cards / Craft Master.
- Nikke Mission Pass/Costume Gacha.

Divine target system:
- Lucky Wheel with daily free spin, transparent odds, pity meter, exchange shop.
- Treasury layered rewards with keys from daily/event tasks.
- Top-up week can offer cosmetics, titles, skins and capped prestige bonuses.
- Event currency expiration must be explicit.

Do import:
- daily free attempt;
- exchange points;
- pity/raffle meter;
- non-consuming stage-drop milestone reward;
- event shop with clear expiration.

Do not import:
- unlimited paid packs;
- paid cooldown/paid revive in competitive;
- top-up exclusive hard counters;
- gambling-like opacity.

## K. Level Sync / Roster Breadth

Sources:
- AFK Arena Resonating Crystal.
- Omniheroes Sanctuary of Eve.
- Figure Fantasy Otaku Committee.

Divine target system:
- Future Divine Resonance / Santuario della Risonanza.
- Top 5/6 heroes define sync baseline.
- Synced heroes inherit base level only, not stars/gear/skills.
- Server-bound sync state.
- Slot unlock progression.

Do import:
- roster breadth friction reduction;
- clear lowest-top-hero rule;
- slot unlock pacing.

Do not import:
- sync so generous that leveling loses meaning;
- confusing gear sync before base level sync is stable.

## L. Archive / Replay / Event History

Sources:
- Nikke Event Archive.
- Genshin Book of Memories/Chronicles-like archive.
- AFK Wandering Balloon / old adventures.
- Epic Seven Side Story archive.

Divine target system:
- Event Archive / Chronicle of Divine Events.
- Old lore events playable with limited or reduced reward.
- No active shop/currency duplication after archive.
- Unlock by Memory Film-like item or server-age milestones.

Do import:
- story replay;
- cutscene archive;
- limited rewards;
- old event rerun/catch-up pools for critical milestones.

Do not import:
- full active shop replay;
- FOMO-heavy archive cost;
- archive that breaks server-age fairness.
