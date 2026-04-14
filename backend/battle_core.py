"""
Divine Waifus - Battle Engine
Inspired by Hokage Crisis: Turn-based auto-battle with formation strategy
6 characters per team, 9x9 grid positioning with buffs
Features: NAD (Normal Attack), SAD (Strong Attack), SP (Ultimate Move)
Active/Passive skills, positional buffs, cinematic ultimate triggers
"""
import random
import math
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

# ===================== POSITION BUFFS ON 9x9 GRID =====================

POSITION_BUFFS = {
    "front": {"rows": [0, 1, 2], "buff": {"defense": 0.20, "hp": 0.15}, "name": "Vanguardia", "desc": "+20% DEF, +15% HP"},
    "mid": {"rows": [3, 4, 5], "buff": {"attack": 0.15, "speed": 0.10}, "name": "Centro", "desc": "+15% ATK, +10% SPD"},
    "back": {"rows": [6, 7, 8], "buff": {"crit_rate": 0.15, "crit_damage": 0.30}, "name": "Retroguardia", "desc": "+15% CRIT, +30% CRIT DMG"},
}

# Special formations that grant extra bonuses
FORMATION_PATTERNS = {
    "v_shape": {
        "name": "Formazione a V",
        "description": "3 davanti, 2 al centro, 1 dietro",
        "check": lambda positions: (
            sum(1 for p in positions if p['y'] <= 2) == 3 and
            sum(1 for p in positions if 3 <= p['y'] <= 5) == 2 and
            sum(1 for p in positions if p['y'] >= 6) == 1
        ),
        "buff": {"attack": 0.10, "defense": 0.10},
    },
    "wall": {
        "name": "Muro di Ferro",
        "description": "Tutti i 6 in prima/seconda riga",
        "check": lambda positions: all(p['y'] <= 3 for p in positions),
        "buff": {"defense": 0.25, "hp": 0.20},
    },
    "sniper": {
        "name": "Cecchini Divini",
        "description": "Tutti i 6 nelle ultime 3 righe",
        "check": lambda positions: all(p['y'] >= 6 for p in positions),
        "buff": {"crit_rate": 0.20, "attack": 0.15},
    },
    "diamond": {
        "name": "Diamante Sacro",
        "description": "1 davanti, 2 centro, 2 centro, 1 dietro",
        "check": lambda positions: (
            sum(1 for p in positions if p['y'] <= 2) == 1 and
            sum(1 for p in positions if 3 <= p['y'] <= 5) >= 3 and
            sum(1 for p in positions if p['y'] >= 6) == 1
        ),
        "buff": {"attack": 0.08, "defense": 0.08, "speed": 0.08, "crit_rate": 0.08},
    },
    "spread": {
        "name": "Dispersione Tattica",
        "description": "2 per ogni zona (davanti, centro, dietro)",
        "check": lambda positions: (
            sum(1 for p in positions if p['y'] <= 2) == 2 and
            sum(1 for p in positions if 3 <= p['y'] <= 5) == 2 and
            sum(1 for p in positions if p['y'] >= 6) == 2
        ),
        "buff": {"attack": 0.12, "speed": 0.12},
    },
    "column": {
        "name": "Colonna di Battaglia",
        "description": "Tutti nella stessa colonna (±1)",
        "check": lambda positions: (
            max(p['x'] for p in positions) - min(p['x'] for p in positions) <= 2
        ),
        "buff": {"attack": 0.18, "crit_damage": 0.20},
    },
}

# Adjacency bonus: characters next to each other get bonuses
def calculate_adjacency_bonus(positions: list) -> dict:
    """Check for adjacent characters and calculate bonuses"""
    bonus = {"attack": 0, "defense": 0, "hp": 0, "speed": 0}
    adj_count = 0
    for i, p1 in enumerate(positions):
        for j, p2 in enumerate(positions):
            if i >= j:
                continue
            dx = abs(p1['x'] - p2['x'])
            dy = abs(p1['y'] - p2['y'])
            if dx <= 1 and dy <= 1:  # Adjacent (including diagonal)
                adj_count += 1
    # More adjacent pairs = bigger bonus
    mult = adj_count * 0.03
    bonus["attack"] = mult
    bonus["defense"] = mult
    return {"bonus": bonus, "adjacent_pairs": adj_count}


# ===================== SKILL DEFINITIONS =====================

