"""
Divine Waifus - Game Data Definitions
All static game data: equipment, story chapters, events, cosmetics, etc.
"""

# ===================== EQUIPMENT DEFINITIONS =====================
EQUIPMENT_SLOTS = ["weapon", "armor", "accessory", "rune"]

EQUIPMENT_TEMPLATES = {
    "weapon": [
        {"name": "Lama del Crepuscolo", "rarity": 6, "stats": {"attack": 500, "crit_rate": 0.08}},
        {"name": "Spada Celestiale", "rarity": 5, "stats": {"attack": 380, "crit_rate": 0.06}},
        {"name": "Katana Lunare", "rarity": 5, "stats": {"attack": 350, "crit_damage": 0.20}},
        {"name": "Ascia del Titano", "rarity": 4, "stats": {"attack": 280, "crit_rate": 0.04}},
        {"name": "Pugnale d'Ombra", "rarity": 4, "stats": {"attack": 250, "speed": 15}},
        {"name": "Arco Sacro", "rarity": 3, "stats": {"attack": 180, "crit_rate": 0.03}},
        {"name": "Bastone Antico", "rarity": 3, "stats": {"attack": 160, "hp": 500}},
        {"name": "Spada Arrugginita", "rarity": 2, "stats": {"attack": 100}},
        {"name": "Pugnale Base", "rarity": 1, "stats": {"attack": 50}},
    ],
    "armor": [
        {"name": "Corazza Divina", "rarity": 6, "stats": {"defense": 400, "hp": 2000}},
        {"name": "Armatura del Drago", "rarity": 5, "stats": {"defense": 300, "hp": 1500}},
        {"name": "Veste Mitica", "rarity": 5, "stats": {"defense": 250, "hp": 1200, "speed": 10}},
        {"name": "Cotta di Maglia", "rarity": 4, "stats": {"defense": 200, "hp": 800}},
        {"name": "Tunica Rinforzata", "rarity": 3, "stats": {"defense": 130, "hp": 500}},
        {"name": "Gilet di Cuoio", "rarity": 2, "stats": {"defense": 80, "hp": 300}},
        {"name": "Veste Logora", "rarity": 1, "stats": {"defense": 40, "hp": 150}},
    ],
    "accessory": [
        {"name": "Corona dell'Olimpo", "rarity": 6, "stats": {"crit_rate": 0.12, "crit_damage": 0.40}},
        {"name": "Anello del Destino", "rarity": 5, "stats": {"crit_rate": 0.10, "crit_damage": 0.25}},
        {"name": "Amuleto Mistico", "rarity": 5, "stats": {"attack": 200, "defense": 100}},
        {"name": "Collana Elementale", "rarity": 4, "stats": {"crit_rate": 0.06, "speed": 12}},
        {"name": "Bracciale di Forza", "rarity": 3, "stats": {"attack": 100, "crit_rate": 0.03}},
        {"name": "Orecchino Comune", "rarity": 2, "stats": {"speed": 8}},
        {"name": "Ciondolo Semplice", "rarity": 1, "stats": {"hp": 200}},
    ],
    "rune": [
        {"name": "Runa Primordiale", "rarity": 6, "stats": {"attack": 300, "defense": 200, "hp": 1000, "speed": 15}},
        {"name": "Runa del Caos", "rarity": 5, "stats": {"attack": 250, "crit_damage": 0.30}},
        {"name": "Runa di Vita", "rarity": 5, "stats": {"hp": 2000, "defense": 150}},
        {"name": "Runa di Velocita", "rarity": 4, "stats": {"speed": 25, "crit_rate": 0.05}},
        {"name": "Runa di Potenza", "rarity": 3, "stats": {"attack": 120}},
        {"name": "Runa Fragile", "rarity": 2, "stats": {"attack": 60}},
        {"name": "Frammento di Runa", "rarity": 1, "stats": {"hp": 100}},
    ],
}

