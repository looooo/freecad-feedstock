#!/usr/bin/env python3
"""Upload built conda packages to exactly one destination.

Upload settings come from the matrix config file (``.ci_support/<config>.yaml``)
using ``mirror`` and ``channel_targets``:

* ``anaconda`` (default): ``channel_targets`` is ``<channel> <label>``
* ``prefix``: ``channel_targets`` is the prefix.dev channel name
* ``github``: ``channel_targets`` is ``<owner>/<repo>`` for GitHub Releases
* ``url``: ``channel_targets`` is a full channel URL on a prefix-compatible server

Optional ``mirror_url`` sets the server base URL (for ``prefix``/``url`` mirrors).

When ``mirror`` is omitted, ``anaconda`` is used. When ``channel_targets`` is
omitted, ``conda-forge main`` is used.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass


DEFAULT_UPLOAD_MIRROR = "anaconda"
DEFAULT_CHANNEL_TARGET = "conda-forge main"


@dataclass(frozen=True)
class UploadTarget:
    mirror: str
    channel_target: str
    mirror_url: str | None = None


def _load_yaml(path):
    try:
        from ruamel.yaml import YAML
    except ImportError:
        import yaml

        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    else:
        yaml = YAML(typ="safe")
        with open(path, encoding="utf-8") as fh:
            return yaml.load(fh) or {}


def _first(value, default=None):
    items = _as_list(value)
    return items[0] if items else default


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item]
    return [str(value)]


def resolve_upload_target(config):
    """Resolve mirror settings from a rendered matrix config."""
    prefix_channels = _as_list(config.get("prefix_dev_channels"))
    if prefix_channels:
        return UploadTarget(
            mirror="prefix",
            channel_target=prefix_channels[0],
            mirror_url=_first(config.get("prefix_dev_url"), "https://prefix.dev"),
        )

    mirror = (_first(config.get("mirror"), DEFAULT_UPLOAD_MIRROR) or DEFAULT_UPLOAD_MIRROR).lower()
    channel_target = _first(config.get("channel_targets"), DEFAULT_CHANNEL_TARGET)
    mirror_url = _first(config.get("mirror_url"))

    if mirror == "prefix" and not mirror_url:
        mirror_url = "https://prefix.dev"

    return UploadTarget(
        mirror=mirror,
        channel_target=channel_target,
        mirror_url=mirror_url,
    )


def _should_upload():
    if os.environ.get("UPLOAD_PACKAGES", "").lower() == "false":
        return False
    if os.environ.get("IS_PR_BUILD", "").lower() != "false":
        return False
    upload_on_branch = os.environ.get("UPLOAD_ON_BRANCH")
    if upload_on_branch:
        git_branch = os.environ.get("GIT_BRANCH")
        if git_branch and upload_on_branch != git_branch:
            print(
                f"The branch {git_branch} is not configured to be uploaded "
                f"(UPLOAD_ON_BRANCH={upload_on_branch})."
            )
            return False
    return True


def _supports_trusted_publishing():
    return os.environ.get("GITHUB_ACTIONS", "").lower() == "true"


def _find_built_packages(feedstock_root):
    build_root = os.environ.get(
        "CONDA_BLD_PATH", os.path.join(feedstock_root, "build_artifacts")
    )
    patterns = [
        os.path.join(build_root, "*", "*.conda"),
        os.path.join(build_root, "*", "*.tar.bz2"),
    ]
    packages = []
    for pattern in patterns:
        packages.extend(glob.glob(pattern))
    return sorted(set(packages))


def _ensure_pixi():
    pixi = shutil.which("pixi")
    if pixi:
        return pixi

    for installer in (
        ["micromamba", "install", "-y", "-c", "conda-forge", "pixi"],
        ["conda", "install", "-y", "-c", "conda-forge", "pixi"],
    ):
        if shutil.which(installer[0]):
            subprocess.check_call(installer)
            pixi = shutil.which("pixi")
            if pixi:
                return pixi

    raise RuntimeError(
        "Could not find or install pixi, which is required for this upload mirror."
    )


def _upload_to_prefix(target, feedstock_root):
    if not _supports_trusted_publishing():
        raise RuntimeError(
            "mirror=prefix requires prefix.dev trusted publishing on GitHub Actions."
        )

    packages = _find_built_packages(feedstock_root)
    if not packages:
        print("No built packages found for prefix.dev upload.")
        return True

    pixi = _ensure_pixi()
    prefix_url = target.mirror_url or "https://prefix.dev"

    for package in packages:
        cmd = [
            pixi,
            "upload",
            "prefix",
            "--channel",
            target.channel_target,
            "--url",
            prefix_url,
            "--skip-existing",
            package,
        ]
        print(
            f"Uploading {package} to prefix.dev channel "
            f"{target.channel_target!r} via trusted publishing..."
        )
        subprocess.check_call(cmd)

    return True


def _upload_to_anaconda(feedstock_root, recipe_root, config_file, args):
    cmd = ["upload_package"]
    if args.validate:
        cmd.extend(["--validate", f"--feedstock-name={args.feedstock_name}"])
    if args.private:
        cmd.append("--private")
    cmd.extend([feedstock_root, recipe_root, config_file])
    subprocess.check_call(cmd)
    return True


def _github_repo(target):
    repo = target.channel_target.strip()
    if "/" in repo:
        return repo
    repository = os.environ.get("GITHUB_REPOSITORY")
    if repository:
        return repository
    raise RuntimeError(
        "mirror=github requires channel_targets to be owner/repo or GITHUB_REPOSITORY."
    )


def _github_release_tag():
    tag = os.environ.get("GITHUB_REF_NAME") or os.environ.get("GIT_BRANCH")
    if not tag:
        raise RuntimeError(
            "mirror=github requires GITHUB_REF_NAME or GIT_BRANCH to identify the release."
        )
    return tag


def _upload_to_github(target, feedstock_root):
    if not shutil.which("gh"):
        raise RuntimeError("mirror=github requires the GitHub CLI (gh) on PATH.")

    packages = _find_built_packages(feedstock_root)
    if not packages:
        print("No built packages found for GitHub release upload.")
        return True

    repo = _github_repo(target)
    tag = _github_release_tag()
    cmd = ["gh", "release", "upload", tag, *packages, "--repo", repo, "--clobber"]
    print(f"Uploading {len(packages)} package(s) to GitHub release {tag!r} on {repo}...")
    subprocess.check_call(cmd)
    return True


def _split_prefix_url(url):
    match = re.match(r"(https?://[^/]+)(?:/(.+))?", url.rstrip("/"))
    if not match:
        raise RuntimeError(f"Could not parse channel URL {url!r}.")
    base_url, channel = match.groups()
    if not channel:
        raise RuntimeError(
            f"Channel URL {url!r} must include a channel path, e.g. "
            "https://prefix.dev/my-channel."
        )
    return base_url, channel


def _upload_to_url(target, feedstock_root):
    if not _supports_trusted_publishing():
        raise RuntimeError(
            "mirror=url with prefix-compatible servers requires GitHub Actions OIDC."
        )

    channel_url = target.channel_target
    if target.mirror_url:
        channel_url = target.mirror_url.rstrip("/")
        if target.channel_target:
            channel_url = f"{channel_url}/{target.channel_target.lstrip('/')}"

    base_url, channel = _split_prefix_url(channel_url)
    packages = _find_built_packages(feedstock_root)
    if not packages:
        print("No built packages found for URL upload.")
        return True

    pixi = _ensure_pixi()
    for package in packages:
        cmd = [
            pixi,
            "upload",
            "prefix",
            "--channel",
            channel,
            "--url",
            base_url,
            "--skip-existing",
            package,
        ]
        print(f"Uploading {package} to {base_url} channel {channel!r}...")
        subprocess.check_call(cmd)

    return True


def upload_built_packages(feedstock_root, recipe_root, config_file, args):
    if not _should_upload():
        return True

    config = _load_yaml(config_file)
    target = resolve_upload_target(config)

    if target.mirror == "prefix":
        return _upload_to_prefix(target, feedstock_root)
    if target.mirror == "anaconda":
        return _upload_to_anaconda(feedstock_root, recipe_root, config_file, args)
    if target.mirror == "github":
        return _upload_to_github(target, feedstock_root)
    if target.mirror == "url":
        return _upload_to_url(target, feedstock_root)

    raise RuntimeError(
        f"Unsupported upload mirror {target.mirror!r}. "
        "Supported values: anaconda, prefix, github, url."
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feedstock_root")
    parser.add_argument("recipe_root")
    parser.add_argument("config_file")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--feedstock-name")
    parser.add_argument("--private", action="store_true")
    args = parser.parse_args(argv)

    if args.validate and not args.feedstock_name:
        print(
            "upload_built_packages.py: --feedstock-name is required with --validate",
            file=sys.stderr,
        )
        return 2

    upload_built_packages(
        args.feedstock_root,
        args.recipe_root,
        args.config_file,
        args,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
