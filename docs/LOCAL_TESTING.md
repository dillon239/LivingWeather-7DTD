# Local Testing Handoff — Living Weather v0.1.0 (Windows)

Status: FEATURE-FROZEN at tag `v0.1.0-freeze`. The only action this
document asks of you is testing; do not retune values until testing is
done. Nexus publication is on hold.

The test build: the release asset `LivingWeather-v0.1.0.zip`
SHA-256: `87f2572ad6e0ce2a9b0a4aa5dcd7ea3122f5cbdac43d453fc113625f77529b28`

Verify the copy after transfer (Command Prompt or PowerShell):

```
certutil -hashfile LivingWeather-v0.1.0.zip SHA256
```

Compare with the value above (certutil is built into Windows; do this in
the folder where the zip downloaded).

## 1. Exact Windows installation steps

Assumes default Steam install location. Adjust if you installed Steam or
the game elsewhere.

1. Unzip `LivingWeather-v0.1.0.zip` (right-click → Extract All is fine).
2. You then have a folder named `LivingWeather`. If the zip extractor
   wrapped it in an extra folder, keep the inner `LivingWeather` folder.
3. Move it so that the final paths are exactly:

```
C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Mods\LivingWeather\ModInfo.xml
C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Mods\LivingWeather\Config\biomes.xml
```

If the `Mods` folder does not exist yet, create it inside
`...\7 Days To Die\` (not inside `Data`; not one level deeper).

Notes:
- Windows Explorer hides `Program Files` names? Unzip anywhere friendly
  (Downloads, Desktop), then move the folder over.
- Alternatively supported: `%APPDATA%\7DaysToDie\Mods\` (paste that path
  into Explorer's address bar).
- Install ONLY the Atmospheric preset for this test round. Do not add
  the Stormy or StormDuration folders yet, and remove any other weather
  mods first.

## 2. Verifying the mod loaded (30 seconds)

1. Launch the game and load/create any world.
2. Press **F1** to open the console.
3. The start-up log lists loaded mods — you should see
   `Living weather` (it also appears in the main menu's mod list).
4. Check the same console for any red error line mentioning
   `biomes.xml` or paths inside `Mods/`. Red lines = failure; see §5.
5. Stronger check (after loading a world): in the console run

```
exportcurrentconfigs
```

then inspect

```
%APPDATA%\7DaysToDie\ConfigsDump\Configs\biomes.xml
```

In the `pine_forest` biome the weather groups must read:
default 60, fog 5, rainlight 20, rainheavy 10, storm 5 (stormbuild,
bloodMoon and twitch_* groups still 0). This is the authoritative
confirmation that the patch applied.

## 3. Short in-game weather testing checklist

Suggested session: new test world, creative/noclip acceptable, but no
other mods. Day 1 weather is protective vanilla behavior — judge from
Day 2 onward (recommend jumping ahead with the "Time set" approach or
playing through several days).

- [ ] Day 2+ Daytime in pine_forest: observe rain starting at least
      once per 2–3 days (rotation weight ≈ 35% per change under the
      Atmospheric preset; vanilla reference was ≈ 10%).
- [ ] Observe at least one storm instance in pine_forest across the
      session (rotation-selected 5% + dynamic-storm scheduling).
      Note whether storms feel doubled-up or excessive (§6 rollback is
      ready if so).
- [ ] Clear weather still occurs regularly (60% default + 5% fog
      weight) — you should NOT be permanently soaked.
- [ ] Visit/teleport to desert and snow: weather there must match
      vanilla behavior (desert sandstorm visuals, snow weather, etc.).
- [ ] burnt_forest: same check (has its own rain values in vanilla).
- [ ] Confirm no zombie/loot/crafting anomalies (inventory full trip,
      a simple quest or POI clear): the mod touches only weather.
- [ ] Performance feels normal (FPS comparable to before).
- [ ] Note the game build/version tested (bottom of main menu or
      console).

Record observations (even negatives) — they feed the TEST_REPORT and
future tuning decisions.

## 4. Collecting logs if something fails

The main startup log (auto-rotated by date on newer builds):

```
%APPDATA%\7DaysToDie\output_log.txt
%APPDATA%\7DaysToDie\logs\*.txt
```

(Open Explorer and paste `%APPDATA%\7DaysToDie` into the address bar.)

When reporting failure, attach the LONGEST/most recent file there plus:
- exact game build number,
- a console (F1) screenshot or transcription of the loaded-mod lines
  and any red XML error,
- whether the ConfigsDump from §2 exists/has old or new values.

Common failure patterns:
- Mod not listed at all → wrong nesting (must be
  `Mods\LivingWeather\ModInfo.xml`, no double folder) or ModInfo lost.
- Red lines naming biomes.xml → structure mismatch: stop, do not tune;
  run the validator (§5) and send me the output.
- Weather never changes → confirm you are judging from Day 2+ and that
  no other weather mod is installed (alphabetical load order: the LAST
  patcher wins).

## 5. Windows commands to validate your local biomes.xml (before/after any failure)

One-time prerequisite: Python 3.8+ (python.org installer; tick "Add
python.exe to PATH" or use the built-in `py` launcher).

In Command Prompt (adjust the first path if your Steam library is
elsewhere; use the folder where this repository is checked out):

```
cd /d %USERPROFILE%\Downloads\LivingWeather-7DTD
copy "C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Data\Config\biomes.xml" tests\vanilla\biomes.xml
py tools\validate_mod.py
```

PowerShell equivalent:

```
Copy-Item "C:\Program Files (x86)\Steam\steamapps\common\7 Days To Die\Data\Config\biomes.xml" tests\vanilla\biomes.xml
py tools\validate_mod.py
```

Expected: all structure checks PASS and the simulated change table
prints. Any FAIL names the exact xpath/target — send that output over
before launching the game. Your vanilla copy is only read (patches are
simulated in memory) and must never be committed or redistributed.

## 6. Easy rollback procedure

The mod never writes to game files and lives purely in load-time
patching:

1. **Full uninstall / restore vanilla weather:** delete the folder
   `...\7 Days To Die\Mods\LivingWeather` (drag to Recycle Bin —
   recoverable). Restart the game. Done; save worlds are untouched and
   playable.
2. **Partial rollback (storms feel too frequent):** open
   `Mods\LivingWeather\Config\biomes.xml` in Notepad and change the
   storm line's value from `5` to `0` — this disables only the
   rotation-added storms and returns to vanilla dynamic-storm behavior
   while keeping the rain boost. Re-run the validator after such an
   edit if you want the numbers re-checked (it tolerates and reports
   the resulting probability distribution honestly).
3. If a game update lands and the mod warns at startup, uninstall
   (§6.1) first and bring the log to the next dev session — do not
   keep patching on top of a changed schema.