# ===================== STORY CHAPTERS =====================
STORY_CHAPTERS = [
    {"id": 1, "name": "L'Inizio della Leggenda", "stages": 10, "difficulty": 1, "element": "neutral",
     "rewards": {"gold": 500, "exp": 200, "gems": 10}, "enemy_power": 3000, "description": "Il tuo viaggio nel mondo delle Dee inizia qui..."},
    {"id": 2, "name": "La Foresta Incantata", "stages": 10, "difficulty": 2, "element": "earth",
     "rewards": {"gold": 800, "exp": 350, "gems": 15}, "enemy_power": 5000, "description": "Spiriti della natura bloccano il cammino."},
    {"id": 3, "name": "Il Tempio del Fuoco", "stages": 10, "difficulty": 3, "element": "fire",
     "rewards": {"gold": 1200, "exp": 500, "gems": 20}, "enemy_power": 8000, "description": "Le fiamme eterne ardono nel tempio sacro."},
    {"id": 4, "name": "L'Abisso Oscuro", "stages": 10, "difficulty": 4, "element": "dark",
     "rewards": {"gold": 1800, "exp": 700, "gems": 25}, "enemy_power": 12000, "description": "Nelle profondita dell'oscurita, attendono orrori indicibili."},
    {"id": 5, "name": "Le Cascate Celesti", "stages": 10, "difficulty": 5, "element": "water",
     "rewards": {"gold": 2500, "exp": 1000, "gems": 30}, "enemy_power": 18000, "description": "L'acqua purifica... o distrugge."},
    {"id": 6, "name": "Il Picco dei Venti", "stages": 10, "difficulty": 6, "element": "wind",
     "rewards": {"gold": 3500, "exp": 1400, "gems": 40}, "enemy_power": 25000, "description": "Tempeste divine sferzano la vetta."},
    {"id": 7, "name": "La Cittadella della Luce", "stages": 12, "difficulty": 7, "element": "light",
     "rewards": {"gold": 5000, "exp": 2000, "gems": 50}, "enemy_power": 35000, "description": "La luce accecante nasconde verita terribili."},
    {"id": 8, "name": "Il Palazzo degli Dei", "stages": 12, "difficulty": 8, "element": "neutral",
     "rewards": {"gold": 8000, "exp": 3000, "gems": 75}, "enemy_power": 50000, "description": "Il destino del mondo si decide qui."},
]

# ===================== EVENTS =====================
DAILY_EVENTS = [
    {"id": "gold_rush", "name": "Corsa all'Oro", "icon": "coin", "description": "Guadagna oro extra!", "reward_type": "gold", "reward_mult": 3, "stamina_cost": 10, "available_days": [0, 1, 2, 3, 4, 5, 6]},
    {"id": "exp_boost", "name": "Campo di Addestramento", "icon": "dumbbell", "description": "EXP tripla per i tuoi eroi!", "reward_type": "exp", "reward_mult": 3, "stamina_cost": 10, "available_days": [0, 2, 4, 6]},
    {"id": "equip_hunt", "name": "Caccia all'Equipaggiamento", "icon": "sword", "description": "Trova equipaggiamento raro!", "reward_type": "equipment", "reward_mult": 1, "stamina_cost": 15, "available_days": [1, 3, 5]},
    {"id": "gem_mine", "name": "Miniera di Gemme", "icon": "gem", "description": "Gemme rare dalle profondita!", "reward_type": "gems", "reward_mult": 1, "stamina_cost": 20, "available_days": [0, 3, 6]},
    {"id": "boss_raid", "name": "Raid del Boss", "icon": "skull", "description": "Sconfiggi il boss per ricompense epiche!", "reward_type": "mixed", "reward_mult": 5, "stamina_cost": 25, "available_days": [5, 6]},
]

