# Research notes — sources and evidence

Everything unverifiable is treated as unknown, not guessed. Compiled
2026-10-27; updated the same day with a version-verified schema
reference supplied for Living Weather development.

## Primary public reference (governs v0.1)

**7D2D Modding Wiki — `Biomes.xml/Raw_file`**, page-self-declared
"Current. Verified for version 3.4.0":
https://7d2dmodding.wiki.gg/wiki/Biomes.xml/Raw_file

A copy (105 KB) was fetched for local testing only:
`tests/vanilla/v34_reference_raw.txt` (raw wikitext) and
`tests/vanilla/biomes.xml` (extracted XML used as the validation
target). These are The Fun Pimps' copyrighted game data, mirrored by
the wiki expressly as reference; they are gitignored and are never
shipped in the mod zips or this repository.

### Version verification

- The page carries a version banner "Current. Verified for version
  3.4.0" plus `{{VersionNotice|version=3.4.0|status=current}}`.
- Independent corroboration of the 3.4.0 stable timeline: official
  site news (`7daystodie.com` — V3.0 "Dead Hot Summer" released 2026,
  posts list V3.2.0/V3.3.0/V3.4.0 Stable; SteamDB patch-feed shows the
  2026 V3.3.0 stable).

### Verified schema facts from that reference (these govern the mod)

1. Root/structure: `<worldgeneration><biomes><biome …>`. Biomes
   present: pine_forest, burnt_forest, desert, snow, wasteland,
   underwater (+ biomemap ids for water/radiated/caveFloor/caveCeiling).
   **There is no biome named `forest` in the 3.4.0 file** — the
   community "forest" of earlier eras is the `pine_forest` biome.
2. Biome weather groups (pine_forest vanilla, verified):
   default prob=83 duration="6"; fog 7; rainlight 6; rainheavy 4;
   stormbuild 0 duration=".2"; storm 0 duration="1.1" delay="26,36";
   bloodMoon 0; twitch_fog/rain/snow/storm 0. Totals exactly 100.
   Groups use `range="x,y"` (or legacy min/max) child conditions.
3. Mechanics per the file's own header comment:
   - each group has "a probability for how often that group is chosen
     when weather decides to change and a duration (in days)(default 3)";
   - probabilities are normalized within the biome's groups (scale free);
   - biome weather sections act as constraints on the *global* weather
     state (the header frames the sections as restrictions for the
     global weather); Temperature adds to the global offset;
   - precipitation becomes visible from 30; rain requires sufficient
     cloud thickness.
4. Duration semantics: game-days; default 3; present on default (6),
   stormbuild (.2), storm (1.1) in pine_forest; rainlight/rainheavy
   carry NO duration attribute (the documented default applies).
   `delay="26,36"` exists on storm groups but its semantics are NOT
   documented — deliberately untouched by this mod.
5. Storm scheduling: storm probability is 0 in every biome group list —
   vanilla rotation does not weight-select storms; dynamic storms are
   scheduled separately (V2.0 release notes: global Storm Frequency
   option 0–500%, random frequency/duration, biome-specific storms):
   https://7daystodie.com/v2-0-storms-brewing-release-notes/

### Which changes can actually affect storm frequency / duration (verified lever analysis)

- **Frequency (rain):** raise the biome rotation weight of the
  rainlight/rainheavy groups (documented selection mechanism).
- **Frequency (storms):** the ONLY XML-only, biome-local lever is
  setting the storm group's prob > 0 so the biome rotation can select
  it. In-game interaction with the dynamic storm system is NOT yet
  observed (in-game testing pending) — documented as an interpretation
  risk with a one-line rollback (set storm back to 0).
- **Frequency (global, non-mod):** the Storm Frequency option is global
  (not biome-local); the mod cannot and does not touch it.
- **Duration:** the `duration` attribute on weather groups (documented
  in the vanilla header, in days). Extended by the gated experimental
  addon only: storm 1.1 -> 1.6 via `set` (attribute exists; verified),
  rainlight/rainheavy 3 -> 4 via `setattribute` (documented default 3).

## Explicitly NOT verified

- A live game install of any specific local build: nothing in the
  development workspace can run the game. **Compatibility with any
  user's local installation remains unverified until the mod is run in
  the game.** The validation script plus the log/console procedure in
  docs/LOCAL_TESTING.md is the accepted verification path.
- Exact runtime interaction between rotation-selected storms and
  dynamically scheduled storms (rising chapter above).
- `delay="26,36"` semantics.

## Historical sources (context only, NOT authoritative)

Older dumps (A20/A21-era GitHub mirrors, 2021/2024 forum threads) were
used earlier to learn schema history; they are NOT used as
authoritative: the wiki 3.4.0 reference overrules everything.
Contradictions found and corrected on retarget: biome `forest` (gone),
entry `rain` (split into rainlight/rainheavy), "prob must sum to 100"
(strict interpreter) vs "normalized totals" (file header; this mod
still keeps exactly 100), duration attribute presence and units.

## Existing weather mods / conflict landscape

- Big overhauls explicitly declare conflict with `biomes.xml` weather
  patches (e.g. Atmospheric Weather V3 on Nexus 10172).
- Pure visual mods (e.g. Rainstorm nexus 8518) are plausible stack
  candidates; untested by us.
- Mechanics: alphabetical modlet load order; last writer wins; missing
  targets log warnings (7D2D modding wiki XPath page, written for
  v3.2.0, whose command syntax `set/setattribute/...` and `//`
  descendant search the mod uses).

## Tooling facts used by the test suite

- No authoritative standalone 7DTD config validator exists; the
  validator behavior is emulated locally against the version-verified
  reference instead.
- In-game confirmation documented by the community: console
  `exportcurrentconfigs` writes merged configs to the ConfigsDump
  folder — kept in the testing checklist.
