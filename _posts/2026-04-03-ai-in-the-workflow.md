---
title: "#1: AI in the workflow"
date: 2026-04-03
tag: meta
excerpt: We kept the server architecture modular. We designed the network to scale to 1000 players with low network load. We built a CLI for scripted testing.
---

**TL;DR** -- We kept the server architecture modular. We designed the network to scale to 1000 players with low network load. We built a CLI for scripted testing.

---

## Vaelund

Vaelund is a 2D isometric MMORPG built in Rust. The engine is custom. The world is one seamless map, no zone loading screens.

The team is one person. The stack: Rust + SQLite + Bevy, for rendering, plus a custom UDP protocol for networking.

## The monolith

At some point `game.rs` was doing game logic, network handling, connection management, and most of the server-side tick. It was not a design decision, it accumulated.

When the context window fills with duplication and too many responsibilities, AI code generation starts producing code that matches the immediate problem but makes the next problem harder. The solution was to drive refactoring by hand: extract `ConnectionManager`, extract `NetStats`, extract `ZoneTracker`, split command handling into its own module, move the network stack out of `game.rs`.

## The network math

Before the architecture was touched, the network was not sustainable. Each `WorldStateDelta` sent full entity state for every entity in the zone, every tick.

Back of the envelope: one entity at 10 bytes per field, 20 fields per entity, 60 entities per zone, 10 ticks per second = 120KB/s per zone. For 1000 players concentrated in one place, this does not hold.

The client-driven mob movement change helped. Instead of broadcasting mob positions every tick, the server sends a path and the client follows it. Bandwidth dropped roughly 75%. The chunk-based visibility culling limits updates to the player's nearby 16x16 chunks, only mobs in those chunks are sent to the client. This is a naive implementation but it works.

Empty deltas are skipped. The server tick rate was not the problem, the issue was sending full state when nothing had changed.

## A CLI tool to script end-to-end testing

Testing required a human with a client in front of a screen. The CLI tool was built to fix this.

The tool connects to the game server over UDP. It can create a character, walk to a position, attack a mob, accept a quest, loot a corpse, all from a terminal. It speaks the same protocol the real client uses. Commands are deterministic: a script can run a sequence of moves and attacks against a known mob spawn and verify the server responds correctly.

This makes it possible to test movement, combat, quests, and inventory through scripted scenarios. What this cannot test: whether the game is fun. That requires a person.

## Asset generation with PixelLab

Sprites are generated through PixelLab.ai, partly through a Python script that calls the API, partly by hand.

The `meadow_rat` took four generations before the result was usable. The anatomy was wrong across frames, the tail was inconsistent between animation frames. This required iteration, not a single pixel adjustment. The process is not automatic.

![Meadow Rat](/static/img/sprites/south-east.png)
![Health Potion](/static/img/sprites/item_001.png)
![Leather Armor](/static/img/sprites/item_010.png)
![Iron Sword](/static/img/sprites/item_030.png)
![Archon's Sigil](/static/img/sprites/item_052.png)

*These are icon placeholders, not entity sprites.*

For someone who does not know how to draw, PixelLab is incredibly useful. Results are very good bases that need refinement. They are not finished assets and not ready to ship without review.