# ===================== FACTIONS (14 fazioni - scelta permanente) =====================
FACTIONS = [
    {"id": "egyptian", "name": "Egiziana", "icon": "\U0001F3FA", "color": "#ffd700",
     "bonus": {"crit_damage": 0.12, "crit_chance": 0.08},
     "description": "Gli dei dell'Egitto antico benedicono con colpi devastanti."},
    {"id": "sumerian", "name": "Sumera", "icon": "\U0001F3DB\uFE0F", "color": "#88aacc",
     "bonus": {"speed": 0.10, "block_rate": 0.08},
     "description": "L'antica Sumeria dona agilita e resistenza ai colpi."},
    {"id": "roman", "name": "Romana", "icon": "\U0001F3DB\uFE0F", "color": "#cc4444",
     "bonus": {"speed": 0.08, "physical_damage": 0.10},
     "description": "La disciplina romana forgia guerrieri veloci e letali."},
    {"id": "greek", "name": "Greca", "icon": "\u2694\uFE0F", "color": "#4488ff",
     "bonus": {"speed": 0.08, "magic_damage": 0.10},
     "description": "La saggezza greca potenzia la magia e la velocita."},
    {"id": "aztec", "name": "Azteca", "icon": "\U0001F31E", "color": "#ff6644",
     "bonus": {"hit_rate": 0.08, "healing": 0.10},
     "description": "I rituali aztechi migliorano precisione e guarigione."},
    {"id": "yoruba", "name": "Yoruba", "icon": "\U0001F3AD", "color": "#44cc88",
     "bonus": {"dodge": 0.08, "block_rate": 0.08},
     "description": "Gli Orisha proteggono con schivata e blocco."},
    {"id": "hindu", "name": "Induismo", "icon": "\U0001F549\uFE0F", "color": "#ff8844",
     "bonus": {"healing": 0.10, "penetration": 0.08},
     "description": "Le divinita hindu curano e perforano ogni difesa."},
    {"id": "confucian", "name": "Confucianesimo", "icon": "\U0001F4DC", "color": "#884444",
     "bonus": {"physical_damage": 0.10, "crit_damage": 0.10},
     "description": "La via del guerriero: forza fisica e colpi critici."},
    {"id": "shinto", "name": "Shintoismo", "icon": "\u26E9\uFE0F", "color": "#ff4488",
     "bonus": {"combo_rate": 0.10, "hit_rate": 0.08},
     "description": "Lo spirito dello Shinto dona combo rapide e precise."},
    {"id": "buddhist", "name": "Buddismo", "icon": "\u2638\uFE0F", "color": "#ffaa00",
     "bonus": {"healing": 0.10, "magic_defense": 0.10},
     "description": "La pace interiore guarisce e protegge dalla magia."},
    {"id": "norse", "name": "Norreno", "icon": "\U0001FA93", "color": "#6688cc",
     "bonus": {"damage_rate": 0.10, "penetration": 0.08},
     "description": "La furia dei Vichinghi aumenta danno e penetrazione."},
    {"id": "christian", "name": "Cristiano", "icon": "\u271D\uFE0F", "color": "#ffffff",
     "bonus": {"hp": 0.12, "physical_defense": 0.08},
     "description": "La fede cristiana dona vitalita e protezione fisica."},
    {"id": "celtic", "name": "Celtica", "icon": "\u2618\uFE0F", "color": "#44aa44",
     "bonus": {"physical_defense": 0.08, "magic_defense": 0.08},
     "description": "I druidi celtici proteggono da ogni tipo di danno."},
    {"id": "maya", "name": "Maya", "icon": "\U0001F319", "color": "#9944ff",
     "bonus": {"magic_damage": 0.10, "crit_chance": 0.08},
     "description": "I segreti Maya potenziano magia e colpi critici."},
]

# Cost to change faction (premium gems only)
FACTION_CHANGE_COST = 1000  # gems (acquistabili solo con soldi veri)

# ===================== AURAS & COSMETICS =====================
AURAS = [
    {"id": "flame", "name": "Aura di Fiamma", "icon": "\U0001f525", "color": "#ff4444", "cost": 2000, "currency": "gold"},
    {"id": "ice", "name": "Aura Glaciale", "icon": "\u2744\ufe0f", "color": "#44aaff", "cost": 2000, "currency": "gold"},
    {"id": "thunder", "name": "Aura del Tuono", "icon": "\u26a1", "color": "#ffd700", "cost": 3000, "currency": "gold"},
    {"id": "shadow", "name": "Aura d'Ombra", "icon": "\U0001f311", "color": "#9944ff", "cost": 3000, "currency": "gold"},
    {"id": "divine", "name": "Aura Divina", "icon": "\u2728", "color": "#ffd700", "cost": 50, "currency": "gems"},
    {"id": "celestial", "name": "Aura Celeste", "icon": "\U0001f31f", "color": "#ffffff", "cost": 100, "currency": "gems"},
]

AVATAR_FRAMES = [
    {"id": "bronze", "name": "Cornice Bronzo", "color": "#cd7f32", "cost": 1000, "currency": "gold"},
    {"id": "silver", "name": "Cornice Argento", "color": "#c0c0c0", "cost": 3000, "currency": "gold"},
    {"id": "gold", "name": "Cornice Oro", "color": "#ffd700", "cost": 5000, "currency": "gold"},
    {"id": "diamond", "name": "Cornice Diamante", "color": "#44ddff", "cost": 30, "currency": "gems"},
    {"id": "legendary", "name": "Cornice Leggendaria", "color": "#ff4444", "cost": 80, "currency": "gems"},
    {"id": "divine", "name": "Cornice Divina", "color": "#ffd700", "cost": 150, "currency": "gems"},
]

