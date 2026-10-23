#!/usr/bin/env python3
"""Verify recovered assets and documentation using only Python's standard library."""

import argparse
from datetime import date
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import zipfile


ROOT = Path(__file__).resolve().parents[1]


class AssetReferences(HTMLParser):
    """Collect local media/navigation references in README HTML and the player."""

    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attributes):
        self.references.extend(value for key, value in attributes
                               if key in {"src", "href", "poster"} and value)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tree_digest(entries):
    return digest("".join(name + "\t" + digest(data) + "\n"
                          for name, data in sorted(entries)).encode())


def sanitize(source_name, data):
    """Apply only the two documented credential substitutions; never log values."""
    if source_name == "OSS_CAM_TEST.ino":
        data = re.sub(rb'(const char\* ssid = )"[^"\r\n]*";',
                      rb'\1"YOUR_WIFI_SSID";', data)
        data = re.sub(rb'(const char\* password = )"[^"\r\n]*";',
                      rb'\1"YOUR_WIFI_PASSWORD";', data)
    elif source_name == "OV3660_Collect_Images_for_EdgeImpulse.ino":
        data = re.sub(rb'(#define WIFI_SSID )"[^"\r\n]*"',
                      rb'\1"YOUR_WIFI_SSID"', data)
        data = re.sub(rb'(#define WIFI_PASS )"[^"\r\n]*"',
                      rb'\1"YOUR_WIFI_PASSWORD"', data)
    return data


def check_media_manifest(relative_path, list_key, path_key, errors, optional=False):
    manifest = ROOT / relative_path
    if optional and not manifest.exists():
        return 0
    label = f"Media manifest {relative_path}"
    try:
        data = json.loads(manifest.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError):
        errors.append(f"{label}: cannot read valid JSON")
        return 0
    if not isinstance(data, dict) or not isinstance(data.get(list_key), list) or not data[list_key]:
        errors.append(f"{label}: expected a nonempty {list_key} list")
        return 0
    source_media = list_key == "files"
    if source_media:
        if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
            errors.append(f"{label}: unsupported schema version")
        try:
            date.fromisoformat(data.get("included_on"))
        except (TypeError, ValueError):
            errors.append(f"{label}: invalid inclusion date")
        for claim in ("successful_operation_claimed", "accuracy_claimed"):
            if data.get(claim) is not False:
                errors.append(f"{label}: {claim} must be false")
    seen = set()
    for index, item in enumerate(data[list_key], 1):
        entry = f"{label}, entry {index}"
        if not isinstance(item, dict):
            errors.append(f"{entry}: expected an object")
            continue
        value = item.get(path_key)
        if (not isinstance(value, str) or not value or "\\" in value or "\0" in value
                or PurePosixPath(value).is_absolute()
                or any(part in {"", ".", ".."} for part in value.split("/"))):
            errors.append(f"{entry}: expected a repository-relative asset path")
            continue
        path = ROOT / value
        if not path.resolve().is_relative_to(ROOT.resolve()):
            errors.append(f"{entry}: asset path escapes the repository")
            continue
        if value in seen:
            errors.append(f"{entry}: duplicate asset path")
        seen.add(value)
        expected_hash = item.get("sha256")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            errors.append(f"{entry}: invalid SHA-256")
        elif not path.is_file():
            errors.append(f"{entry}: missing asset {value}")
        elif digest(path.read_bytes()) != expected_hash:
            errors.append(f"{entry}: asset hash differs for {value}")
        if source_media:
            basename = item.get("source_basename")
            if (not isinstance(basename, str) or not basename or basename in {".", ".."}
                    or any(char in basename for char in ("/", "\\", "\0"))):
                errors.append(f"{entry}: invalid source basename")
            if item.get("status") not in ("prototype_photo", "unsuccessful_prototype_test", "concept_drawing"):
                errors.append(f"{entry}: unsupported prototype status")
            if item.get("byte_preserved") is not True:
                errors.append(f"{entry}: source media must preserve its original bytes")
            if "video" in item:
                video = item["video"]
                if not isinstance(video, dict):
                    errors.append(f"{entry}: invalid video metadata")
                    continue
                duration = video.get("duration_seconds")
                if (type(duration) not in (int, float)
                        or (type(duration) is float and not math.isfinite(duration))
                        or duration <= 0):
                    errors.append(f"{entry}: invalid video duration")
                for dimension in ("width", "height"):
                    if type(video.get(dimension)) is not int or video[dimension] <= 0:
                        errors.append(f"{entry}: invalid video {dimension}")
                frame_rate = video.get("nominal_frame_rate")
                if (not isinstance(frame_rate, str)
                        or not re.fullmatch(r"[1-9][0-9]*/[1-9][0-9]*", frame_rate)):
                    errors.append(f"{entry}: invalid nominal frame rate")
    return len(data[list_key])