SKILL_TYPES = {
    "nad": {"name": "Attacco Normale", "type": "nad", "cooldown": 0, "hits": 3},
    "sad": {"name": "Attacco Forte", "type": "sad", "cooldown": 3, "hits": 1},
    "sp": {"name": "Mossa Finale", "type": "sp", "cooldown": 0, "gauge_cost": 100, "hits": 1},
}

# Element-specific skill effects
ELEMENT_SKILLS = {
    "fire": {
        "nad": {"name": "Colpo Infernale", "animation": "slash_fire", "damage_mult": 1.0, "effect": None, "icon": "🔥"},
        "sad": {"name": "Tempesta di Fiamme", "animation": "burst_fire", "damage_mult": 2.5, "effect": {"type": "burn", "damage_per_turn": 0.05, "duration": 3}, "icon": "🌋", "description": "Infligge Ustione per 3 turni"},
        "sp": {"name": "Inferno Divino", "animation": "ultimate_fire", "damage_mult": 5.0, "effect": {"type": "burn", "damage_per_turn": 0.08, "duration": 3}, "icon": "☄️", "description": "Devastante attacco di fuoco che brucia tutto!"},
    },
    "water": {
        "nad": {"name": "Lama d'Acqua", "animation": "slash_water", "damage_mult": 1.0, "effect": None, "icon": "💧"},
        "sad": {"name": "Tsunami", "animation": "burst_water", "damage_mult": 2.3, "effect": {"type": "slow", "speed_reduction": 0.30, "duration": 2}, "icon": "🌊", "description": "Rallenta i nemici del 30%"},
        "sp": {"name": "Maremoto Celeste", "animation": "ultimate_water", "damage_mult": 4.5, "effect": {"type": "freeze", "duration": 1}, "icon": "🧊", "description": "Congela tutti i nemici per 1 turno!"},
    },
    "earth": {
        "nad": {"name": "Pugno di Terra", "animation": "slash_earth", "damage_mult": 1.0, "effect": None, "icon": "🪨"},
        "sad": {"name": "Terremoto", "animation": "burst_earth", "damage_mult": 2.0, "effect": {"type": "stun", "duration": 1}, "icon": "⛰️", "description": "Stordisce il nemico per 1 turno"},
        "sp": {"name": "Collasso Tettonico", "animation": "ultimate_earth", "damage_mult": 4.0, "effect": {"type": "defense_break", "reduction": 0.40, "duration": 3}, "icon": "🌍", "description": "Riduce la DEF nemica del 40%!"},
    },
    "wind": {
        "nad": {"name": "Taglio del Vento", "animation": "slash_wind", "damage_mult": 1.0, "effect": None, "icon": "💨"},
        "sad": {"name": "Lame di Vento", "animation": "burst_wind", "damage_mult": 2.8, "effect": {"type": "bleed", "damage_per_turn": 0.04, "duration": 3}, "icon": "🌪️", "description": "Provoca Sanguinamento per 3 turni"},
        "sp": {"name": "Uragano Divino", "animation": "ultimate_wind", "damage_mult": 5.5, "effect": {"type": "bleed", "damage_per_turn": 0.06, "duration": 3}, "icon": "🌀", "description": "Attacco devastante che lacera i nemici!"},
    },
    "light": {
        "nad": {"name": "Raggio Sacro", "animation": "slash_light", "damage_mult": 1.0, "effect": None, "icon": "✨"},
        "sad": {"name": "Giudizio Divino", "animation": "burst_light", "damage_mult": 2.4, "effect": {"type": "weaken", "attack_reduction": 0.25, "duration": 2}, "icon": "🌟", "description": "Indebolisce ATK nemica del 25%"},
        "sp": {"name": "Apocalisse Luminosa", "animation": "ultimate_light", "damage_mult": 6.0, "effect": {"type": "purify", "removes_buffs": True}, "icon": "💫", "description": "Rimuove tutti i buff nemici e infligge danno enorme!"},
    },
    "dark": {
        "nad": {"name": "Artiglio d'Ombra", "animation": "slash_dark", "damage_mult": 1.0, "effect": None, "icon": "🌑"},
        "sad": {"name": "Maledizione Oscura", "animation": "burst_dark", "damage_mult": 2.6, "effect": {"type": "poison", "damage_per_turn": 0.06, "duration": 4}, "icon": "💀", "description": "Avvelena per 4 turni"},
        "sp": {"name": "Eclissi Totale", "animation": "ultimate_dark", "damage_mult": 5.8, "effect": {"type": "death_mark", "instant_kill_chance": 0.15}, "icon": "🕳️", "description": "15% di eliminazione istantanea!"},
    },
    "neutral": {
        "nad": {"name": "Colpo Rapido", "animation": "slash_neutral", "damage_mult": 1.0, "effect": None, "icon": "⚔️"},
        "sad": {"name": "Assalto Potenziato", "animation": "burst_neutral", "damage_mult": 2.2, "effect": None, "icon": "💥", "description": "Attacco forte senza effetti speciali"},
        "sp": {"name": "Furia Primordiale", "animation": "ultimate_neutral", "damage_mult": 4.5, "effect": None, "icon": "⚡", "description": "Attacco potente puro"},
    },
}

