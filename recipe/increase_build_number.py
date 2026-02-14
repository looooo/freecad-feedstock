#!/usr/bin/env python

import re
import requests

API_URL = "https://api.github.com/repos/FreeCAD/FreeCAD/releases"


def get_latest_freecad_weekly_source_and_sha():
    """
    Gibt zurück:
    (source_url, sha256_string)
    """

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    for release in response.json():
        if release.get("prerelease") and release.get("tag_name", "").startswith("weekly-"):

            source_url = None
            sha_url = None
            source_filename = None

            for asset in release.get("assets", []):
                name = asset.get("name", "")

                if name.startswith("freecad_source_weekly") and name.endswith(".tar.gz"):
                    source_url = asset["browser_download_url"]
                    source_filename = name

                elif name.endswith(".tar.gz-SHA256.txt"):
                    sha_url = asset["browser_download_url"]

            if source_url and sha_url:
                # SHA-Datei herunterladen
                sha_response = requests.get(sha_url, timeout=30)
                sha_response.raise_for_status()

                # Beispielzeile:
                # bca0587...39fe  freecad_source_weekly-2026.02.11.tar.gz
                for line in sha_response.text.splitlines():
                    if source_filename in line:
                        sha256_value = line.split()[0]
                        return source_url, sha256_value

                raise RuntimeError("SHA256 für Source-Datei nicht gefunden.")

    raise RuntimeError("Kein vollständiges Weekly-Release gefunden.")



# read meta.yaml file
with open("recipe/meta.yaml", "r") as f:
    text = f.read()

# increase build number
build_number_old = int(re.search(r"(?<={% set build_number = )\d+", text)[0])
build_number_new = build_number_old + 1
print(f"set build_number from build_number {build_number_old} to {build_number_new}")
text = re.sub(r"(?<={% set build_number = )\d+", str(build_number_new), text)

url, sha256 = get_latest_freecad_weekly_source_and_sha()

# set sha256sum
print(f"set sha256:  {sha256}")
text = re.sub(r'(?<={% set sha256sum = ")[^"]+(?=" %})', sha256, text)

# write download
print(f"set url:  {url}")
text = re.sub(r'(?<={% set url = ")[^"]+(?=" %})', url, text)

# write meta.yaml file
with open("recipe/meta.yaml", "w") as f:
    f.write(text)