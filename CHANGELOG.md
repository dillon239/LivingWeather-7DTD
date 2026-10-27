# Changelog

## v0.1.0-alpha (2026-10-27) — first public GitHub experimental release

- Community-testing pre-release of the frozen Atmospheric preset
  (gameplay files identical to tag `v0.1.0-freeze`).
- Public release documentation: experimental-prototype warning,
  Windows installation/verification instructions, known limitations,
  community issue templates (Bug Report, Weather Feedback).
- Stormy preset and the experimental StormDuration addon are NOT part
  of this release distribution.
- No gameplay changes. Nexus Mods publication deliberately withheld.

## v0.1.0 (2026-10-27) — initial internal release

### Corrected against the version-verified 3.4.0 reference (same day)

A version-self-verified public reference copy of biomes.xml for 3.4.0
(7D2D Modding Wiki, `Biomes.xml/Raw_file`) became available and was
adopted as the validation target (kept locally, never shipped):

- **Retargeted all patches to biome `pine_forest`**: the 1.0-era
  biome name `forest` no longer exists in the current schema; the old
  targets would have matched zero nodes in a real 3.4.0 install.
- **Rain groups**: vanilla splits rain into `rainlight` (6) and
  `rainheavy` (4) — presets updated accordingly (no `rain` group).
- **Storm lever documented honestly**: vanilla storm group prob is 0
  (storms come from the dynamic storm system, global Storm Frequency
  option). Presets make the storm group rotation-selectable (Atmospheric
  5%, Stormy 16%) via the documented per-group probability mechanism,
  with an explicit interpretation-risk note and one-line rollback.
- **Duration verified** from the vanilla file header (game-days,
  default 3): storm 1.1 → 1.6 via `set`; rainlight/rainheavy 3 → 4 via
  `setattribute`. `delay` untouched.
- Validator updated: verified 11-entry group set, event-driven groups
  must stay 0, `set`-requires-existing-attribute semantics, new
  negative case; selftest 154/154; full pass 174/174 against the
  reference.

### Added
- `LivingWeather` modlet (Atmospheric preset) for the pine_forest
  (forest-generation) biome:
  - default 60 / fog 5 / rainlight 20 / rainheavy 10 / storm 5.
  - Optional Stormy preset modlet: 40 / 4 / 24 / 16 / 16.
- Experimental `LivingWeather-StormDuration` addon: extends storm duration
  1.1 → 1.6 and rainlight/rainheavy 3 → 4 (verified semantics).
- Optional `LivingWeather-Stormy` preset modlet (install INSTEAD OF the
  Atmospheric modlet, never together).
- `tools/validate_mod.py`: automated checks for XML well-formedness,
  ModInfo.xml structure, patch command syntax, xpath presence/scope,
  simulated application against a biomes.xml copy (unique matches,
  post-patch probability sum = 100, range 0–100, no other biome
  modified, diff-scope limited to forest weather attributes),
  experimental-addon gating, distribution-zip layout checks, and a
  self-test with negative cases.
- `tools/package.py`: reproducible packaging + SHA256SUMS.
- Documentation: installation/uninstallation, compatibility, test
  report, research notes, Nexus listing draft.

### Design decisions
- All four forest weather-entry `prob` values are set explicitly so the
  biome's probability total is always 100, making the mod independent
  of (unpublished) vanilla numbers for your build.
- XPath patches use the root-agnostic `//biome[...]` descendant search
  documented by the 7D2D modding wiki (v3.2.0-era), so the patch does
  not hardcode a root element name that changed across game versions.
- No `duration`/`delay` (V2.0 dynamic-storm parameters) values are
  invented or guessed: the duration addon is gated behind validation
  against your own vanilla file, and `delay` is left untouched entirely.