# Passive skill templates based on rarity
PASSIVE_SKILLS = {
    1: [{"name": "Resistenza Base", "effect": {"defense": 0.05}, "icon": "🛡️"}],
    2: [{"name": "Agilità", "effect": {"speed": 0.08}, "icon": "💨"}, {"name": "Forza Bruta", "effect": {"attack": 0.08}, "icon": "💪"}],
    3: [{"name": "Occhio Critico", "effect": {"crit_rate": 0.08}, "icon": "👁️"}, {"name": "Rigenerazione", "effect": {"heal_per_turn": 0.03}, "icon": "💚"}],
    4: [{"name": "Poise", "effect": {"damage_reduction": 0.10}, "icon": "🛡️"}, {"name": "Frenesia", "effect": {"attack_at_full_hp": 0.20}, "icon": "🔥"}],
    5: [{"name": "Immunità Status", "effect": {"status_immunity": 0.50}, "icon": "✨"}, {"name": "Colpo Fatale", "effect": {"crit_damage": 0.30}, "icon": "💥"}, {"name": "Schivata", "effect": {"dodge_rate": 0.12}, "icon": "💨"}],
    6: [{"name": "Divino", "effect": {"all_stats": 0.15}, "icon": "👑"}, {"name": "Invincibilità Temporanea", "effect": {"invincible_turns_start": 1}, "icon": "🌟"}, {"name": "Super Armatura", "effect": {"damage_reduction": 0.20, "status_immunity": 0.80}, "icon": "⚜️"}],
}


