import re
import sys
import subprocess
from pathlib import Path
from packaging.version import Version
import argparse
from os import getenv

from github import Github

this_directory = Path(__file__).parent
project_root = this_directory.parent.parent
pyproject_dot_toml = project_root / "pyproject.toml"


def get_current_version() -> Version:
    content = pyproject_dot_toml.read_text()
    match = re.search(r'^version\s*=\s*["\'](.+?)["\']', content, re.MULTILINE)
    if not match:
        sys.exit("Version not found in pyproject.toml")
    return Version(match.group(1))


def get_new_version(version: Version, kind: str) -> str:
    if kind == "patch":
        return f"{version.major}.{version.minor}.{version.micro + 1}"
    elif kind == "minor":
        return f"{version.major}.{version.minor + 1}.0"
    elif kind == "major":
        return f"{version.major + 1}.0.0"
    elif kind == "dev":
        return f"{version.major}.{version.minor}.{version.micro + 1}.dev0"
    else:
        sys.exit(f"Invalid bump type: {kind}")


def set_new_version(new_version: str):
    content = pyproject_dot_toml.read_text()
    new_content = re.sub(
        r'(^version\s*=\s*["\'])(.+?)(["\'])',
        rf'version = "{new_version}"',
        content,
        flags=re.MULTILINE,
    )
    pyproject_dot_toml.write_text(new_content)


def run(cmd, check=True):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=check, cwd=project_root)


def create_release(version):
    github_token = getenv("GITHUB_TOKEN")
    if not github_token:
        raise RuntimeError("GITHUB_TOKEN environment variable not set")

    github_client = Github(github_token)
    github_repo = github_client.get_repo("camratchford/sqlmodel-yaml")

    release = github_repo.create_git_release(
        tag=version,
        name=version,
        message="Release notes here",
        draft=False,
        prerelease=False,
    )
    print(f"Release {release.title} created: {release.html_url}")


def git_tag(version: str):
    run(f"git add {pyproject_dot_toml}")
    run(f'git commit -m "Release {version}"')
    run(f"git tag v{version}")
    run("git push")
    run(f"git push origin v{version}")


def main(
    patch_release: bool,
    minor_release: bool,
    major_release: bool,
    dry_run: bool = False,
    no_release: bool = False,
) -> None:
    kind = (
        "patch"
        if patch_release
        else "minor"
        if minor_release
        else "major"
        if major_release
        else "dev"
    )
    current_version = get_current_version()
    new_version = get_new_version(current_version, kind)

    print(f"Bumping version: {current_version} → {new_version}")
    if not dry_run:
        set_new_version(new_version)
        git_tag(new_version)
        if not no_release:
            create_release(new_version)


def cli():
    parser = argparse.ArgumentParser(description="Bump version and create release.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--patch", action="store_true", help="Bump patch version (x.y.z → x.y.z+1)"
    )
    group.add_argument(
        "--minor", action="store_true", help="Bump minor version (x.y.z → x.y+1.0)"
    )
    group.add_argument(
        "--major", action="store_true", help="Bump major version (x.y.z → x+1.0.0)"
    )
    group.add_argument(
        "--dev",
        action="store_true",
        help="Bump to next patch with dev suffix (x.y.z → x.y.z+1.dev0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show log messages, do not modify version in any way",
    )
    parser.add_argument(
        "--no-release", action="store_true", help="Skip doing a github release"
    )
    args = parser.parse_args()

    main(
        patch_release=args.patch,
        minor_release=args.minor,
        major_release=args.major,
        dry_run=args.dry_run,
        no_release=args.no_release,
    )


if __name__ == "__main__":
    cli()
