# Installation & uninstallation — Living Weather v0.1.0

## Pre-flight (strongly recommended — one command)

This release was validated by automated tests but is NOT yet confirmed
against a live game install of your exact build. Before installing:

1. Make a copy of your vanilla config (this file is TFP's property;
   do not redistribute it; do not edit it):
   - Game: `<game>\Data\Config\biomes.xml`
2. Put the copy in a checkout of this project as
   `tests/vanilla/biomes.xml` and run:

   ```
   py tools\validate_mod.py
   ```

   Expected: all checks PASS with the change table printed. If any
   xpath FAILS to match (game update changed the file), do NOT install
   the mod and file the issue — that is the strongest evidence we can
   get before launching the game.

## Install (client)

Unzip `LivingWeather-v0.1.0.zip` directly into one of these folders so
that you end up with `<target>\LivingWeather\ModInfo.xml`:

- `<game>\Mods\` — Steam default:
  `C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Mods\`
  (create `Mods` if missing)
- `%APPDATA%\7DaysToDie\Mods\` (user-data location; also supported)

Do NOT nest the folder one level deeper (no
`Mods\LivingWeather\LivingWeather\ModInfo.xml`).

## Install (server / multiplayer)

Copy the same `LivingWeather` folder into the server's `Mods\` folder
and restart the server. It is an XML patch modlet: clients do not need
to install anything themselves. Keep presets consistent across a
server and its players.

## Verify it loaded

- Start the game. Open the console (F1).
- Look for the confirmation mentioning `Living weather`.
- Check the log: `%APPDATA%\7DaysToDie\output_log.txt` (or the
  `%APPDATA%\7DaysToDie\logs\` folder on newer builds). Any red XML
  error lines naming biomes.xml mean a game update broke the patch:
  uninstall and report it.
- Optional in-game confirmation of the merged config: run the console
  command `exportcurrentconfigs` and search the generated ConfigsDump
  for the pine_forest biome's weather groups (`default 60 / fog 5 /
  rainlight 20 / rainheavy 10 / storm 5`).

## Debugging

1. Red biomes.xml errors at startup → run the validator against your
   live copy (pre-flight above); if it matches everything, the issue is
   elsewhere — check other mods (alphabetically LATER modlets patch
   after us and can shadow the same attributes).
2. Mod not listed at all → wrong folder nesting (`Mods\...\Mods\`), or
   ModInfo missing. The path must be `Mods\LivingWeather\ModInfo.xml`.
3. Weather seems vanilla → you may be on Day 1 (the game gives a
   protected first day), or another weather mod overrides (alphabetical
   load order, last wins).
4. Both presets installed together → remove `LivingWeather-Stormy` and
   keep exactly one preset.

## Uninstall

Delete the `LivingWeather` folder (and, if used, the optional preset /
addon folder) from `Mods\`. Restart the game/server. Because the mod
writes nothing to disk and lives only in load-time patching, vanilla
weather is fully restored; save files are never touched and remain
valid with or without the mod.