def simulate_battle(team_a: list, team_b: list, max_turns: int = 20) -> dict:
    """
    Simulate a full battle between two teams.
    Each team is a list of character dicts with stats and skills.
    Returns detailed battle log with animations.
    """
    battle_log = []
    turn = 0
    
    # Initialize combat state
    for char in team_a + team_b:
        char['current_hp'] = char.get('max_hp', char.get('hp', 10000))
        char['max_hp_battle'] = char['current_hp']
        char['sp_gauge'] = 0
        char['sad_cooldown'] = 0
        char['status_effects'] = []
        char['is_alive'] = True
        char['total_damage_dealt'] = 0
    
    while turn < max_turns:
        turn += 1
        turn_log = {"turn": turn, "actions": []}
        
        # Combine and sort by speed
        all_chars = [(c, 'team_a') for c in team_a if c['is_alive']] + \
                    [(c, 'team_b') for c in team_b if c['is_alive']]
        all_chars.sort(key=lambda x: x[0].get('speed', 100), reverse=True)
        
        for char, team_id in all_chars:
            if not char['is_alive']:
                continue
            
            # Process status effects
            status_actions = process_status_effects(char)
            turn_log['actions'].extend(status_actions)
            
            if not char['is_alive']:
                continue
            
            # Check if stunned/frozen
            if any(s['type'] in ('stun', 'freeze') for s in char['status_effects']):
                turn_log['actions'].append({
                    "type": "skip",
                    "actor": char['name'],
                    "actor_id": char['id'],
                    "team": team_id,
                    "reason": "Stordito/Congelato",
                    "animation": "stunned",
                })
                continue
            
            # Pick target
            enemies = [c for c in (team_b if team_id == 'team_a' else team_a) if c['is_alive']]
            if not enemies:
                break
            
            target = min(enemies, key=lambda e: e['current_hp'])  # Target lowest HP
            
            # Decide action: SP > SAD > NAD
            element = char.get('element', 'neutral')
            skills = ELEMENT_SKILLS.get(element, ELEMENT_SKILLS['neutral'])
            
            action = None
            if char['sp_gauge'] >= 100:
                # Ultimate move!
                action = execute_skill(char, target, enemies, skills['sp'], 'sp', team_id)
                char['sp_gauge'] = 0
            elif char['sad_cooldown'] <= 0:
                # Strong attack
                action = execute_skill(char, target, enemies, skills['sad'], 'sad', team_id)
                char['sad_cooldown'] = 3
            else:
                # Normal attack
                action = execute_skill(char, target, enemies, skills['nad'], 'nad', team_id)
                char['sp_gauge'] = min(100, char['sp_gauge'] + 20)
                char['sad_cooldown'] = max(0, char['sad_cooldown'] - 1)
            
            if action:
                turn_log['actions'].append(action)
            
            # Passive: heal per turn
            for passive in char.get('passives', []):
                if 'heal_per_turn' in passive.get('effect', {}):
                    heal_amount = int(char['max_hp_battle'] * passive['effect']['heal_per_turn'])
                    char['current_hp'] = min(char['max_hp_battle'], char['current_hp'] + heal_amount)
                    turn_log['actions'].append({
                        "type": "heal", "actor": char['name'], "actor_id": char['id'],
                        "team": team_id, "amount": heal_amount, "animation": "heal_green",
                    })
            
            # Check if battle is over
            if not any(c['is_alive'] for c in team_b):
                break
            if not any(c['is_alive'] for c in team_a):
                break
        
        battle_log.append(turn_log)
        
        # Check victory conditions
        team_a_alive = any(c['is_alive'] for c in team_a)
        team_b_alive = any(c['is_alive'] for c in team_b)
        
        if not team_a_alive or not team_b_alive:
            break
    
    # Determine winner
    team_a_hp = sum(c['current_hp'] for c in team_a if c['is_alive'])
    team_b_hp = sum(c['current_hp'] for c in team_b if c['is_alive'])
    team_a_alive_count = sum(1 for c in team_a if c['is_alive'])
    team_b_alive_count = sum(1 for c in team_b if c['is_alive'])
    
    victory = team_a_alive_count > team_b_alive_count or (team_a_alive_count == team_b_alive_count and team_a_hp > team_b_hp)
    
    # Build result
    result = {
        "victory": victory,
        "turns": turn,
        "battle_log": battle_log,
        "team_a_survivors": team_a_alive_count,
        "team_b_survivors": team_b_alive_count,
        "team_a_final": [{"id": c['id'], "name": c['name'], "hp": c['current_hp'], "max_hp": c['max_hp_battle'], "is_alive": c['is_alive'], "damage_dealt": c['total_damage_dealt'], "image": c.get('image'), "element": c.get('element'), "hero_class": c.get('hero_class'), "rarity": c.get('rarity', 1)} for c in team_a],
        "team_b_final": [{"id": c['id'], "name": c['name'], "hp": c['current_hp'], "max_hp": c['max_hp_battle'], "is_alive": c['is_alive'], "damage_dealt": c['total_damage_dealt'], "image": c.get('image'), "element": c.get('element'), "hero_class": c.get('hero_class'), "rarity": c.get('rarity', 1)} for c in team_b],
        "mvp": max(team_a, key=lambda c: c['total_damage_dealt'])['name'] if victory else None,
    }
    
    return result


