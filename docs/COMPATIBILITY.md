# Compatibility — Living Weather v0.1.0

## Game versions

- Patch targets are **verified against the public 3.4.0 schema
  reference** (7D2D Modding Wiki, `Biomes.xml/Raw_file`, page banner
  "Current. Verified for version 3.4.0"): biome `pine_forest` (the
  current generation's forest; the 1.0-era `forest` biome no longer
  exists), weather groups default/fog/rainlight/rainheavy/stormbuild/
  storm/bloodMoon/twitch_*.
- **Compatibility with your local installation remains unverified**
  until the validator is run against your own `biomes.xml` copy and
  the mod actually loads in the game. No in-game test has occurred
  (not possible in the development workspace); this is stated
  everywhere it matters, including the release README.
- Vanilla numbers used in the docs are the verified 3.4.0 values
  (pine_forest: default 83/fog 7/rainlight 6/rainheavy 4/storm 0).
  A local file that differs from the reference is flagged loudly by
  the validator rather than silently patched.

## Load order

Modlets load alphabetically by folder name. `LivingWeather` patches
only five `prob` attributes in the pine_forest biome, so:

- Any mod that patches the SAME attributes (pine_forest weather
  probabilities) loads-Last-Wins. Notable published weather overhaul
  mods (e.g. Atmospheric Weather V3) declare themselves incompatible
  with biomes.xml weather patches — do not combine.
- Full-file biome/weather replacements are unsupported together with
  this mod (our patch may hit a file whose contents differ wildly).

## Plugins that should coexist (untested claims — verify by testing)

- Pure visual weather/sky/cloud overhauls that do not touch
  biomes.xml probabilities.
- UI, loot, crafting, zombie, map and progression mods (we touch no
  block, item, entity or progression XML at all).

## Multiplayer / EAC

- XML-only modlet; no C# code mod → EAC friendly; functions as a
  server-side mod. Speedy permitted. Keep presets consistent across
  a server and its players to avoid confusion.

## The experimental duration addon

`LivingWeather-StormDuration` extends the verified `duration`
parameter (game-days, default 3, documented in the vanilla file
header): storm 1.1 → 1.6 via `set` (attribute exists in vanilla),
rainlight/rainheavy 3 → 4 via `setattribute` (documented default
applies). `delay="26,36"` is deliberately untouched (semantics not
documented). The whole addon is still marked experimental until
in-game confirmation because weather durations were re-tuned between
releases by TFP (V2.1 notes famously adjusted storm durations), and
its combination with dynamic-storm scheduling is unobserved.