def check_public_paths(errors):
    docs = ROOT / "docs"
    if docs.is_dir() and any(path.name.casefold() == "proposals" for path in docs.iterdir()):
        errors.append("Excluded private document directory exists")
    if not (ROOT / ".git").exists():
        return
    try:
        result = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"],
                                capture_output=True, check=False)
    except OSError:
        errors.append("Cannot inspect tracked paths: Git is unavailable")
        return
    if result.returncode:
        errors.append("Cannot inspect tracked paths")
        return
    excluded_name = re.compile(r"proposal|procurement|price[-_ ]*list", re.IGNORECASE)
    for encoded in result.stdout.split(b"\0"):
        if not encoded:
            continue
        path = PurePosixPath(encoded.decode("utf-8", errors="surrogateescape"))
        if (path.as_posix().casefold().startswith("docs/proposals/")
                or excluded_name.search(path.name)):
            errors.append("Excluded private document path is tracked")


def check(check_sources=False, source_roots=None):
    inventory = json.loads((ROOT / "docs/source-inventory.json").read_text())
    errors = []
    roots = {name: ROOT / value for name, value in inventory["source_roots"].items()}
    if source_roots:
        unknown = set(source_roots) - roots.keys()
        if unknown:
            print("FAIL: Unknown source root; use a name from the inventory", file=sys.stderr)
            return 1
        roots.update({name: Path(value).expanduser().resolve()
                      for name, value in source_roots.items()})
    for item in inventory["files"]:
        path = ROOT / item["destination"]
        if not path.is_file():
            errors.append(f"Missing imported file: {item['destination']}")
            continue
        content = path.read_bytes()
        if digest(content) != item["repository_sha256"]:
            errors.append(f"Imported file changed: {item['destination']}")
        if not item["changes"] and item["source_sha256"] != item["repository_sha256"]:
            errors.append(f"Undocumented content change: {item['destination']}")
        if check_sources:
            source = roots[item["source_root"]] / item["source"]
            if not source.is_file():
                errors.append(f"Original source missing: {item['source']}")
            else:
                original = source.read_bytes()
                if digest(original) != item["source_sha256"]:
                    errors.append(f"Original source changed: {item['source']}")
                if sanitize(source.name, original) != content:
                    errors.append(f"Import differs beyond permitted substitutions: {item['destination']}")

    for item in inventory["model_exports"]:
        path = ROOT / item["destination"]
        if not path.is_file():
            errors.append(f"Missing model archive: {item['destination']}")
            continue
        if digest(path.read_bytes()) != item["archive_sha256"]:
            errors.append(f"Model archive changed: {item['destination']}")
        try:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                top = Path(item["source"]).name
                if len(names) != len(set(names)):
                    errors.append(f"Duplicate ZIP entries: {path.name}")
                entries = []
                for name in names:
                    parts = PurePosixPath(name)
                    if parts.is_absolute() or ".." in parts.parts or not name.startswith(top + "/"):
                        errors.append(f"Unexpected ZIP member: {path.name}")
                        continue
                    entries.append((name[len(top) + 1:], archive.read(name)))
                if len(entries) != item["file_count"] or tree_digest(entries) != item["tree_sha256"]:
                    errors.append(f"Model contents differ: {path.name}")
        except (zipfile.BadZipFile, RuntimeError) as exc:
            errors.append(f"Invalid ZIP {path.name}: {type(exc).__name__}")
        if check_sources:
            source = roots[item["source_root"]] / item["source"]
            entries = [(p.relative_to(source).as_posix(), p.read_bytes())
                       for p in source.rglob("*") if p.is_file()]
            if len(entries) != item["file_count"] or tree_digest(entries) != item["tree_sha256"]:
                errors.append(f"Original model tree differs: {item['source']}")

    sketches = sorted((ROOT / "firmware").rglob("*.ino"))
    imported_sketches = {item["destination"] for item in inventory["files"]
                         if item["destination"].endswith(".ino")}
    if len(sketches) != 7 or {p.relative_to(ROOT).as_posix() for p in sketches} != imported_sketches:
        errors.append("Expected exactly the seven inventoried Arduino sketches")
    for path in sketches:
        if path.stem != path.parent.name:
            errors.append(f"Arduino sketch/folder mismatch: {path.relative_to(ROOT)}")
        content = path.read_text()
        patterns = [r'const char\*\s+(?:ssid|password)\s*=\s*"([^"\r\n]*)"',
                    r'#define WIFI_(?:SSID|PASS)\s+"([^"\r\n]*)"']
        for pattern in patterns:
            if any(value not in {"YOUR_WIFI_SSID", "YOUR_WIFI_PASSWORD"}
                   for value in re.findall(pattern, content)):
                errors.append(f"Non-placeholder Wi-Fi credential: {path.relative_to(ROOT)}")

    source_media_count = check_media_manifest("docs/media/source-media.json", "files",
                                             "destination", errors)
    generated_count = check_media_manifest("docs/media/generated-assets.json", "assets",
                                          "path", errors, optional=True)
    hardware_asset_count = check_media_manifest("hardware/assets/manifest.json", "assets",
                                               "path", errors)
    check_public_paths(errors)

    link_count = 0
    for path in sorted(set(ROOT.rglob("*.md")) | set(ROOT.rglob("*.html"))):
        if {".git", ".source-assets"}.intersection(path.relative_to(ROOT).parts):
            continue
        content = path.read_text()
        if content.count("```") % 2:
            errors.append(f"Unbalanced Markdown code fences: {path.relative_to(ROOT)}")
        references = [match.group(1).strip().strip("<>") for match in
                      re.finditer(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', content)]
        parser = AssetReferences()
        parser.feed(content)
        references.extend(parser.references)
        for reference in references:
            target = urlsplit(reference)
            if target.scheme or target.netloc or not target.path:
                continue
            link_count += 1
            if not (path.parent / unquote(target.path)).exists():
                errors.append(f"Broken relative link in {path.relative_to(ROOT)}: {target.path}")

    for error in errors:
        print("FAIL:", error, file=sys.stderr)
    if errors:
        return 1
    print(f"PASS: {len(inventory['files'])} imported files, {len(sketches)} sketches, "
          f"{len(inventory['model_exports'])} model archives, {source_media_count} source media, "
          f"{generated_count} generated assets, {hardware_asset_count} hardware asset files, "
          f"{link_count} relative links.")
    if check_sources:
        print("PASS: original source hashes, exact credential substitutions, and model trees.")
    return 0


def source_root_override(value):
    name, separator, path = value.partition("=")
    if not separator or not name.strip() or not path.strip():
        raise argparse.ArgumentTypeError("expected NAME=PATH with a nonempty name and path")
    return name, path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-sources", action="store_true",
                        help="Also compare originals at the paths recorded in the inventory")
    parser.add_argument("--source-root", action="append", type=source_root_override, default=[],
                        metavar="NAME=PATH", help="Override a source root for --check-sources; repeatable")
    args = parser.parse_args()
    if args.source_root and not args.check_sources:
        parser.error("--source-root requires --check-sources")
    sys.exit(check(args.check_sources, dict(args.source_root)))
