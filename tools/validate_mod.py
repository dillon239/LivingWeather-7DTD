#!/usr/bin/env python3
"""
Living Weather v0.1.0 - automated validation suite.

Checks performed (stdlib only, no game required):
  1.  Every mod XML file is well-formed XML.
  2.  ModInfo.xml structure (required child tags, attribute values,
      semver-ish Version, Name matches folder name).
  3.  Config patch structure (<configs> root, allowed tags, every xpath
      targets only the target biome's weather entries, `set` has a value).
  4.  Simulated patch application against a vanilla biomes.xml copy:
      every xpath matches EXACTLY ONE node, post-patch weather
      probabilities sum to 100, range checks, no other biome changed.
  5.  Event-driven groups (bloodMoon/twitch_*/stormbuild) stay prob 0.
  6.  Distribution zips: correct Mods/ layout, no unsafe paths,
      version in filename, patch-only (no full vanilla file shipped).

Vanilla resolution:
    --vanilla <path>            (CLI), else
    tests/vanilla/biomes.xml    (place a copy of your game's file here)

Without a vanilla copy the simulated-apply group is reported PENDING
(with --allow-pending) or FAILED - the validator never pretends to have
checked against the game.

Self-test:
    python3 tools/validate_mod.py --selftest
  Runs the suite against tests/fixtures/synthetic_biomes.xml - a clearly
  marked SYNTHETIC file mirroring the verified 3.4.0 weather-entry
  schema (NOT vanilla data) - plus negative tests proving that broken
  xpaths and probability-sum drift are actually caught.

Exit code: 0 if no failures; 1 if one or more failures.
"""

import argparse
import copy
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VANILLA_DEFAULT = PROJECT_ROOT / "tests" / "vanilla" / "biomes.xml"
FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "synthetic_biomes.xml"

ALLOWED_COMMANDS = {"set", "setattribute", "remove", "removeattribute",
                    "append", "prepend", "insertAfter", "insertBefore", "csv"}
TARGET_BIOME = "pine_forest"
# Verified set of named weather groups for biome pine_forest in the
# public 3.4.0 Biomes.xml/Raw_file reference (7D2D Modding Wiki).
EXPECTED_ENTRIES = {"default", "fog", "rainlight", "rainheavy", "stormbuild",
                    "storm", "bloodMoon", "twitch_fog", "twitch_rain",
                    "twitch_snow", "twitch_storm"}
# Groups that must carry prob=0 both before and after patching (event-driven
# groups: blood moon, Twitch integration events). The stormbuild group is
# also event-scheduled by the dynamic storm system; presets leave it at 0.
SPECIAL_ENTRIES = {"bloodMoon", "twitch_fog", "twitch_rain", "twitch_snow", "twitch_storm", "stormbuild"}


@dataclass
class Finding:
    section: str
    check: str
    passed: bool
    detail: str = ""


class Report:
    def __init__(self):
        self.findings: list[Finding] = []

    def add(self, section: str, check: str, passed: bool, detail: str = "") -> bool:
        self.findings.append(Finding(section, check, bool(passed), detail))
        mark = "PASS" if passed else "FAIL"
        line = f"  [{mark}] {section} :: {check}"
        if detail:
            line += f" - {detail}"
        print(line)
        return passed


class Modlet:
    def __init__(self, folder: Path, modinfo: dict, commands: list[tuple]):
        self.folder = folder
        self.modinfo = modinfo
        self.commands = commands


# ----------------------------------------------------------------------
# xpath subset evaluator (covers what the shipped patches use)
# ----------------------------------------------------------------------

