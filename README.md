# **EXPERIMENTAL PROTOTYPE — NOT YET VERIFIED IN-GAME**

**Living Weather v0.1.0 is an early community-testing build targeting
7 Days to Die v3.4.0.**

The mod's XML patches have passed automated validation against a
version-matched public configuration reference. However, the mod has
**not yet been confirmed working in a running game**.

Unexpected weather behavior, compatibility problems, and interactions
with the game's dynamic storm system are possible.

**Community testing, bug reports, and feedback are greatly appreciated!**

---

## Overview

Living Weather aims to make forest exploration more atmospheric by
making rain (and, carefully, storm) weather more frequent in the game's
forest biome — through **only** configuration changes, using 7 Days to
Die's native XML modlet system.

No new textures, particles, sounds, or code are introduced. Remove one
folder and the game is exactly vanilla again.

## Features (implemented, verified against the v3.4.0 reference)

Target biome (`pine_forest`, the current game's forest) weather
**selection weights** change as follows:

| Weather group | Vanilla 3.4.0 | Living Weather v0.1.0 |
|---------------|---------------|-----------------------|
| default       | 83            | 60                    |
| fog           | 7             | 5                     |
| rainlight     | 6             | 20                    |
| rainheavy     | 4             | 10                    |
| storm         | 0             | 5                     |

- Probabilities are normalized within each biome (per the vanilla file
  header); this mod keeps the total at exactly 100.
- In vanilla, the storm group's weight is `0` — biome rotation never
  weight-selects storms; they are scheduled by the game's separate
  dynamic-storm system (global Storm Frequency option). Setting storm
  to 5% makes the group rotation-selectable in pine_forest — noted as
  an interpretation risk with a one-line rollback in
  `docs/LOCAL_TESTING.md`.
- **Not included / not claimed:** new lightning, custom rain particles,
  sound effects, new weather systems, or any balancing changes.
- What is NOT changed: all other biomes, condition values (temperature,
  clouds, precipitation, fog, wind), spectrums, particle effects,
  zombies, loot, crafting, progression, saves, and no game file is
  overwritten.

## Compatibility

- **Exact target: 7 Days to Die v3.4.0 (PC)** — patch targets verified
  against the public `Biomes.xml/Raw_file` reference marked
  "Current. Verified for version 3.4.0" on the 7D2D Modding Wiki.
- **Any other game version is unverified.** Game updates that change
  biome weather structure will produce load-time warnings; the bundled
  validator fails loudly instead of half-applying.
- Other weather mods (in particular any mod overriding biome weather
  probabilities or shipping a full `biomes.xml` replacement) can
  conflict. Load order is alphabetical by modlet folder; the last
  patcher wins.
- Purely visual weather overhauls are plausible stack candidates, but
  untested.

## Installation (Windows, native XML modlet — no client-side prerequisites)

1. Extract `LivingWeather-v0.1.0.zip` (attached to the release).
2. Keep the *inner* `LivingWeather` folder — avoid double-nested
   folders such as `Mods\LivingWeather\LivingWeather\ModInfo.xml`.
3. Move it so these exact paths exist:

```
C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Mods\LivingWeather\ModInfo.xml
C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Mods\LivingWeather\Config\biomes.xml
```

Create the `Mods` folder inside `...\7 Days To Die\` if it does not
exist (it sits next to `Data`, not inside it). An alternative location
is also supported: `%APPDATA%\7DaysToDie\Mods\`.

Server hosts: copy the same folder into the server's `Mods\` directory
and restart. The mod is XML-only; no client code mod or EAC exclusion
is needed.

## Verification

After loading a world:

1. Press **F1** and read the startup console — `Living weather` must be
   listed and there must be **no red error lines** mentioning
   `biomes.xml`.
2. Run this console command to dump the game's merged configurations:

```
exportcurrentconfigs
```

3. Open
   `%APPDATA%\7DaysToDie\ConfigsDump\Configs\biomes.xml` and check the
   `pine_forest` biome: its weather groups must match the table above
   (default 60 / fog 5 / rainlight 20 / rainheavy 10 / storm 5).

This is the authoritative confirmation the patch actually applied.

## Uninstallation

Delete the folder
`...\7 Days To Die\Mods\LivingWeather`
and restart the game/server. Because the mod is a load-time-only patch
that never writes game files, vanilla weather is fully restored and
save worlds remain playable with or without the mod.

## Known limitations

- Only the `pine_forest` biome is modified (the historical `forest`
  biome no longer exists in the current schema).
- The game's dynamic storm system may interact unexpectedly with the
  modified storm selection weight — this is the build's biggest open
  question (see the interpreter-risk note in
  [docs/RESEARCH.md](docs/RESEARCH.md)).
- The current build has **not been tested in-game**; automation covers
  structure/targeting, not runtime behavior.
- Day-1 weather is protected vanilla behavior; differences appear from
  Day 2 onward.
- Other weather mods may conflict (load-order rules above).
- Actual gameplay effects remain to be verified by community testing —
  please help by reporting results, including negative results.

## Feedback

Please use GitHub Issues for all feedback — whether it works, fails to
load, feels too rainy, or needs tuning. Useful templates are provided:

- **Bug Report** — load failures, errors, crashes, wrong values
- **Weather Feedback** — gameplay observations and impressions

## Development notes

- `tools/validate_mod.py` re-validates the patch against a copy of your
  own `Data/Config/biomes.xml` (place it at `tests/vanilla/biomes.xml`;
  it is never committed or redistributed) and self-tests the validator
  itself. Commands are in the report
  ([docs/TEST_REPORT.md](docs/TEST_REPORT.md)); Windows users can run
  it with the `py` launcher (see
  [docs/LOCAL_TESTING.md](docs/LOCAL_TESTING.md)).
- Documentation: research notes, compatibility notes, the Windows
  testing guide, and the full validated change table live in `docs/`.
- The duration of rainfall/storms in game-days is documented by the
  vanilla configuration header itself; an *experimental* duration
  addon exists in this repository's `OptionalPresets/` for advanced
  testing, but it is gated and NOT part of this public release.

## License

Original mod code, configuration patches, documentation and tooling:
**MIT License** (see [LICENSE](LICENSE)).
The Fun Pimps' game (including `biomes.xml` and all game assets,
schemas and data files) remains the copyrighted property of The Fun
Pimps; this project contains no game assets, ships no vanilla
configuration files, and patches the in-memory configuration only at
load time. Third parties' mods/tools referenced in the research notes
are not relicensed or redistributed here.