# ===================== TERRITORIES =====================
TERRITORIES = [
    {"id": "volcano", "name": "Monte Vulcano", "element": "fire", "reward_gold": 5000, "reward_gems": 10},
    {"id": "ocean", "name": "Abisso Oceanico", "element": "water", "reward_gold": 5000, "reward_gems": 10},
    {"id": "forest", "name": "Foresta Eterna", "element": "earth", "reward_gold": 5000, "reward_gems": 10},
    {"id": "skylands", "name": "Isole Celesti", "element": "wind", "reward_gold": 5000, "reward_gems": 10},
    {"id": "sanctum", "name": "Santuario della Luce", "element": "light", "reward_gold": 8000, "reward_gems": 15},
    {"id": "abyss", "name": "Abisso Oscuro", "element": "dark", "reward_gold": 8000, "reward_gems": 15},
    {"id": "olympus", "name": "Trono dell'Olimpo", "element": "neutral", "reward_gold": 15000, "reward_gems": 30},
]

# ===================== RAID BOSSES =====================
RAID_BOSSES = [
    {"id": "hydra", "name": "Idra delle Tenebre", "element": "dark", "hp": 500000, "attack": 5000, "defense": 2000,
     "reward_gold": 10000, "reward_gems": 20, "reward_exp": 5000, "min_players": 1, "max_players": 5,
     "description": "Un mostro a 9 teste che rigenera i danni. Servono eroi di luce!"},
    {"id": "titan", "name": "Titano di Fuoco", "element": "fire", "hp": 800000, "attack": 7000, "defense": 3000,
     "reward_gold": 18000, "reward_gems": 35, "reward_exp": 8000, "min_players": 2, "max_players": 5,
     "description": "Un colosso infuocato. L'acqua e il vento sono essenziali!"},
    {"id": "leviathan", "name": "Leviatano Abissale", "element": "water", "hp": 1200000, "attack": 9000, "defense": 4000,
     "reward_gold": 30000, "reward_gems": 50, "reward_exp": 12000, "min_players": 3, "max_players": 5,
     "description": "Il signore degli abissi. Solo la terra e il fulmine possono fermarlo!"},
    {"id": "chaos", "name": "Entita del Caos", "element": "neutral", "hp": 2000000, "attack": 12000, "defense": 5000,
     "reward_gold": 50000, "reward_gems": 100, "reward_exp": 25000, "min_players": 4, "max_players": 5,
     "description": "L'incarnazione del caos primordiale. Solo i piu forti sopravvivono!"},
]

# ===================== EXCLUSIVE ITEMS =====================
EXCLUSIVE_ITEMS = [
    {"hero_name": "Amaterasu", "item": {"name": "Specchio di Yata", "slot": "weapon", "rarity": 6, "stats": {"attack": 800, "crit_rate": 0.15, "crit_damage": 0.5}, "description": "Lo specchio sacro che riflette la verita divina."}},
    {"hero_name": "Tsukuyomi", "item": {"name": "Lama della Luna Nera", "slot": "weapon", "rarity": 6, "stats": {"attack": 900, "crit_rate": 0.20, "speed": 25}, "description": "Una lama forgiata nell'oscurita eterna della luna."}},
    {"hero_name": "Susanoo", "item": {"name": "Kusanagi no Tsurugi", "slot": "weapon", "rarity": 6, "stats": {"attack": 700, "defense": 400, "hp": 3000}, "description": "La leggendaria spada che taglia anche le tempeste."}},
    {"hero_name": "Izanami", "item": {"name": "Velo dell'Oltretomba", "slot": "armor", "rarity": 6, "stats": {"defense": 500, "hp": 5000, "speed": 15}, "description": "Un velo che connette il mondo dei vivi e dei morti."}},
    {"hero_name": "Athena", "item": {"name": "Egida di Athena", "slot": "armor", "rarity": 5, "stats": {"defense": 450, "hp": 3500, "crit_rate": 0.08}, "description": "Lo scudo della dea della saggezza, impenetrabile."}},
    {"hero_name": "Aphrodite", "item": {"name": "Cintura di Afrodite", "slot": "accessory", "rarity": 5, "stats": {"hp": 4000, "defense": 200, "speed": 20}, "description": "La cintura che incanta chiunque la guardi."}},
    {"hero_name": "Artemis", "item": {"name": "Arco d'Argento", "slot": "weapon", "rarity": 5, "stats": {"attack": 600, "crit_rate": 0.18, "speed": 30}, "description": "L'arco della cacciatrice, non manca mai il bersaglio."}},
    {"hero_name": "Freya", "item": {"name": "Collana Brisingamen", "slot": "accessory", "rarity": 5, "stats": {"attack": 400, "crit_damage": 0.40, "crit_rate": 0.12}, "description": "Il gioiello piu prezioso di tutti i nove mondi."}},
    {"hero_name": "Medusa", "item": {"name": "Sguardo Pietrificante", "slot": "rune", "rarity": 5, "stats": {"attack": 500, "defense": 300, "speed": -10}, "description": "Il potere di trasformare in pietra con lo sguardo."}},
    {"hero_name": "Valkyrie", "item": {"name": "Lancia del Valhalla", "slot": "weapon", "rarity": 5, "stats": {"attack": 550, "hp": 2000, "defense": 250}, "description": "La lancia che sceglie i guerrieri degni del Valhalla."}},
]