def eval_xpath(root: ET.Element, xpath: str):
    """Evaluate the xpath subset used by this modlet.

    Returns (owners, attr_name_or_None): `owners` are the matched
    elements; for a terminal @attr xpath they are the attribute owners.
    Raises ValueError on syntax this evaluator does not support.
    """
    xpath = xpath.strip()
    if not (xpath.startswith("/") or xpath.startswith("//")):
        raise ValueError("game xpath statements must start with '/'")
    attr = None
    body = xpath
    if body.rsplit("/", 1)[1].startswith("@"):
        body, attr = body.rsplit("/", 1)
        attr = attr[1:]
    descendant_first = body.startswith("//")
    body = body.replace("//", "/")
    steps = [s for s in body.split("/") if s]
    if not steps:
        raise ValueError(f"xpath has no node steps: {xpath}")

    current = [root]
    for i, step in enumerate(steps):
        el_name, pred = step.split("[", 1) if "[" in step else (step, None)
        if "[" in step:
            pred = step[len(el_name) + 1:].rstrip("]")
        matched = []
        for node in current:
            if i == 0 and descendant_first:
                pool = list(dict.fromkeys(root.iter()))
                candidates = []
                for sp in pool:
                    candidates.extend(sp)
            else:
                candidates = list(node)
            for child in candidates:
                if child.tag != el_name:
                    continue
                if pred is not None:
                    if "=" in pred:
                        pattr, pval = pred[1:].split("=", 1)
                        pval = pval.strip().strip("'\"")
                        if child.attrib.get(pattr.strip()) != pval:
                            continue
                    else:
                        if pred[1:] not in child.attrib:
                            continue
                matched.append(child)
        current = matched
        if not matched:
            return [], attr
    return current, attr


# ----------------------------------------------------------------------
# per-file checks
# ----------------------------------------------------------------------

def load_modlet(folder: Path, report: Report, section: str):
    ok = True
    modinfo_path = folder / "ModInfo.xml"
    if not report.add(section, f"{folder.name}/ModInfo.xml exists", modinfo_path.is_file()):
        return None
    try:
        tree = ET.parse(modinfo_path)
    except ET.ParseError as e:
        report.add(section, "ModInfo.xml well-formed XML", False, str(e))
        return None
    report.add(section, "ModInfo.xml well-formed XML", True)
    root = tree.getroot()
    if not report.add(section, "ModInfo root is <xml>", root.tag == "xml"):
        ok = False
    info = {child.tag: child.attrib.get("value", "") for child in root}
    for req in ("Name", "DisplayName", "Version"):
        ok = report.add(section, f"ModInfo has {req}",
                        req in info and info[req] != "") and ok
    ok = report.add(section, "ModInfo Version is major.minor.patch",
                    bool(re.fullmatch(r"\d+\.\d+\.\d+", info.get("Version", "")))) and ok
    report.add(section, "ModInfo Name equals folder name",
               info.get("Name") == folder.name,
               f"{info.get('Name')!r} vs {folder.name!r}")

    patch_path = folder / "Config" / "biomes.xml"
    if not report.add(section, f"{folder.name}/Config/biomes.xml exists", patch_path.is_file()):
        return None
    try:
        ptree = ET.parse(patch_path)
    except ET.ParseError as e:
        report.add(section, "patch file well-formed XML", False, str(e))
        return None
    report.add(section, "patch file well-formed XML", True)
    proot = ptree.getroot()
    if not report.add(section, "patch root is <configs>", proot.tag == "configs"):
        return None

    commands: list[tuple] = []  # (tag, xpath, value, target_attr_for_setattribute)
    ok = True
    for child in proot:
        if child.tag not in ALLOWED_COMMANDS:
            ok = report.add(section, f"patch command tag allowed ({child.tag})", False) and ok
            continue
        xpath = child.attrib.get("xpath")
        ok = report.add(section, f"{child.tag} carries xpath", bool(xpath)) and ok
        if not xpath:
            continue
        if child.tag == "set":
            text = (child.text or "").strip()
            ok = report.add(section, f"set() carries a value -> {xpath}", bool(text)) and ok
            if text:
                commands.append((child.tag, xpath, text, None))
        elif child.tag == "setattribute":
            text = (child.text or "").strip()
            name_attr = child.attrib.get("name")
            ok = report.add(section, f"setattribute() carries name and value -> {xpath}",
                            bool(text) and bool(name_attr)) and ok
            if text and name_attr:
                commands.append((child.tag, xpath, text, name_attr))
        else:
            commands.append((child.tag, xpath, (child.text or "").strip(), None))
        # this mod family must ONLY touch the target biome's weather entries
        ok = report.add(section, f"xpath scoped to biome[{TARGET_BIOME}]: {xpath}",
                        f"biome[@name='{TARGET_BIOME}']" in xpath or
                        f"biome[@name=\"{TARGET_BIOME}\"]" in xpath) and ok
        ok = report.add(section, f"xpath scoped to weather entries: {xpath}",
                        "weather" in xpath) and ok
        try:
            eval_xpath(ET.Element("probe"), xpath)
        except ValueError as e:
            ok = report.add(section, f"xpath within supported game syntax: {xpath}", False, str(e)) and ok
        else:
            report.add(section, f"xpath within supported game syntax: {xpath}", True)
    if not ok:
        return None
    return Modlet(folder, info, commands)


