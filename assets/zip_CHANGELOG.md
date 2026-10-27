# Living Weather - Changelog

## v0.1.0 - initial release (2026-10-27, version-validated against the 3.4.0 schema)

- Weather probability retune for the forest biome (pine_forest in
  recent builds) only:
  - default 60 / fog 5 / rainlight 20 / rainheavy 10 / storm 5
    (Atmospheric preset, installs by default).
  - Optional Stormy preset modlet: 40 / 4 / 24 / 16 / 16 (install
    INSTEAD OF, never together with, the Atmospheric one).
  - Vanilla 3.4.0 reference values: 83 / 7 / 6 / 4 / 0 (+ stormbuild,
    bloodMoon and twitch_* groups untouched at 0).
- Experimental `LivingWeather-StormDuration` addon: extends weather
  group durations using parameters documented in the vanilla file
  header (duration in game-days, default 3): storm 1.1 -> 1.6,
  rainlight/rainheavy 3 -> 4. `delay` untouched.
- XML patch modlet only (`<configs>` xpath `set`/`setattribute`
  patches); no game files overwritten, no new assets, no C#/Harmony.
- Automated validation suite included (tools/validate_mod.py): XML
  well-formedness, ModInfo structure, xpath targets, probability sum
  and range checks, event-group safety, no-unintended-biome-change
  diff, zip layout checks, plus a self-test with negative cases.