# ===================== RANKINGS =====================
RANK_TIERS = [
    {"min": 0, "name": "Bronzo", "color": "#cd7f32", "icon": "\U0001F949"},
    {"min": 300, "name": "Argento", "color": "#c0c0c0", "icon": "\U0001F948"},
    {"min": 800, "name": "Oro", "color": "#ffd700", "icon": "\U0001F947"},
    {"min": 1500, "name": "Platino", "color": "#44ddff", "icon": "\U0001F48E"},
    {"min": 2500, "name": "Diamante", "color": "#ff44ff", "icon": "\u2B50"},
    {"min": 4000, "name": "Leggenda", "color": "#ff4444", "icon": "\U0001F451"},
]

# ===================== SHOP =====================
SHOP_ITEMS = [
    {"id": "gems_small", "name": "Sacchetto di Gemme", "description": "100 Gemme", "icon": "\U0001F48E", "price_type": "gold", "price": 10000, "reward": {"gems": 100}, "category": "gems"},
    {"id": "gems_medium", "name": "Scrigno di Gemme", "description": "500 Gemme + 50K Oro", "icon": "\U0001F48E", "price_type": "gold", "price": 40000, "reward": {"gems": 500, "gold": 50000}, "category": "gems"},
    {"id": "gems_large", "name": "Tesoro Divino", "description": "2000 Gemme + 200K Oro", "icon": "\U0001F48E", "price_type": "gold", "price": 150000, "reward": {"gems": 2000, "gold": 200000}, "category": "gems"},
    {"id": "stamina_50", "name": "Pozione Energia", "description": "+50 Stamina", "icon": "\u26A1", "price_type": "gems", "price": 30, "reward": {"stamina": 50}, "category": "stamina"},
    {"id": "stamina_full", "name": "Elisir Completo", "description": "Stamina al massimo", "icon": "\u26A1", "price_type": "gems", "price": 50, "reward": {"stamina_full": True}, "category": "stamina"},
    {"id": "gold_pack", "name": "Sacco d'Oro", "description": "50.000 Oro", "icon": "\U0001F4B0", "price_type": "gems", "price": 20, "reward": {"gold": 50000}, "category": "gold"},
    {"id": "gold_chest", "name": "Forziere d'Oro", "description": "250.000 Oro", "icon": "\U0001F4B0", "price_type": "gems", "price": 80, "reward": {"gold": 250000}, "category": "gold"},
    {"id": "exp_boost", "name": "Tomo dell'Esperienza", "description": "Livella un eroe +5 livelli", "icon": "\U0001F4DA", "price_type": "gems", "price": 60, "reward": {"hero_levels": 5}, "category": "boost"},
    {"id": "gacha_ticket", "name": "Biglietto Evocazione", "description": "1 Pull Premium gratuita", "icon": "\U0001F3AB", "price_type": "gems", "price": 150, "reward": {"premium_pull": 1}, "category": "gacha"},
    {"id": "gacha_ticket_10", "name": "Pacchetto 10 Biglietti", "description": "10 Pull Premium", "icon": "\U0001F3AB", "price_type": "gems", "price": 1200, "reward": {"premium_pull": 10}, "category": "gacha"},
]