def execute_skill(attacker: dict, target: dict, all_enemies: list, skill: dict, skill_type: str, team_id: str) -> dict:
    """Execute a skill and return the action log"""
    
    atk = attacker.get('attack', 1000)
    dfn = target.get('defense', 500)
    
    # Apply passive bonuses
    for passive in attacker.get('passives', []):
        eff = passive.get('effect', {})
        if 'attack_at_full_hp' in eff and attacker['current_hp'] >= attacker['max_hp_battle'] * 0.99:
            atk *= (1 + eff['attack_at_full_hp'])
        if 'all_stats' in eff:
            atk *= (1 + eff['all_stats'])
    
    # Base damage
    base_damage = max(1, atk - dfn * 0.5)
    damage_mult = skill.get('damage_mult', 1.0)
    total_damage = int(base_damage * damage_mult * random.uniform(0.9, 1.1))
    
    # Crit check
    crit = False
    crit_rate = attacker.get('crit_rate', 0.10)
    crit_damage = attacker.get('crit_damage', 1.5)
    if random.random() < crit_rate:
        crit = True
        total_damage = int(total_damage * crit_damage)
    
    # Dodge check
    dodge_rate = target.get('dodge_rate', 0)
    dodged = random.random() < dodge_rate
    
    if dodged:
        return {
            "type": "dodge", "actor": attacker['name'], "actor_id": attacker['id'],
            "target": target['name'], "target_id": target['id'],
            "team": team_id, "skill": skill, "skill_type": skill_type,
            "animation": "dodge",
        }
    
    # Apply damage reduction
    for passive in target.get('passives', []):
        if 'damage_reduction' in passive.get('effect', {}):
            total_damage = int(total_damage * (1 - passive['effect']['damage_reduction']))
    
    # Apply damage
    targets_hit = []
    if skill_type == 'sp':
        # Ultimate hits all enemies
        for enemy in all_enemies:
            if enemy['is_alive']:
                dmg = int(total_damage * random.uniform(0.85, 1.0))
                enemy['current_hp'] = max(0, enemy['current_hp'] - dmg)
                if enemy['current_hp'] <= 0:
                    enemy['is_alive'] = False
                attacker['total_damage_dealt'] += dmg
                targets_hit.append({"name": enemy['name'], "id": enemy['id'], "damage": dmg, "killed": not enemy['is_alive'], "hp_remaining": enemy['current_hp']})
    else:
        # Single target
        target['current_hp'] = max(0, target['current_hp'] - total_damage)
        if target['current_hp'] <= 0:
            target['is_alive'] = False
        attacker['total_damage_dealt'] += total_damage
        targets_hit.append({"name": target['name'], "id": target['id'], "damage": total_damage, "killed": not target['is_alive'], "hp_remaining": target['current_hp']})
    
    # Apply status effect
    effect_applied = None
    if skill.get('effect'):
        eff = skill['effect']
        if eff['type'] == 'death_mark' and random.random() < eff.get('instant_kill_chance', 0):
            target['current_hp'] = 0
            target['is_alive'] = False
            effect_applied = {"type": "instant_kill", "target": target['name']}
        elif eff['type'] in ('burn', 'poison', 'bleed'):
            for enemy in (all_enemies if skill_type == 'sp' else [target]):
                if enemy['is_alive']:
                    enemy['status_effects'].append({
                        "type": eff['type'],
                        "damage_per_turn": eff.get('damage_per_turn', 0.05),
                        "turns_remaining": eff.get('duration', 3),
                        "source": attacker['name'],
                    })
            effect_applied = {"type": eff['type'], "duration": eff.get('duration', 0)}
        elif eff['type'] in ('stun', 'freeze'):
            target['status_effects'].append({
                "type": eff['type'],
                "turns_remaining": eff.get('duration', 1),
            })
            effect_applied = {"type": eff['type'], "duration": eff.get('duration', 1)}
        elif eff['type'] == 'slow':
            target['speed'] = int(target.get('speed', 100) * (1 - eff.get('speed_reduction', 0.3)))
            effect_applied = {"type": "slow", "reduction": eff.get('speed_reduction', 0.3)}
        elif eff['type'] == 'weaken':
            target['attack'] = int(target.get('attack', 1000) * (1 - eff.get('attack_reduction', 0.25)))
            effect_applied = {"type": "weaken", "reduction": eff.get('attack_reduction', 0.25)}
        elif eff['type'] == 'defense_break':
            target['defense'] = int(target.get('defense', 500) * (1 - eff.get('reduction', 0.4)))
            effect_applied = {"type": "defense_break", "reduction": eff.get('reduction', 0.4)}
    
    return {
        "type": "attack",
        "actor": attacker['name'],
        "actor_id": attacker['id'],
        "team": team_id,
        "skill_type": skill_type,
        "skill": {
            "name": skill.get('name', 'Attacco'),
            "icon": skill.get('icon', '⚔️'),
            "description": skill.get('description', ''),
            "animation": skill.get('animation', 'slash_neutral'),
        },
        "targets": targets_hit,
        "total_damage": sum(t['damage'] for t in targets_hit),
        "crit": crit,
        "effect": effect_applied,
    }


def process_status_effects(char: dict) -> list:
    """Process DoT and other status effects at start of turn"""
    actions = []
    new_effects = []
    
    for effect in char.get('status_effects', []):
        if effect['type'] in ('burn', 'poison', 'bleed'):
            dot_damage = int(char['max_hp_battle'] * effect.get('damage_per_turn', 0.05))
            char['current_hp'] = max(0, char['current_hp'] - dot_damage)
            if char['current_hp'] <= 0:
                char['is_alive'] = False
            
            effect_names = {'burn': '🔥 Ustione', 'poison': '☠️ Veleno', 'bleed': '🩸 Sanguinamento'}
            actions.append({
                "type": "dot",
                "target": char['name'],
                "target_id": char['id'],
                "damage": dot_damage,
                "effect_type": effect['type'],
                "effect_name": effect_names.get(effect['type'], effect['type']),
                "animation": f"dot_{effect['type']}",
            })
        
        effect['turns_remaining'] -= 1
        if effect['turns_remaining'] > 0:
            new_effects.append(effect)
    
    char['status_effects'] = new_effects
    return actions