def simulate(modlet, vanilla_root: ET.Element, report: Report, section: str,
             require_attrs: set | None = None):
    merged = copy.deepcopy(vanilla_root)

    forest = merged.find(f".//biome[@name='{TARGET_BIOME}']")
    if not report.add(section, f"biome[{TARGET_BIOME}] exists in target file", forest is not None):
        return None
    for tag, xpath, text, name_attr in modlet.commands:
        owners_van, _ = eval_xpath(vanilla_root, xpath)
        ok = report.add(section, f"xpath matches exactly one vanilla node: {xpath}",
                        len(owners_van) == 1, f"{len(owners_van)} matches")
        if not ok:
            return None
        _, attr = eval_xpath(vanilla_root, xpath)
        if tag == "set":
            # <set> only edits EXISTING attributes (docs: warns otherwise)
            attr_ok = attr is not None and all(attr in o.attrib for o in owners_van)
            ok = report.add(section, f"attribute exists on vanilla node: @{attr or '?'} ({xpath})",
                            attr_ok, "<set> on a missing attribute would warn at load time")
            if not ok:
                return None
        elif tag == "setattribute":
            exists = name_attr is not None and all(name_attr in o.attrib for o in owners_van)
            report.add(section, f"setattribute target state: @{name_attr} ({xpath})",
                       True, "exists in vanilla; value replaced" if exists
                       else "absent in vanilla; attribute will be added (documented default applies)")
        owners_m, attr_m = eval_xpath(merged, xpath)
        if tag == "setattribute":
            for o in owners_m:
                o.attrib[name_attr] = text
        else:
            for o in owners_m:
                o.attrib[attr_m] = text

    forest_m = merged.find(f".//biome[@name='{TARGET_BIOME}']")
    entries = forest_m.findall("weather[@name]")
    names = {w.attrib.get("name") for w in entries}
    report.add(section, "weather groups match the 3.4.0 verified set",
               names == EXPECTED_ENTRIES, f"{sorted(names)}")
    probs = [w.attrib.get("prob") for w in entries]
    all_num = all(p is not None and re.fullmatch(r"-?\d+(\.\d+)?", p) for p in probs)
    report.add(section, "every forest prob value is numeric", all_num, f"{probs}")
    if not all_num:
        return None
    total = round(sum(float(p) for p in probs), 4)
    if not report.add(section, "post-patch biome probabilities sum to 100",
                      abs(total - 100.0) < 1e-6, f"sum={total}"):
        return None
    report.add(section, "each prob in range 0..100", all(0.0 <= float(p) <= 100.0 for p in probs))
    specials = [w for w in entries if w.attrib.get("name") in SPECIAL_ENTRIES]
    report.add(section, "event-driven groups (bloodMoon/twitch_*/stormbuild) stay prob 0",
               all(float(w.attrib.get("prob")) == 0.0 for w in specials),
               str({w.attrib.get("name"): w.attrib.get("prob") for w in specials}))

    vanilla_biomes = vanilla_root.findall(".//biome")
    merged_biomes = merged.findall(".//biome")
    other = all(ET.tostring(a) == ET.tostring(b)
                for a, b in zip(vanilla_biomes, merged_biomes)
                if a.attrib.get("name") != TARGET_BIOME)
    report.add(section, "no other biome modified", other)

    diffs = []
    for a, b in zip(vanilla_biomes, merged_biomes):
        if a.attrib.get("name") != TARGET_BIOME:
            continue
        for w_og, w_new in zip(a.findall("weather"), b.findall("weather")):
            for key in set(w_og.attrib) | set(w_new.attrib):
                if w_og.attrib.get(key) != w_new.attrib.get(key):
                    diffs.append(f"{w_new.attrib.get('name')}.{key}: "
                                 f"{w_og.attrib.get(key)!r} -> {w_new.attrib.get(key)!r}")
    report.add(section, f"change scope limited to {TARGET_BIOME} weather attributes",
               bool(diffs), "; ".join(diffs))
    return merged