DAILY_FREE = [
    {"id": "daily_gold", "name": "Oro Giornaliero", "icon": "\U0001F4B0", "reward": {"gold": 5000}},
    {"id": "daily_stamina", "name": "Stamina Giornaliera", "icon": "\u26A1", "reward": {"stamina": 30}},
]

# ===================== BATTLE PASS =====================
BATTLE_PASS_REWARDS = [
    {"level": 1, "free": {"gold": 5000}, "premium": {"gems": 50}},
    {"level": 2, "free": {"gold": 8000}, "premium": {"gems": 80}},
    {"level": 3, "free": {"stamina": 50}, "premium": {"gold": 30000}},
    {"level": 4, "free": {"gold": 12000}, "premium": {"gems": 100}},
    {"level": 5, "free": {"gems": 30}, "premium": {"gold": 50000, "gems": 100}},
    {"level": 6, "free": {"gold": 15000}, "premium": {"gems": 120}},
    {"level": 7, "free": {"stamina": 80}, "premium": {"gold": 80000}},
    {"level": 8, "free": {"gold": 20000}, "premium": {"gems": 150}},
    {"level": 9, "free": {"gems": 50}, "premium": {"gold": 100000}},
    {"level": 10, "free": {"gold": 30000, "gems": 50}, "premium": {"gems": 500, "gold": 200000}},
    {"level": 11, "free": {"gold": 25000}, "premium": {"gems": 150}},
    {"level": 12, "free": {"stamina": 100}, "premium": {"gold": 120000}},
    {"level": 13, "free": {"gold": 30000}, "premium": {"gems": 200}},
    {"level": 14, "free": {"gems": 80}, "premium": {"gold": 150000}},
    {"level": 15, "free": {"gold": 50000, "gems": 100}, "premium": {"gems": 800, "gold": 500000}},
]

# ===================== SERVERS =====================
SERVERS = [
    {"id": "eu_1", "name": "Europa 1 - Olimpo", "region": "EU", "status": "online", "max_players": 500},
    {"id": "eu_2", "name": "Europa 2 - Asgard", "region": "EU", "status": "online", "max_players": 500},
    {"id": "eu_3", "name": "Europa 3 - Yomi", "region": "EU", "status": "online", "max_players": 500},
    {"id": "asia_1", "name": "Asia 1 - Nirvana", "region": "ASIA", "status": "online", "max_players": 500},
    {"id": "asia_2", "name": "Asia 2 - Izanagi", "region": "ASIA", "status": "online", "max_players": 300},
    {"id": "na_1", "name": "America 1 - Pantheon", "region": "NA", "status": "online", "max_players": 500},
    {"id": "na_2", "name": "America 2 - Valhalla", "region": "NA", "status": "new", "max_players": 200},
]

# ===================== VIP =====================
VIP_LEVELS = [
    {"level": 0, "name": "Free", "min_spend": 0, "perks": {}, "color": "#888"},
    {"level": 1, "name": "VIP 1", "min_spend": 100, "perks": {"gold_bonus": 0.05, "stamina_max": 110, "daily_gems": 5}, "color": "#44aa44"},
    {"level": 2, "name": "VIP 2", "min_spend": 500, "perks": {"gold_bonus": 0.10, "stamina_max": 120, "daily_gems": 10, "gacha_discount": 0.05}, "color": "#4488ff"},
    {"level": 3, "name": "VIP 3", "min_spend": 1500, "perks": {"gold_bonus": 0.15, "stamina_max": 130, "daily_gems": 20, "gacha_discount": 0.10, "extra_pvp": 3}, "color": "#aa44ff"},
    {"level": 4, "name": "VIP 4", "min_spend": 5000, "perks": {"gold_bonus": 0.25, "stamina_max": 150, "daily_gems": 40, "gacha_discount": 0.15, "extra_pvp": 5, "exclusive_frame": True}, "color": "#ff4444"},
    {"level": 5, "name": "VIP 5", "min_spend": 15000, "perks": {"gold_bonus": 0.40, "stamina_max": 200, "daily_gems": 80, "gacha_discount": 0.20, "extra_pvp": 10, "exclusive_frame": True, "exclusive_aura": True}, "color": "#ffd700"},
]
