# Divine Waifus - PRD

## Overview
Idle auto-battle RPG gacha mobile game featuring 2D HD graphics.
Characters are gods, heroes, and mythological beasts reimagined as anime girls.

## Core Features
- Grid combat (9x9, 6 characters per team)
- Auto-battle with speed controls (Hokage Crisis style)
- Active/passive skills and ultimate moves
- Gacha system with multiple banners
- Team formation with positional buffs
- Equipment and inventory
- Guild/Faction system
- Community Plaza

## Technical Stack
- Frontend: Expo (React Native) with expo-router
- Backend: FastAPI + MongoDB
- Landscape orientation
- File-based routing

## Combat System (Hokage Crisis Style)
- Turn-based auto-battle
- 6v6 on 9x9 grid
- Position zones: Front (DEF+HP), Mid (ATK+SPD), Back (CRIT)
- Formation patterns give bonus buffs
- NAD (Normal Attack), SAD (Strong Attack), SP (Ultimate)
- Element system: fire, water, earth, wind, light, dark
- Status effects: burn, freeze, stun, poison, bleed, slow
- Ultimate moves with cinematic cut-in animation