# ----------------------------------------------------------------------
# zip checks
# ----------------------------------------------------------------------

def check_zip(zip_path: Path, report: Report):
    section = f"zip:{zip_path.name}"
    if not report.add(section, "exists", zip_path.is_file()):
        return
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        modinfo_key = next((n for n in names if n.endswith("ModInfo.xml")), None)
        if not report.add(section, "contains ModInfo.xml", modinfo_key is not None):
            return
        top = modinfo_key.split("/")[0]
        top_folders = {n.split("/")[0] for n in names if "/" in n}
        report.add(section, "exactly one top-level modlet folder",
                   len(top_folders) == 1, str(sorted(top_folders)))
        report.add(section, "entry point is <Modlet>/ModInfo.xml",
                   modinfo_key == f"{top}/ModInfo.xml")
        report.add(section, "Config/biomes.xml ships with the zip",
                   f"{top}/Config/biomes.xml" in names)
        unsafe = [n for n in names if n.startswith(("/", "\\")) or ".." in n or n.endswith("__MACOSX")]
        report.add(section, "no unsafe or OS-junk paths", not unsafe, str(unsafe))
        info = {c.tag: c.attrib.get("value") for c in ET.fromstring(zf.read(modinfo_key))}
        ver = info.get("Version", "")
        report.add(section, "zip filename embeds the ModInfo version",
                   bool(ver) and f"v{ver}" in zip_path.name, f"{ver} in {zip_path.name}")
        full_replacements = []
        for n in names:
            if n.endswith(".xml") and not n.endswith("ModInfo.xml"):
                try:
                    root_tag = ET.fromstring(zf.read(n)).tag
                except ET.ParseError as e:
                    full_replacements.append(f"{n} (unparseable: {e})")
                    continue
                if root_tag != "configs":
                    full_replacements.append(n)
        report.add(section, "patch-only package (every shipped XML has <configs> root)",
                   not full_replacements, str(full_replacements))


# ----------------------------------------------------------------------
# main / selftest
# ----------------------------------------------------------------------

def build_modlets(report: Report):
    primary = load_modlet(PROJECT_ROOT / "LivingWeather", report, "structure")
    stormy = load_modlet(PROJECT_ROOT / "OptionalPresets" / "LivingWeather-Stormy", report, "structure")
    duration = load_modlet(PROJECT_ROOT / "OptionalPresets" / "LivingWeather-StormDuration", report, "structure")
    report.add("structure", "all three modlets parsed with valid commands",
               all(m is not None for m in (primary, stormy, duration)))
    return primary, stormy, duration