def prepare_battle_character(hero_data: dict, user_hero_data: dict = None, position: dict = None) -> dict:
    """Prepare a character for battle with all stats, skills, and passives"""
    stats = hero_data.get('base_stats', {})
    element = hero_data.get('element', 'neutral')
    rarity = hero_data.get('rarity', 1)
    
    # Level multiplier
    level = user_hero_data.get('level', 1) if user_hero_data else 1
    level_mult = 1 + (level - 1) * 0.05
    
    # Base combat stats
    char = {
        'id': hero_data.get('id', str(uuid.uuid4())),
        'name': hero_data.get('name', 'Sconosciuto'),
        'element': element,
        'rarity': rarity,
        'image': hero_data.get('image_url') or hero_data.get('image'),
        'hero_class': hero_data.get('hero_class', 'DPS'),
        'hp': int(stats.get('hp', 8000) * level_mult),
        'attack': int(stats.get('attack', 1000) * level_mult),
        'defense': int(stats.get('defense', 500) * level_mult),
        'speed': int(stats.get('speed', 100) * level_mult),
        'crit_rate': stats.get('crit_rate', 0.10),
        'crit_damage': stats.get('crit_damage', 1.5),
        'dodge_rate': 0,
    }
    
    # Get skills based on element
    element_skills = ELEMENT_SKILLS.get(element, ELEMENT_SKILLS['neutral'])
    char['skills'] = {
        'nad': element_skills['nad'],
        'sad': element_skills['sad'],
        'sp': element_skills['sp'],
    }
    
    # Get passives based on rarity
    rarity_passives = PASSIVE_SKILLS.get(min(rarity, 6), PASSIVE_SKILLS[1])
    char['passives'] = rarity_passives
    
    # Apply passive stat bonuses
    for passive in char['passives']:
        eff = passive.get('effect', {})
        if 'dodge_rate' in eff:
            char['dodge_rate'] += eff['dodge_rate']
        if 'all_stats' in eff:
            char['attack'] = int(char['attack'] * (1 + eff['all_stats']))
            char['defense'] = int(char['defense'] * (1 + eff['all_stats']))
            char['hp'] = int(char['hp'] * (1 + eff['all_stats']))
            char['speed'] = int(char['speed'] * (1 + eff['all_stats']))
    
    # Apply position buffs
    if position:
        y = position.get('y', 4)
        for zone_name, zone_data in POSITION_BUFFS.items():
            if y in zone_data['rows']:
                for stat, buff_val in zone_data['buff'].items():
                    if stat in char:
                        char[stat] = int(char[stat] * (1 + buff_val))
                char['position_zone'] = zone_name
                break
    
    char['max_hp'] = char['hp']
    
    return char


def generate_enemy_team(power_level: int, count: int = 6) -> list:
    """Generate an enemy team based on power level"""
    elements = ['fire', 'water', 'earth', 'wind', 'light', 'dark']
    enemy_names = [
        "Ombra Errante", "Spirito Maligno", "Bestia Infernale",
        "Guerriero Oscuro", "Mago Corrotto", "Titano Caduto",
        "Demone Minore", "Custode Antico", "Drago d'Ombra",
    ]
    
    enemies = []
    for i in range(count):
        element = elements[i % len(elements)]
        mult = power_level / 10000
        enemy = {
            'id': f'enemy_{i}',
            'name': random.choice(enemy_names),
            'element': element,
            'rarity': min(6, max(1, int(mult))),
            'hero_class': random.choice(['DPS', 'Tank', 'Support']),
            'hp': int(8000 * mult * random.uniform(0.8, 1.2)),
            'attack': int(1000 * mult * random.uniform(0.8, 1.2)),
            'defense': int(500 * mult * random.uniform(0.8, 1.2)),
            'speed': int(100 * mult * random.uniform(0.8, 1.2)),
            'crit_rate': 0.08,
            'crit_damage': 1.4,
            'dodge_rate': 0.03,
            'skills': ELEMENT_SKILLS.get(element, ELEMENT_SKILLS['neutral']),
            'passives': PASSIVE_SKILLS.get(min(int(mult), 6), PASSIVE_SKILLS[1]),
        }
        enemies.append(enemy)
    
    return enemies


