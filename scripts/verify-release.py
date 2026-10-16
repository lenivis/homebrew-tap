#!/usr/bin/env python3
"""Validate release metadata and the generated cask before importing it."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import plistlib
import re
import stat
import sys
import zipfile


SPARKLE = PurePosixPath("koe.app/Contents/Frameworks/Sparkle.framework")


def check_link(path, target):
    """Only Sparkle.framework's own relative links (Versions/Current, Sparkle, Resources...) are expected."""
    target = PurePosixPath(target)
    if SPARKLE not in path.parents or target.is_absolute():
        raise ValueError("Symbolic links are only expected inside Sparkle.framework.")
    resolved = []
    for part in (path.parent / target).parts:
        if part == "..":
            if not resolved:
                raise ValueError("Symbolic links must stay inside Sparkle.framework.")
            resolved.pop()
        elif part != ".":
            resolved.append(part)
    if SPARKLE not in PurePosixPath(*resolved).parents:
        raise ValueError("Symbolic links must stay inside Sparkle.framework.")


def verify(version, directory):
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        raise ValueError("Use MAJOR.MINOR.PATCH.")
    directory = Path(directory)
    metadata = json.loads((directory / "release.json").read_text())
    if metadata["isDraft"] or metadata["isPrerelease"] or metadata["tagName"] != f"v{version}":
        raise ValueError("Require a published, non-prerelease version.")
    name = f"koe-{version}-macos-arm64.zip"
    archive = directory / name
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    checksum = digest.hexdigest()
    # SHA256SUMS lists the disk image and the ZIP; the cask uses the ZIP.
    sums = {}
    for line in (directory / "SHA256SUMS").read_text().splitlines():
        fields = line.split()
        if len(fields) != 2 or fields[1] in sums:
            raise ValueError("Malformed release checksum file.")
        sums[fields[1]] = fields[0]
    if sums.get(name) != checksum:
        raise ValueError("Release checksum does not match the exact ZIP.")
    with zipfile.ZipFile(archive) as bundle:
        for entry in bundle.infolist():
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Unsafe archive path.")
            if not path.parts or path.parts[0] not in ["koe.app", "__MACOSX"]:
                raise ValueError("Unexpected top-level release content.")
            if stat.S_ISLNK(entry.external_attr >> 16):
                check_link(path, bundle.read(entry).decode("utf-8"))
        info = plistlib.loads(bundle.read("koe.app/Contents/Info.plist"))
        if info.get("CFBundleIdentifier") != "com.koe.dictation" or info.get("CFBundleShortVersionString") != version:
            raise ValueError("Unexpected app identity or version.")
    cask = (directory / "koe.rb").read_text()
    # Import only the expected declarative cask, not arbitrary release-supplied Ruby.
    expected = f'''cask "koe" do
  version "{version}"
  sha256 "{checksum}"

  url "https://github.com/YIPG/koe-releases/releases/download/v#{{version}}/koe-#{{version}}-macos-arm64.zip"
  name "koe"
  desc "Menu bar dictation for Japanese and English"
  homepage "https://saykoe.com/"

  livecheck do
    url "https://github.com/YIPG/koe-releases/releases/latest/download/appcast.xml"
    strategy :sparkle
  end

  auto_updates true
  depends_on arch: :arm64
  depends_on macos: :ventura

  app "koe.app"

  uninstall quit: "com.koe.dictation"

  zap trash: [
    "~/Library/Application Support/com.koe.dictation",
    "~/Library/Caches/com.koe.dictation",
    "~/Library/HTTPStorages/com.koe.dictation",
    "~/Library/Preferences/com.koe.dictation.plist",
    "~/Library/Saved Application State/com.koe.dictation.savedState",
  ]
end
'''
    if cask != expected:
        raise ValueError("The release cask differs from the reviewed declarative template.")
    print(f"Verified metadata and SHA-256 for {name}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: verify-release.py VERSION DOWNLOAD_DIRECTORY")
    try:
        verify(sys.argv[1], sys.argv[2])
    except (ValueError, OSError, KeyError, zipfile.BadZipFile, plistlib.InvalidFileException) as error:
        sys.exit(f"Release validation failed: {error}")
