from pathlib import Path
from argparse import ArgumentParser
import shutil

import build
import twine.commands.upload
from twine.settings import Settings

default_sdist_path = Path(__file__).parent.parent.parent / "sdist"


def build_python_package(sdist_dir: Path):
    this_file = Path(__file__).resolve()
    this_dir = this_file.parent
    project_root = this_dir.parent.parent

    if sdist_dir.exists():
        shutil.rmtree(sdist_dir)
    sdist_dir.mkdir(parents=True, exist_ok=True)

    try:
        builder = build.ProjectBuilder(project_root)
        builder.build("wheel", output_directory=str(sdist_dir.absolute()))
        builder.build("sdist", output_directory=str(sdist_dir.absolute()))
    except build.BuildException:
        raise build.BuildException(
            "Unable to find project root. Did you forget to install the project with 'pip install -e'?"
        )

    dist_files = [str(p) for p in sdist_dir.iterdir()]

    return dist_files


def publish(dist_files: list[str]):
    settings = Settings(
        verbose=True,
        repository_name="pypi",
    )
    twine.commands.upload.upload(settings, dist_files)


def main(sdist_dir: Path, publish_to_pypi: bool):
    dist_files = build_python_package(sdist_dir)
    if publish_to_pypi:
        publish(dist_files)


def cli():
    parser = ArgumentParser()
    parser.add_argument(
        "--sdist-dir",
        type=Path,
        default=default_sdist_path,
        help="Where to put the sdist files",
    )
    parser.add_argument(
        "--publish", action="store_true", help="Publish to PyPi after build"
    )
    args = parser.parse_args()
    main(args.sdist_dir, publish_to_pypi=args.publish)


if __name__ == "__main__":
    cli()
