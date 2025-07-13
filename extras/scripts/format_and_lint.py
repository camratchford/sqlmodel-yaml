import subprocess
from argparse import ArgumentParser
from pathlib import Path
from sys import exit

this_directory = Path(__file__).parent
project_root = this_directory.parent.parent


def run(cmd):
    print(f"Running: {cmd}")
    return subprocess.run(
        cmd,
        shell=True,
        text=True,
        cwd=project_root,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
        check=False,
    )


def main(directories: list[str], test_mode: bool):
    dir_arg = " ".join(directories)
    check_test_arg, format_test_arg = "", ""
    if test_mode:
        check_test_arg = "--exit-non-zero-on-fix"
        format_test_arg = "--check --exit-non-zero-on-fix"

    check_process = run(f"ruff check --show-fixes --fix {check_test_arg} {dir_arg}")
    format_process = run(f"ruff format {format_test_arg} {dir_arg}")

    # return code will be zero if both pass
    if test_mode:
        if check_process.returncode != 0:
            print(f"::error:: ruff check encountered changes: {check_process.stdout}")
        if format_process.returncode != 0:
            print(f"::error:: ruff format encountered changes: {format_process.stdout}")

        exit(check_process.returncode + format_process.returncode)


def cli():
    parser = ArgumentParser()
    parser.add_argument(
        "--test",
        action="store_true",
        help="Exits with error if ruff needs to make changes",
    )
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
            f""
        )

    main(directories=args.directories, test_mode=args.test)


if __name__ == "__main__":
    cli()
