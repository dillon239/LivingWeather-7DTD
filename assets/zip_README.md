# Living Weather v0.1.0

Living Weather makes the **forest (pine_forest) biome** in 7 Days to Die
feel more atmospheric: rain and storms are markedly more frequent, while
plenty of clear weather remains. Everything else in the game is
untouched: same weather visuals (no new assets), same zombies, loot,
crafting and survival rules, and every other biome behaves exactly
vanilla.

## Requirements

- 7 Days to Die PC. The patch targets are verified against the public
  Biomes.xml/Raw_file reference marked "Current. Verified for version
  3.4.0" on the 7D2D Modding Wiki.
- This is an XML patch modlet: no client code mod needed; works as a
  server-side mod for online play.
- IMPORTANT: compatibility with any particular local installation
  remains unverified until the game actually loads the mod. Verify with
  the bundled validation script against a copy of your own
  `Data/Config/biomes.xml` before playing (see below), and watch the
  game log on first launch.

## Installation

1. Unzip this archive so the folder `LivingWeather` lands in your game's
   `Mods` directory, i.e. you end up with
   `<...>\7 Days To Die\Mods\LivingWeather\ModInfo.xml`.
   - Steam default: `C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Mods\`
     (create the `Mods` folder if it does not exist)
   - Also supported: `%APPDATA%\7DaysToDie\Mods\`
2. Start the game / server. Check the console and the log
   (`%APPDATA%\7DaysToDie\output_log.txt` or
   `%APPDATA%\7DaysToDie\logs\`) for the mod's load confirmation and for
   any red error next to `biomes.xml`; red lines mean the XML structure
   differs from the verified reference - uninstall and file a bug.
3. Optional in-game verification: run the console command
   `exportcurrentconfigs` and check the forest groups in the dumped
   `biomes.xml` (values in the table below).

## What it changes (verified 3.4.0 values)

Only `prob` attributes of named weather groups in the biome
`pine_forest`. Vanilla probabilities for that biome: default 83,
fog 7, rainlight 6, rainheavy 4, storm 0 (plus stormbuild / bloodMoon /
twitch_* at 0). Probabilities are normalized within the biome's groups
(per the file header), the mod keeps a total of exactly 100:

| Weather group | Vanilla 3.4.0 | Living Weather v0.1 (Atmospheric) |
|---------------|---------------|-----------------------------------|
| default       | 83            | 60                                |
| fog           | 7             | 5                                 |
| rainlight     | 6             | 20                                |
| rainheavy     | 4             | 10                                |
| storm         | 0             | 5                                 |

Nothing else is modified: no condition values (temperature, clouds,
precipitation, fog, wind), no spectrums, no duration (except the
separate experimental addon), no other biome, no gameplay systems.

## Weather-scheduling caveat (honest disclosure)

The game's global rotation never weight-selects the storm group in
vanilla (prob="0"): dynamic storms (the server "Storm Frequency"
option) schedule them instead. Living Weather sets the storm group's
prob to a small non-zero value so the biome's own rotation can select
it - the only XML-only, biome-local storm-frequency lever in the
verified schema. The in-game interaction between these two systems has
NOT yet been observed; if storms feel too frequent on your setup, set
the storm group's prob back to 0 by editing one line in
`Config/biomes.xml` inside the mod folder.

## Storm duration (separate experimental addon, V2.0+ era builds)

The vanilla file header documents `duration` (in game-days, default 3)
and pine_forest carries `default duration="6"`, `stormbuild=".2"`,
`storm duration="1.1" delay="26,36"` (delay deliberately untouched by
this mod - semantics not documented). The optional
`LivingWeather-StormDuration` addon extends: storm 1.1 -> 1.6 (set on
the existing attribute) and rainlight/rainheavy duration 3 -> 4
(setattribute; the documented default applies). Its gate was
already verified against the 3.4.0 reference.

## Uninstallation

Delete the `LivingWeather` folder (and any optional preset/addon
folder) from your `Mods` directory. The patch loads at game startup and
writes nothing to disk: vanilla weather is fully restored and save
worlds are unaffected.

## Optional presets (separate downloads)

- **Stormy preset** - heavier rain (24+16%) and rotation-reachable
  storms (16%): install `LivingWeather-Stormy` INSTEAD OF this modlet,
  never together with it.
- **Longer storms (experimental)** - the separate addon zip above.
