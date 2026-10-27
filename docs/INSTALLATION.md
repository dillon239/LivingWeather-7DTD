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
