# MaceSmoke

A Minecraft (Paper/Spigot **1.21.11**) plugin. When a player lands a hit with a
**mace**, an expanding circle of `CLOUD` particles bursts out of the victim's
body, flies outward fast, and lingers.

## Build

```bash
mvn clean package
```

The plugin jar is produced at `target/MaceSmoke.jar`.

## Install

1. Drop `MaceSmoke.jar` into your server's `plugins/` folder.
2. Restart the server (requires Java 21).

## How it works

The plugin listens for `EntityDamageByEntityEvent`. If the damager is a player
holding a `MACE` in their main hand, it spawns rings of cloud particles at
several body-height layers around the victim. Each particle is given an outward
velocity so the smoke shoots out of the body and spreads, matching the
"smoke circle" effect.

Tweak the constants at the top of `MaceSmokePlugin.java` to change the effect:

- `OUTWARD_SPEED` — how fast the smoke flies out.
- `POINTS_PER_RING` — density of the circle.
- `RING_HEIGHTS` — vertical layers of the burst.
