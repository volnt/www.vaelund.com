---
title: "#6: Procedural animations, world editor, and combat polish"
date: 2026-05-07
tag: progress
excerpt: Added procedural player animations to reduce asset load, re-evaluated world editor tools, used RenderDoc for performance optimization, and refined combat with the "Chief" mini-boss.
---

**TL;DR** -- Switched to procedural player animations to solve the asset production bottleneck, re-evaluated world editor tools, optimized performance using [RenderDoc](https://renderdoc.org/), and added the "Chief" mini-boss along with a batch of new world tiles.

## What I did

### Solving the asset bottleneck: Procedural animations

The biggest shift this week was moving towards procedural animations for the player. Previously, with traditional sprite sheets, adding a single new piece of armor or a weapon required drawing it for every frame of every animation in every direction. With our current set of animations (around 40 frames total across 2 directions, mirrored to 4), that’s a combinatorial explosion of work.

By using procedural animation, we only need to draw **two frames** per item (one per direction). The engine then handles the "bobbing" and movement logic. It’s a massive reduction in asset production load and lets us scale the equipment system much faster.

### World Editor: Re-evaluating the approach

Tooling is hard. I’m currently evaluating existing industry standards like [**Tiled**](https://www.mapeditor.org/) to see how they integrate into our pipeline. I'll report back on how that test goes.


### Performance: RenderDoc to the rescue

I added background tiles to the world this week, but my first implementation was too naive. FPS dropped from a smooth 60+ down to 15. I spent a lot of time in [RenderDoc](https://renderdoc.org/) analyzing the draw calls and pipeline. It made it incredibly easy to see exactly where the bottleneck was. After some refactoring and optimization, we’re back to full speed even with the new tile rendering.

### New Tiles

The world is starting to look like a world. Here are some of the new tiles I've added:

![Tile 0](/static/img/tiles/diablo_0.png)
![Tile 1](/static/img/tiles/diablo_1.png)
![Tile 2](/static/img/tiles/diablo_2.png)
![Tile 3](/static/img/tiles/diablo_3.png)
![Tile 4](/static/img/tiles/diablo_4.png)

### Combat updates: The "Chief"

Added the **Chief**, a new mini-boss with its own unique patterns. The Chief uses a special spell and spawns adds (other mobs) for defense, making combat encounters more unique.

- **Target of Target (ToT) frame:** Added to the UI so you can see who a mob is currently hitting.
- **Cast while moving:** Some abilities can now be cast while the player is moving, improving kiting.
- **Wrath update:** Now emits 4 damaging projectiles.
![Wrath Impact](/static/img/screenshot-wrath-impact.jpg)
- **Teleport:** Implemented a quick repositioning spell.
- **Visual feedback:** Added flashing red cells and abilities when damage is dealt.

### Bug fixes

- Fix aggro synchronization between client and server.
- Fix quest objective tracking and item inventory updates.
- Fix patrolling behavior for mobs to prevent "jitter".
- Fix z-index issues for combat UI elements.
- Fix range computation for circular and line abilities.
- Fix tile despawning when exiting the game state.

## What's next

Testing [Tiled](https://www.mapeditor.org/) for map design, continuing work on the procedural animation system, and developing the level 1-5 starter zone logic.
