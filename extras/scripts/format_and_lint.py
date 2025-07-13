import subprocess
from argparse import ArgumentParser
from pathlib import Path


this_directory = Path(__file__).parent
project_root = this_directory.parent.parent


def run(cmd, check=True):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=check, cwd=project_root)


def main(directories: list[str]):
    dir_arg = " ".join(directories)
    run(f"ruff check {dir_arg} --fix")
    run(f"ruff format {dir_arg}")


def cli():
    parser = ArgumentParser()
    parser.add_argument(
        "--directories",
        nargs="+",
        help="List of directories to format and lint",
        default=["sqlmodel_yaml", "tests", "extras/examples", "extras/scripts"],
    )
    args = parser.parse_args()
    dir_paths = [project_root / directory for directory in args.directories]
    missing_paths = [d for d in dir_paths if not d.exists()]
    if missing_paths:
        paths_str = " ".join(str(i) for i in missing_paths)
        raise ValueError(
            f"Some directories are not accessible: {paths_str}. "
            f"Did forget to install this pacakge with 'pip install -e'?"
        )

    main(args.directories)


if __name__ == "__main__":
    cli()