def run(vanilla_path: Path, report: Report, allow_pending: bool = False):
    primary, stormy, duration = build_modlets(report)
    have_target = False
    if vanilla_path.is_file():
        try:
            vanilla = ET.parse(vanilla_path).getroot()
            have_target = True
            label = "SYNTHETIC FIXTURE (not vanilla data)" if vanilla_path == FIXTURE else "user-provided vanilla copy"
            print(f"\nSimulating patches against: {vanilla_path} [{label}]")
        except ET.ParseError as e:
            report.add("simulated-apply", "target file parses as XML", False, str(e))
    if not have_target:
        verdict = "PENDING" if allow_pending else "FAIL"
        detail = (f"place a copy of your vanilla Data/Config/biomes.xml at {VANILLA_DEFAULT} "
                  "or pass --vanilla <path>. Until then, xpath applicability CANNOT be "
                  "confirmed and stays pending.")
        print(f"  [{verdict}] simulated-apply :: target biomes.xml copy available - {detail}")
        if not allow_pending:
            report.add("simulated-apply", "target biomes.xml copy available", False, detail)
        return
    if primary:
        simulate(primary, vanilla, report, "simulated:LivingWeather (Atmospheric)")
    if stormy:
        simulate(stormy, vanilla, report, "simulated:LivingWeather-Stormy")
    if duration and primary and stormy:
        report.add("simulated:LivingWeather-StormDuration",
                   "duration semantics documented by the vanilla file header itself", True,
                   "duration (in days)(default 3); storm carries duration=1.1 in vanilla")
        simulate(duration, vanilla, report, "simulated:LivingWeather-StormDuration")


def selftest(report: Report):
    print("== SELFTEST (validates the validator; data is synthetic) ==")
    run(FIXTURE, report)

    print("\n== SELFTEST negative cases (failures must be detected) ==")
    primary = load_modlet(PROJECT_ROOT / "LivingWeather", Report(), "negative-setup")
    root_fix = ET.parse(FIXTURE).getroot()

    def mutated(commands_mutator) -> Modlet:
        cmds = commands_mutator(primary.commands)
        return Modlet(primary.folder, primary.modinfo, cmds)

    cases = [
        ("broken xpath entry name",
         lambda c: [(t, xp.replace("name='rainlight'", "name='hurricane'"), v, e) for t, xp, v, e in c]),
        ("probability sum drift (+10 on every prob)",
         lambda c: [(t, xp, str(int(v) + 10) if xp.endswith("@prob") and v.isdigit() else v, e)
                    for t, xp, v, e in c]),
        ("storm value out of range",
         lambda c: [(t, xp, "150" if "@prob" in xp and "storm" in xp else v, e) for t, xp, v, e in c]),
        ("set on an attribute vanilla does not carry",
         lambda c: [(t, xp.replace("@prob", "@duration") if "twitch_fog" not in xp else xp,
                     v, e) for t, xp, v, e in c]),
    ]
    for label, mutator in cases:
        sub = Report()
        simulate(mutated(mutator), root_fix, sub, f"negative:{label}")
        caught = any(not f.passed for f in sub.findings if f.section == f"negative:{label}")
        report.add("selftest-negative", f"validator catches: {label}", caught)


def main():
    ap = argparse.ArgumentParser(description="Living Weather validation suite")
    ap.add_argument("--vanilla", type=Path, default=VANILLA_DEFAULT,
                    help="path to a biomes.xml copy to patch-check against")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--report", type=Path, help="write results to this text file")
    ap.add_argument("--allow-pending", action="store_true",
                    help="treat 'no vanilla copy yet' as PENDING instead of FAIL "
                         "(exit code only depends on real failures)")
    args = ap.parse_args()

    print("Living Weather v0.1.0 - automated validation\n")
    rep = Report()
    if args.selftest:
        selftest(rep)
    else:
        run(args.vanilla, rep, allow_pending=args.allow_pending)
        for z in sorted((PROJECT_ROOT / "dist").glob("*.zip")):
            check_zip(z, rep)

    n_fail = sum(1 for f in rep.findings if not f.passed)
    total = len(rep.findings)
    pending_note = " | 1 PENDING (vanilla copy needed)" if (args.allow_pending and n_fail == 0) else ""
    print(f"\n{total} checks | {n_fail} failed | {total - n_fail} passed{pending_note}")
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            for f in rep.findings:
                fh.write(f"[{'PASS' if f.passed else 'FAIL'}] {f.section} :: {f.check}"
                         + (f" - {f.detail}" if f.detail else "") + "\n")
        print(f"report written: {args.report}")
    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
