---
title: "#5: Tick rate, entity refactor, and mob patrol"
date: 2026-04-30
tag: progress
excerpt: Reduced server tick rate from 20Hz to 10Hz, centralized entity position tracking, replaced wandering pathfinding with hardcoded patrol paths, and fixed a pile of combat and UI bugs.
---

**TL;DR** -- Reduced server tick rate from 20Hz to 10Hz, centralized entity position tracking so spatial indexes stay consistent, replaced wandering pathfinding with hardcoded patrol paths, and fixed a pile of combat and UI bugs.

## What I did

### Tick rate: 20Hz to 10Hz

The server now runs at 10 ticks per second instead of 20. This cuts server CPU and bandwidth usage in half. For a grid-based game with discrete cell movement, 10Hz gives enough responsiveness without the overhead.

### Entity position: fix spatial consistency

After teleporting, an entity needs to be removed from the old chunk, added to the new one, grid position updated, blocked cells updated. The old system scattered these steps across different places and they were easy to get wrong. I centralized the position update logic so spatial indexes stay consistent in all cases.

### Mob patrol paths

Mobs were pathfinding to random wander spots, which uses CPU for something that could be hardcoded. I replaced it with predefined patrol paths. We can revisit pathfinding later if mobs need more dynamic behavior.

### Bug fixes

A lot of this week was bug fixes. Here's a partial list:

- Fix mana regen and health regen
- Fix mob attack and chase
- Fix mob interpolation and speed
- Fix AOE hitting multiple mobs correctly
- Fix respawn mobs going crazy
- Fix loot and NPC quest acceptance
- Fix quest descriptions and objectives updating from inventory
- Fix entity IDs on reconnect
- Fix NPC despawn
- Fix Rock Mace ability so it can attack
- Fix level up behavior
- Fix glow and nameplate for larger mobs
- Fix ability bar click handling
- Fix disconnect/reconnect

### UI

Added a login modal. The ability bar is now clickable. Range rendering shows the area of abilities. Quick cast option to bypass the action queue.

![Range Rendering](/static/img/screenshot-range-rendering.jpg)
![Quick Cast](/static/img/screenshot-quickcast.jpg)

## What's next

The current goal is to iterate on the gameplay loop from level 1 to 5 in a starter zone inspired by Mulgore, with its quests, items, and mobs.
