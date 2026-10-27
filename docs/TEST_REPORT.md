# Test Report — Living Weather v0.1.0

## 0. Version-verified update (development day, after a verified schema reference arrived)

A public reference copy of the game's `biomes.xml` self-verified as
**3.4.0** (7D2D Modding Wiki, `Biomes.xml/Raw_file`, page banner
"Current. Verified for version 3.4.0"; corroborated against the
official 7daystodie.com news timeline listing V3.x stable releases)
was used as the validation target (kept locally outside the
repository; gitignored).

Analysis of the REAL 3.4.0 file changed the design (all facts in
docs/RESEARCH.md):

- The biome named `forest` no longer exists; the forest of this
  generation is `pine_forest` → **all patches retargeted to
  pine_forest**. The old patch targets would have matched ZERO nodes
  in a real 3.4.0 install — this iterate-on-reference step is exactly
  why the validator exists.
- Rain is split into `rainlight` (6) + `rainheavy` (4); there is no
  `rain` group. Compositions updated.
- Storm group carries prob=0: vanilla rotation never weight-selects
  storms; dynamic storms are scheduled separately (global Storm
  Frequency option). The mod makes the storm group rotation-selectable
  (5% Atmospheric / 16% Stormy) — the only XML-only biome-local storm
  lever, flagged as an interpretation risk with a one-line rollback.
- `duration` semantics verified from the file's own header comment:
  game-days, default 3. Verified vanilla values in pine_forest:
  default 6, stormbuild .2, storm 1.1 (delay="26,36" untouched).
  Experimental addon updated: storm 1.1 -> 1.6 via `set` (attribute
  exists — verified), rainlight/rainheavy 3 -> 4 via `setattribute`
  (documented default; attribute added).

## 1. What was checked and how (final state)

Automated checks in `tools/validate_mod.py`; raw outputs regenerate
deterministically at any time with the commands below (they are not
committed; they are tool output, not documentation).

| # | Check group | Result |
|---|-------------|--------|
| 1 | XML well-formedness of every mod file | PASS |
| 2 | ModInfo.xml structure (root children, required fields, semver Version, Name == folder) | PASS (all 3 modlets) |
| 3 | Patch structure (<configs> root, documented commands, valued `set`s, xpaths scoped to biome[pine_forest] weather groups, game-syntax subset) | PASS |
| 4 | Simulated application **against the 3.4.0 reference**: every xpath matches the target exactly once; weather groups match the verified 11-entry set; post-patch probabilities sum to exactly 100; all in 0..100; event-driven groups (bloodMoon/twitch_*/stormbuild) stay 0; **no other biome modified** (byte compare); diff scope limited to pine_forest weather attrs | PASS |
| 5 | Verified change tables: Atmospheric default 83→60, fog 7→5, rainlight 6→20, rainheavy 4→10, storm 0→5; Stormy 83→40, 7→4, 6→24, 4→16, 0→16; Duration addon rainlight/rainheavy duration None→4, storm 1.1→1.6 | PASS |
| 6 | zip layout (single modlet folder, entry points, no unsafe paths, version in filename, every shipped XML has <configs> root — no full-file replacements) | PASS for all 3 zips |
| 7 | Validator self-test incl. 4 negative cases (broken group name, probability-sum drift, out-of-range value, `set` on an attribute vanilla doesn't carry) | 154 checks, 0 failed |

Final deliverable pass: **174 checks, 0 failed**.

Reproduce locally: `python3 tools/validate_mod.py` (needs a vanilla or
reference copy at `tests/vanilla/biomes.xml`), and
`python3 tools/validate_mod.py --selftest` (uses the committed
synthetic fixture only).

## 2. Bugs found and fixed during development (evidence the suite is real)

1. Terminal-attribute bug in the xpath evaluator (phantom `@prob` key) —
   exposed by negative cases; fixed.
2. patch-only zip check mis-parsed the XML declaration — fixed by
   parsing each shipped XML and requiring a `<configs>` root.
3. **Schema-targeting exposure found by the 3.4.0 reference**: the
   original `forest`-biome targets matched nothing in the current
   schema; retargeted to `pine_forest` with the real group set. This is
   formally a mod bug fixed before release — correct by construction
   now, since the validator refuses zero-match or ambiguous-match
   targets.

## 3. What these results prove — and what they do NOT

Proven:
- The mods' XML structure matches the documented current modlet system
  and the patch targets/scope are correct for the version-verified
  3.4.0 schema, including duration semantics from the file header.
- Packaging is valid for direct extraction into Mods/.

NOT proven (deliberately not claimed anywhere):
- **Compatibility with a local installation remains unverified**
  (different build, local modifications, other weather overhauls).
  Accepted path: run the validator against a copy of your own
  `Data/Config/biomes.xml`; then in-game log/console verification per
  docs/LOCAL_TESTING.md.
- In-game observable weather changes and the interaction between
  rotation-selected and dynamically scheduled storms (documented,
  roll-back plan shipped).

## 4. Pending acceptance checklist (machine with the game)

1. `cp "Data/Config/biomes.xml" tests/vanilla/biomes.xml`, run
   `python3 tools/validate_mod.py` → must report 0 failed; record the
   ORIGINAL vs NEW table it prints.
2. Install `LivingWeather-v0.1.0.zip` into `Mods/`, launch, check
   console/log for load confirmation and absence of red biomes.xml
   errors.
3. Gameplay observation over several days/nights in pine_forest:
   rain/storm frequency vs expectation (~35% precipitation-group
   weight Atmospheric; storms may now also appear via rotation in
   addition to dynamic storms); verify other biomes unchanged; verify
   Day-1 protected start still applies.
4. If storms feel excessive or doubled-up, set the storm group's prob
   back to 0 (single edit) or swap to the Stormy values as preferred.
5. Optional: `exportcurrentconfigs` dump → verify merged values.
6. Uninstall (delete folder), relaunch, verify zero residual warnings.

## 5. Clean install / removal reasoning

Load-time-only XPath patch; never writes game files; removal restores
vanilla exactly; save files are untouched and arbitrarily compatible.
